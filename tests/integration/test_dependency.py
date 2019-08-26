import os

from tests.base import BaseIntegrationTest


class TestIntegrationDependencyCommands(BaseIntegrationTest):

    def test_deps_handling(self):
        env_name = self._env_name()
        proj_name, py_version = 'test-proj', '3.7'

        proj_dir = self._create_project_dir(proj_name)
        out = self._commander.run(
            f'create --name={env_name} --version={py_version} {str(proj_dir)}')
        self.assertCommandOk(out)

        with self._commander.active_env(env_name) as env:
            os.chdir(proj_dir)

            out = self._commander.run('list-packages', env=env)
            self.assertCommandOk(out)
            self.assertNotIn(f'pydockenv', out.stdout.decode('utf8'))

            out = self._commander.run('install pydockenv', env=env)
            self.assertCommandOk(out)

            out = self._commander.run('list-packages', env=env)
            self.assertCommandOk(out)
            self.assertIn(f'pydockenv', out.stdout.decode('utf8'))

            out = self._commander.run('uninstall -y pydockenv ', env=env)
            self.assertCommandOk(out)

            out = self._commander.run('list-packages', env=env)
            self.assertCommandOk(out)
            self.assertNotIn(f'pydockenv', out.stdout.decode('utf8'))
