import os

import click

import docker
from docker.types import Mount

from pydockenv import definitions
from pydockenv.client import Client


def get_current_env():
    return os.environ.get('PYDOCKENV')


def create(name, project_dir, version):
    version = version or 'latest'
    click.echo(f'Creating environment {name} with python version {version}...')
    image_name = f'python:{version}'

    client = Client.get_instance()
    try:
        image = client.images.get(image_name)
    except docker.errors.ImageNotFound:
        click.echo(f'Image {image_name} not found, pulling...')
        image = client.images.pull('python', tag=version)

    create_network(name)
    create_env(image, name, project_dir)

    click.echo(f'Environment {name} with python version {version} created!')


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


def create_env(image, name, project_dir):
    workdir = os.path.abspath(project_dir)
    mounts = [
        Mount('/usr/src', workdir, type='bind')
    ]
    kwargs = {
        'command': '/bin/sh',
        'stdin_open': True,
        'labels': {
            'workdir': workdir
        },
        'name': definitions.CONTAINERS_PREFIX + name,
        'mounts': mounts,
        'network': definitions.CONTAINERS_PREFIX + name + '_network',
    }
    Client.get_instance().containers.create(image, **kwargs)
