import os
import subprocess
import json
from pathlib import Path

import click
import docker

client = docker.from_env()
status_file_dir = Path(str(Path.home()), '.pydockenv')
status_file_path = Path(str(status_file_dir), 'status.json')
containers_prefix = 'pydockenv_'


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.option('--version', help='Python version')
def create(name, version):
    version = version or 'latest'
    click.echo(f'Creating environment {name} with python version {version}...')
    image_name = f'python:{version}'
    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound:
        click.echo(f'Image {image_name} not found, pulling...')
        client.images.pull('python', tag=version)

    kwargs = {
        'command': '/bin/sh',
        'stdin_open': True,
        'name': containers_prefix + name,
    }
    client.containers.create(f'python:{version}', **kwargs)
    click.echo(f'Environment {name} with python version {version} created!')


@cli.command()
@click.argument('name')
def remove(name):
    click.echo(f'Removing environment {name}...')
    try:
        container = client.containers.get(containers_prefix + name)
    except docker.errors.NotFound:
        click.echo(f'Environment {name} not found, exiting...')

    kwargs = {
        'force': True,
    }
    container.remove(**kwargs)
    click.echo(f'Environment {name} removed!')


@cli.command()
def list_environments():
    click.echo(f'Listing environments...')
    kwargs = {
        'all': True,
    }
    containers = client.containers.list(kwargs)
    envs = [c.name[len(containers_prefix):] for c in containers
            if c.name.startswith(containers_prefix)]
    click.echo('\n'.join(envs))
    click.echo(f'Environments listed!')


# This is really hacky... this should be changed using env vars or maybe daemon
# manager
# /-----\
def _get_current_status():
    if not status_file_path.exists():
        return {}

    with open(str(status_file_path)) as fin:
        return json.load(fin)


def _set_current_env(env_name):
    status = _get_current_status()
    status[os.environ['SHELL_ID']] = env_name

    os.makedirs(str(status_file_dir), exist_ok=True)
    with open(str(status_file_path), 'w') as fout:
        return json.dump(status, fout)


def _get_current_env():
    return _get_current_status().get(os.environ['SHELL_ID'])
# \-----/


@cli.command()
def status():
    current_env = _get_current_env()
    if not current_env:
        click.echo('No active environment')
    else:
        click.echo(
            f'Active environment: {current_env[len(containers_prefix):]}')


@cli.command()
@click.argument('name')
def activate(name):
    click.echo('Activating environment...')
    try:
        container = client.containers.get(containers_prefix + name)
    except docker.errors.NotFound:
        click.echo(f'Environment {name} not found, exiting...')
    else:
        container.start()
        _set_current_env(containers_prefix + name)
        click.echo('Environment activated!')


@cli.command()
def deactivate():
    click.echo('Deactivating current environment...')
    current_env = _get_current_env()
    try:
        container = client.containers.get(current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Environment {current_env} not found, exiting...')
    else:
        container.stop()
        _set_current_env('')
        click.echo('Environment deactivated!')


@cli.command()
@click.argument('args', nargs=-1)
def run(args):
    click.echo('Running...')
    try:
        _run('python', *args)
    finally:
        click.echo('Exited!')


# Using `pip` for now
@cli.command()
@click.argument('package')
def install(package):
    click.echo('Running...')
    try:
        _run('pip', 'install', package)
    finally:
        click.echo('Exited!')


@cli.command()
@click.argument('package')
def uninstall(package):
    click.echo('Running...')
    try:
        _run('pip', 'uninstall', package)
    finally:
        click.echo('Exited!')


@cli.command()
def list_packages():
    click.echo('Running...')
    try:
        _run('pip', 'freeze')
    finally:
        click.echo('Exited!')


def _run(*args):
    current_env = _get_current_env()
    try:
        client.containers.get(current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Container {current_env} not found, exiting...')
        raise
    else:
        # This cannot be done with docker python sdk
        args = ['docker', 'exec', '-i', '-t', current_env] + list(args)
        subprocess.check_call(args)


if __name__ == '__main__':
    cli()
