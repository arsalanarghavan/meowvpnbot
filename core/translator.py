import json
import os
from typing import Dict, Any

class Translator:
    """
    Handles loading, accessing, and updating user-facing texts from a JSON file.
    This allows for easy editing of all bot messages and button labels by the admin.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Singleton pattern to ensure only one instance of Translator exists.
        if not cls._instance:
            cls._instance = super(Translator, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, file_path: str = "locales/fa.json"):
        # The __init__ is called every time, but we only load the file once.
        if not hasattr(self, '_initialized'):
            self.file_path = file_path
            self._texts: Dict[str, Any] = self._load_texts()
            self._initialized = True

    def _load_texts(self) -> Dict[str, Any]:
        """Loads texts from the JSON file. Returns an empty dict if not found."""
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is empty/corrupt, create it with a default structure
            default_structure = {"messages": {}, "buttons": {}}
            self._save_texts(default_structure)
            return default_structure

    def _save_texts(self, data: Dict[str, Any]):
        """Saves the current texts dictionary to the JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get(self, key: str, **kwargs) -> str:
        """
        Retrieves a text value using a dot-separated key (e.g., 'messages.welcome').
        Formats the string with any provided keyword arguments.
        """
        try:
            value = self._texts
            for k in key.split('.'):
                value = value[k]
            
            if kwargs:
                return str(value).format(**kwargs)
            return str(value)
        except (KeyError, TypeError):
            # Return the key itself if not found, making it easy to spot missing texts.
            return key

    def update_text(self, key: str, new_value: str) -> bool:
        """Updates a text value and saves the changes to the JSON file."""
        try:
            data = self._texts
            keys = key.split('.')
            for k in keys[:-1]:
                data = data[k]
            
            data[keys[-1]] = new_value
            self._save_texts(self._texts)
            return True
        except KeyError:
            return False

# Create a single, globally accessible instance of the translator.
translator = Translator()

def _(key: str, **kwargs) -> str:
    """A convenient shorthand function for accessing translator.get()."""
    return translator.get(key, **kwargs)