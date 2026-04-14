"""Character agents powered by CrewAI and Ollama"""
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"


class CharacterAgent:
    """Base character agent for dialogue"""

    def __init__(self, character_id: str, character_data: dict):
        self.character_id = character_id
        self.name = character_data.get("name", character_id.capitalize())
        self.theology = character_data.get("theology", {})
        self.personality = character_data.get("personality", "")
        self.teaching_areas = character_data.get("teaching_areas", [])
        self.conversation_history = []

    def get_system_prompt(self) -> str:
        """Generate system prompt with character theology and personality"""
        
        return f"""You are {self.name}, a biblical character from the KJV 1611 Scripture.

Personality: {self.personality}
Teaching focus: {', '.join(self.teaching_areas)}

INSTRUCTIONS:
1. Answer from the perspective of {self.name}
2. Ground responses in KJV 1611 Scripture
3. Reference specific Bible verses when relevant
4. Keep responses brief (1-2 sentences typically)
5. Teach biblical truth with compassion
6. Use "thee" and "thou" when appropriate for 1611 style

Respond authentically as your character would."""

    def get_dialogue_response(self, player_name: str, player_message: str) -> str:
        """Get character response to player message using Ollama API"""
        
        # Build conversation context
        full_message = f"{player_name}: {player_message}"
        
        try:
            # Build prompt with system context
            system_prompt = self.get_system_prompt()
            prompt = f"{system_prompt}\n\nPlayer: {player_message}\n\n{self.name}:"
            
            # Call Ollama API
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"\n[OLLAMA ERROR] Status {response.status_code}: {response.text}\n")
                return f"Forgive me, {player_name}. A difficulty hath arisen with the local model. Please try again."
            
            # Extract response
            response_data = response.json()
            character_response = response_data.get("response", "").strip()
            
            if not character_response:
                return f"Forgive me, {player_name}. I could not generate a response. Please try again."
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": full_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": character_response
            })
            
            return character_response
            
        except requests.exceptions.ConnectionError:
            return f"Forgive me, {player_name}. I cannot reach the local model. Is Ollama running? Start it with 'ollama serve'."
        except requests.exceptions.Timeout:
            return f"Forgive me, {player_name}. The model is taking too long to respond. Please try again."
        except Exception as e:
            error_msg = str(e)
            print(f"\n[OLLAMA ERROR FULL] {type(e).__name__}: {error_msg}\n")
            import traceback
            traceback.print_exc()
            return f"Forgive me, {player_name}. A difficulty hath arisen: {error_msg}"

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []


class CharacterAgentFactory:
    """Factory to create character agents"""

    def __init__(self, character_profiles_path: str = None):
        """Initialize with character profiles"""
        if character_profiles_path is None:
            character_profiles_path = "config/character_profiles.json"
        
        self.character_data = self._load_character_profiles(character_profiles_path)
        self.agents = {}

    def _load_character_profiles(self, path: str) -> dict:
        """Load character profiles from JSON"""
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("characters", {})
        except Exception as e:
            print(f"Error loading character profiles: {e}")
        
        # Return default minimal profiles if file doesn't exist
        return {
            "jesus": {"name": "Jesus", "theology": {}, "personality": "Compassionate and wise", "teaching_areas": ["Grace", "Love", "Redemption"]},
            "david": {"name": "David", "theology": {}, "personality": "Repentant and hopeful", "teaching_areas": ["Psalms", "Faith", "Worship"]},
            "solomon": {"name": "Solomon", "theology": {}, "personality": "Wise and reflective", "teaching_areas": ["Wisdom", "Vanity", "Truth"]},
        }

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
            
            # Create agent
            self.agents[character_id] = CharacterAgent(character_id, char_data)
        
        return self.agents[character_id]

    def get_all_characters(self) -> list:
        """Get list of all available characters"""
        return list(self.character_data.keys())


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
