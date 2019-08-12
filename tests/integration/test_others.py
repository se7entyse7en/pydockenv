import os

from pydockenv import definitions
from tests.base import BaseIntegrationTest


class TestIntegrationOtherCommands(BaseIntegrationTest):

    def test_run(self):
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
            proj_dir = self._create_project_dir(d['proj_name'])
            out = self._commander.run(
                f"create {d['env_name']} {str(proj_dir)} --version={d['v']}")
            self.assertEqual(out.returncode, 0)
            with self._commander.active_env(d['env_name']) as env:
                os.chdir(proj_dir)
                out = self._commander.run('run -- python --version', env=env)
                self.assertEqual(out.returncode, 0)
                self.assertIn(f"Python {d['v']}", out.stdout.decode('utf8'))

            os.chdir(definitions.ROOT_DIR)
