"""Services package marker without eager imports.

Avoid importing heavy submodules at package import time to keep tests light.
Import individual modules directly where needed.
"""

__all__: list[str] = []