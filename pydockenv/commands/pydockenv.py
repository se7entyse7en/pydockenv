import os
import subprocess
import json
from pathlib import Path

import click
import docker
from docker.types import Mount

client = docker.from_env()
conf_file_dir = Path(str(Path.home()), '.pydockenv')
status_file_path = Path(str(conf_file_dir), 'status.json')
envs_conf_path = Path(str(conf_file_dir), 'envs.json')
containers_prefix = 'pydockenv_'


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.argument('project_dir')
@click.option('--version', help='Python version')
def create(name, project_dir, version):
    version = version or 'latest'
    click.echo(f'Creating environment {name} with python version {version}...')
    image_name = f'python:{version}'
    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound:
        click.echo(f'Image {image_name} not found, pulling...')
        client.images.pull('python', tag=version)

    workdir = os.path.abspath(project_dir)
    mounts = [
        Mount('/usr/src', workdir, type='bind')
    ]
    kwargs = {
        'command': '/bin/sh',
        'stdin_open': True,
        'name': containers_prefix + name,
        'mounts': mounts,
    }
    client.containers.create(f'python:{version}', **kwargs)

    _set_conf(containers_prefix + name, {'workdir': workdir})
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


def _get_conf(env_name):
    if not envs_conf_path.exists():
        return {}

    with open(str(envs_conf_path)) as fin:
        return json.load(fin).get(env_name, {})


def _set_conf(env_name, conf):
    status = _get_conf(env_name)
    status[env_name] = conf

    os.makedirs(str(conf_file_dir), exist_ok=True)
    with open(str(envs_conf_path), 'w') as fout:
        return json.dump(status, fout)


def _get_current_env():
    return os.environ.get('PYDOCKENV')


@cli.command()
def status():
    current_env = _get_current_env()
    if not current_env:
        click.echo('No active environment')
    else:
        click.echo(
            f'Active environment: {current_env}')


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
        click.echo('Environment activated!')


@cli.command()
def deactivate():
    click.echo('Deactivating current environment...')
    current_env = _get_current_env()
    try:
        container = client.containers.get(containers_prefix + current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Environment {current_env} not found, exiting...')
    else:
        container.stop()
        click.echo('Environment deactivated!')


@cli.command()
@click.argument('args', nargs=-1)
def shell(args):
    click.echo('Running...')
    try:
        _run('python', *args)
    finally:
        click.echo('Exited!')


# Using `pip` for now
@cli.command()
@click.argument('package', required=False)
@click.option('-f', '--file', 'requirements_file',
              help='File to containing the requirements to install')
def install(package, requirements_file):
    click.echo('Running...')
    args = ['pip', 'install']
    if requirements_file:
        args.extend(['-r', requirements_file])
    else:
        args.append(package)

    try:
        _run(*args)
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
        client.containers.get(containers_prefix + current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Container {current_env} not found, exiting...')
        raise
    else:
        # This cannot be done with docker python sdk
        host_base_wd = _get_conf(containers_prefix + current_env)['workdir']
        current_wd = os.getcwd()
        if not current_wd.startswith(host_base_wd):
            raise RuntimeError(f'Cannot run files outside of {host_base_wd}')

        relative_wd = current_wd[len(host_base_wd):]
        guest_wd = f'/usr/src{relative_wd}'
        args = ['docker', 'exec',
                '-w', guest_wd, '-i', '-t',
                (containers_prefix + current_env)] + list(args)
        subprocess.check_call(args)


if __name__ == '__main__':
    cli()
