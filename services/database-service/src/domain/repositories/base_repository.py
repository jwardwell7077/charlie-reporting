"""Abstract base repository defining the repository interface.
All concrete repositories must implement these methods.
"""

from abc import ABC, abstractmethod
from uuid import UUID


class BaseRepository(ABC):
    """Abstract base class for all repositories"""
    pass

    @abstractmethod
    async def create(self, entity) -> object:
        """Create a new entity in the repository"""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> object | None:
        """Get an entity by its ID"""
        pass

    @abstractmethod
    async def update(self, entity) -> object | None:
        """Update an existing entity"""
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its ID, returns True if successful"""
        pass

    @abstractmethod
    async def list_all(self) -> list[object]:
        """List all entities in the repository"""
        pass

    @abstractmethod
    async def exists(self, entity_id: UUID) -> bool:
        """Check if an entity exists by its ID"""
        pass
