"""
Utilities for working with the Monster group.
"""

from typing import List, Tuple
import math
from monster_group import MonsterGroup


def format_large_number(n: int) -> str:
    """
    Format a large number with scientific notation and commas.
    
    Args:
        n: The number to format
        
    Returns:
        A formatted string representation
    """
    # Regular formatting with commas
    formatted = f"{n:,}"
    
    # Scientific notation
    if n > 0:
        exponent = int(math.log10(n))
        mantissa = n / (10 ** exponent)
        scientific = f"{mantissa:.2f} × 10^{exponent}"
    else:
        scientific = "0"
    
    return f"{formatted} (≈ {scientific})"


def compare_group_orders() -> List[Tuple[str, int, str]]:
    """
    Compare the Monster group order with other notable groups.
    
    Returns:
        List of tuples (group_name, order, description)
    """
    monster_order = MonsterGroup.ORDER
    
    groups = [
        ("Symmetric S_n groups", {
            "S_5": math.factorial(5),
            "S_10": math.factorial(10),
            "S_20": math.factorial(20)
        }),
        ("Sporadic groups", {
            "Mathieu M_24": 244823040,
            "Conway Co_1": 4157776806543360000,
            "Baby Monster B": 4154781481226426191177580544000000,
            "Monster M": monster_order
        })
    ]
    
    comparisons = []
    
    for category, group_dict in groups:
        for name, order in group_dict.items():
            ratio = monster_order / order if order != monster_order else 1
            if ratio > 1:
                desc = f"Monster is {ratio:.2e} times larger"
            elif ratio == 1:
                desc = "Same as Monster"
            else:
                desc = f"Monster is {1/ratio:.2e} times smaller"
            
            comparisons.append((name, order, desc))
    
    return comparisons


def get_moonshine_info() -> dict:
    """
    Get information about monstrous moonshine.
    
    Returns:
        Dictionary with moonshine-related information
    """
    return {
        "description": "Monstrous moonshine is a connection between the Monster group and modular functions",
        "j_invariant_expansion": "j(τ) = q^(-1) + 744 + 196884q + 21493760q^2 + ...",
        "significance": "The coefficient 196884 = 196883 + 1, where 196883 is the dimension of the smallest faithful representation of M",
        "generalized_moonshine": "Extends to other sporadic groups",
        "fields_medalist": "Richard Borcherds proved the moonshine conjectures in 1992, winning the Fields Medal in 1998"
    }


def analyze_factorization():
    """
    Analyze the prime factorization of the Monster group order.
    """
    monster = MonsterGroup()
    factorization = monster.get_factorization()
    
    print("Monster Group Prime Factorization Analysis")
    print("=" * 45)
    
    print(f"\nTotal order: {format_large_number(monster.order)}")
    
    print(f"\nPrime factorization: M = ", end="")
    factors = []
    for prime, power in sorted(factorization.items()):
        if power == 1:
            factors.append(f"{prime}")
        else:
            factors.append(f"{prime}^{power}")
    print(" × ".join(factors))
    
    print(f"\nNumber of distinct prime factors: {len(factorization)}")
    print(f"Largest prime factor: {max(factorization.keys())}")
    print(f"Highest power: {max(factorization.values())} (for prime {[p for p, pow in factorization.items() if pow == max(factorization.values())][0]})")
    
    # Calculate contribution of each prime
    print("\nContribution of each prime to the total order:")
    total_order = monster.order
    for prime in sorted(factorization.keys()):
        power = factorization[prime]
        contribution = prime ** power
        percentage = (contribution / total_order) * 100
        print(f"  {prime}^{power} contributes {contribution:,} ({percentage:.10f}%)")


def demonstrate_utilities():
    """Demonstrate the utility functions."""
    print("Monster Group Utilities Demonstration")
    print("=" * 40)
    
    # Large number formatting
    monster = MonsterGroup()
    print(f"\nMonster group order: {format_large_number(monster.order)}")
    
    # Group comparisons
    print("\nGroup Order Comparisons:")
    comparisons = compare_group_orders()
    for name, order, desc in comparisons[:8]:  # Show first 8
        print(f"  {name}: {order:,}")
        print(f"    {desc}")
    
    # Moonshine information
    print("\nMonstrous Moonshine:")
    moonshine = get_moonshine_info()
    print(f"  {moonshine['description']}")
    print(f"  J-invariant: {moonshine['j_invariant_expansion']}")
    print(f"  Significance: {moonshine['significance']}")
    
    # Factorization analysis
    print("\n")
    analyze_factorization()


if __name__ == "__main__":
    demonstrate_utilities()