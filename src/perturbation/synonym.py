import re
import random
from typing import Optional, List, Tuple, Dict, Any
import nltk
from nltk.corpus import wordnet

# Ensure WordNet is downloaded
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Also need part-of-speech tagging
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

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

def find_replaceable_word(text: str) -> Optional[Tuple[str, str, List[str], int, int]]:
    """
    Find a word in the text that can be replaced with a synonym.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (word, pos, synonyms, start_index, end_index) or None if no suitable word found
    """
    # Tokenize and POS tag the text
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    
    # Look for content words (nouns, verbs, adjectives, adverbs)
    replaceable_words = []
    
    for word, tag in tagged:
        # Skip short words, stopwords, and non-content words
        if len(word) <= 3 or not re.match(r'^[a-zA-Z]+$', word):
            continue
        
        # Get WordNet POS
        wordnet_pos = get_wordnet_pos(tag)
        if not wordnet_pos:
            continue
        
        # Get synonyms
        synonyms = []
        for synset in wordnet.synsets(word, pos=wordnet_pos):
            for lemma in synset.lemmas():
                synonym = lemma.name().replace('_', ' ')
                if synonym.lower() != word.lower() and synonym not in synonyms:
                    synonyms.append(synonym)
        
        # Only consider words with at least one synonym
        if synonyms:
            # Find the start and end indices of this word in the original text
            word_pattern = r'\b' + re.escape(word) + r'\b'
            for match in re.finditer(word_pattern, text):
                # Avoid words in named entities (crude approximation)
                prev_char = text[match.start()-1] if match.start() > 0 else ' '
                if not prev_char.isupper():
                    replaceable_words.append((word, wordnet_pos, synonyms, match.start(), match.end()))
    
    # If we found replaceable words, choose one randomly
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
                "To": synonym
            }
        }
    
    return None
