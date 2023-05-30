from maasserver.config import RegionConfiguration
from mozilla_django_oidc.auth import OIDCAuthenticationBackend as AuthenticationBackend

class OIDCAuthenticationBackend(AuthenticationBackend):

    def __init__(self, *args, **kwargs):
        super(OIDCAuthenticationBackend, self).__init__(*args, **kwargs)
        try:
            with RegionConfiguration.open() as config:
                self.ADMIN_GROUP = config.oidc_admin_group
        except Exception:
            self.ADMIN_GROUP = 'MaaSAdmin'
        finally:
            if not self.ADMIN_GROUP:
                self.ADMIN_GROUP = 'MaaSAdmin'

    def create_user(self, claims):
        user = super(OIDCAuthenticationBackend, self).create_user(claims)

        user.username = claims.get('preferred_username', '')
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.email = claims.get('email', '')
        user.is_staff = True
        user.is_superuser = self.ADMIN_GROUP in claims.get('groups', [])
        user.save()

        return user

    def update_user(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.is_superuser = self.ADMIN_GROUP in claims.get('groups', [])
        user.save()

        return user
