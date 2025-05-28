from typing import Optional, List, Dict, Any, Callable
import random
from .utils import get_sentence_spans, replace_span_in_text

class PerturbationManager:
    """
    Manager class to handle all perturbation types.
    Allows multiple perturbations per text (entity_reorder, date_format, number_rephrase),
    with synonym replacement as a last resort if no other perturbations are possible.
    """
    
    def __init__(self):
        self.perturbation_functions = {}
        self.usage_counts = {}  # Just for stats
        # Primary perturbations that can be combined
        self.primary_perturbations = [
            'entity_reorder',  # Entity list reordering
            'date_format',     # Date format changes
            'number_rephrase'  # Number format changes
        ]
        # Fallback perturbation when no primary ones work
        self.fallback_perturbation = 'synonym'
    
    def register_perturbation(self, name: str, func: Callable):
        """Register a perturbation function."""
        self.perturbation_functions[name] = func
        self.usage_counts[name] = 0  # For stats only
    
    def print_stats(self):
        """Print current perturbation statistics."""
        print("\nPerturbation Statistics:")
        print("------------------------")
        for name in self.primary_perturbations + [self.fallback_perturbation]:
            if name in self.usage_counts:
                print(f"{name}: {self.usage_counts[name]} perturbations")
        print("------------------------")
    
    def apply_sentence_level_perturbation(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Apply perturbations at the sentence level.
        Try all primary perturbations first, fall back to synonym if none work.
        Can generate multiple perturbations for the same text.
        """
        results = []
        
        # Split text into sentences with their spans
        sentence_spans = get_sentence_spans(text)
        
        # Try each sentence
        for sentence, start, end in sentence_spans:
            # Try each primary perturbation type
            for pert_type in self.primary_perturbations:
                if pert_type not in self.perturbation_functions:
                    continue
                    
                result = self.perturbation_functions[pert_type](sentence)
                if result:
                    # Found a valid perturbation
                    perturbed_sentence = result["perturbed_text"]
                    full_perturbed_text = replace_span_in_text(text, start, end, perturbed_sentence)
                    self.usage_counts[pert_type] += 1
                    
                    results.append({
                        "statement": text,
                        "updated_statement": full_perturbed_text,
                        "operations": [result["operation"]]
                    })
        
        # If no primary perturbations worked, try synonym as fallback
        if not results and self.fallback_perturbation in self.perturbation_functions:
            for sentence, start, end in sentence_spans:
                result = self.perturbation_functions[self.fallback_perturbation](sentence)
                if result:
                    # Found a synonym replacement
                    perturbed_sentence = result["perturbed_text"]
                    full_perturbed_text = replace_span_in_text(text, start, end, perturbed_sentence)
                    self.usage_counts[self.fallback_perturbation] += 1
                    
                    results.append({
                        "statement": text,
                        "updated_statement": full_perturbed_text,
                        "operations": [result["operation"]]
                    })
        
        # Return all results if any, otherwise None
        return results if results else None 