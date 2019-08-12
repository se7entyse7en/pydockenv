import os
import shutil
import unittest
from pathlib import Path

import docker

from pydockenv import definitions
from pydockenv.client import Client
from pydockenv.commands.environment import delete_network
from tests.commander import Commander


class BaseIntegrationTest(unittest.TestCase):

    ENV_SUFFIX = '__test-{index}'

    @classmethod
    def setUpClass(cls):
        cls._client = docker.from_env()
        cls._low_level_client = docker.APIClient()

    @classmethod
    def tearDownClass(cls):
        cls._client.close()
        cls._low_level_client.close()

    def setUp(self):
        self._cwd = os.getcwd()
        self._test_dir = Path(definitions.ROOT_DIR, '.test-dir')
        self._projs_dir = Path(str(self._test_dir), 'projs')

        self._commander = Commander()

        self._env_index = 1
        os.makedirs(str(self._projs_dir))

    def tearDown(self):
        os.chdir(self._cwd)
        try:
            for i in range(1, self._env_index):
                env_name = self._create_env_name(i)
                try:
                    Client.get_instance().containers.get(
                        definitions.CONTAINERS_PREFIX + env_name).remove(
                            force=True)
                    delete_network(env_name)
                except docker.errors.NotFound:
                    pass

                self._remove_port_mappers(env_name)
        finally:
            shutil.rmtree(self._test_dir.name)

    def _remove_port_mappers(self, env_name):
        prefix = definitions.CONTAINERS_PREFIX + env_name + '_port_mapper_'
        for c in Client.get_instance().containers.list(all=True):
            if c.name.startswith(prefix):
                c.remove(force=True)

    def _env_name(self):
        env_name = self._create_env_name(self._env_index)
        self._env_index += 1
        return env_name

    def _create_env_name(self, index):
        suffix = self.ENV_SUFFIX.format(index=index)
        return f'env{suffix}'

    def _create_project_dir(self, proj_name):
        proj_dir = Path(str(self._projs_dir), proj_name)
        os.makedirs(str(proj_dir))
        return proj_dir
