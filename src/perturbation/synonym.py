import re
import random
from typing import Optional, List, Tuple, Dict, Any
import nltk
import os

# Import our configuration
from .config import get_config

config = get_config()
nltk_config = config.get("nltk", {})
nltk_download_enabled = nltk_config.get("download_enabled", True)
nltk_data_path = nltk_config.get("data_path")

# Add custom NLTK data path if configured
if nltk_data_path:
    nltk.data.path.append(nltk_data_path)

# Flag to track if we have WordNet available
wordnet_available = False
punkt_available = False
tagger_available = False

# Try to access the resources, download if allowed and needed
try:
    nltk.data.find('corpora/wordnet')
    from nltk.corpus import wordnet
    wordnet_available = True
except LookupError:
    if nltk_download_enabled:
        try:
            nltk.download('wordnet', quiet=True)
            from nltk.corpus import wordnet
            wordnet_available = True
        except Exception as e:
            print(f"Could not download or use WordNet: {e}")
            # Create dummy wordnet constants for compatibility
            class DummyWordNet:
                ADJ = 'a'
                VERB = 'v'
                NOUN = 'n'
                ADV = 'r'
            wordnet = DummyWordNet()
    else:
        print("WordNet not available and downloads disabled")
        # Create dummy wordnet constants for compatibility
        class DummyWordNet:
            ADJ = 'a'
            VERB = 'v'
            NOUN = 'n'
            ADV = 'r'
        wordnet = DummyWordNet()

# Try to access the tokenizer, download if allowed and needed
try:
    nltk.data.find('tokenizers/punkt')
    punkt_available = True
except LookupError:
    if nltk_download_enabled:
        try:
            nltk.download('punkt', quiet=True)
            punkt_available = True
        except Exception as e:
            print(f"Could not download or use Punkt tokenizer: {e}")
    else:
        print("Punkt tokenizer not available and downloads disabled")

# Try to access the POS tagger, download if allowed and needed
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
    tagger_available = True
except LookupError:
    if nltk_download_enabled:
        try:
            nltk.download('averaged_perceptron_tagger', quiet=True)
            tagger_available = True
        except Exception as e:
            print(f"Could not download or use POS tagger: {e}")
    else:
        print("POS tagger not available and downloads disabled")

# Fallback simple adjective synonyms
SIMPLE_SYNONYMS = {
    'big': ['large', 'huge', 'enormous', 'substantial', 'significant'],
    'small': ['tiny', 'little', 'miniature', 'minute', 'compact'],
    'good': ['great', 'excellent', 'fine', 'quality', 'superior'],
    'bad': ['poor', 'inferior', 'substandard', 'inadequate', 'unsatisfactory'],
    'important': ['significant', 'crucial', 'essential', 'vital', 'key'],
    'significant': ['substantial', 'considerable', 'important', 'major', 'notable'],
    'new': ['novel', 'modern', 'recent', 'fresh', 'innovative'],
    'old': ['ancient', 'aged', 'vintage', 'traditional', 'classic'],
    'fast': ['quick', 'rapid', 'swift', 'speedy', 'prompt'],
    'slow': ['gradual', 'leisurely', 'unhurried', 'measured', 'deliberate'],
    'strong': ['powerful', 'robust', 'sturdy', 'solid', 'vigorous'],
    'weak': ['feeble', 'fragile', 'delicate', 'frail', 'flimsy'],
    'high': ['elevated', 'tall', 'lofty', 'towering', 'soaring'],
    'low': ['minimal', 'modest', 'slight', 'minor', 'reduced'],
    'effective': ['efficient', 'productive', 'successful', 'useful', 'beneficial'],
    'ineffective': ['inefficient', 'unproductive', 'unsuccessful', 'useless', 'futile'],
    'expensive': ['costly', 'premium', 'high-priced', 'valuable', 'premium'],
    'cheap': ['inexpensive', 'affordable', 'economical', 'reasonable', 'budget-friendly'],
    'difficult': ['challenging', 'complex', 'complicated', 'demanding', 'tough'],
    'easy': ['simple', 'straightforward', 'uncomplicated', 'effortless', 'manageable']
}

