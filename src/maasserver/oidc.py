from maasserver.config import RegionConfiguration

# TODO: do basic checkings

def configure_region_with_oidc_client(
    client_id: str,
    client_secret: str,
):
    """Configure the region OIDC client.

    """

    with RegionConfiguration.open_for_update() as config:
        config.oidc_client_id = client_id
        config.oidc_client_secret = client_secret

def configure_region_with_oidc_signing_key(
    signing_algo: str,
    signing_key: str,
):
    """Configure the region OIDC signing key.

    """

    with RegionConfiguration.open_for_update() as config:
        config.oidc_sign_algo = signing_algo
        config.oidc_sign_key = signing_key

def configure_region_with_oidc_endpoint(
    verify: bool,
    authorization_endpoint: str,
    token_endpoint: str,
    user_endpoint: str,
):
    """Configure the region OIDC endpoint.

    """

    with RegionConfiguration.open_for_update() as config:
        config.oidc_endpoint_verify_ssl = verify
        config.oidc_authorization_endpoint = authorization_endpoint
        config.oidc_token_endpoint = token_endpoint
        config.oidc_user_endpoint = user_endpoint

