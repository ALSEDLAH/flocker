# Copyright Hybrid Logic Ltd.  See LICENSE file for details.
# -*- test-case-name: flocker.node.test.test_deploy -*-

"""
Deploy applications on nodes.
"""

from .gear import GearClient
from ._model import Application


class Deployer(object):
    """
    Start and stop containers.
    """
    def __init__(self, gear_client=None):
        """
        :param IGearClient gear_client: The gear client API to use in
            deployment operations. Default ``GearClient``.
        """
        if gear_client is None:
            gear_client = GearClient(hostname=b'127.0.0.1')
        self._gear_client = gear_client

    def start_container(self, application):
        """
        Launch the supplied application as a `gear` unit.

        :param Application application: The ``Application`` to create and
            start.
        :returns: A ``Deferred`` which fires with ``None`` when the application
           has started.
        """
        return self._gear_client.add(application.name,
                                     application.image.full_name)

    def stop_container(self, application):
        """
        Stop and disable the application.

        :param Application application: The ``Application`` to stop.
        :returns: A ``Deferred`` which fires with ``None`` when the application
            has stopped.
        """
        unit_name = application.name
        return self._gear_client.remove(unit_name)

    def discover_node_configuration(self):
        """
        List all the ``Application``\ s running on this node.

        :returns: A ``Deferred`` which fires with a list of ``Application``
            instances.
        """
        d = self._gear_client.list()

        def applications_from_units(units):
            applications = []
            for unit in units:
                # XXX: This currently only populates the Application name. The
                # container_image will be available on the Unit when
                # https://github.com/ClusterHQ/flocker/issues/207 is resolved.
                applications.append(Application(name=unit.name))
            return applications
        d.addCallback(applications_from_units)
        return d

    def change_node_configuration(self, desired_configuration, hostname):
        """
        Work out which containers need to be started and stopped for the
        configuration to match the given configuration file.

        :param Deployment desired_configuration: The intended configuration
            of all nodes.
        :param bytes hostname: The hostname of the node that this is running
            on.

        :return: A ``Deferred`` which fires with a ``dict`` specifying which
            containers must be started and which must be stopped.
        """
        desired_node_applications = []
        for node in desired_configuration.nodes:
            if node.hostname == hostname:
                desired_node_applications = node.applications

        d = self.discover_node_configuration()

        def find_differences(current_configuration):
            changes = {}
            current = set(current_configuration)
            desired = set(desired_node_applications)
            changes['start_containers'] = desired.difference(current)
            changes['stop_containers'] = current.difference(desired)
            return changes
        d.addCallback(find_differences)
        return d
