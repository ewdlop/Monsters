#!/usr/bin/env python3
"""
Example usage of the Monster Group implementation.

This script demonstrates how to use the Monster group classes and utilities.
"""

from monster_group import MonsterGroup, MonsterElement
from monster_utils import (
    format_large_number, 
    compare_group_orders, 
    get_moonshine_info,
    analyze_factorization
)


def main():
    """Main example function."""
    print("Monster Group Implementation Example")
    print("=" * 40)
    
    # 1. Basic Monster group usage
    print("\n1. Creating and exploring the Monster group:")
    monster = MonsterGroup()
    
    print(f"   Name: {monster.name}")
    print(f"   Symbol: {monster.symbol}")
    print(f"   Order: {format_large_number(monster.order)}")
    print(f"   Is simple: {monster.is_simple()}")
    print(f"   Is sporadic: {monster.is_sporadic()}")
    
    # 2. Working with elements
    print("\n2. Working with Monster group elements:")
    identity = MonsterElement()  # Default is identity
    element_g = MonsterElement("g")
    
    print(f"   Identity element: {identity}")
    print(f"   Identity is identity: {identity.is_identity}")
    print(f"   Identity order: {identity.order()}")
    print(f"   General element: {element_g}")
    print(f"   General element is identity: {element_g.is_identity}")
    
    # 3. Prime factorization details
    print("\n3. Prime factorization verification:")
    factorization = monster.get_factorization()
    print(f"   Number of distinct primes: {len(factorization)}")
    print(f"   Largest prime: {max(factorization.keys())}")
    print(f"   Order verification: {monster.verify_order()}")
    
    # 4. Mathematical properties
    print("\n4. Mathematical properties:")
    print(f"   Conjugacy classes: {monster.get_conjugacy_classes_count()}")
    char_info = monster.get_character_table_info()
    print(f"   Irreducible representations: {char_info['irreducible_representations']}")
    print(f"   Smallest faithful representation: {char_info['smallest_faithful_representation']}")
    
    # 5. Moonshine connection
    print("\n5. Monstrous Moonshine connection:")
    moonshine = get_moonshine_info()
    print(f"   {moonshine['description']}")
    print(f"   Key insight: {moonshine['significance']}")
    
    # 6. Size comparison
    print("\n6. Size comparison with other groups:")
    comparisons = compare_group_orders()
    for name, order, desc in comparisons[-3:]:  # Last 3 (largest)
        if "Monster" not in desc or "Same" in desc:
            continue
        print(f"   {name}: {desc}")
    
    print("\n" + "=" * 40)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()