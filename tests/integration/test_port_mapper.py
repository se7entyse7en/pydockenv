import os

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import docker

from pydockenv import definitions
from pydockenv.client import Client
from tests.base import BaseIntegrationTest


class TestIntegrationPortMapperCommands(BaseIntegrationTest):

    def assertPortMapperExists(self, env_name, port):
        port_mapper_container_name = (
            definitions.CONTAINERS_PREFIX + env_name + f'_port_mapper_{port}'
        )

        try:
            Client.get_instance().containers.get(
                port_mapper_container_name)
        except docker.errors.NotFound:
            self.fail(
                f'Cannot find port mapper for environment {env_name} with'
                f'port {port}'
            )

    def test_port_mapping_single_port(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'

        proj_dir = self._create_project_dir(proj_name)
        self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        with self._commander.active_env(env_name) as env:
            os.chdir(proj_dir)

            port = 8000
            out = self._commander.run(
                f'run -d -p {port} -- python -m http.server {port}', env=env)
            self.assertEqual(out.returncode, 0)
            self.assertPortMapperExists(env_name, port)

            s = requests.Session()
            s.mount('http://', HTTPAdapter(
                max_retries=Retry(connect=3, backoff_factor=1)))
            r = s.get(f'http://localhost:{port}')

            self.assertEqual(r.status_code, 200)

    def test_port_mapping_multi_ports(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'

        proj_dir = self._create_project_dir(proj_name)
        self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        with self._commander.active_env(env_name) as env:
            os.chdir(proj_dir)

            for port in range(8000, 8003):
                out = self._commander.run(
                    f'run -d -p {port} -- python -m http.server {port}',
                    env=env
                )
                self.assertEqual(out.returncode, 0)
                self.assertPortMapperExists(env_name, port)

                s = requests.Session()
                s.mount('http://', HTTPAdapter(
                    max_retries=Retry(connect=3, backoff_factor=1)))
                r = s.get(f'http://localhost:{port}')

                self.assertEqual(r.status_code, 200)
