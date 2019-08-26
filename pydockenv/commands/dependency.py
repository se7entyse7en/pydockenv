import click

from pydockenv.executor import Executor


def _build_install_args(packages, requirements_file):
    if not isinstance(packages, list):
        packages = [packages]

    args = ['pip', 'install']
    if requirements_file:
        args.extend(['-r', requirements_file])
    else:
        args.extend(packages)

    return args


def install(packages, requirements_file):
    return Executor.execute(
        *_build_install_args(packages, requirements_file))


def install_for_container(container, packages, requirements_file):
    return Executor.execute_for_container(
        container, *_build_install_args(packages, requirements_file),
        bypass_check=True)


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
