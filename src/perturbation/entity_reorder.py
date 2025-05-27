import re
import random
from typing import Optional, List, Tuple, Dict, Any
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

# Import our configuration
from .config import get_config

def find_entity_list(text: str) -> Optional[Tuple[str, List[str], int, int]]:
    """
    Find a list of named entities (people or organizations) in the text using NLTK.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (original_text, list_of_entities, start_index, end_index) or None if no list found
    """
    try:
        print("Attempting NLTK entity recognition...")
        # Tokenize and tag the text
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        
        # Extract named entities
        named_entities = []
        chunks = ne_chunk(tagged)
        print(f"Found chunks: {chunks}")
        
        for chunk in chunks:
            if isinstance(chunk, Tree):
                if chunk.label() in ['PERSON', 'ORGANIZATION']:
                    entity = ' '.join([token for token, pos in chunk.leaves()])
                    # Find the position of this entity in the original text
                    start = text.find(entity)
                    if start != -1:
                        named_entities.append((entity, start, start + len(entity)))
        
        print(f"Found named entities: {named_entities}")
        
        # Sort entities by their position in text
        named_entities.sort(key=lambda x: x[1])
        
        # If we have at least 2 entities, look for list patterns
        if len(named_entities) >= 2:
            # Look for patterns like "A, B and C" or "A, B, C, and D"
            list_pattern = r'([^,.]+(?:,\s*|\s+and\s+|\s*&\s*)[^,.]+(?:,\s*|\s+and\s+|\s*&\s*)[^,.]+)'
            
            for match in re.finditer(list_pattern, text):
                match_text = match.group()
                match_start = match.start()
                match_end = match.end()
                
                # Check which entities are in this match
                contained_entities = [
                    ent for ent, start, end in named_entities 
                    if start >= match_start and end <= match_end
                ]
                
                if len(contained_entities) >= 2:
                    print(f"Found entity list: {contained_entities}")
                    return (match_text, contained_entities, match_start, match_end)
        
        print("No list pattern found, trying simple regex approach...")
        # If no list pattern found, try simple regex-based approach
        return _find_entity_list_simple(text)
        
    except Exception as e:
        print(f"Error in NLTK processing: {e}")
        # Fallback to simple pattern matching
        return _find_entity_list_simple(text)

def _find_entity_list_simple(text: str) -> Optional[Tuple[str, List[str], int, int]]:
    """
    A simple fallback method to find potential entity lists using regex patterns.
    This uses simple regex patterns to identify potential lists of capitalized names.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (original_text, list_of_entities, start_index, end_index) or None if no list found
    """
    print("Using simple regex-based entity detection...")
    # Look for patterns like "Name1, Name2 and Name3" where names are capitalized
    list_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)+(?:\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)'
    
    for match in re.finditer(list_pattern, text):
        match_text = match.group()
        match_start = match.start()
        match_end = match.end()
        
        # Extract potential entities from the match
        # Split by commas and "and"
        potential_entities = re.split(r',\s+|\s+and\s+', match_text)
        potential_entities = [e.strip() for e in potential_entities if e.strip()]
        
        if len(potential_entities) >= 2:
            print(f"Found entities using regex: {potential_entities}")
            return (match_text, potential_entities, match_start, match_end)
    
    print("No entities found using regex either.")
    return None

def reorder_entities(entity_list: List[str]) -> List[str]:
    """
    Reorder a list of entities randomly, ensuring the order changes.
    
    Args:
        entity_list: List of entity strings
    
    Returns:
        Reordered list of entities
    """
    if len(entity_list) <= 1:
        return entity_list
    
    # Make a copy to avoid modifying the original
    new_order = entity_list.copy()
    
    # Keep shuffling until we get a different order
    while new_order == entity_list:
        random.shuffle(new_order)
    
    return new_order

def reconstruct_text_with_entities(original_text: str, original_entities: List[str], reordered_entities: List[str]) -> str:
    """
    Reconstruct the text with reordered entities, preserving separators.
    
    Args:
        original_text: The original text containing the entities
        original_entities: The original list of entities
        reordered_entities: The reordered list of entities
    
    Returns:
        The reconstructed text with reordered entities
    """
    result = original_text
    
    # Replace each original entity with its reordered counterpart
    for orig, reord in zip(original_entities, reordered_entities):
        result = result.replace(orig, "ENTITY_PLACEHOLDER", 1)
    
    # Replace placeholders with reordered entities
    for reord in reordered_entities:
        result = result.replace("ENTITY_PLACEHOLDER", reord, 1)
    
    return result

def perturb_entity_reorder(text: str) -> Optional[Dict[str, Any]]:
    """
    Find and reorder a list of named entities in the text.
    
    Args:
        text: The input text
    
    Returns:
        A dictionary with the perturbation details or None if no perturbation possible
    """
    entity_list_match = find_entity_list(text)
    if entity_list_match:
        original_text, entities, start, end = entity_list_match
        
        # Only proceed if we have at least two entities
        if len(entities) >= 2:
            reordered_entities = reorder_entities(entities)
            
            # If we managed to create a different order
            if reordered_entities != entities:
                reconstructed_text = reconstruct_text_with_entities(
                    original_text, entities, reordered_entities
                )
                
                # Return the perturbation if successful
                if reconstructed_text != original_text:
                    return {
                        "perturbed_text": text[:start] + reconstructed_text + text[end:],
                        "operation": {
                            "Target": "entity_reorder",
                            "From": original_text,
                            "To": reconstructed_text
                        }
                    }
    
    return None
