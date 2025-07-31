"""
Abstract base repository defining the repository interface.
All concrete repositories must implement these methods.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


from uuid import UUID
from typing import Optional
from typing import List


class BaseRepository(ABC):
        """Abstract base class for all repositories"""

    @abstractmethod

    async def create(self, entity) -> object:
            """Create a new entity in the repository"""
        pass

    @abstractmethod

    async def get_by_id(self, entity_id: UUID) -> Optional[object]:
            """Get an entity by its ID"""
        pass

    @abstractmethod

    async def update(self, entity) -> Optional[object]:
            """Update an existing entity"""
        pass

    @abstractmethod

    async def delete(self, entity_id: UUID) -> bool:
            """Delete an entity by its ID, returns True if successful"""
        pass

    @abstractmethod

    async def list_all(self) -> List[object]:
            """List all entities in the repository"""
        pass

    @abstractmethod

    async def exists(self, entity_id: UUID) -> bool:
        """Check if an entity exists by its ID"""
        pass
