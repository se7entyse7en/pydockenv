import json
import os
import subprocess
from itertools import chain
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
        image = client.images.get(image_name)
    except docker.errors.ImageNotFound:
        click.echo(f'Image {image_name} not found, pulling...')
        image = client.images.pull('python', tag=version)

    _create_network(name)
    _create_env(image, name, project_dir)

    click.echo(f'Environment {name} with python version {version} created!')


@cli.command()
@click.argument('name')
@click.argument('project_dir')
@click.argument('input_file')
def load(name, project_dir, input_file):
    click.echo(f'Loading environment {name} from {input_file}...')
    with open(input_file, 'rb') as fin:
        image = client.images.load(fin)[0]

    _create_network(name)
    _create_env(image, name, project_dir)

    click.echo(f'Environment {name} loaded from {input_file}!')


def _create_env(image, name, project_dir):
    workdir = os.path.abspath(project_dir)
    mounts = [
        Mount('/usr/src', workdir, type='bind')
    ]
    kwargs = {
        'command': '/bin/sh',
        'stdin_open': True,
        'name': containers_prefix + name,
        'mounts': mounts,
        'network': containers_prefix + name + '_network',
    }
    client.containers.create(image, **kwargs)

    _set_conf(containers_prefix + name, {'workdir': workdir})


def _create_network(env_name):
    network_name = containers_prefix + env_name + '_network'
    client.networks.create(network_name, check_duplicate=True)


def _delete_network(env_name):
    network_name = containers_prefix + env_name + '_network'
    try:
        network = client.networks.get(network_name)
    except docker.errors.ImageNotFound:
        click.echo(f'Network {network_name} not found, exiting...')
        raise

    for c in network.containers:
        network.disconnect(c)

    network.remove()


@cli.command()
@click.option('--output', help='Name of the output file')
def save(name, output):
    current_env = _get_current_env()
    click.echo(f'Saving environment {current_env}...')

    try:
        container = client.containers.get(containers_prefix + current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Container {current_env} not found, exiting...')
        raise

    if not name:
        repository, tag = f'{containers_prefix + current_env}', 'latest'
    else:
        repository, tag = name.split(':')

    container.commit(repository=repository, tag=tag)
    image_name = f'{repository}:{tag}'
    click.echo(f'Environment {current_env} saved as image {image_name}!')
    click.echo(f'Saving image {image_name} to {output}...')

    try:
        image = client.images.get(image_name)
    except docker.errors.ImageNotFound:
        raise

    output = output or f'{image_name}.tar.gz'
    with open(output, 'wb') as fout:
        for chunk in image.save(named=True):
            fout.write(chunk)

    click.echo(f'Image {image_name} saved to {output}!')
    click.echo(f'Removing image {image_name}...')
    client.images.remove(image_name)
    click.echo(f'Image {image_name} removed')


@cli.command()
@click.argument('name')
def remove(name):
    click.echo(f'Removing environment {name}...')
    try:
        container = client.containers.get(containers_prefix + name)
    except docker.errors.NotFound:
        click.echo(f'Environment {name} not found, exiting...')
        raise

    kwargs = {
        'force': True,
    }
    container.remove(**kwargs)
    _delete_network(name)
    click.echo(f'Environment {name} removed!')


@cli.command()
def list_environments():
    click.echo(f'Listing environments...')
    kwargs = {
        'all': True,
    }
    containers = client.containers.list(kwargs)

    current_env = _get_current_env()
    envs = []
    for c in containers:
        if not c.name.startswith(containers_prefix):
            continue

        env_name = c.name[len(containers_prefix):]
        prefix = '* ' if env_name == current_env else '  '
        envs.append(f'{prefix}{env_name}')

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


@cli.command()
@click.argument('cmd')
@click.argument('args', nargs=-1)
@click.option('-e', '--env-var', multiple=True,
              help='Environment variable to set')
@click.option('-p', '--port', multiple=True,
              help='Port to reach')
def run(cmd, args, env_var, port):
    click.echo('Running...')
    env_vars = dict(e.split('=') for e in env_var)
    try:
        _run(cmd, *args, env_vars=env_vars, ports=list(port))
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


def _run(*args, **kwargs):
    current_env = _get_current_env()
    try:
        container = client.containers.get(containers_prefix + current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Container {current_env} not found, exiting...')
        raise
    else:
        # This cannot be done with docker python sdk
        host_base_wd = _get_conf(containers_prefix + current_env)['workdir']
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
            port_mappers_containers_names = _run_port_mapper(
                container, kwargs['ports'])
        else:
            port_mappers_containers_names = []

        args = (
            ['docker', 'exec', '-w', guest_wd, '-i', '-t'] +
            env_vars +
            [(containers_prefix + current_env)] +
            list(args)
        )

        subprocess.check_call(args)

        for container_name in port_mappers_containers_names:
            container = client.containers.get(container_name)
            container.stop()


def _run_port_mapper(container, ports):
    guest_ip = container.attrs[
        'NetworkSettings']['Networks']['bridge']['IPAddress']
    containers_names = []
    for port in ports:
        # TODO: Use a single container for all port mappings instead of
        # spinning a container for each port
        name = f'{container.name}_port_mapper_{port}'
        kwargs = {
            'command': f'TCP-LISTEN:1234,fork TCP-CONNECT:{guest_ip}:{port}',
            'ports': {'1234': f'{port}/tcp'},
            'name': name,
            'detach': True,
            'auto_remove': True
        }

        client.containers.run('alpine/socat', **kwargs)
        containers_names.append(name)

    return containers_names


if __name__ == '__main__':
    cli()
