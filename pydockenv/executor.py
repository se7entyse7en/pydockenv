import os
import subprocess
from itertools import chain

import click

import docker

from pydockenv import definitions
from pydockenv.client import Client
from pydockenv.commands.environment import StateConfig


class Executor:

    @classmethod
    def execute(cls, *args, **kwargs):
        client = Client.get_instance()
        current_env = StateConfig.get_current_env()
        try:
            container = client.containers.get(
                definitions.CONTAINERS_PREFIX + current_env)
        except docker.errors.ImageNotFound:
            click.echo(f'Container {current_env} not found, exiting...')
            raise

        # This cannot be done with docker python sdk
        host_base_wd = StateConfig.get_instance().get_env_conf(
            definitions.CONTAINERS_PREFIX + current_env)['workdir']
        current_wd = os.getcwd()
        if not current_wd.startswith(host_base_wd):
            raise RuntimeError(
                f'Cannot run commands outside of {host_base_wd}')

        relative_wd = current_wd[len(host_base_wd):]
        guest_wd = f'/usr/src{relative_wd}'
        if kwargs.get('env_vars'):
            env_vars = list(chain.from_iterable([
                ['-e', f'{k}={v}']for k, v in kwargs['env_vars'].items()
            ]))
        else:
            env_vars = []

        if kwargs.get('ports'):
            port_mappers_containers_names = cls._run_port_mapper(
                container, kwargs['ports'])
        else:
            port_mappers_containers_names = []

        args = (
            ['docker', 'exec', '-w', guest_wd, '-i', '-t'] +
            env_vars +
            [(definitions.CONTAINERS_PREFIX + current_env)] +
            list(args)
        )

        subprocess.check_call(args)

        for container_name in port_mappers_containers_names:
            container = client.containers.get(container_name)
            container.stop()

    @classmethod
    def _run_port_mapper(cls, container, ports):
        guest_ip = container.attrs[
            'NetworkSettings']['Networks']['bridge']['IPAddress']
        containers_names = []
        for port in ports:
            # TODO: Use a single container for all port mappings instead of
            # spinning a container for each port
            name = f'{container.name}_port_mapper_{port}'
            cmd = f'TCP-LISTEN:1234,fork TCP-CONNECT:{guest_ip}:{port}'
            kwargs = {
                'command': cmd,
                'ports': {'1234': f'{port}/tcp'},
                'name': name,
                'detach': True,
                'auto_remove': True
            }

            Client.get_instance().containers.run('alpine/socat', **kwargs)
            containers_names.append(name)

        return containers_names
