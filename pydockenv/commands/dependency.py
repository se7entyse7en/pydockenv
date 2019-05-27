import click

from pydockenv.executor import Executor


def install(package, requirements_file):
    args = ['pip', 'install']
    if requirements_file:
        args.extend(['-r', requirements_file])
    else:
        args.append(package)

    return Executor.execute(*args)


def uninstall(package, yes):
    click.echo('Running...')
    args = ['pip', 'uninstall']
    if yes:
        args.append('-y')

    args.append(package)
    try:
        Executor.execute(*args)
    finally:
        click.echo('Exited!')


def list_packages():
    click.echo('Running...')
    try:
        Executor.execute('pip', 'freeze')
    finally:
        click.echo('Exited!')
