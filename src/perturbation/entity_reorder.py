import re
import random
from typing import Optional, List, Tuple, Dict, Any
import spacy

# Load spaCy model for named entity recognition
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If the model is not installed, we need to install it
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def find_entity_list(text: str) -> Optional[Tuple[str, List[str], int, int]]:
    """
    Find a list of named entities (people or organizations) in the text.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (original_text, list_of_entities, start_index, end_index) or None if no list found
    """
    # Process the text with spaCy
    doc = nlp(text)
    
    # Extract entities of type PERSON or ORG
    entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) 
                for ent in doc.ents 
                if ent.label_ in ["PERSON", "ORG"]]
    
    # Find contiguous lists of entities separated by commas, 'and', or other list separators
    if len(entities) >= 2:
        # Look for patterns like "A, B and C" or "A, B, C, and D"
        list_pattern = r'([^,.]+(?:,\s*|\s+and\s+|\s*&\s*)[^,.]+(?:,\s*|\s+and\s+|\s*&\s*)[^,.]+)'
        
        for match in re.finditer(list_pattern, text):
            match_text = match.group()
            match_start = match.start()
            match_end = match.end()
            
            # Check if this match contains multiple entities
            contained_entities = [
                ent for ent in entities 
                if ent[1] >= match_start and ent[2] <= match_end
            ]
            
            if len(contained_entities) >= 2:
                entity_list = [ent[0] for ent in contained_entities]
                return (match_text, entity_list, match_start, match_end)
    
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
    # This is a simplified approach that might not work for all cases
    # For a more robust solution, you would need to track the exact positions of entities and separators
    
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
