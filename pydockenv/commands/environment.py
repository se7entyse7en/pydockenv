import json
import os
from dataclasses import dataclass
from dataclasses import field
from typing import Dict

import click
import toml

import docker
from docker.types import Mount

from pydockenv import definitions
from pydockenv.client import Client


def get_current_env():
    return os.environ.get('PYDOCKENV')


@dataclass(frozen=True)
class EnvironmentConfig:
    name: str
    python: str = 'latest'
    dependencies: Dict[str, str] = field(default_factory=dict)
    container_args: Dict[str, str] = field(default_factory=dict)
    aliases: Dict[str, Dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_file(cls, file_: str) -> 'EnvironmentConfig':
        config = toml.load(file_)['tool']['pydockenv']
        return EnvironmentConfig(**config)


def create(project_dir, file_, name, version):
    if file_:
        config = EnvironmentConfig.from_file(file_)
    else:
        config = EnvironmentConfig(name, python=version or 'latest')

    create_from_config(project_dir, config)


def create_from_config(project_dir: str, config: EnvironmentConfig):
    click.echo(f'Creating environment {config.name} with python version '
               f'{config.python}...')
    image_name = f'python:{config.python}'

    client = Client.get_instance()
    try:
        image = client.images.get(image_name)
    except docker.errors.ImageNotFound:
        click.echo(f'Image {image_name} not found, pulling...')
        image = client.images.pull('python', tag=config.python)

    create_network(config.name)
    create_env(image, project_dir, config)

    click.echo(f'Environment {config.name} with python version '
               f'{config.python} created!')


def status():
    current_env = get_current_env()
    if not current_env:
        click.echo('No active environment')
    else:
        click.echo(f'Active environment: {current_env}')


def activate(name):
    click.echo('Activating environment...')
    try:
        container = Client.get_instance().containers.get(
            definitions.CONTAINERS_PREFIX + name)
    except docker.errors.NotFound:
        click.echo(f'Environment {name} not found, exiting...')
    else:
        container.start()
        click.echo('Environment activated!')


def deactivate():
    click.echo('Deactivating current environment...')
    current_env = get_current_env()
    try:
        container = Client.get_instance().containers.get(
            definitions.CONTAINERS_PREFIX + current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Environment {current_env} not found, exiting...')
    else:
        container.stop()
        click.echo('Environment deactivated!')


def remove(name):
    click.echo(f'Removing environment {name}...')
    try:
        container = Client.get_instance().containers.get(
            definitions.CONTAINERS_PREFIX + name)
    except docker.errors.NotFound:
        click.echo(f'Environment {name} not found, exiting...')
        raise

    kwargs = {
        'force': True,
    }
    container.remove(**kwargs)
    delete_network(name)
    click.echo(f'Environment {name} removed!')


def list_environments():
    click.echo(f'Listing environments...')
    kwargs = {
        'all': True,
    }
    containers = Client.get_instance().containers.list(kwargs)

    current_env = get_current_env()
    envs = []
    for c in containers:
        if not c.name.startswith(definitions.CONTAINERS_PREFIX):
            continue

        env_name = c.name[len(definitions.CONTAINERS_PREFIX):]
        prefix = '* ' if env_name == current_env else '  '
        envs.append(f'{prefix}{env_name}')

    click.echo('\n'.join(envs))
    click.echo(f'Environments listed!')


def create_network(env_name):
    network_name = definitions.CONTAINERS_PREFIX + env_name + '_network'
    Client.get_instance().networks.create(network_name, check_duplicate=True)


def delete_network(env_name):
    network_name = definitions.CONTAINERS_PREFIX + env_name + '_network'
    try:
        network = Client.get_instance().networks.get(network_name)
    except docker.errors.ImageNotFound:
        click.echo(f'Network {network_name} not found, exiting...')
        raise

    for c in network.containers:
        network.disconnect(c)

    network.remove()


def create_env(image, project_dir, config):
    workdir = os.path.abspath(project_dir)
    mounts = [
        Mount('/usr/src', workdir, type='bind')
    ]
    kwargs = {
        'command': '/bin/sh',
        'stdin_open': True,
        'labels': {
            'workdir': workdir,
            'env_name': config.name,
            'aliases': json.dumps(config.aliases),
        },
        'name': definitions.CONTAINERS_PREFIX + config.name,
        'mounts': mounts,
        'network': definitions.CONTAINERS_PREFIX + config.name + '_network',
    }

    filtered_container_args = {k: v for k, v in config.container_args.items()
                               if k not in kwargs}
    kwargs.update(filtered_container_args)

    container = Client.get_instance().containers.create(image, **kwargs)

    if config.dependencies:
        # TODO: Remove this from here just to avoid circular imports
        from pydockenv.commands import dependency

        container.start()

        click.echo(f'Installing {len(config.dependencies)} dependencies...')
        packages = [f'{dep}{v}' for dep, v in config.dependencies.items()]
        click.echo(f'Installing {packages}...')
        dependency.install_for_container(container, packages, None)

        container.stop()
