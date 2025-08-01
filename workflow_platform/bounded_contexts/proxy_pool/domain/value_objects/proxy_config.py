"""Value objects for proxy configuration."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
import re
from urllib.parse import urlparse

from ..exceptions import InvalidProxyConfigException


class ProxyProtocol(Enum):
    """Supported proxy protocols."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyStatus(Enum):
    """Proxy status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    FAILED = "failed"
    BLOCKED = "blocked"


class AnonymityLevel(Enum):
    """Proxy anonymity levels."""
    TRANSPARENT = 1  # Real IP visible
    ANONYMOUS = 2    # Real IP hidden but proxy detected
    ELITE = 3        # Real IP hidden and proxy not detected


class SelectionStrategy(Enum):
    """Proxy selection strategies."""
    BEST = "best"
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED = "weighted"
    GEO_PREFERRED = "geo_preferred"


@dataclass(frozen=True)
class ProxyCredentials:
    """Proxy authentication credentials."""
    username: str
    password: str
    
    def __post_init__(self):
        if not self.username or not self.password:
            raise InvalidProxyConfigException("Username and password cannot be empty")


@dataclass(frozen=True)
class GeoLocation:
    """Geographic location information."""
    country: Optional[str] = None
    country_code: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    def __post_init__(self):
        if self.country_code and len(self.country_code) != 2:
            raise InvalidProxyConfigException("Country code must be 2 characters")
        
        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise InvalidProxyConfigException("Latitude must be between -90 and 90")
        
        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise InvalidProxyConfigException("Longitude must be between -180 and 180")


@dataclass(frozen=True)
class ProxyEndpoint:
    """Proxy endpoint configuration."""
    host: str
    port: int
    protocol: ProxyProtocol
    
    def __post_init__(self):
        if not self.host:
            raise InvalidProxyConfigException("Host cannot be empty")
        
        if not self._is_valid_host(self.host):
            raise InvalidProxyConfigException(f"Invalid host format: {self.host}")
        
        if not (1 <= self.port <= 65535):
            raise InvalidProxyConfigException(f"Port must be between 1 and 65535, got {self.port}")
    
    def _is_valid_host(self, host: str) -> bool:
        """Validate host format (IP or domain)."""
        # Check if it's a valid IP address
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, host):
            parts = host.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        
        # Check if it's a valid domain name
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(domain_pattern, host))
    
    @property
    def url(self) -> str:
        """Get proxy URL without credentials."""
        return f"{self.protocol.value}://{self.host}:{self.port}"
    
    def url_with_credentials(self, credentials: Optional[ProxyCredentials] = None) -> str:
        """Get proxy URL with credentials."""
        if credentials:
            return f"{self.protocol.value}://{credentials.username}:{credentials.password}@{self.host}:{self.port}"
        return self.url
    
    @classmethod
    def from_url(cls, url: str) -> 'ProxyEndpoint':
        """Create ProxyEndpoint from URL."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.hostname or not parsed.port:
                raise ValueError("Invalid proxy URL format")
            
            protocol = ProxyProtocol(parsed.scheme.lower())
            return cls(
                host=parsed.hostname,
                port=parsed.port,
                protocol=protocol
            )
        except (ValueError, AttributeError) as e:
            raise InvalidProxyConfigException(f"Invalid proxy URL: {url}") from e


@dataclass(frozen=True)
class ProxyConfiguration:
    """Complete proxy configuration."""
    endpoint: ProxyEndpoint
    credentials: Optional[ProxyCredentials] = None
    geo_location: Optional[GeoLocation] = None
    tags: List[str] = None
    max_concurrent: int = 10
    timeout: float = 30.0
    retry_count: int = 3
    
    def __post_init__(self):
        if self.tags is None:
            object.__setattr__(self, 'tags', [])
        
        if self.max_concurrent <= 0:
            raise InvalidProxyConfigException("max_concurrent must be positive")
        
        if self.timeout <= 0:
            raise InvalidProxyConfigException("timeout must be positive")
        
        if self.retry_count < 0:
            raise InvalidProxyConfigException("retry_count cannot be negative")
    
    @property
    def url(self) -> str:
        """Get complete proxy URL."""
        return self.endpoint.url_with_credentials(self.credentials)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'host': self.endpoint.host,
            'port': self.endpoint.port,
            'protocol': self.endpoint.protocol.value,
            'username': self.credentials.username if self.credentials else None,
            'password': self.credentials.password if self.credentials else None,
            'country': self.geo_location.country if self.geo_location else None,
            'country_code': self.geo_location.country_code if self.geo_location else None,
            'city': self.geo_location.city if self.geo_location else None,
            'tags': self.tags,
            'max_concurrent': self.max_concurrent,
            'timeout': self.timeout,
            'retry_count': self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProxyConfiguration':
        """Create ProxyConfiguration from dictionary."""
        try:
            protocol = ProxyProtocol(data['protocol'])
            endpoint = ProxyEndpoint(
                host=data['host'],
                port=data['port'],
                protocol=protocol
            )
            
            credentials = None
            if data.get('username') and data.get('password'):
                credentials = ProxyCredentials(
                    username=data['username'],
                    password=data['password']
                )
            
            geo_location = None
            if any(data.get(key) for key in ['country', 'country_code', 'city']):
                geo_location = GeoLocation(
                    country=data.get('country'),
                    country_code=data.get('country_code'),
                    city=data.get('city')
                )
            
            return cls(
                endpoint=endpoint,
                credentials=credentials,
                geo_location=geo_location,
                tags=data.get('tags', []),
                max_concurrent=data.get('max_concurrent', 10),
                timeout=data.get('timeout', 30.0),
                retry_count=data.get('retry_count', 3)
            )
        except (KeyError, ValueError, TypeError) as e:
            raise InvalidProxyConfigException(f"Invalid proxy configuration data") from e


@dataclass(frozen=True)
class HealthCheckConfig:
    """Health check configuration."""
    test_url: str = "http://httpbin.org/ip"
    timeout: float = 10.0
    interval: float = 300.0  # 5 minutes
    max_failures: int = 3
    recovery_interval: float = 900.0  # 15 minutes
    anonymity_check: bool = True
    geo_verification: bool = True
    
    def __post_init__(self):
        if not self.test_url:
            raise InvalidProxyConfigException("test_url cannot be empty")
        
        if self.timeout <= 0:
            raise InvalidProxyConfigException("timeout must be positive")
        
        if self.interval <= 0:
            raise InvalidProxyConfigException("interval must be positive")
        
        if self.max_failures <= 0:
            raise InvalidProxyConfigException("max_failures must be positive")
        
        if self.recovery_interval <= 0:
            raise InvalidProxyConfigException("recovery_interval must be positive")