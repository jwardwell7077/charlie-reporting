"""
Unit tests for abstract base repository.
Following TDD - these tests are written BEFORE implementation.
"""

import pytest
from abc import ABC
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock
from typing import List, Optional, Type

from src.domain.repositories.base_repository import BaseRepository
from src.domain.models.email_record import EmailRecord


class MockEntity:
    """Mock entity for testing base repository"""
    def __init__(self, entity_id: UUID = None):
        self.id = entity_id or uuid4()


class TestBaseRepository:
    """Test abstract base repository"""
    
    def test_base_repository_is_abstract(self):
        """Test that BaseRepository cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseRepository()
    
    def test_base_repository_has_required_abstract_methods(self):
        """Test that BaseRepository defines required abstract methods"""
        # Check that the class has the expected abstract methods
        abstract_methods = BaseRepository.__abstractmethods__
        
        expected_methods = {
            'create',
            'get_by_id', 
            'update',
            'delete',
            'list_all',
            'exists'
        }
        
        assert expected_methods.issubset(abstract_methods)
    
    def test_concrete_repository_must_implement_all_methods(self):
        """Test that concrete repositories must implement all abstract methods"""
        
        # This should fail because we don't implement all methods
        with pytest.raises(TypeError):
            class IncompleteRepository(BaseRepository):
                async def create(self, entity):
                    pass
                # Missing other required methods
            
            IncompleteRepository()
    
    def test_concrete_repository_can_be_instantiated_when_complete(self):
        """Test that concrete repository can be instantiated when all methods are implemented"""
        
        class CompleteRepository(BaseRepository):
            def __init__(self):
                self._entities = {}
            
            async def create(self, entity):
                self._entities[entity.id] = entity
                return entity
            
            async def get_by_id(self, entity_id: UUID):
                return self._entities.get(entity_id)
            
            async def update(self, entity):
                if entity.id in self._entities:
                    self._entities[entity.id] = entity
                    return entity
                return None
            
            async def delete(self, entity_id: UUID):
                return self._entities.pop(entity_id, None) is not None
            
            async def list_all(self):
                return list(self._entities.values())
            
            async def exists(self, entity_id: UUID):
                return entity_id in self._entities
        
        # This should work without raising an error
        repository = CompleteRepository()
        assert repository is not None
        assert isinstance(repository, BaseRepository)


class TestRepositoryInterface:
    """Test repository interface contracts"""
    
    @pytest.fixture
    async def mock_repository(self):
        """Create mock repository for testing interface contracts"""
        
        class MockRepository(BaseRepository):
            def __init__(self):
                self._entities = {}
            
            async def create(self, entity):
                self._entities[entity.id] = entity
                return entity
            
            async def get_by_id(self, entity_id: UUID):
                return self._entities.get(entity_id)
            
            async def update(self, entity):
                if entity.id in self._entities:
                    self._entities[entity.id] = entity
                    return entity
                return None
            
            async def delete(self, entity_id: UUID):
                return self._entities.pop(entity_id, None) is not None
            
            async def list_all(self):
                return list(self._entities.values())
            
            async def exists(self, entity_id: UUID):
                return entity_id in self._entities
        
        return MockRepository()
    
    @pytest.mark.asyncio
    async def test_create_method_contract(self, mock_repository):
        """Test create method returns the created entity"""
        entity = MockEntity()
        
        result = await mock_repository.create(entity)
        
        assert result == entity
        assert await mock_repository.exists(entity.id) is True
    
    @pytest.mark.asyncio
    async def test_get_by_id_method_contract(self, mock_repository):
        """Test get_by_id returns entity or None"""
        entity = MockEntity()
        await mock_repository.create(entity)
        
        # Existing entity
        result = await mock_repository.get_by_id(entity.id)
        assert result == entity
        
        # Non-existing entity
        non_existing_id = uuid4()
        result = await mock_repository.get_by_id(non_existing_id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_method_contract(self, mock_repository):
        """Test update method returns updated entity or None"""
        entity = MockEntity()
        await mock_repository.create(entity)
        
        # Update existing entity
        result = await mock_repository.update(entity)
        assert result == entity
        
        # Update non-existing entity
        non_existing_entity = MockEntity()
        result = await mock_repository.update(non_existing_entity)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_method_contract(self, mock_repository):
        """Test delete method returns boolean success"""
        entity = MockEntity()
        await mock_repository.create(entity)
        
        # Delete existing entity
        result = await mock_repository.delete(entity.id)
        assert result is True
        assert await mock_repository.exists(entity.id) is False
        
        # Delete non-existing entity
        non_existing_id = uuid4()
        result = await mock_repository.delete(non_existing_id)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_list_all_method_contract(self, mock_repository):
        """Test list_all returns list of all entities"""
        # Empty repository
        result = await mock_repository.list_all()
        assert result == []
        
        # Repository with entities
        entity1 = MockEntity()
        entity2 = MockEntity()
        await mock_repository.create(entity1)
        await mock_repository.create(entity2)
        
        result = await mock_repository.list_all()
        assert len(result) == 2
        assert entity1 in result
        assert entity2 in result
    
    @pytest.mark.asyncio
    async def test_exists_method_contract(self, mock_repository):
        """Test exists method returns boolean"""
        entity = MockEntity()
        
        # Non-existing entity
        result = await mock_repository.exists(entity.id)
        assert result is False
        
        # Existing entity
        await mock_repository.create(entity)
        result = await mock_repository.exists(entity.id)
        assert result is True
