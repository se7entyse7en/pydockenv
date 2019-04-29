import os
import subprocess
from contextlib import contextmanager
from pathlib import Path

from pydockenv import definitions


BIN_PATH = str(Path(definitions.ROOT_DIR, 'bin', 'pydockenv'))


class Commander:

    _instance = None

    def __init__(self):
        self._bin_path = BIN_PATH

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Commander()

        return cls._instance

    def run(self, cmd, env=None):
        args = cmd.split(' ')
        return subprocess.run([self._bin_path, *args], capture_output=True,
                              env=env)

    @contextmanager
    def active_env(self, env_name):
        env_diff = self.activate_env(env_name)
        env = os.environ.copy()
        env.update({k: v[1] for k, v in env_diff.items()})

        try:
            yield env
        finally:
            self.deactivate_env(env=env)

    def activate_env(self, env_name, env=None):
        return self.source(f'activate {env_name}', env=env)

    def deactivate_env(self, env=None):
        return self.source('deactivate', env=env)

    def source(self, cmd, env=None):
        proc = subprocess.Popen('env', stdout=subprocess.PIPE, shell=True,
                                env=env)
        initial_env = self._get_env(proc.stdout)
        proc.communicate()

        command = f"bash -c 'PYDOCKENV_DEBUG=1 source {self._bin_path} {cmd}'"
        proc = subprocess.Popen(command, stdout=subprocess.DEVNULL,
                                stderr=subprocess.PIPE, shell=True, env=env)
        post_env = self._get_env(proc.stderr)
        proc.communicate()

        env_diff = {}
        for k in set().union(initial_env.keys(), post_env.keys()):
            initial_value, post_value = initial_env.get(k), post_env.get(k)
            if initial_value != post_value:
                env_diff[k] = (initial_value, post_value)

        return env_diff

    def _get_env(self, stdout):
        env = {}
        for line in stdout:
            (key, _, value) = line.decode('utf8').strip().partition("=")
            env[key] = value

        return env
