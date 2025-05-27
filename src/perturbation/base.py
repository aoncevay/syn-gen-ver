from typing import Optional, List, Dict, Any, Callable
import random
from .utils import get_sentence_spans, replace_span_in_text

class PerturbationManager:
    """
    Manager class to handle all perturbation types.
    Uses a fixed priority order: entity_reorder -> date_format -> number_rephrase -> synonym
    """
    
    def __init__(self):
        self.perturbation_functions = {}
        self.usage_counts = {}  # Just for stats
        self.priority_order = [
            'entity_reorder',  # Hardest but most interesting
            'date_format',     # Format changes
            'number_rephrase', # Number format changes
            'synonym'          # Easiest fallback
        ]
    
    def register_perturbation(self, name: str, func: Callable):
        """Register a perturbation function."""
        self.perturbation_functions[name] = func
        self.usage_counts[name] = 0  # For stats only
    
    def print_stats(self):
        """Print current perturbation statistics."""
        print("\nPerturbation Statistics:")
        print("------------------------")
        for name in self.priority_order:
            if name in self.usage_counts:
                print(f"{name}: {self.usage_counts[name]} perturbations")
        print("------------------------")
    
    def apply_sentence_level_perturbation(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Apply perturbation at the sentence level using fixed priority order.
        Try harder perturbations first, fall back to easier ones.
        """
        # Split text into sentences with their spans
        sentence_spans = get_sentence_spans(text)
        
        # Try each sentence
        for sentence, start, end in sentence_spans:
            # Try perturbations in priority order
            for pert_type in self.priority_order:
                if pert_type not in self.perturbation_functions:
                    continue
                    
                result = self.perturbation_functions[pert_type](sentence)
                if result:
                    # Found a valid perturbation
                    perturbed_sentence = result["perturbed_text"]
                    full_perturbed_text = replace_span_in_text(text, start, end, perturbed_sentence)
                    self.usage_counts[pert_type] += 1
                    
                    return {
                        "statement": text,
                        "updated_statement": full_perturbed_text,
                        "operations": [result["operation"]]
                    }
        
        # No perturbation was applied
        return None 