import unittest
import sys
import os
import random

# Add the parent directory to the path so we can import the perturbation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perturbation.synonym import (
    get_wordnet_pos,
    find_replaceable_word,
    perturb_synonym
)

class TestSynonym(unittest.TestCase):
    def setUp(self):
        # Set random seed for reproducibility
        random.seed(42)
    
    def test_get_wordnet_pos(self):
        # Test mapping NLTK POS tags to WordNet POS tags
        from nltk.corpus import wordnet
        
        self.assertEqual(get_wordnet_pos("JJ"), wordnet.ADJ)
        self.assertEqual(get_wordnet_pos("VB"), wordnet.VERB)
        self.assertEqual(get_wordnet_pos("NN"), wordnet.NOUN)
        self.assertEqual(get_wordnet_pos("RB"), wordnet.ADV)
        self.assertIsNone(get_wordnet_pos("DT"))
    
    def test_find_replaceable_word(self):
        # Test finding a replaceable word in text
        text = "The company announced a significant increase in quarterly revenue."
        result = find_replaceable_word(text)
        self.assertIsNotNone(result)
        self.assertIn(result[0], ["company", "significant", "increase", "quarterly", "revenue"])
        
        # Test with a simple text
        text = "The cat jumped over the fence."
        result = find_replaceable_word(text)
        self.assertIsNotNone(result)
        self.assertIn(result[0], ["cat", "jumped", "fence"])
    
    def test_perturb_synonym(self):
        # Test perturbing text with synonym replacement
        text = "The company announced a significant increase in quarterly revenue."
        result = perturb_synonym(text)
        self.assertIsNotNone(result)
        self.assertEqual(result["operation"]["Target"], "synonym")
        self.assertNotEqual(text, result["perturbed_text"])
        
        # Test capitalization preservation
        text = "Significant growth was reported by the company."
        result = perturb_synonym(text)
        self.assertIsNotNone(result)
        
        if result["operation"]["From"] == "Significant":
            # If the replaced word was "Significant", the replacement should also be capitalized
            self.assertTrue(result["operation"]["To"][0].isupper())

if __name__ == "__main__":
    unittest.main() 