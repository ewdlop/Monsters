"""
Tests for Monster Group implementation.
"""

import unittest
import sys
import os

# Add the current directory to the path so we can import monster_group
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monster_group import MonsterGroup, MonsterElement


class TestMonsterGroup(unittest.TestCase):
    """Test cases for MonsterGroup class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monster = MonsterGroup()
    
    def test_group_properties(self):
        """Test basic group properties."""
        self.assertEqual(self.monster.name, "Monster")
        self.assertEqual(self.monster.symbol, "M")
        self.assertTrue(self.monster.is_sporadic())
        self.assertTrue(self.monster.is_simple())
        self.assertEqual(self.monster.get_conjugacy_classes_count(), 194)
    
    def test_group_order(self):
        """Test the Monster group order."""
        expected_order = 808017424794512875886459904961710757005754368000000000
        self.assertEqual(self.monster.order, expected_order)
    
    def test_order_verification(self):
        """Test that the order matches the prime factorization."""
        self.assertTrue(self.monster.verify_order())
    
    def test_prime_factorization(self):
        """Test the prime factorization."""
        factorization = self.monster.get_factorization()
        
        # Check that all expected primes are present
        expected_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 41, 47, 59, 71]
        self.assertEqual(set(factorization.keys()), set(expected_primes))
        
        # Check specific powers
        self.assertEqual(factorization[2], 46)
        self.assertEqual(factorization[3], 20)
        self.assertEqual(factorization[5], 9)
        self.assertEqual(factorization[7], 6)
    
    def test_maximal_subgroups(self):
        """Test maximal subgroups information."""
        subgroups = self.monster.get_maximal_subgroups_info()
        self.assertGreater(len(subgroups), 0)
        self.assertIn("2^1+24.Co1 (Baby Monster normalizer)", subgroups)
    
    def test_character_table_info(self):
        """Test character table information."""
        char_info = self.monster.get_character_table_info()
        self.assertEqual(char_info["irreducible_representations"], 194)
        self.assertEqual(char_info["smallest_faithful_representation"], 196883)
        self.assertTrue(char_info["moonshine_connection"])
    
    def test_string_representations(self):
        """Test string representations."""
        self.assertIn("Monster Group", str(self.monster))
        self.assertIn("MonsterGroup", repr(self.monster))


class TestMonsterElement(unittest.TestCase):
    """Test cases for MonsterElement class."""
    
    def test_identity_element(self):
        """Test the identity element."""
        identity = MonsterElement("e")
        self.assertTrue(identity.is_identity)
        self.assertEqual(identity.order(), 1)
        self.assertEqual(identity.conjugacy_class(), "1A")
    
    def test_general_element(self):
        """Test a general (non-identity) element."""
        element = MonsterElement("g1")
        self.assertFalse(element.is_identity)
        self.assertIsNone(element.order())  # Would require computation
        self.assertIsNone(element.conjugacy_class())  # Would require computation
    
    def test_string_representations(self):
        """Test string representations of elements."""
        element = MonsterElement("test")
        self.assertIn("MonsterElement", str(element))
        self.assertIn("test", str(element))
        self.assertIn("MonsterElement", repr(element))


class TestDemonstration(unittest.TestCase):
    """Test the demonstration function."""
    
    def test_demonstration_runs(self):
        """Test that the demonstration function runs without error."""
        from monster_group import demonstrate_monster_group
        
        # This should run without raising an exception
        try:
            demonstrate_monster_group()
        except Exception as e:
            self.fail(f"Demonstration function raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()