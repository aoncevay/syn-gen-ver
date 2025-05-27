from typing import Optional, List, Dict, Any, Callable
import random
from .utils import get_sentence_spans, replace_span_in_text

class PerturbationManager:
    """
    Manager class to handle all perturbation types.
    """
    
    def __init__(self):
        self.perturbation_functions = {}
        self.usage_counts = {}  # Track how many times each perturbation is used
        self.attempt_counts = {}  # Track how many attempts for each type
        self.max_attempts_per_type = 1000  # Maximum attempts before skipping a type
    
    def register_perturbation(self, name: str, func: Callable):
        """
        Register a perturbation function.
        
        Args:
            name: Name of the perturbation
            func: Perturbation function
        """
        self.perturbation_functions[name] = func
        self.usage_counts[name] = 0  # Initialize usage count
        self.attempt_counts[name] = 0  # Initialize attempt count
    
    def get_available_perturbations(self) -> List[str]:
        """
        Get list of available perturbation types.
        
        Returns:
            List of perturbation names
        """
        return list(self.perturbation_functions.keys())
    
    def print_stats(self):
        """Print current perturbation statistics."""
        print("\nPerturbation Statistics:")
        print("------------------------")
        for name in self.perturbation_functions.keys():
            success_rate = (self.usage_counts[name] / max(1, self.attempt_counts[name])) * 100
            print(f"{name}:")
            print(f"  Successful: {self.usage_counts[name]}")
            print(f"  Attempts: {self.attempt_counts[name]}")
            print(f"  Success Rate: {success_rate:.1f}%")
        print("------------------------")
    
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
            self.attempt_counts[perturbation_type] += 1
            if self.attempt_counts[perturbation_type] % 100 == 0:
                print(f"Attempted {perturbation_type} {self.attempt_counts[perturbation_type]} times...")
            
            result = self.perturbation_functions[perturbation_type](text)
            if result:
                self.usage_counts[perturbation_type] += 1
            return result
        else:
            # Sort perturbations by usage count (least used first)
            perturbation_types = sorted(
                self.perturbation_functions.keys(),
                key=lambda x: (self.usage_counts[x], self.attempt_counts[x])  # Sort by usage, then attempts
            )
            
            # Try perturbations in order of least used
            for pert_type in perturbation_types:
                # Skip if we've tried this type too many times
                if self.attempt_counts[pert_type] >= self.max_attempts_per_type:
                    continue
                
                self.attempt_counts[pert_type] += 1
                if self.attempt_counts[pert_type] % 100 == 0:
                    print(f"Attempted {pert_type} {self.attempt_counts[pert_type]} times...")
                    self.print_stats()
                
                result = self.perturbation_functions[pert_type](text)
                if result:
                    self.usage_counts[pert_type] += 1
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
        
        # First try with balanced approach
        perturbation_types = sorted(
            [p for p in self.perturbation_functions.keys() 
             if self.attempt_counts[p] < self.max_attempts_per_type],
            key=lambda x: (self.usage_counts[x], self.attempt_counts[x])
        )
        
        # If no perturbation types available or we've tried too many times,
        # fall back to any available type that hasn't hit max attempts
        if not perturbation_types:
            print("\nFalling back to any available perturbation type...")
            perturbation_types = [p for p in self.perturbation_functions.keys() 
                                if self.attempt_counts[p] < self.max_attempts_per_type]
        
        if not perturbation_types:
            print("All perturbation types have reached maximum attempts!")
            self.print_stats()
            return None
        
        # Try each sentence with each perturbation type
        for sentence, start, end in sentence_spans:
            # First try least used perturbation types
            for pert_type in perturbation_types:
                self.attempt_counts[pert_type] += 1
                if self.attempt_counts[pert_type] % 100 == 0:
                    print(f"Attempted {pert_type} {self.attempt_counts[pert_type]} times...")
                    self.print_stats()
                
                result = self.perturbation_functions[pert_type](sentence)
                if result:
                    # If we found a perturbation, update the full text
                    perturbed_sentence = result["perturbed_text"]
                    full_perturbed_text = replace_span_in_text(text, start, end, perturbed_sentence)
                    
                    # Update usage count
                    self.usage_counts[pert_type] += 1
                    
                    return {
                        "statement": text,
                        "updated_statement": full_perturbed_text,
                        "operations": [result["operation"]]
                    }
            
            # If no perturbation worked with balanced approach, try any type that works
            if any(self.attempt_counts[p] < self.max_attempts_per_type for p in self.perturbation_functions):
                print("\nTrying any available perturbation type...")
                for pert_type in self.perturbation_functions:
                    if self.attempt_counts[pert_type] >= self.max_attempts_per_type:
                        continue
                        
                    self.attempt_counts[pert_type] += 1
                    result = self.perturbation_functions[pert_type](sentence)
                    if result:
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