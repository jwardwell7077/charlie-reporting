"""
Database configuration module for database-service
"""

from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from urllib.parse import urlparse


class DatabaseConfig(BaseModel):
    """Database configuration settings"""
    
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/charlie_reporting.db",
        description="Database connection URL"
    )
    database_pool_size: int = Field(
        default=5,
        gt=0,
        description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        description="Database max overflow connections"
    )
    database_pool_timeout: int = Field(
        default=30,
        gt=0,
        description="Database pool timeout in seconds"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )
    environment: str = Field(default="development", description="Environment")
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v:
            raise ValueError("Database URL cannot be empty")
        
        try:
            parsed = urlparse(v)
            if not parsed.scheme:
                raise ValueError("Database URL must include a scheme")
            
            # Check for supported schemes
            supported_schemes = {
                'sqlite+aiosqlite', 'postgresql+asyncpg', 
                'mysql+aiomysql', 'oracle+cx_oracle'
            }
            
            if parsed.scheme not in supported_schemes:
                # Allow if it looks like a database URL pattern
                if '+' not in parsed.scheme and parsed.scheme not in ['http', 'https', 'ftp']:
                    # Might be a valid database scheme we don't know about
                    pass
                else:
                    raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
            
        except Exception as e:
            if "Unsupported database scheme" in str(e):
                raise
            raise ValueError(f"Invalid database URL format: {v}")
        
        return v
    
    @validator('database_max_overflow')
    def validate_max_overflow(cls, v, values):
        """Validate max overflow is reasonable compared to pool size"""
        pool_size = values.get('database_pool_size', 5)
        if v < 0:
            raise ValueError("Max overflow cannot be negative")
        return v
    
    def __init__(self, **kwargs):
        """Initialize with environment-specific defaults"""
        if 'environment' in kwargs:
            env = kwargs['environment']
            if env == "development":
                kwargs.setdefault('database_echo', True)
                kwargs.setdefault('database_pool_size', 5)
            elif env == "production":
                kwargs.setdefault('database_echo', False)
                kwargs.setdefault('database_pool_size', 20)
        
        super().__init__(**kwargs)
    
    def to_connection_params(self) -> Dict[str, Any]:
        """Convert to SQLAlchemy connection parameters"""
        return {
            'url': self.database_url,
            'pool_size': self.database_pool_size,
            'max_overflow': self.database_max_overflow,
            'pool_timeout': self.database_pool_timeout,
            'echo': self.database_echo
        }
    
    @classmethod
    def from_service_config(cls, service_config) -> 'DatabaseConfig':
        """Create database config from service config"""
        return cls(
            database_url=service_config.database_url,
            database_pool_size=service_config.database_pool_size,
            database_max_overflow=service_config.database_max_overflow,
            database_pool_timeout=service_config.database_pool_timeout,
            database_echo=service_config.database_echo
        )
    
    def __repr__(self):
        """String representation with masked password"""
        masked_url = self._mask_password(self.database_url)
        return (f"DatabaseConfig(url='{masked_url}', "
                f"pool_size={self.database_pool_size}, "
                f"max_overflow={self.database_max_overflow})")
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Export config with masked password"""
        data = super().model_dump(**kwargs)
        data['database_url'] = self._mask_password(data['database_url'])
        return data
    
    def _mask_password(self, url: str) -> str:
        """Mask password in database URL"""
        try:
            parsed = urlparse(url)
            if parsed.password:
                # Replace password with asterisks
                masked_netloc = parsed.netloc.replace(parsed.password, "****")
                return url.replace(parsed.netloc, masked_netloc)
        except Exception:
            pass
        return url