def get_wordnet_pos(tag: str) -> str:
    """
    Map NLTK POS tag to WordNet POS tag.
    
    Args:
        tag: NLTK POS tag
    
    Returns:
        WordNet POS tag
    """
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return None

def get_synonyms_from_wordnet(word: str, pos=None) -> List[str]:
    """
    Get synonyms for a word using WordNet.
    
    Args:
        word: The word to find synonyms for
        pos: Part of speech (optional)
        
    Returns:
        List of synonyms
    """
    if not wordnet_available:
        return []
    
    synonyms = []
    
    if pos:
        synsets = wordnet.synsets(word, pos=pos)
    else:
        synsets = wordnet.synsets(word)
        
    for synset in synsets:
        for lemma in synset.lemmas():
            synonym = lemma.name().replace('_', ' ')
            if synonym.lower() != word.lower() and synonym not in synonyms:
                synonyms.append(synonym)
                
    return synonyms

def get_synonyms_from_fallback(word: str) -> List[str]:
    """
    Get synonyms from the fallback dictionary.
    
    Args:
        word: The word to find synonyms for
        
    Returns:
        List of synonyms
    """
    return SIMPLE_SYNONYMS.get(word.lower(), [])

def find_replaceable_word(text: str) -> Optional[Tuple[str, str, List[str], int, int]]:
    """
    Find an adjective in the text that can be replaced with a synonym.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (word, pos, synonyms, start_index, end_index) or None if no suitable adjective found
    """
    replaceable_words = []
    
    # If we have NLTK resources, use them
    if punkt_available and tagger_available:
        # Tokenize and POS tag the text
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        
        # Look for adjectives only
        for word, tag in tagged:
            # Skip short words and non-alphabetic words
            if len(word) <= 3 or not re.match(r'^[a-zA-Z]+$', word):
                continue
            
            # Only process adjectives (tags starting with 'JJ')
            if not tag.startswith('JJ'):
                continue
            
            # Get synonyms
            synonyms = []
            
            if wordnet_available:
                synonyms = get_synonyms_from_wordnet(word, wordnet.ADJ)
            
            # If no WordNet synonyms found, try fallback dictionary
            if not synonyms:
                synonyms = get_synonyms_from_fallback(word)
            
            # If we found synonyms, find the word position in text
            if synonyms:
                # Find the word in text (respecting word boundaries)
                pattern = r'\b' + re.escape(word) + r'\b'
                for match in re.finditer(pattern, text):
                    replaceable_words.append((word, tag, synonyms, match.start(), match.end()))
    else:
        # Fallback to simple dictionary lookup if NLTK is not available
        for word in re.finditer(r'\b[a-zA-Z]{4,}\b', text):
            word_text = word.group()
            synonyms = get_synonyms_from_fallback(word_text)
            if synonyms:
                replaceable_words.append((word_text, 'JJ', synonyms, word.start(), word.end()))
    
    # If we found any replaceable words, return a random one
    if replaceable_words:
        return random.choice(replaceable_words)
    
    return None

def perturb_synonym(text: str) -> Optional[Dict[str, Any]]:
    """
    Find a word and replace it with a synonym in the text.
    
    Args:
        text: The input text
    
    Returns:
        A dictionary with the perturbation details or None if no perturbation possible
    """
    replaceable_word = find_replaceable_word(text)
    if replaceable_word:
        word, pos, synonyms, start, end = replaceable_word
        
        # Choose a random synonym
        synonym = random.choice(synonyms)
        
        # Preserve capitalization
        if word[0].isupper():
            synonym = synonym.capitalize()
        
        return {
            "perturbed_text": text[:start] + synonym + text[end:],
            "operation": {
                "Target": "synonym",
                "From": word,
                "To": synonym,
                "Type": "Supported"
            }
        }
    
    return None
