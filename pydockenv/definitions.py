import os
from pathlib import Path

import pydockenv


ROOT_DIR = os.path.dirname(os.path.dirname(pydockenv.__file__))
CONTAINERS_PREFIX = 'pydockenv_'
CONF_FILE_DIR = os.environ.get('PYDOCKENV_CONF_FILE_DIR')
if not CONF_FILE_DIR:
    CONF_FILE_DIR = Path(str(Path.home()), '.pydockenv')
else:
    CONF_FILE_DIR = Path(CONF_FILE_DIR)

ENVS_CONF_PATH = Path(str(CONF_FILE_DIR), 'envs.json')
