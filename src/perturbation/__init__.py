from .base import PerturbationManager
from .date_format import perturb_date_format
from .entity_reorder import perturb_entity_reorder
from .number_rephrase import perturb_number_rephrase
from .synonym import perturb_synonym

__all__ = [
    'PerturbationManager',
    'perturb_date_format',
    'perturb_entity_reorder',
    'perturb_number_rephrase',
    'perturb_synonym'
]

def create_perturbation_manager() -> PerturbationManager:
    """
    Create and configure a perturbation manager with all available perturbation types.
    
    Returns:
        Configured PerturbationManager
    """
    manager = PerturbationManager()
    
    # Register all perturbation functions
    manager.register_perturbation('date_format', perturb_date_format)
    manager.register_perturbation('entity_reorder', perturb_entity_reorder)
    manager.register_perturbation('number_rephrase', perturb_number_rephrase)
    manager.register_perturbation('synonym', perturb_synonym)
    
    return manager 