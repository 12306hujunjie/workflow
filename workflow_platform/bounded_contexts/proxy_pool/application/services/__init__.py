"""Application services for proxy pool."""

from .proxy_pool_application_service import (
    ProxyPoolApplicationService,
    GetProxyRequest,
    GetProxyResponse,
    AddProxyRequest,
    ReportResultRequest,
    HealthCheckRequest,
)

__all__ = [
    'ProxyPoolApplicationService',
    'GetProxyRequest',
    'GetProxyResponse',
    'AddProxyRequest',
    'ReportResultRequest',
    'HealthCheckRequest',
]