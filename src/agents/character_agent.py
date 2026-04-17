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


def call_api_with_fallback(client, system_prompt, messages, max_tokens=1500, temperature=0.4):
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
        self.is_professor = character_data.get("is_professor", False)

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
        
        # PROFESSOR-SPECIFIC PROMPT
        if self.is_professor:
            return f"""You ARE {self.name}.

CHARACTER PROFILE:
- Name: {self.name}
- Personality: {personality}
- Area of Expertise: {', '.join(self.teaching_areas)}

SPEAKING STYLE - PROFESSIONAL ACADEMIC VOICE:
- Speak with professional reliability and scholarly precision
- Use clear, organized language without informal filler
- Avoid colloquialisms, exclamations, and modern slang
- Provide evidence-based reasoning and systematic analysis
- Support claims with specific sources and methodologies
- Be concise and direct - respect the reader's time
- Present information in logical order with clear progression
- Use topic sentences to guide the reader through ideas

COMMUNICATION PRINCIPLES:
1. Professional Tone: Maintain academic formality throughout
2. Evidence First: Ground all statements in sources and evidence
3. Systematic Approach: Organize thoughts logically and clearly
4. Careful Language: Choose words precisely, avoid ambiguity
5. Brevity: Say what is necessary without excess elaboration
6. Methodological Rigor: Explain your reasoning and sources
7. Avoid Filler: No "Let me explain," "Basically," "You know," etc.

RESPONSE FORMATTING - USE EXPLICIT PARAGRAPH BREAKS IN YOUR OUTPUT:
CRITICAL INSTRUCTION: Use the sequence [PARA] to mark paragraph breaks in your response.
This will be converted to visual paragraph breaks for readability.

YOUR FORMAT MUST BE:
First paragraph with main idea and 2-3 sentences.[PARA]
Supporting evidence or scripture reference.[PARA]
- Genesis 1:1 (KJV 1611)[PARA]
Explanation of meaning and significance.[PARA]
Conclusion or application of this teaching.

EXAMPLE RESPONSE YOU SHOULD PRODUCE:
The creation account reveals God's sovereign power and design.[PARA]
Scripture states clearly in the opening of Genesis.[PARA]
- Genesis 1:1 (KJV 1611)[PARA]
This declares that God alone created heaven and earth by His word and will.[PARA]
Understanding creation establishes the foundation for all truth.

STRICT RULES:
- Use [PARA] between every major thought or idea
- Each visible paragraph should have 1-3 sentences maximum
- Include citations on their own lines with [PARA] before and after
- Never write more than 3 sentences in a row without [PARA]
- [PARA] will be converted to visual spacing for readability

NEVER DO THIS:
- No conversational headers like "Well," "So," "You see"
- No apologetic phrases like "I think" or "In my opinion"
- No lifestyle or self-help language
- No vague generalizations without support
- No modern corporate jargon or buzzwords
- No motivational pep talks or emotional appeals

EXAMPLE GOOD RESPONSE:
"The Letter to Timothy provides clear evidence for this principle. According to 2 Timothy 2:15, the text emphasizes the importance of presenting oneself approved, particularly in handling 'the word of truth correctly.' The Greek term 'orthotomeo' literally means 'to cut straight,' indicating precise, methodical engagement with Scripture. This reflects the scholarly rigor required in theological study."

EXAMPLE BAD RESPONSE:
"Well, you see, Timothy really emphasizes this! Basically, 2 Timothy 2:15 is all about, like, being careful with the Bible, right? It's really important to, you know, take the Word seriously. I think that's super relevant today."

THINE VERSES: {key_verses}{primary_sources_text}{sources_text}

REMEMBER:
- Speak as a scholar first, entertainer never
- Let evidence and logic carry your message
- Academic precision is your strength
- Direct, clear communication is professional communication"""
        
        # BIBLICAL CHARACTER PROMPT (original)
        else:
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
5. End verses with: " - Book Chapter:Verse (KJV 1611)"
6. Only use authorized sources listed below - NO other books
7. ONLY include visual content if user explicitly asks for illustrations, maps, diagrams, or visual aids
8. Use [PARA] markers to separate all major thoughts and ideas
9. Each visible paragraph should have 1-3 sentences maximum
10. Citations must be on their own lines with [PARA] before and after
11. Never write more than 3 sentences in a row without [PARA]
12. [PARA] will be converted to visual spacing for readability

RESPONSE FORMATTING - USE EXPLICIT [PARA] PARAGRAPH BREAKS IN YOUR OUTPUT:
CRITICAL INSTRUCTION: Use the sequence [PARA] to mark paragraph breaks in your response.
This will be converted to visual paragraph breaks for readability.

