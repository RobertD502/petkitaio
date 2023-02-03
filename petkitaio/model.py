""" Data classes for PetKit API """
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class PetKitData:
    """Dataclass for all PetKit Data."""

    user_id: str
    feeders: Optional[dict[int, Any]] = None
    litter_boxes: Optional[dict[int, Any]] = None
    water_fountains: Optional[dict[int, W5Fountain]] = None

@dataclass
class Feeder:
    """Dataclass for PetKit Feeders."""

    id: int
    data: dict[str, Any]
    type: str

@dataclass
class LitterBox:
    """Dataclass for PetKit Litter Boxes."""

    id: int
    data: dict[str, Any]
    type: str

@dataclass
class W5Fountain:
    """Dataclass for W5 Water Fountain."""

    id: int
    data: dict[str, Any]
    type: str
    ble_relay: Optional[int] = None
