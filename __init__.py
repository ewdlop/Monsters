"""
Monster Group Package

A Python implementation for working with the Monster group,
the largest sporadic simple group.
"""

from .monster_group import MonsterGroup, MonsterElement, demonstrate_monster_group
from .monster_utils import (
    format_large_number,
    compare_group_orders,
    get_moonshine_info,
    analyze_factorization,
    demonstrate_utilities
)

__version__ = "1.0.0"
__author__ = "Monster Group Implementation"
__description__ = "Python implementation of Monster group functionality"

__all__ = [
    "MonsterGroup",
    "MonsterElement", 
    "demonstrate_monster_group",
    "format_large_number",
    "compare_group_orders",
    "get_moonshine_info",
    "analyze_factorization",
    "demonstrate_utilities"
]