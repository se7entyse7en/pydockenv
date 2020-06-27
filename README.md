# pydockenv

![Python versions](https://img.shields.io/pypi/pyversions/pydockenv.svg)
![Pypi](https://img.shields.io/pypi/v/pydockenv.svg)
![License](https://img.shields.io/github/license/se7entyse7en/pydockenv.svg)

*Notice: This project is currently in alpha stage*

`pydockenv` is a library that aims to give the same experience of having a virtual environment, but backed by Docker! The idea is to make the usage of Docker completely hidden so that even non-expert Docker users can leverage the advantages provided by using it as the underlying engine.

## Installation

To install `pydockenv` simply run the following:
```
pip install pydockenv
```

## Why?

I assume that everybody landing here knows the great advantages that virtual environment brings. The reason I've started this project is that Docker provides even better isolation from the underlying system, and brings the advantage of being really portable across different systems.

In my personal experience sometimes it is difficult to replicate the same local virtual environment, and eventually save it and share it with somebody else, especially if the one you want to share the environment with runs, for example, a different operating system.

Using Docker as the engine of the virtual environment makes the environment itself isolated, easily sharable, and also eventually ready-to-be-deployed given that it is still a Docker container.

## Quickstart

The installation will provide you with the `pydockenv` binary that lets you create, save, load an environment, and handle its dependencies.

Let's start by creating an environment!

### Let's create the environment!

To create an environment run the following command:
```
pydockenv create --name=<env name> <project directory>
```

For example, if you are in the root of a project named `awesome-project` this could be:
```
pydockenv create --name=awesome-project .
```

This will create a Docker container with the latest Python version installed! If you want to create an environment with a specific Python version you only just need to add the `--version=<python version>` to the previous command:
```
pydockenv create --name=awesome-project --version=3.6 .
```

As you may have noticed, to create the environment you have to set a project directory. This means that everything that is not inside the project directory is completely invisible to the environment. For example, you cannot access a Python script that resides outside your project directory. See the details in the [Advanced](#advanced) section.

#### Creating an environment from a `*.toml` file

Alternatively, you can use a `*.toml` file describing your environment. This is analogous to having a `requirements.txt` file. This file describes both the dependencies and the python version to use, for example:
```
[tool.pydockenv]
name = "awesome-project"
python = "3.7.4"

[tool.pydockenv.dependencies]
requests = ">=2.22.0"
```

*All the version specifiers described in [PEP 440](https://www.python.org/dev/peps/pep-0440/#version-specifiers) are supported.*

Let's say that this is the content of a `pydockenv.toml` file in the current working directory. You can then create the environment as follows:
```
pydockenv create --file=pydockenv.toml <project directory>
```

You can eventually create it with a different name still using the `--name` flag:
```
pydockenv create --file=pydockenv.toml --name=another-awesome-project <project directory>
```

The `*.toml` file can be automatically created from an already existing environment by running:
```
pydockenv export --output=pydockenv.toml
```

### Activation and packages installation

Now you can activate your newly created environment!
```
source pydockenv activate <env name>
```

You can verify that the environment has been successfully activated by also running
```
pydockenv status
```

With `pydockenv` you can install Python packages simply by using the install command:
```
pydockenv install <package>
```
such as:
```
pydockenv install requests
```

and that's it! You can list all your environments and all the packages installed in the currently active environment with the following commands respectively:
```
# list all environments
pydockenv list-environments
# list packages installed in the current environment
pydockenv list-packages
```

### Running the Python shell

To run the Python shell you simply have to run the `shell` command:
```
pydockenv shell
```
and the shell with the correct version of Python will start.

### Running a sample application

Running a Python script is very easy as well. Instead of running it as:
```
python script.py arg1 arg2 ...
```
you just have to prefix it with `pydockenv run` as follows:
```
pydockenv run python script.py arg1 arg2 ...
```

And that's it! You're now ready to go!
For a more complete overview of the commands see the [Examples](#examples) and the [Commands reference](#commands-reference) sections.


## Examples

Here are some examples that are available in the `examples` directory to show more practically how to use `pydockenv`.

### Hello World!

File: `examples/hello_world.py`.

This first example just shows how different environments work. The script simply prints the `Hello World!` string followed by the Python version being used. You can run this in different environments and see how the output changes.

- Environment created with Python 3.8:
```
✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv create --name=hello-world --version=3.8 .
INFO[0000] Creating virtual environment...               name=hello-world project-dir=. toml-file= version=3.8
ERROR: You must give at least one requirement to install (see "pip help install")
INFO[0017] Virtual environment created!                  name=hello-world project-dir=. toml-file= version=3.8
✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ source pydockenv activate hello-world
INFO[0000] Activating virtual environment...             name=hello-world
INFO[0000] Virtual environment activated!                name=hello-world
(hello-world) ✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv run python hello_world.py
INFO[0000] Running command...                            command="[python hello_world.py]" detach=false env-vars="map[]" ports="[]"
Hello World!
Python version: 3.8.3 (default, Jun  9 2020, 17:39:39)
[GCC 8.3.0]
INFO[0000] Command ran!                                  command="[python hello_world.py]" detach=false env-vars="map[]" ports="[]"
```

- Environment created with Python 3.7.
```
✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv create --name=hello-world --version=3.7 .
INFO[0000] Creating virtual environment...               name=hello-world project-dir=. toml-file= version=3.7
ERROR: You must give at least one requirement to install (see "pip help install")
INFO[0013] Virtual environment created!                  name=hello-world project-dir=. toml-file= version=3.7
✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ source pydockenv activate hello-world
INFO[0000] Activating virtual environment...             name=hello-world
INFO[0000] Virtual environment activated!                name=hello-world
(hello-world) ✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv run python hello_world.py
INFO[0000] Running command...                            command="[python hello_world.py]" detach=false env-vars="map[]" ports="[]"
Hello World!
Python version: 3.7.7 (default, Jun  9 2020, 17:58:51)
[GCC 8.3.0]
INFO[0000] Command ran!
```

### Requests

File: `examples/requests_get.py`.

This second example shows how you can install external packages and run Python scripts by passing arguments as you would do normally.

```
✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv create --name=requests --version=3.8 .
INFO[0000] Creating virtual environment...               name=requests project-dir=. toml-file= version=3.8
INFO[0001] Virtual environment created!                  name=requests project-dir=. toml-file= version=3.8
✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ source pydockenv activate requests
INFO[0000] Activating virtual environment...             name=requests
INFO[0000] Virtual environment activated!                name=requests
(requests) ✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv install requests
INFO[0000] Installing packages...                        file= packages="[requests]"
Collecting requests
  Downloading requests-2.24.0-py2.py3-none-any.whl (61 kB)
     |████████████████████████████████| 61 kB 155 kB/s
Collecting urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1
  Downloading urllib3-1.25.9-py2.py3-none-any.whl (126 kB)
     |████████████████████████████████| 126 kB 1.2 MB/s
Collecting idna<3,>=2.5
  Downloading idna-2.9-py2.py3-none-any.whl (58 kB)
     |████████████████████████████████| 58 kB 1.2 MB/s
Collecting chardet<4,>=3.0.2
  Downloading chardet-3.0.4-py2.py3-none-any.whl (133 kB)
     |████████████████████████████████| 133 kB 1.4 MB/s
Collecting certifi>=2017.4.17
  Downloading certifi-2020.6.20-py2.py3-none-any.whl (156 kB)
     |████████████████████████████████| 156 kB 1.4 MB/s
Installing collected packages: urllib3, idna, chardet, certifi, requests
Successfully installed certifi-2020.6.20 chardet-3.0.4 idna-2.9 requests-2.24.0 urllib3-1.25.9
INFO[0005] Packages installed!                           file= packages="[requests]"
(requests) (base) ✔ (☸|gke_athenian-1_us-east1-c_production-cluster:default) se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples (go-porting)  $ pydockenv run requests_get.py https://github.com
INFO[0000] Running command...                            command="[requests_get.py https://github.com]" detach=false env-vars="map[]" ports="[]"
OCI runtime exec failed: exec failed: container_linux.go:349: starting container process caused "exec: \"requests_get.py\": executable file not found in $PATH": unknown
INFO[0000] Command ran!                                  command="[requests_get.py https://github.com]" detach=false env-vars="map[]" ports="[]"
(requests) ✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv run python requests_get.py https://github.com
INFO[0000] Running command...                            command="[python requests_get.py https://github.com]" detach=false env-vars="map[]" ports="[]"
Requested https://github.com: status code = 200
INFO[0000] Command ran!
```

### Flask web app

File: `examples/flask_hello_world.py`.

This third example shows how you can run a Flask web application. This example is important as it shows some caveats that make the experience of using `pydockenv` not completely identical to using a local environment. Given the environment runs inside a container, the host must be `0.0.0.0` and not `localhost`, and the port being used must be told to `pydockenv` using the `-p/--port` flag of the `run` command.

```
✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv create --name=flask --version=3.8 .
INFO[0000] Creating virtual environment...               name=flask project-dir=. toml-file= version=3.8
INFO[0000] Virtual environment created!                  name=flask project-dir=. toml-file= version=3.8
(base) ✔ (☸|gke_athenian-1_us-east1-c_production-cluster:default) se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples (go-porting)  $ source pydockenv activate flask
INFO[0000] Activating virtual environment...             name=flask
INFO[0000] Virtual environment activated!                name=flask
(flask) ✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv install flask
INFO[0000] Installing packages...                        file= packages="[flask]"
Collecting flask
  Downloading Flask-1.1.2-py2.py3-none-any.whl (94 kB)
     |████████████████████████████████| 94 kB 359 kB/s
Collecting itsdangerous>=0.24
  Downloading itsdangerous-1.1.0-py2.py3-none-any.whl (16 kB)
Collecting Werkzeug>=0.15
  Downloading Werkzeug-1.0.1-py2.py3-none-any.whl (298 kB)
     |████████████████████████████████| 298 kB 1.5 MB/s
Collecting Jinja2>=2.10.1
  Downloading Jinja2-2.11.2-py2.py3-none-any.whl (125 kB)
     |████████████████████████████████| 125 kB 1.7 MB/s
Collecting click>=5.1
  Downloading click-7.1.2-py2.py3-none-any.whl (82 kB)
     |████████████████████████████████| 82 kB 671 kB/s
Collecting MarkupSafe>=0.23
  Downloading MarkupSafe-1.1.1-cp38-cp38-manylinux1_x86_64.whl (32 kB)
Installing collected packages: itsdangerous, Werkzeug, MarkupSafe, Jinja2, click, flask
Successfully installed Jinja2-2.11.2 MarkupSafe-1.1.1 Werkzeug-1.0.1 click-7.1.2 flask-1.1.2 itsdangerous-1.1.0
INFO[0004] Packages installed!                           file= packages="[flask]"
(flask) ✔ se7entyse7en in ~/Projects/se7entyse7en/pydockenv/examples $ pydockenv run -p 5000 python flask_hello_world.py
INFO[0000] Running command...                            command="[python flask_hello_world.py]" detach=false env-vars="map[]" ports="[5000]"
 * Serving Flask app "flask_hello_world" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 241-187-134
```

Now you can go to `localhost:5000` and the Flask server will respond.


## Commands reference

(TODO)

### Environment handling

### Packages handling

### Others

## Advanced

(TODO)

## Development

To test changes locally during development you need to compile the program since it is called by a bash script. Once you have the project cloned locally you can do as follows from the root of the project:

1. create a link to `pydockenv` from `dev-pydockenv` that should be placed in a path of your choice that is included in `PATH`:
```
ln -s `pwd`/bin/pydockenv /usr/local/bin/dev-pydockenv
```
2. make `dev-pydockenv` call the local compiled binary:
```
export PYDOCKENV_EXEC_PATH=$(pwd)/bin
```
3. compile the program:
```
make compile-dev
```
This last step has to be ran everytime a new change has to tested.

Now you have `dev-pydockenv` that runs the development version of `pydockenv`!
