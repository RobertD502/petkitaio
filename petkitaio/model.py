""" Data classes for PetKit API """
from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import Any, Optional

@dataclass
class PetKitData:
    """Dataclass for all PetKit Data."""

    user_id: str
    feeders: Optional[dict[int, Any]] = None
    litter_boxes: Optional[dict[int, Any]] = None
    water_fountains: Optional[dict[int, W5Fountain]] = None
    pets: Optional[dict[int, Pet]] = None
    purifiers: Optional[dict[int, Purifier]] = None


@dataclass
class Feeder:
    """Dataclass for PetKit Feeders."""

    id: int
    data: dict[str, Any]
    type: str
    sound_list: Optional[dict[int, str]] = None
    last_manual_feed_id: Optional[str] = None


@dataclass
class LitterBox:
    """Dataclass for PetKit Litter Boxes."""

    id: int
    device_detail: dict[str, Any]
    device_record: dict[str, Any]
    statistics: dict[str, Any]
    type: str
    manually_paused: bool
    manual_pause_end: Optional[datetime] = None


@dataclass
class Purifier:
    """Dataclass for PetKit Purifiers."""

    id: int
    device_detail: dict[str, Any]
    type: str


@dataclass
class W5Fountain:
    """Dataclass for W5 Water Fountain."""

    id: int
    data: dict[str, Any]
    type: str
    group_relay: bool
    ble_relay: Optional[int] = None


@dataclass
class Pet:
    """Dataclass for registered pets."""

    id: int
    data: dict[str, Any]
    type: str
