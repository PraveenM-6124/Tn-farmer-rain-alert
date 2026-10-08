"""Notification provider abstract base stub.

TODO (Phase 6):
Abstract base class for outbound notifications with delivery receipt handling.
"""

from abc import ABC, abstractmethod


class BaseNotificationProvider(ABC):
    @abstractmethod
    async def send_message(self, recipient: str, message: str) -> dict:
        pass
