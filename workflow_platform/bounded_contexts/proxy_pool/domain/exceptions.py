"""Proxy Pool Domain Exceptions."""

from shared_kernel.application.exceptions import DomainException


class ProxyPoolDomainException(DomainException):
    """代理池领域异常基类"""
    pass


class InvalidProxyConfigException(ProxyPoolDomainException):
    """无效的代理配置异常"""
    
    def __init__(self, message: str):
        super().__init__(f"Invalid proxy configuration: {message}")


class ProxyNotFoundError(ProxyPoolDomainException):
    """代理未找到异常"""
    
    def __init__(self, proxy_id: str):
        super().__init__(f"Proxy not found: {proxy_id}")


class NoAvailableProxyError(ProxyPoolDomainException):
    """没有可用代理异常"""
    
    def __init__(self, message: str = "No available proxies found"):
        super().__init__(message)


class ProxySelectionError(ProxyPoolDomainException):
    """代理选择异常"""
    
    def __init__(self, message: str):
        super().__init__(f"Proxy selection failed: {message}")


class ProxyHealthCheckError(ProxyPoolDomainException):
    """代理健康检查异常"""
    
    def __init__(self, proxy_id: str, error: str):
        super().__init__(f"Health check failed for proxy {proxy_id}: {error}")


class ProxyQuarantineError(ProxyPoolDomainException):
    """代理隔离异常"""
    
    def __init__(self, proxy_id: str, reason: str):
        super().__init__(f"Proxy {proxy_id} quarantined: {reason}")


class InvalidSelectionStrategyError(ProxyPoolDomainException):
    """无效的选择策略异常"""
    
    def __init__(self, strategy: str):
        super().__init__(f"Invalid selection strategy: {strategy}")


class ProxyPoolApplicationError(Exception):
    """代理池应用层异常"""
    
    def __init__(self, message: str, inner_exception: Exception = None):
        super().__init__(message)
        self.inner_exception = inner_exception