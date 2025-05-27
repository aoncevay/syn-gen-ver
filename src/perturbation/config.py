import json
import os

_DEFAULT_CONFIG = {
    "nltk": {
        "download_enabled": True
    },
    "perturbation": {
        "enabled_types": ["date_format", "entity_reorder", "number_rephrase", "synonym"]
    }
}

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

try:
    with open(_CONFIG_PATH, 'r', encoding='utf-8') as f:
        _config = json.load(f)
    print(f"Loaded configuration from {_CONFIG_PATH}")
except Exception as e:
    print(f"Could not load config.json, using default config: {e}")
    _config = _DEFAULT_CONFIG

def get_config():
    """Return the loaded configuration as a dict."""
    return _config 