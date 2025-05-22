import unittest
import sys
import os
import random

# Add the parent directory to the path so we can import the perturbation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perturbation.entity_reorder import (
    find_entity_list,
    reorder_entities,
    reconstruct_text_with_entities,
    perturb_entity_reorder
)

class TestEntityReorder(unittest.TestCase):
    def setUp(self):
        # Set random seed for reproducibility
        random.seed(42)
    
    def test_find_entity_list(self):
        # Test finding entity list with commas
        text = "The meeting was attended by John Smith, Jane Doe, and Robert Johnson."
        result = find_entity_list(text)
        self.assertIsNotNone(result)
        self.assertIn("John Smith", result[1])
        self.assertIn("Jane Doe", result[1])
        self.assertIn("Robert Johnson", result[1])
        
        # Test finding entity list with 'and'
        text = "The contract was signed by Apple and Microsoft."
        result = find_entity_list(text)
        self.assertIsNotNone(result)
        self.assertIn("Apple", result[1])
        self.assertIn("Microsoft", result[1])
        
        # Test with no entity list
        text = "The meeting was productive."
        result = find_entity_list(text)
        self.assertIsNone(result)
    
    def test_reorder_entities(self):
        # Test reordering a list of entities
        entities = ["John Smith", "Jane Doe", "Robert Johnson"]
        reordered = reorder_entities(entities)
        self.assertNotEqual(entities, reordered)
        self.assertEqual(set(entities), set(reordered))
        
        # Test reordering a list with only one entity (should remain the same)
        entities = ["John Smith"]
        reordered = reorder_entities(entities)
        self.assertEqual(entities, reordered)
    
    def test_reconstruct_text_with_entities(self):
        # Test reconstructing text with reordered entities
        original_text = "John Smith, Jane Doe, and Robert Johnson"
        original_entities = ["John Smith", "Jane Doe", "Robert Johnson"]
        reordered_entities = ["Jane Doe", "Robert Johnson", "John Smith"]
        
        reconstructed = reconstruct_text_with_entities(
            original_text, original_entities, reordered_entities
        )
        
        self.assertNotEqual(original_text, reconstructed)
        self.assertIn("Jane Doe", reconstructed)
        self.assertIn("Robert Johnson", reconstructed)
        self.assertIn("John Smith", reconstructed)
    
    def test_perturb_entity_reorder(self):
        # Test perturbing text with entity list
        text = "The meeting was attended by John Smith, Jane Doe, and Robert Johnson."
        result = perturb_entity_reorder(text)
        self.assertIsNotNone(result)
        self.assertEqual(result["operation"]["Target"], "entity_reorder")
        self.assertNotEqual(text, result["perturbed_text"])
        
        # Test with no entity list
        text = "The meeting was productive."
        result = perturb_entity_reorder(text)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main() 