YOUR FORMAT MUST BE:
Opening teaching point with main concept explained.[PARA]
Supporting scripture verse(s):[PARA]
- Genesis 1:1 (KJV 1611)[PARA]
- Psalm 119:105 (KJV 1611)[PARA]
Explanation of what this means for thy understanding.[PARA]
Application of this truth to thy life.[PARA]
- Additional supporting source reference

EXAMPLE BIBLICAL RESPONSE YOU SHOULD PRODUCE:
Behold, the Lord God created the heaven and the earth, declaring His sovereign power and dominion.[PARA]
In the beginning, the Scriptures reveal the foundation of all creation.[PARA]
- Genesis 1:1 (KJV 1611)[PARA]
This truth establishes that all things exist by the will and word of God, and none other.[PARA]
Therefore, understanding creation is the key to understanding God's divine purpose.

VISUAL ILLUSTRATION FORMAT (Only when user requests):
If asked for visual content, include using this format:
[IMAGE: Detailed description of a map showing ancient Israel with the twelve tribes]
[IMAGE: Diagram of the Tabernacle layout with the Holy of Holies and brass altar]
[IMAGE: Timeline of biblical events from Creation through the prophets]
[IMAGE: Chart showing the genealogy of kings of Israel and Judah]

WHEN TO USE ILLUSTRATIONS:
- User asks: "Can you draw a map?", "Show me a diagram?", "Visualize this?", "Create an illustration?"
- User requests specific visual types: maps, charts, timelines, genealogies, diagrams
- User says: "with a picture", "show visually", "illustration of", "visual representation"

DO NOT include illustrations unless explicitly requested - stick to biblical teaching by default.{primary_sources_text}{sources_text}

THY VERSES: {key_verses}

REMEMBER:
- Teach theology first and primarily without illustrations
- Only add [IMAGE: ...] tags if user specifically asks for visual content
- Default: give biblical teaching directly from KJV 1611 sources

WRONG:
"Absolutely! Here's an explanation..." or "As I mentioned earlier..."
Including [IMAGE: ...] tags when not requested

