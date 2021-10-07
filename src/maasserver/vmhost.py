from urllib.parse import urlparse

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from maasserver.clusterrpc.pods import (
    discover_pod,
    get_best_discovered_result,
    send_pod_commissioning_results,
)
from maasserver.exceptions import PodProblem
from maasserver.models import (
    BMCRoutableRackControllerRelationship,
    Event,
    Pod,
    RackController,
    VMCluster,
)
from maasserver.rpc import getClientFromIdentifiers
from maasserver.utils import absolute_reverse
from maasserver.utils.orm import post_commit_do, transactional
from maasserver.utils.threads import deferToDatabase
from metadataserver.models import NodeKey
from provisioningserver.drivers.pod import DiscoveredCluster
from provisioningserver.events import EVENT_TYPES


@inlineCallbacks
def request_commissioning_results(pod):
    """Request commissioning results from machines associated with the Pod."""
    nodes = yield deferToDatabase(lambda: list(pod.hints.nodes.all()))
    # libvirt Pods don't create machines for the host.
    if not nodes:
        return pod
    client_identifiers = yield deferToDatabase(pod.get_client_identifiers)
    client = yield getClientFromIdentifiers(client_identifiers)
    for node in nodes:
        token = yield deferToDatabase(NodeKey.objects.get_token_for_node, node)
        try:
            yield send_pod_commissioning_results(
                client,
                pod.id,
                pod.name,
                pod.power_type,
                node.system_id,
                pod.power_parameters,
                token.consumer.key,
                token.key,
                token.secret,
                urlparse(
                    absolute_reverse("metadata-version", args=["latest"])
                ),
            )
        except PodProblem as e:
            yield deferToDatabase(
                Event.objects.create_node_event,
                node,
                EVENT_TYPES.NODE_COMMISSIONING_EVENT_FAILED,
                event_description=str(e),
            )
    return pod


def discover_and_sync_vmhost(vmhost, user):
    """Sync resources and information for the VM host from discovery."""
    try:
        discovered = discover_pod(
            vmhost.power_type,
            vmhost.power_parameters,
            pod_id=vmhost.id,
            name=vmhost.name,
        )
        discovered_pod = get_best_discovered_result(discovered)
    except Exception as error:
        raise PodProblem(str(error))

    if discovered_pod is None:
        raise PodProblem(
            "Unable to start the VM host discovery process. "
            "No rack controllers connected."
        )
    elif isinstance(discovered_pod, DiscoveredCluster):
        vmhost = sync_vmcluster(discovered_pod, discovered, vmhost, user)
    else:
        vmhost = _update_db(discovered_pod, discovered, vmhost, user)
        # The data isn't committed to the database until the transaction is
        # complete. The commissioning results must be sent after the
        # transaction completes so the metadata server can process the
        # data.
        post_commit_do(
            reactor.callLater,
            0,
            request_commissioning_results,
            vmhost,
        )

    return vmhost


async def discover_and_sync_vmhost_async(vmhost, user):
    """Sync resources and information for the VM host from discovery."""
    try:
        discovered = await discover_pod(
            vmhost.power_type,
            vmhost.power_parameters,
            pod_id=vmhost.id,
            name=vmhost.name,
        )
        discovered_pod = get_best_discovered_result(discovered)
    except Exception as error:
        raise PodProblem(str(error))

    if discovered_pod is None:
        raise PodProblem(
            "Unable to start the VM host discovery process. "
            "No rack controllers connected."
        )
    elif isinstance(discovered_pod, DiscoveredCluster):
        vmhost = await sync_vmcluster_async(
            discovered_pod, discovered, vmhost, user
        )
    else:
        await deferToDatabase(
            transactional(_update_db), discovered_pod, discovered, vmhost, user
        )
        await request_commissioning_results(vmhost)

    return vmhost


def _generate_cluster_power_params(pod, pod_address, first_host):
    new_params = first_host.power_parameters.copy()
    if pod_address.startswith("http://") or pod_address.startswith("https://"):
        pod_address = pod_address.split("://")[1]
    new_params["power_address"] = pod_address
    new_params["instance_name"] = pod.name
    return new_params


def sync_vmcluster(discovered_cluster, discovered, vmhost, user):
    cluster = VMCluster.objects.create(
        name=discovered_cluster.name or vmhost.name,
        project=discovered_cluster.project,
    )
    new_host = vmhost
    for i, pod in enumerate(discovered_cluster.pods):
        power_parameters = _generate_cluster_power_params(
            pod, discovered_cluster.pod_addresses[i], vmhost
        )
        if (
            power_parameters["power_address"]
            != vmhost.power_parameters["power_address"]
        ):
            new_host = Pod.objects.create(
                name=pod.name,
                architectures=pod.architectures,
                capabilities=pod.capabilities,
                version=pod.version,
                cores=pod.cores,
                cpu_speed=pod.cpu_speed,
                power_parameters=power_parameters,
                power_type="lxd",  # VM clusters are only supported in LXD
            )
        new_host = _update_db(pod, discovered, new_host, user, cluster)
        post_commit_do(
            reactor.callLater,
            0,
            request_commissioning_results,
            new_host,
        )
        if i == 0:
            vmhost = new_host
    return vmhost


async def sync_vmcluster_async(discovered_cluster, discovered, vmhost, user):
    def _transaction(discovered_cluster, discovered, vmhost, user):
        cluster = VMCluster.objects.create(
            name=discovered_cluster.name or vmhost.name,
            project=discovered_cluster.project,
        )
        new_hosts = []
        for i, pod in enumerate(discovered_cluster.pods):
            power_parameters = _generate_cluster_power_params(
                pod, discovered_cluster.pod_addresses[i], vmhost
            )
            new_host = vmhost
            if (
                power_parameters["power_address"]
                != vmhost.power_parameters["power_address"]
            ):
                new_host = Pod.objects.create(
                    name=pod.name,
                    architectures=pod.architectures,
                    capabilities=pod.capabilities,
                    version=pod.version,
                    cores=pod.cores,
                    cpu_speed=pod.cpu_speed,
                    power_parameters=power_parameters,
                    power_type="lxd",  # VM clusters are only supported in LXD
                )
            new_host = _update_db(pod, discovered, new_host, user, cluster)
            new_hosts.append(new_host)
        return new_hosts

    new_hosts = await deferToDatabase(
        transactional(_transaction),
        discovered_cluster,
        discovered,
        vmhost,
        user,
    )
    for new_host in new_hosts:
        await request_commissioning_results(new_host)
    return new_hosts[0]


def _update_db(discovered_pod, discovered, vmhost, user, cluster=None):
    # If this is a new instance it will be stored in the database at the end of
    # sync.
    vmhost.sync(discovered_pod, user, cluster=cluster)

    # Save which rack controllers can route and which cannot.
    discovered_rack_ids = [rack_id for rack_id, _ in discovered[0].items()]
    for rack_controller in RackController.objects.all():
        routable = rack_controller.system_id in discovered_rack_ids
        (
            relation,
            created,
        ) = BMCRoutableRackControllerRelationship.objects.get_or_create(
            bmc=vmhost.as_bmc(),
            rack_controller=rack_controller,
            defaults={"routable": routable},
        )
        if not created and relation.routable != routable:
            relation.routable = routable
            relation.save()
    return vmhost