"""Character agents powered by Anthropic Claude API"""
import os
import json
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Model candidates to try (in order of preference)
MODEL_CANDIDATES = [
    # Primary choice for Bible Game
    "claude-sonnet-4-6",
    # Other Claude models (high priority)
    "claude-opus-4-6",
    "claude-sonnet-4-5-20250929",
    "claude-opus-4-5-20250514",
    "claude-haiku-4-5-20251001",
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    # GPT models (fallback)
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gpt-5.4-2026-03-05",
    "gpt-5.4-mini-2026-03-17",
    # Gemini models (last resort)
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

# Cache for the validated model
_VALIDATED_MODEL = None

def get_available_model():
    """Find and return the first available model from candidates"""
    global _VALIDATED_MODEL
    
    if _VALIDATED_MODEL:
        return _VALIDATED_MODEL
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("[WARNING] No ANTHROPIC_API_KEY found - will fail on first API call", file=sys.stderr)
        return MODEL_CANDIDATES[0]
    
    print(f"[DEBUG] Testing {len(MODEL_CANDIDATES)} model candidates...", file=sys.stderr)
    client = Anthropic(api_key=api_key)
    
    for i, model in enumerate(MODEL_CANDIDATES):
        try:
            print(f"[DEBUG] Testing model {i+1}/{len(MODEL_CANDIDATES)}: {model}", file=sys.stderr)
            # Quick test with minimal request
            client.messages.create(
                model=model,
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}]
            )
            _VALIDATED_MODEL = model
            print(f"\n✅ [SUCCESS] Found working model: {model}\n", file=sys.stderr)
            return model
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not_found" in error_msg.lower():
                print(f"[DEBUG]   -> Not available (404)", file=sys.stderr)
            else:
                print(f"[DEBUG]   -> Error: {error_msg[:50]}", file=sys.stderr)
            continue
    
    # If no model works, return the first candidate
    print(f"\n⚠️ [WARNING] No working model found! Will try {MODEL_CANDIDATES[0]} anyway\n", file=sys.stderr)
    return MODEL_CANDIDATES[0]

# Get the model at module load time
print("[STARTUP] Initializing character_agent module...", file=sys.stderr)
ANTHROPIC_MODEL = get_available_model()
print(f"[STARTUP] Using ANTHROPIC_MODEL = {ANTHROPIC_MODEL}", file=sys.stderr)


def call_api_with_fallback(client, system_prompt, messages, max_tokens=400, temperature=0.4):
    """Call Anthropic API, trying multiple models if needed"""
    
    # First try the pre-validated model
    models_to_try = [ANTHROPIC_MODEL] + [m for m in MODEL_CANDIDATES if m != ANTHROPIC_MODEL]
    
    last_error = None
    for model in models_to_try:
        try:
            print(f"[API] Trying model: {model}", file=sys.stderr)
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            print(f"[API] ✅ Success with model: {model}", file=sys.stderr)
            return response
        except Exception as e:
            error_msg = str(e)
            last_error = e
            if "404" in error_msg or "not_found" in error_msg.lower():
                print(f"[API] Model not found: {model}, trying next...", file=sys.stderr)
                continue
            else:
                # Non-404 errors should probably stop the loop
                print(f"[API] Error with {model}: {error_msg[:60]}", file=sys.stderr)
                raise
    
    # If we get here, all models failed with 404
    print(f"[API] ❌ All models returned 404!", file=sys.stderr)
    raise last_error if last_error else Exception("No working model found")