CORRECT:
"In the beginning God created the heaven and the earth. - Genesis 1:1 (KJV 1611)"
"I and my Father are one. - John 10:30 (KJV 1611)"
(And ONLY include [IMAGE: ...] if user asks for a map, diagram, or visual)"""

    def _format_response(self, text: str) -> str:
        """Convert formatted response markers into readable paragraphs"""
        import re
        
        text = text.strip()
        if not text:
            return text
        
        # Replace [PARA] markers with double newlines for visual paragraph breaks
        text = text.replace('[PARA]', '\n\n')
        
        # Clean up excessive spacing
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        # If response doesn't have paragraph markers, try to add intelligent breaks
        if '\n\n' not in text and len(text) > 250:
            # Split at sentence boundaries and create paragraphs
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
            
            formatted_parts = []
            current_section = []
            
            for i, sent in enumerate(sentences):
                sent = sent.strip()
                if not sent:
                    continue
                
                current_section.append(sent)
                
                # Create new paragraph after every 2-3 sentences or at logical breaks
                transition_words = ['Therefore', 'Thus', 'However', 'Moreover', 'Furthermore', 
                                   'Additionally', 'Consequently', 'This means', 'But', 'Yet']
                
                should_break = (len(current_section) >= 2 and i < len(sentences) - 1)
                
                if i < len(sentences) - 1:
                    next_sent = sentences[i + 1] if i + 1 < len(sentences) else ''
                    starts_with_transition = any(next_sent.strip().startswith(word) for word in transition_words)
                    if starts_with_transition:
                        should_break = True
                
                if should_break:
                    formatted_parts.append(' '.join(current_section))
                    current_section = []
            
            if current_section:
                formatted_parts.append(' '.join(current_section))
            
            text = '\n\n'.join(formatted_parts)
        
        # Ensure proper spacing around citation lines
        lines = text.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            formatted_lines.append(line)
            
            # Add spacing after citation lines if not already spaced
            if line.strip().startswith('-') and i < len(lines) - 1:
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                if next_line.strip() and not next_line.startswith('\n'):
                    # Ensure blank line after citations
                    if i + 1 < len(lines):
                        formatted_lines.append('')
        
        text = '\n'.join(formatted_lines)
        
        # Final cleanup
        text = re.sub(r'\n\n\n+', '\n\n', text)
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        
        return text.strip()

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
            
            # Integrate knowledge base if available
            try:
                from agents.knowledge_base import get_knowledge_base
                kb = get_knowledge_base()
                
                # Determine knowledge collection type based on character
                collection_type = "academic" if self.is_professor else "biblical"
                
                # Search knowledge base for relevant passages
                knowledge_results = kb.search_knowledge(
                    query=player_message,
                    collection_type=collection_type,
                    n_results=3
                )
                
                # Inject knowledge context into system prompt if results found
                if knowledge_results:
                    knowledge_context = "\n\n[KNOWLEDGE BASE CONTEXT]\nYou have access to authoritative sources. When relevant, cite from these:\n"
                    for i, result in enumerate(knowledge_results, 1):
                        knowledge_context += f"\nSource {i}: {result['citation']}\n{result['text']}\n"
                    knowledge_context += "\n[END KNOWLEDGE BASE]\n"
                    system_prompt += knowledge_context
                    print(f"[KB] Injected {len(knowledge_results)} relevant passages for context", flush=True)
            except ImportError:
                print("[KB] Knowledge base not available, proceeding without knowledge injection", flush=True)
            except Exception as e:
                print(f"[KB] Warning: Failed to retrieve knowledge: {e}", flush=True)
            
            # Build conversation history for context
            messages = []
            for msg in self.conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": player_message})
            
            # Call Anthropic API with fallback model handling
            # Use higher token limit for complete theological responses
            response = call_api_with_fallback(client, system_prompt, messages, max_tokens=1500)
            
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
            
            # Light cleaning - only remove clear instructional/meta text (NOT for professors)
            if not self.is_professor:
                forbidden_starts = [
                    "Here are", "Here is", "For example", "Suggestions:",
                    "Yes, of course", "Examples:",
                    "Absolutely", "Here's", "Let me explain", "As I mentioned",
                    "Of course", "Actually", "Well,", "So,", "You see,",
                    "In conclusion", "To summarize", "In summary"
                ]
                
                # Remove lines that start with forbidden phrases but PRESERVE paragraph structure
                lines = character_response.split('\n')
                cleaned_lines = []
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        # Preserve empty lines (paragraph breaks)
                        cleaned_lines.append('')
                        continue
                    # Skip lines starting with forbidden phrases (with word boundary check)
                    if any(stripped.lower().startswith(forbidden.lower()) for forbidden in forbidden_starts):
                        continue
                    cleaned_lines.append(stripped)
                
                # Join with newlines to preserve paragraph structure
                character_response = '\n'.join(cleaned_lines).strip()
            
            # Stop at dialogue markers (but NOT markdown ### headers or Q&A in content)
            # Only stop at these if they appear at line boundaries (meta-markers)
            dialogue_markers = [
                "\n\nPlayer:", "\n\nUser:", "\n\nSystem:", "\n\nAssistant:",
                "\nPlayer:", "\nUser:", "\nSystem:", "\nAssistant:",
                "Another question?", "If thou asketh", "Should thou ask",
                "\n---END---"
            ]
            for marker in dialogue_markers:
                if marker in character_response:
                    character_response = character_response.split(marker)[0].strip()
            
            print(f"[DEBUG] Cleaned response: {character_response[:200]}...")
            
            if not character_response:
                # Fallback: return raw response if cleaning removed everything
                if raw_response:
                    print(f"[DEBUG] Using raw response as fallback")
                    # Re-extract illustrations from raw response
                    character_response, illustrations = self._extract_illustrations(raw_response)
            
            # Final cleaning - remove inappropriate content based on character type
            if self.is_professor:
                # Professors should avoid New Age and self-help language, but can use scholarly expressions
                forbidden_phrases = [
                    "Psychology", "Therapy", "Meditation technique",
                    "Self-help", "Personal growth", "Mindfulness",
                    "Inner peace", "Find yourself", "Discover your",
                    "Visualize", "Manifest", "Energy", "Universe",
                    "Chakra", "Aura", "Cosmic", "Transcendence"
                ]
            else:
                # Biblical characters should avoid modern phrases and self-help language
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
            
            # Clean up double spaces and normalize WHILE PRESERVING PARAGRAPH BREAKS
            # Split on double newlines to preserve paragraph structure
            paragraphs = character_response.split('\n\n')
            cleaned_paragraphs = []
            for para in paragraphs:
                # Clean within each paragraph but preserve the paragraph structure
                cleaned = ' '.join(para.split())
                if cleaned:
                    cleaned_paragraphs.append(cleaned)
            character_response = '\n\n'.join(cleaned_paragraphs)
            
            # Ensure it starts with first-person if possible (biblical characters only)
            if not self.is_professor:
                first_person_starts = ["I ", "My ", "Mine ", "Me ", "Verily,", "Behold,"]
                if character_response and not any(character_response.startswith(fp) for fp in first_person_starts):
                    # If response doesn't start with I/My, check if we need to prefix
                    if not character_response.startswith(("Thou", "Thee")):
                        character_response = "I say unto thee, " + character_response
            
            # Final check
            if not character_response:
                error_msg = f"I could not generate a proper response. Please try again." if not self.is_professor else f"Unable to generate a substantive response. Please rephrase your question."
                return {
                    "text": f"{error_msg}",
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
            
            # Format response into organized paragraphs for readability
            formatted_response = self._format_response(character_response)
            
            return {
                "text": formatted_response,
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
