# Copyright 2022 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Django command: configure OIDC integration."""

import argparse
from textwrap import dedent
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
import yaml

from maasserver.oidc import (
    configure_region_with_oidc_client,
    configure_region_with_oidc_signing_key,
    configure_region_with_oidc_endpoint,
)


class Command(BaseCommand):
    help = "Configure MAAS OIDC integration."
    CONFIGURE_CLIENT_COMMAND = "client"
    CONFIGURE_SIGNING_KEY_COMMAND = "signing-key"
    CONFIGURE_ENDPOINT_COMMAND = "endpoint"
    STATUS_COMMAND = "status"

    def _configure_oidc_client(
        self,
        client_id: str,
        client_secret: str,
    ) -> Optional[str]:
        try:
            configure_region_with_oidc_client(
                client_id=client_id,
                client_secret=client_secret,
            )

            return dedent(
                """
                OIDC Client successfully configured!

                """
            )
        except Error as e:
            raise CommandError(e)

    def _configure_oidc_signing_key(
        self,
        signing_algo: str,
        signing_key: str,
    ) -> Optional[str]:
        try:
            configure_region_with_oidc_signing_key(
                signing_algo=signing_algo,
                signing_key=signing_key,
            )

            return dedent(
                """
                OIDC Signing Key successfully configured!

                """
            )
        except Error as e:
            raise CommandError(e)

    def _configure_oidc_endpoint(
        self,
        verify: bool,
        authorization_endpoint: str,
        token_endpoint: str,
        user_endpoint: str,
    ) -> Optional[str]:
        try:
            configure_region_with_oidc_endpoint(
                verify=verify,
                authorization_endpoint=authorization_endpoint,
                token_endpoint=token_endpoint,
                user_endpoint=user_endpoint,
            )

            return dedent(
                """
                OIDC Endpoint successfully configured!

                """
            )
        except Error as e:
            raise CommandError(e)


    def _handle_status(self, options):
        report = {"status": "disabled"}
        print(yaml.safe_dump(report), end=None)

    def _handle_configure_client(self, options):
        return self._configure_oidc_client(
            options["client_id"],
            options["client_secret"],
        )

    def _handle_configure_signing_key(self, options):
        return self._configure_oidc_signing_key(
            options["signing_algo"],
            options["signing_key"],
        )

    def _handle_configure_endpoint(self, options):
        return self._configure_oidc_endpoint(
            options["verify"],
            options["authorization_endpoint"],
            options["token_endpoint"],
            options["user_endpoint"],
        )

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="command")
        subparsers.required = True

        configure_oidc_client_parser_append = subparsers.add_parser(
            self.CONFIGURE_CLIENT_COMMAND,
            help="Update OIDC client configuration.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        configure_oidc_client_parser_append.add_argument("client_id", help="OIDC Client ID")
        configure_oidc_client_parser_append.add_argument("client_secret", help="OIDC Client Secret")

        configure_oidc_signing_key_parser_append = subparsers.add_parser(
            self.CONFIGURE_SIGNING_KEY_COMMAND,
            help="Update OIDC Provider Signing Key.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        configure_oidc_signing_key_parser_append.add_argument("signing_algo", help="Signing Key Algorithm: HS256 or RS256")
        configure_oidc_signing_key_parser_append.add_argument("signing_key", help="Signing Key in PEM or DER format")

        configure_oidc_endpoint_append = subparsers.add_parser(
            self.CONFIGURE_ENDPOINT_COMMAND,
            help="Update OIDC Endpoints.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        group = configure_oidc_endpoint_append.add_mutually_exclusive_group()
        group.add_argument("--verify-ssl", help="Verify the SSL of the OIDC endpoints", action='store_const', default=True, const=True, dest='verify')
        group.add_argument("--no-verify-ssl", help="Do not verify the SSL of the OIDC endpoints", action='store_const', const=False, dest='verify')
        configure_oidc_endpoint_append.add_argument("authorization_endpoint", help="URL of the OIDC OP authorization endpoint")
        configure_oidc_endpoint_append.add_argument("token_endpoint", help="URL of the OIDC OP token endpoint")
        configure_oidc_endpoint_append.add_argument("user_endpoint", help="URL of the OIDC OP userinfo endpoint")

        subparsers.add_parser(
            self.STATUS_COMMAND,
            help="Report status of OIDC integration",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

    def handle(self, *args, **options):
        handlers = {
            self.CONFIGURE_CLIENT_COMMAND: self._handle_configure_client,
            self.CONFIGURE_SIGNING_KEY_COMMAND: self._handle_configure_signing_key,
            self.CONFIGURE_ENDPOINT_COMMAND: self._handle_configure_endpoint,
            self.STATUS_COMMAND: self._handle_status,
        }
        return handlers[options["command"]](options)
