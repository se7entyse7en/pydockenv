from pathlib import Path

import docker

from pydockenv import definitions
from tests.base import BaseIntegrationTest


class TestIntegrationEnvironmentCommands(BaseIntegrationTest):

    def test_create(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'

        cont_name = definitions.CONTAINERS_PREFIX + env_name

        with self.assertRaises(docker.errors.NotFound):
            self._client.containers.get(cont_name)

        proj_dir = self._create_project_dir(proj_name)
        out = self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        self.assertEqual(out.returncode, 0)

        expected = (f'Environment {env_name} with python version '
                    f'{py_version} created!')
        self.assertIn(expected, out.stdout.decode('utf8'))

        r = self._client.containers.get(cont_name)
        self.assertEqual(r.status, 'created')

        r = self._low_level_client.inspect_container(cont_name)
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

        expected = {f'{cont_name}_network'}
        actual = set(r['NetworkSettings']['Networks'].keys())
        self.assertEqual(expected, actual)

        expected = {'workdir': str(Path(self._projs_dir, proj_name))}
        actual = r['Config']['Labels']
        self.assertEqual(expected, actual)

    def test_remove(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'

        cont_name = definitions.CONTAINERS_PREFIX + env_name

        with self.assertRaises(docker.errors.NotFound):
            self._client.containers.get(cont_name)

        proj_dir = self._create_project_dir(proj_name)
        out = self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        self.assertEqual(out.returncode, 0)

        r = self._client.containers.get(cont_name)
        self.assertEqual(r.status, 'created')

        out = self._commander.run(f'remove {env_name}')
        self.assertEqual(out.returncode, 0)

        with self.assertRaises(docker.errors.NotFound):
            self._client.containers.get(cont_name)

        with self.assertRaises(docker.errors.NotFound):
            self._client.networks.get(f'{cont_name}_network')

    def test_activate(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'
        proj_dir = self._create_project_dir(proj_name)

        out = self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        self.assertEqual(out.returncode, 0)
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

        out = self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        self.assertEqual(out.returncode, 0)

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
            self.assertEqual(out.returncode, 0)

        out = self._commander.run('list-environments')
        self.assertEqual(out.returncode, 0)

        stdout_lines = out.stdout.decode('utf8').split('\n')
        envs = set([s.strip() for s in stdout_lines if s][1:-1])

        self.assertEqual(envs - initial_envs, {d['env_name'] for d in data})

    def test_status(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'
        proj_dir = self._create_project_dir(proj_name)

        out = self._commander.run(
            f'create {env_name} {str(proj_dir)} --version={py_version}')
        self.assertEqual(out.returncode, 0)

        out = self._commander.run('status')
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout.decode('utf8').strip(),
                         'No active environment')

        with self._commander.active_env(env_name) as env:
            out = self._commander.run('status', env=env)
            self.assertEqual(out.returncode, 0)
            self.assertEqual(out.stdout.decode('utf8').strip(),
                             f'Active environment: {env_name}')
