import click

from pydockenv.commands import dependency
from pydockenv.commands import environment
from pydockenv.commands import io
from pydockenv.executor import Executor


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.argument('project_dir')
@click.option('--version', help='Python version')
def create(name, project_dir, version):
    environment.create(name, project_dir, version)


@cli.command()
def status():
    environment.status()


@cli.command()
@click.argument('name')
def activate(name):
    environment.activate(name)


@cli.command()
def deactivate():
    environment.deactivate()


@cli.command()
@click.argument('name')
def remove(name):
    environment.remove(name)


@cli.command()
def list_environments():
    environment.list_environments()


@cli.command()
@click.argument('package', required=False)
@click.option('-f', '--file', 'requirements_file',
              help='File to containing the requirements to install')
def install(package, requirements_file):
    dependency.install(package, requirements_file)


@cli.command()
@click.argument('package')
@click.option('-y', '--yes', is_flag=True)
def uninstall(package, yes):
    dependency.uninstall(package, yes)


@cli.command()
def list_packages():
    dependency.list_packages()


@cli.command()
@click.argument('name')
@click.argument('project_dir')
@click.argument('input_file')
def load(name, project_dir, input_file):
    io.load(name, project_dir, input_file)


@cli.command()
@click.option('--output', help='Name of the output file')
def save(name, output):
    io.save(name, output)


@cli.command()
@click.argument('args', nargs=-1)
def shell(args):
    click.echo('Running...')
    try:
        Executor.execute('python', *args)
    finally:
        click.echo('Exited!')


@cli.command()
@click.argument('cmd')
@click.argument('args', nargs=-1)
@click.option('-d', '--detach', is_flag=True)
@click.option('-e', '--env-var', multiple=True,
              help='Environment variable to set')
@click.option('-p', '--port', multiple=True,
              help='Port to reach')
def run(cmd, args, detach, env_var, port):
    click.echo('Running...')
    env_vars = dict(e.split('=') for e in env_var)
    try:
        Executor.execute(cmd, *args, detach=detach,
                         env_vars=env_vars, ports=list(port))
    finally:
        click.echo('Exited!')


if __name__ == '__main__':
    cli()
