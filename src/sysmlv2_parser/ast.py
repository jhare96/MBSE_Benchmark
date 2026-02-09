from dataclasses import dataclass
from typing import List, Optional, Union


# ============================================================================
# AST Node Definitions
# ============================================================================

@dataclass
class Element:
    name: str
    type: Optional[str] = None
    attributes: Optional[dict] = None
    children: Optional[List['Element']] = None