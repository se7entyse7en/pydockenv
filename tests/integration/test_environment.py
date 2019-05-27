from pathlib import Path

import docker

from pydockenv import definitions
from tests.base import BaseIntegrationTest


class TestIntegrationEnvironmentCommands(BaseIntegrationTest):

    def test_create(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'

        with self.assertRaises(docker.errors.NotFound):
            self._client.containers.get(
                definitions.CONTAINERS_PREFIX + env_name)

        proj_dir = self._create_project_dir(proj_name)
        out = self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')

        expected = (f'Environment {env_name} with python version '
                    f'{py_version} created!')

        self.assertEqual(out.returncode, 0)
        self.assertIn(expected, out.stdout.decode('utf8'))

        r = self._client.containers.get(
            definitions.CONTAINERS_PREFIX + env_name)
        self.assertEqual(r.status, 'created')

        r = self._low_level_client.inspect_container(
            definitions.CONTAINERS_PREFIX + env_name)
        self.assertEqual(len(r['Mounts']), 1)

        expected = {
            'Destination': '/usr/src',
            'Mode': '',
            'Propagation': 'rprivate',
            'RW': True,
            'Source': str(proj_dir.absolute()),
            'Type': 'bind'
        }
        actual = r['Mounts'][0]
        self.assertEqual(expected, actual)

        expected = {f'{definitions.CONTAINERS_PREFIX}{env_name}_network'}
        actual = set(r['NetworkSettings']['Networks'].keys())
        self.assertEqual(expected, actual)

        conf = self._get_conf()

        container_name = f'{definitions.CONTAINERS_PREFIX}{env_name}'
        expected = {
            container_name: {
                'workdir': str(Path(self._projs_dir, proj_name))
            }
        }
        self.assertEqual(conf, expected)

    def test_multi_create(self):
        data = [
            {
                'env_name': self._env_name(),
                'proj_name': 'test-proj-1',
                'v': '3.7',
            },
            {
                'env_name': self._env_name(),
                'proj_name': 'test-proj-2',
                'v': '3.6',
            },
            {
                'env_name': self._env_name(),
                'proj_name': 'test-proj-3',
                'v': '2.7',
            },
        ]

        for d in data:
            with self.assertRaises(docker.errors.NotFound):
                self._client.containers.get(
                    definitions.CONTAINERS_PREFIX + d['env_name'])

            proj_dir = self._create_project_dir(d['proj_name'])
            self._commander.run(
                f"create {d['env_name']} {str(proj_dir)} --version={d['v']}"
            )

        conf = self._get_conf()
        expected = {
            f"{definitions.CONTAINERS_PREFIX}{d['env_name']}": {
                'workdir': str(Path(self._projs_dir, d['proj_name']))
            } for d in data
        }

        self.assertEqual(conf, expected)

    def test_remove(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'

        with self.assertRaises(docker.errors.NotFound):
            self._client.containers.get(
                definitions.CONTAINERS_PREFIX + env_name)

        proj_dir = self._create_project_dir(proj_name)
        self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')

        r = self._client.containers.get(
            definitions.CONTAINERS_PREFIX + env_name)
        self.assertEqual(r.status, 'created')

        self._commander.run(f'remove {env_name}')

        with self.assertRaises(docker.errors.NotFound):
            self._client.containers.get(
                definitions.CONTAINERS_PREFIX + env_name)

        with self.assertRaises(docker.errors.NotFound):
            self._client.networks.get(
                definitions.CONTAINERS_PREFIX + env_name + '_network')

        self.assertEqual(self._get_conf(), {})

    def test_activate(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'
        proj_dir = self._create_project_dir(proj_name)

        self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        env_diff = self._commander.activate_env(f'{env_name}')

        self.assertTrue({'PYDOCKENV', 'PYDOCKENV_DEBUG', 'PS1', 'SHLVL'} <=
                        set(env_diff.keys()))
        self.assertEqual(env_diff['PYDOCKENV'][1], env_name)
        self.assertEqual(env_diff['PYDOCKENV_DEBUG'][1], '1')
        self.assertEqual(env_diff['PS1'][1], f'({env_name})')
        self.assertEqual(int(env_diff['SHLVL'][1]),
                         int(env_diff['SHLVL'][0] or 0) + 1)

    def test_deactivate(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'
        proj_dir = self._create_project_dir(proj_name)

        self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')

        with self._commander.active_env(env_name) as env:
            env_diff_post_deactivate = self._commander.deactivate_env(env=env)

            self.assertEqual({'PYDOCKENV', 'PS1', 'SHLVL'},
                             env_diff_post_deactivate.keys())
            self.assertEqual(env_diff_post_deactivate['PYDOCKENV'][1], '')
            self.assertEqual(env_diff_post_deactivate['PS1'][1], '')
            self.assertEqual(int(env_diff_post_deactivate['SHLVL'][1]),
                             int(env_diff_post_deactivate['SHLVL'][0]) + 1)

    def test_list_environments(self):
        out = self._commander.run('list-environments')
        self.assertEqual(out.returncode, 0)

        stdout_lines = out.stdout.decode('utf8').split('\n')
        initial_envs = set([s.strip() for s in stdout_lines if s][1:-1])

        data = [
            {
                'env_name': self._env_name(),
                'proj_name': 'test-proj-1',
                'v': '3.7',
            },
            {
                'env_name': self._env_name(),
                'proj_name': 'test-proj-2',
                'v': '3.6',
            },
            {
                'env_name': self._env_name(),
                'proj_name': 'test-proj-3',
                'v': '2.7',
            },
        ]

        for d in data:
            with self.assertRaises(docker.errors.NotFound):
                self._client.containers.get(
                    definitions.CONTAINERS_PREFIX + d['env_name'])

            proj_dir = self._create_project_dir(d['proj_name'])
            out = self._commander.run(
                f"create {d['env_name']} {str(proj_dir)} --version={d['v']}"
            )

        out = self._commander.run('list-environments')
        self.assertEqual(out.returncode, 0)

        stdout_lines = out.stdout.decode('utf8').split('\n')
        envs = set([s.strip() for s in stdout_lines if s][1:-1])

        self.assertEqual(envs - initial_envs, {d['env_name'] for d in data})

    def test_status(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'
        proj_dir = self._create_project_dir(proj_name)

        self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')

        out = self._commander.run('status')
        self.assertEqual(out.stdout.decode('utf8').strip(),
                         'No active environment')

        with self._commander.active_env(env_name) as env:
            out = self._commander.run('status', env=env)
            self.assertEqual(out.stdout.decode('utf8').strip(),
                             f'Active environment: {env_name}')