class CharacterAgent:
    """Base character agent for dialogue"""

    def __init__(self, character_id: str, character_data: dict, sources_data: dict = None):
        self.character_id = character_id
        self.name = character_data.get("name", character_id.capitalize())
        self.theology = character_data.get("theology", {})
        self.personality = character_data.get("personality", "")
        self.teaching_areas = character_data.get("teaching_areas", [])
        self.conversation_history = []
        self.sources_data = sources_data or {}

    def get_system_prompt(self) -> str:
        """Generate system prompt with character theology and personality"""
        
        personality = self.personality
        key_verses = ', '.join(self.theology.get('key_verses', [])[:3]) if self.theology else ''
        
        # Build additional sources text from character-specific sources
        additional_sources = self.theology.get('additional_sources', [])
        sources_text = ""
        if additional_sources:
            sources_text = "\n\nADDITIONAL AUTHORIZED SOURCES:\n"
            for source in additional_sources:
                sources_text += f"- {source.get('book', 'Unknown')} by {source.get('author', 'Unknown')}\n"
                if source.get('relevant_passages'):
                    passages = ', '.join(source.get('relevant_passages', []))
                    sources_text += f"  Passages: {passages}\n"
        
        # Build primary reference sources text
        primary_sources_text = ""
        if self.sources_data and 'primary_references' in self.sources_data:
            primary_sources_text = "\n\nPRIMARY REFERENCE SOURCES FOR ALL WISDOM:\n"
            for ref in self.sources_data['primary_references']:
                primary_sources_text += f"- {ref.get('title', 'Unknown')} by {ref.get('author', 'Unknown')}\n"
                primary_sources_text += f"  Focus: {ref.get('focus', 'General knowledge')}\n"
        
        return f"""You ARE {self.name} from the King James Version 1611 Holy Bible.

CRITICAL - PRIMARY SOURCE IS KJV 1611:
- Thy words MUST primarily be from the KJV 1611 Bible
- NO modern commentary, explanations, or filler words
- NO "Absolutely," "Here's," "Let me explain," "As I mentioned"
- Quote exact KJV 1611 verses first, then add context from authorized sources
- Speak ONLY the words {self.name} spoke in Scripture and authorized texts

THY CHARACTER:
- Name: {self.name}
- Personality: {personality}
- Language: KJV 1611 style (thee, thou, thy, verily, behold, shall, unto)

STRICT RULES:
1. First-person ONLY: "I, me, my, mine" - NEVER third-person
2. Address player as "thee" or "thou"
3. NO modern words: "Absolutely," "Explanation," "Here's," "Actually," "Of course"
4. Begin with KJV Scripture quote, then draw from authorized sources
5. End with: " - Book Chapter:Verse (Source)"
6. Only use authorized sources listed below - NO other books
7. When appropriate, include visual content using: [IMAGE: detailed description of visualization]

VISUAL ILLUSTRATION FORMAT:
Include images to enhance teaching when relevant, using this format:
[IMAGE: Detailed description of a map showing ancient Israel with the twelve tribes]
[IMAGE: Diagram of the Tabernacle layout with the Holy of Holies and brass altar]
[IMAGE: Timeline of biblical events from Creation through the prophets]
[IMAGE: Chart showing the genealogy of kings of Israel and Judah]

ILLUSTRATION EXAMPLES:
"Behold the glory of the Tabernacle:
[IMAGE: Bird's eye view diagram of the Tabernacle showing the Holy of Holies containing the Ark, the altar of incense, the table of showbread, the lampstand, and the bronze altar in the outer court]
The Tabernacle was the dwelling place of God among His people. - Exodus 25:8 (KJV 1611)"

"Consider the waters at Creation:
[IMAGE: Map showing the division of waters under the firmament from waters above, with the Earth at the center surrounded by the cosmic waters, as described in Genesis]
In the beginning God created the heaven and the earth. - Genesis 1:1 (KJV 1611)"{primary_sources_text}{sources_text}

THY VERSES: {key_verses}

WRONG:
"Absolutely! Here's an explanation..." or "As I mentioned earlier..."

CORRECT:
"In the beginning God created the heaven and the earth. - Genesis 1:1 (KJV 1611)"
"I and my Father are one. - John 10:30 (KJV 1611)"""

    def _extract_illustrations(self, text: str) -> tuple[str, list]:
        """Extract [IMAGE: ...] tags from response and return cleaned text and image list"""
        import re
        
        # Find all [IMAGE: ...] patterns
        image_pattern = r'\[IMAGE:\s*([^\]]+)\]'
        illustrations = []
        
        matches = list(re.finditer(image_pattern, text))
        for match in matches:
            description = match.group(1).strip()
            if description:
                illustrations.append({
                    "description": description,
                    "type": "illustration"
                })
        
        # Remove all [IMAGE: ...] tags from text
        cleaned_text = re.sub(image_pattern, '', text).strip()
        
        # Clean up any extra whitespace that might result
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text, illustrations

    def get_dialogue_response(self, player_name: str, player_message: str) -> dict:
        """Get character response to player message using Anthropic Claude API
        Returns dict with 'text' and 'illustrations' keys"""
        
        # Build conversation context
        full_message = f"{player_name}: {player_message}"
        
        try:
            # Initialize Anthropic client
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                return f"Forgive me, {player_name}. The API key is not configured. Please set ANTHROPIC_API_KEY environment variable."
            
            client = Anthropic(api_key=api_key)
            
            # Get system prompt and build messages
            system_prompt = self.get_system_prompt()
            
            # Build conversation history for context
            messages = []
            for msg in self.conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": player_message})
            
            # Call Anthropic API with fallback model handling
            response = call_api_with_fallback(client, system_prompt, messages)
            
            # Extract response content
            raw_response = response.content[0].text.strip()
            
            print(f"\n[DEBUG] Raw model response: {raw_response[:200]}...")
            
            character_response = raw_response
            
            # Extract illustrations BEFORE cleaning text
            character_response, illustrations = self._extract_illustrations(character_response)
            
            print(f"[DEBUG] Extracted {len(illustrations)} illustrations from response")
            if illustrations:
                for i, ill in enumerate(illustrations):
                    print(f"[DEBUG]   Illustration {i+1}: {ill['description'][:80]}...")
            
            # Light cleaning - only remove clear instructional/meta text
            forbidden_starts = [
                "Here are", "Here is", "For example", "Suggestions:",
                "Yes, of course", "Examples:",
                "Absolutely", "Here's", "Let me explain", "As I mentioned",
                "Of course", "Actually", "Well,", "So,", "You see,",
                "In conclusion", "To summarize", "In summary"
            ]
            
            # Remove lines that start with forbidden phrases (case insensitive)
            lines = character_response.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Skip lines starting with forbidden phrases (with word boundary check)
                if any(line.lower().startswith(forbidden.lower()) for forbidden in forbidden_starts):
                    continue
                cleaned_lines.append(line)
            
            character_response = ' '.join(cleaned_lines).strip()
            
            # Stop at any stop sequences (including multiple Q&A patterns)
            stop_sequences = [
                "###", "Player:", "User:", "System:", "Assistant:", 
                "\n\nPlayer", "Question:", "Q:", "A:",
                "Another question", "If thou asketh", "Should thou ask"
            ]
            for stop in stop_sequences:
                if stop in character_response:
                    character_response = character_response.split(stop)[0].strip()
            
            print(f"[DEBUG] Cleaned response: {character_response[:200]}...")
            
            if not character_response:
                # Fallback: return raw response if cleaning removed everything
                if raw_response:
                    print(f"[DEBUG] Using raw response as fallback")
                    # Re-extract illustrations from raw response
                    character_response, illustrations = self._extract_illustrations(raw_response)
            
            # Final cleaning - remove third-person and modern filler phrases
            forbidden_phrases = [
                f"{self.name} said", f"{self.name} says", f"{self.name} spoke",
                "He said", "She said", "He says", "She says",
                "The scriptures say", "According to", "In the Bible",
                "Response:", "Answer:",
                "I think", "I believe that", "In my opinion", "I feel",
                "Psychology", "Therapy", "Meditation technique",
                "Self-help", "Personal growth", "Mindfulness",
                "Inner peace", "Find yourself", "Discover your",
                "Visualize", "Manifest", "Energy", "Universe",
                "Absolutely", "Actually", "Of course", "Well,", "So,", "You see,",
                "Let me explain", "As I mentioned", "As I said earlier"
            ]
            for phrase in forbidden_phrases:
                if phrase in character_response:
                    character_response = character_response.replace(phrase, "").strip()
            
            # Clean up double spaces and normalize
            character_response = ' '.join(character_response.split())
            
            # Ensure it starts with first-person if possible
            first_person_starts = ["I ", "My ", "Mine ", "Me ", "Verily,", "Behold,"]
            if character_response and not any(character_response.startswith(fp) for fp in first_person_starts):
                # If response doesn't start with I/My, check if we need to prefix
                if not character_response.startswith(("Thou", "Thee")):
                    character_response = "I say unto thee, " + character_response
            
            # Final check
            if not character_response:
                return {
                    "text": f"Forgive me, {player_name}. I could not generate a proper response. Please try again.",
                    "illustrations": []
                }
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": full_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": character_response
            })
            
            return {
                "text": character_response,
                "illustrations": illustrations
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n[CLAUDE ERROR FULL] {type(e).__name__}: {error_msg}\n")
            import traceback
            traceback.print_exc()
            return {
                "text": f"Forgive me, {player_name}. A difficulty hath arisen: {error_msg}",
                "illustrations": []
            }

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []


class CharacterAgentFactory:
    """Factory to create character agents"""

    def __init__(self, character_profiles_path: str = None):
        """Initialize with character profiles"""
        if character_profiles_path is None:
            # Get path relative to this file's location (src/agents/)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            character_profiles_path = os.path.join(project_root, "config", "character_profiles.json")
        
        self.character_data = {}
        self.groups_data = {}
        self.sources_data = {}
        self._load_character_profiles(character_profiles_path)
        self.agents = {}

    def _load_character_profiles(self, path: str) -> None:
        """Load character profiles, groups, and sources from JSON"""
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.character_data = data.get("characters", {})
                    self.groups_data = data.get("groups", {})
                    self.sources_data = data.get("sources", {})
                    return
        except Exception as e:
            print(f"Error loading character profiles: {e}")
        
        # Return default minimal profiles if file doesn't exist
        self.character_data = {
            "jesus": {"name": "Jesus", "theology": {}, "personality": "Compassionate and wise", "teaching_areas": ["Grace", "Love", "Redemption"]},
            "david": {"name": "David", "theology": {}, "personality": "Repentant and hopeful", "teaching_areas": ["Psalms", "Faith", "Worship"]},
            "solomon": {"name": "Solomon", "theology": {}, "personality": "Wise and reflective", "teaching_areas": ["Wisdom", "Vanity", "Truth"]},
        }
        self.groups_data = {
            "theology": {
                "name": "Theology & Scripture",
                "description": "Learn biblical theology",
                "characters": ["jesus", "david", "solomon"]
            }
        }
        self.sources_data = {}

    def get_agent(self, character_id: str) -> CharacterAgent:
        """Get or create character agent"""
        character_id = character_id.lower()
        
        if character_id not in self.agents:
            # Get character data
            char_data = self.character_data.get(character_id, {
                "name": character_id.capitalize(),
                "theology": {},
                "personality": "",
                "teaching_areas": []
            })
            
            # Create agent with sources data
            self.agents[character_id] = CharacterAgent(character_id, char_data, self.sources_data)
        
        return self.agents[character_id]

    def get_all_characters(self) -> list:
        """Get list of all available characters"""
        return list(self.character_data.keys())
    
    def get_groups(self) -> dict:
        """Get all character groups with their info"""
        return self.groups_data
    
    def get_characters_by_group(self, group_id: str) -> dict:
        """Get all characters in a specific group"""
        if group_id not in self.groups_data:
            return None
        
        group = self.groups_data[group_id]
        characters_list = []
        
        for char_id in group.get("characters", []):
            if char_id in self.character_data:
                char_data = self.character_data[char_id]
                characters_list.append({
                    "id": char_id,
                    "name": char_data.get("name", char_id),
                    "title": char_data.get("title", ""),
                    "personality": char_data.get("personality", ""),
                    "avatar": char_data.get("avatar", "👤"),
                    "birth_date": char_data.get("birth_date", ""),
                    "death_date": char_data.get("death_date", "")
                })
        
        return {
            "group_id": group_id,
            "group_name": group.get("name", ""),
            "group_description": group.get("description", ""),
            "characters": characters_list
        }
    
    def get_sources(self) -> dict:
        """Get all primary reference sources for character knowledge"""
        return self.sources_data


# Global factory instance
_factory = None

def get_character_agent(character_id: str) -> CharacterAgent:
    """Get character agent (singleton factory)"""
    global _factory
    if _factory is None:
        _factory = CharacterAgentFactory()
    return _factory.get_agent(character_id)

def get_all_characters() -> list:
    """Get all available characters"""
    global _factory
    if _factory is None:
        _factory = CharacterAgentFactory()
    return _factory.get_all_characters()

def get_character_groups() -> dict:
    """Get all character groups"""
    global _factory
    if _factory is None:
        _factory = CharacterAgentFactory()
    return _factory.get_groups()

def get_characters_in_group(group_id: str) -> dict:
    """Get all characters in a specific group"""
    global _factory
    if _factory is None:
        _factory = CharacterAgentFactory()
    return _factory.get_characters_by_group(group_id)

def get_reference_sources() -> dict:
    """Get all primary reference sources for character wisdom"""
    global _factory
    if _factory is None:
        _factory = CharacterAgentFactory()
    return _factory.get_sources()
