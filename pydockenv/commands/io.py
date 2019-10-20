import subprocess

import click
import toml

import docker

from pydockenv import definitions
from pydockenv.client import Client
from pydockenv.commands.environment import EnvironmentConfig
from pydockenv.commands.environment import create_env
from pydockenv.commands.environment import create_network
from pydockenv.commands.environment import get_current_env
from pydockenv.executor import Executor


def load(name, project_dir, input_file):
    click.echo(f'Loading environment {name} from {input_file}...')
    with open(input_file, 'rb') as fin:
        image = Client.get_instance().images.load(fin)[0]

    create_network(name)
    config = EnvironmentConfig(name)
    create_env(image, project_dir, config)

    click.echo(f'Environment {name} loaded from {input_file}!')


def save(name, output):
    current_env = get_current_env()

    click.echo(f'Saving environment {current_env}...')

    image_name = _commit(name, current_env)
    _export(image_name, output)

    click.echo(f'Removing image {image_name}...')
    Client.get_instance().images.remove(image_name)
    click.echo(f'Image {image_name} removed')


def export(output):
    client = Client.get_instance()
    current_env = get_current_env()
    try:
        container = client.containers.get(
            definitions.CONTAINERS_PREFIX + current_env)
    except docker.errors.NotFound:
        click.echo(f'Container {current_env} not found, exiting...')
        raise

    click.echo(f'Exporting environment {current_env}...')

    out = Executor.execute_for_container(
        container, 'pip', 'freeze', subprocess_kwargs={
            'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE
        })

    deps = {
        k: f'=={v}' for k, v in (
            r.split('==') for r in out.stdout.decode('utf8').splitlines()
        )
    }

    # TODO: this is a hacky way to get the python version. One way to achieve
    # this could be to add a label to the initial image. But this requires
    # rebuilding the image with the new label as it's not possible to add a
    # label to an already built image.
    out = Executor.execute_for_container(
        container, 'python', '--version', subprocess_kwargs={
            'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE
        })

    python_version = out.stdout.strip().decode('utf8').split(' ')[1]

    toml_doc = {
        'tool': {
            'pydockenv': {
                'name': current_env,
                'python': python_version,
                'dependencies': deps
            }
        }
    }

    if not output:
        click.echo(toml.dumps(toml_doc))
    else:
        with open(output, 'w') as fout:
            toml.dump(toml_doc, fout)

    click.echo(f'Environment {current_env} exported!')


def _commit(name, current_env):
    click.echo(f'Saving environment {current_env} as image...')
    try:
        container = Client.get_instance().containers.get(
            definitions.CONTAINERS_PREFIX + current_env)
    except docker.errors.ImageNotFound:
        click.echo(f'Container {current_env} not found, exiting...')
        raise

    if not name:
        repository = f'{definitions.CONTAINERS_PREFIX + current_env}'
        tag = 'latest'
    else:
        repository, tag = name.split(':')

    container.commit(repository=repository, tag=tag)

    image_name = f'{repository}:{tag}'
    click.echo(f'Environment {current_env} saved as image {image_name}!')
    return image_name


def _export(image_name, output):
    click.echo(f'Saving image {image_name} to {output}...')

    try:
        image = Client.get_instance().images.get(image_name)
    except docker.errors.ImageNotFound:
        raise

    output = output or f'{image_name}.tar.gz'
    with open(output, 'wb') as fout:
        for chunk in image.save(named=True):
            fout.write(chunk)

    click.echo(f'Image {image_name} saved to {output}!')
