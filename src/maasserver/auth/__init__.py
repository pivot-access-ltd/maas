from .local import MAASAuthorizationBackend
from .oidc import OIDCAuthenticationBackend

__all__ = ["MAASAuthorizationBackend", "OIDCAuthenticationBackend"]
