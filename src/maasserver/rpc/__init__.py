# Copyright 2014 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Region Controller RPC."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

str = None

__metaclass__ = type
__all__ = [
    "getClientFor",
    "getAllClients",
]

from maasserver import eventloop
from provisioningserver.rpc import exceptions
from provisioningserver.utils.twisted import (
    asynchronous,
    FOREVER,
    )


@asynchronous(timeout=FOREVER)  # getClientFor handles times-out itself.
def getClientFor(uuid, timeout=0):
    """getClientFor(uuid)

    Get a client with which to make RPCs to the specified cluster.

    :param timeout: The number of seconds to wait before giving up
        getting a connection. By default, `timeout` is 0.
    :raises: :py:class:`~.exceptions.NoConnectionsAvailable` when there
        are no open connections to the specified cluster controller.
    """
    try:
        service = eventloop.services.getServiceNamed("rpc")
    except KeyError:
        raise exceptions.NoConnectionsAvailable()
    else:
        return service.getClientFor(uuid, timeout=timeout)


@asynchronous(timeout=FOREVER)  # getAllClients does not defer work.
def getAllClients():
    """getAllClients()

    Get all recorded clients ready to make RPCs to clusters.
    """
    try:
        service = eventloop.services.getServiceNamed("rpc")
    except KeyError:
        return []
    else:
        return service.getAllClients()
