from typing import Optional, List, Dict, Any, Callable
import random
from .utils import get_sentence_spans, replace_span_in_text

class PerturbationManager:
    """
    Manager class to handle all perturbation types.
    """
    
    def __init__(self):
        self.perturbation_functions = {}
    
    def register_perturbation(self, name: str, func: Callable):
        """
        Register a perturbation function.
        
        Args:
            name: Name of the perturbation
            func: Perturbation function
        """
        self.perturbation_functions[name] = func
    
    def get_available_perturbations(self) -> List[str]:
        """
        Get list of available perturbation types.
        
        Returns:
            List of perturbation names
        """
        return list(self.perturbation_functions.keys())
    
    def apply_perturbation(self, text: str, perturbation_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Apply a perturbation to the text.
        
        Args:
            text: The input text
            perturbation_type: Type of perturbation to apply (if None, try all)
            
        Returns:
            Dictionary with perturbation results or None if no perturbation applied
        """
        if perturbation_type and perturbation_type in self.perturbation_functions:
            # Apply specific perturbation
            return self.perturbation_functions[perturbation_type](text)
        else:
            # Try all perturbations in random order
            perturbation_types = list(self.perturbation_functions.keys())
            random.shuffle(perturbation_types)
            
            for pert_type in perturbation_types:
                result = self.perturbation_functions[pert_type](text)
                if result:
                    return result
        
        return None
    
    def apply_sentence_level_perturbation(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Apply perturbation at the sentence level.
        
        Args:
            text: The input text
            
        Returns:
            Dictionary with perturbation results or None if no perturbation applied
        """
        # Split text into sentences with their spans
        sentence_spans = get_sentence_spans(text)
        
        # Shuffle sentences to try perturbations in random order
        shuffled_indices = list(range(len(sentence_spans)))
        random.shuffle(shuffled_indices)
        
        for idx in shuffled_indices:
            sentence, start, end = sentence_spans[idx]
            
            # Try to apply a perturbation to this sentence
            result = self.apply_perturbation(sentence)
            
            if result:
                # If we found a perturbation, update the full text
                perturbed_sentence = result["perturbed_text"]
                full_perturbed_text = replace_span_in_text(text, start, end, perturbed_sentence)
                
                return {
                    "statement": text,
                    "updated_statement": full_perturbed_text,
                    "operations": [result["operation"]]
                }
        
        # No perturbation was applied
        return None 