from .base import PerturbationManager
from typing import List, Optional

__all__ = [
    'PerturbationManager',
    'create_perturbation_manager'
]

def create_perturbation_manager(enabled_types: Optional[List[str]] = None) -> PerturbationManager:
    """
    Create and configure a perturbation manager with specified or all available perturbation types.
    Args:
        enabled_types: List of perturbation type names to enable (None for all)
    Returns:
        Configured PerturbationManager
    """
    manager = PerturbationManager()

    # Map of perturbation type names to their functions (imported only as needed)
    perturbation_imports = {
        'date_format': lambda: __import__(__name__ + '.date_format', fromlist=['perturb_date_format']).perturb_date_format,
        'entity_reorder': lambda: __import__(__name__ + '.entity_reorder', fromlist=['perturb_entity_reorder']).perturb_entity_reorder,
        'number_rephrase': lambda: __import__(__name__ + '.number_rephrase', fromlist=['perturb_number_rephrase']).perturb_number_rephrase,
        'synonym': lambda: __import__(__name__ + '.synonym', fromlist=['perturb_synonym']).perturb_synonym
    }

    if enabled_types is None:
        enabled_types = list(perturbation_imports.keys())

    for name in enabled_types:
        if name in perturbation_imports:
            func = perturbation_imports[name]()
            manager.register_perturbation(name, func)
        else:
            print(f"Warning: Unknown perturbation type '{name}' specified")

    return manager 