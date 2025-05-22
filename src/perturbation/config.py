import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "spacy_model": {
        "name": "en_core_web_sm",
        "local_path": None,
        "use_local_model": False
    },
    "nltk": {
        "data_path": None,
        "download_enabled": True
    },
    "perturbation": {
        "enabled_types": ["date_format", "entity_reorder", "number_rephrase", "synonym"]
    }
}

class Config:
    """
    Configuration handler for the perturbation system.
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one config instance exists."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._config = DEFAULT_CONFIG.copy()
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from config.json file if it exists."""
        # Try different paths for config.json
        possible_paths = [
            os.path.join(os.getcwd(), 'config.json'),
            os.path.join(os.getcwd(), 'src', 'config.json'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                        self._update_config(user_config)
                    print(f"Loaded configuration from {path}")
                    return
                except Exception as e:
                    print(f"Error loading config from {path}: {e}")
        
        print("No config.json found, using default configuration")
    
    def _update_config(self, user_config: Dict[str, Any]):
        """Update config with user-provided values."""
        for section, values in user_config.items():
            if section in self._config:
                if isinstance(self._config[section], dict) and isinstance(values, dict):
                    self._config[section].update(values)
                else:
                    self._config[section] = values
            else:
                self._config[section] = values
    
    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: The configuration section
            key: The specific key within the section (or None for entire section)
            default: Default value if the key doesn't exist
            
        Returns:
            The configuration value or default
        """
        if section not in self._config:
            return default
        
        if key is None:
            return self._config[section]
        
        return self._config[section].get(key, default)
    
    def get_spacy_model_info(self) -> Dict[str, Any]:
        """
        Get spaCy model configuration.
        
        Returns:
            Dictionary with spaCy model info
        """
        return self.get("spacy_model", default={})

# Create a singleton instance
config = Config()

def get_config() -> Config:
    """
    Get the configuration instance.
    
    Returns:
        The Config singleton instance
    """
    return config 