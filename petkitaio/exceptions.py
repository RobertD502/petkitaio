"""Exceptions for PetKit."""

from typing import Any


class PetKitError(Exception):
    """Error from PetKit api."""

    def __init__(self, *args: Any) -> None:
        """Initialize the exception."""
        Exception.__init__(self, *args)


class AuthError(Exception):
    """Authentication issue from PetKit api."""

    def __init__(self, *args: Any) -> None:
        """Initialize the exception."""
        Exception.__init__(self, *args)

class BluetoothError(Exception):
    """Bluetooth issue from PetKit api."""

    def __init__(self, *args: Any) -> None:
        """Initialize the exception."""
        Exception.__init__(self, *args)