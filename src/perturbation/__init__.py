from .base import PerturbationManager
from .date_format import perturb_date_format
from .entity_reorder import perturb_entity_reorder
from .number_rephrase import perturb_number_rephrase
from .synonym import perturb_synonym
from typing import List, Optional

__all__ = [
    'PerturbationManager',
    'perturb_date_format',
    'perturb_entity_reorder',
    'perturb_number_rephrase',
    'perturb_synonym',
    'create_perturbation_manager'
]

# Map of perturbation type names to their functions
PERTURBATION_FUNCTIONS = {
    'date_format': perturb_date_format,
    'entity_reorder': perturb_entity_reorder,
    'number_rephrase': perturb_number_rephrase,
    'synonym': perturb_synonym
}

def create_perturbation_manager(enabled_types: Optional[List[str]] = None) -> PerturbationManager:
    """
    Create and configure a perturbation manager with specified or all available perturbation types.
    
    Args:
        enabled_types: List of perturbation type names to enable (None for all)
    
    Returns:
        Configured PerturbationManager
    """
    manager = PerturbationManager()
    
    # If no specific types are provided, use all available perturbations
    if enabled_types is None:
        for name, func in PERTURBATION_FUNCTIONS.items():
            manager.register_perturbation(name, func)
    else:
        # Register only the enabled perturbation types
        for name in enabled_types:
            if name in PERTURBATION_FUNCTIONS:
                manager.register_perturbation(name, PERTURBATION_FUNCTIONS[name])
            else:
                print(f"Warning: Unknown perturbation type '{name}' specified")
    
    return manager 