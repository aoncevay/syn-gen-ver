import re
import random
from typing import Optional, List, Tuple, Dict, Any
import spacy
import os
import sys
import importlib.util
from pathlib import Path

# Import our configuration
from .config import get_config

# Load spaCy model based on configuration
config = get_config()
spacy_config = config.get_spacy_model_info()
model_name = spacy_config.get("name", "en_core_web_sm")
local_path = spacy_config.get("local_path", None)
use_local_model = spacy_config.get("use_local_model", False)

try:
    if use_local_model and local_path:
        # Path to the manually downloaded model
        model_path = Path(local_path)
        
        if model_path.exists():
            print(f"Loading spaCy model from local path: {model_path}")
            # Load from the specified path
            if importlib.util.find_spec("spacy.cli.info") is not None:
                # This approach works with newer spaCy versions
                nlp = spacy.load(model_path)
            else:
                # Alternative approach for older spaCy versions
                model_path_str = str(model_path)
                sys.path.insert(0, model_path_str)
                nlp = importlib.import_module(model_name).load()
                sys.path.pop(0)
        else:
            print(f"Warning: Local model path {model_path} not found, falling back to installed model")
            nlp = spacy.load(model_name)
    else:
        # Load the installed model
        nlp = spacy.load(model_name)
        
except OSError as e:
    print(f"Error loading spaCy model: {e}")
    print("Attempting to download the model...")
    try:
        # If the model is not installed, we need to install it
        import subprocess
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
        nlp = spacy.load(model_name)
    except Exception as download_error:
        print(f"Failed to download spaCy model: {download_error}")
        print("Using a simpler approach for entity recognition...")
        # Fallback to a very simple entity recognition method
        nlp = None

def find_entity_list(text: str) -> Optional[Tuple[str, List[str], int, int]]:
    """
    Find a list of named entities (people or organizations) in the text.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (original_text, list_of_entities, start_index, end_index) or None if no list found
    """
    if nlp is None:
        # Fallback method if spaCy is not available
        return _find_entity_list_simple(text)
    
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

def _find_entity_list_simple(text: str) -> Optional[Tuple[str, List[str], int, int]]:
    """
    A simple fallback method to find potential entity lists when spaCy is not available.
    This uses simple regex patterns to identify potential lists of capitalized names.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (original_text, list_of_entities, start_index, end_index) or None if no list found
    """
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
            return (match_text, potential_entities, match_start, match_end)
    
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
