# Monster Group Implementation

A Python implementation providing basic functionality for working with the Monster group (M), the largest sporadic simple group.

## About the Monster Group

The Monster group is:
- The largest sporadic simple group
- Has order approximately 8×10^53 
- Contains 194 conjugacy classes
- Connected to moonshine theory and the j-invariant
- First constructed by Griess in 1980

## Features

- `MonsterGroup` class with basic group properties
- `MonsterElement` class for representing group elements
- Prime factorization of the group order
- Information about maximal subgroups
- Character table properties
- Verification utilities

## Usage

```python
from monster_group import MonsterGroup, MonsterElement, demonstrate_monster_group

# Create Monster group instance
monster = MonsterGroup()

# Get basic properties
print(f"Order: {monster.order}")
print(f"Is sporadic: {monster.is_sporadic()}")
print(f"Conjugacy classes: {monster.get_conjugacy_classes_count()}")

# Work with elements
identity = MonsterElement("e")
print(f"Identity order: {identity.order()}")

# Run demonstration
demonstrate_monster_group()
```

## Running Tests

```bash
python test_monster_group.py
```

## References

- https://mmgroup.readthedocs.io/en/latest/
- Griess, R. L. (1982). "The Friendly Giant"
- Conway, J. H. & Norton, S. P. (1979). "Monstrous Moonshine"
