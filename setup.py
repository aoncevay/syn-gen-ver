#!/usr/bin/env python3

import os
import sys
import nltk

def setup_nltk_data():
    """Download required NLTK data packages."""
    print("Setting up NLTK data...")
    
    # List of required NLTK data packages
    required_packages = [
        'punkt',  # Sentence tokenizer
        'wordnet',  # For synonym replacement
        'averaged_perceptron_tagger',  # POS tagger
        'maxent_ne_chunker',  # Named Entity chunker
        'words',  # Words corpus
        'omw-1.4',  # Open Multilingual Wordnet
    ]
    
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