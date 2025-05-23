#!/usr/bin/env python3

import os
import sys
import nltk
from pathlib import Path
import json

def setup_nltk_data():
    """Download required NLTK data packages."""
    print("Setting up NLTK data...")
    
    # List of required NLTK data packages
    required_packages = [
        # For tokenization
        'punkt',  # Sentence tokenizer
        'wordnet',  # For synonym replacement
        
        # For entity recognition
        'averaged_perceptron_tagger',  # POS tagger
        'maxent_ne_chunker',  # Named Entity chunker
        'words',  # Words corpus
        
        # Additional resources that might be useful
        'omw-1.4',  # Open Multilingual Wordnet
    ]
    
    # Create data directory if specified in config
    config_path = Path('src/config.json')
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
            nltk_config = config.get('nltk', {})
            data_path = nltk_config.get('data_path')
            
            if data_path:
                data_path = Path(data_path)
                data_path.mkdir(parents=True, exist_ok=True)
                nltk.data.path.append(str(data_path))
                print(f"NLTK data will be downloaded to: {data_path}")
    
    # Download each required package
    for package in required_packages:
        print(f"Downloading {package}...")
        try:
            nltk.download(package, quiet=True)
            print(f"✓ Successfully downloaded {package}")
        except Exception as e:
            print(f"✗ Error downloading {package}: {e}")
            sys.exit(1)
    
    print("\nNLTK setup completed successfully!")

def main():
    """Main setup function."""
    print("Starting project setup...")
    
    # Ensure we're in the project root directory
    if not os.path.exists('src/config.json'):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup NLTK data
    setup_nltk_data()
    
    print("\nSetup completed! You can now run the perturbation generator.")
    print("Example usage:")
    print("  python src/main.py --input data/sample.json --output data/perturbed.json")

if __name__ == "__main__":
    main() 