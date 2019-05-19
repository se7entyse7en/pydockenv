# pydockenv

![Python versions](https://img.shields.io/pypi/pyversions/pydockenv.svg)
![Pypi](https://img.shields.io/pypi/v/pydockenv.svg)
![Travis build](https://img.shields.io/travis/se7entyse7en/pydockenv.svg)
![License](https://img.shields.io/github/license/se7entyse7en/pydockenv.svg)

*Notice: This project is currently in alpha stage*

`pydockenv` is a library that aims to give the same experience of having a virtual environment, but backed by Docker! The idea is to make the usage of Docker completely hidden so that even non-expert Docker users can leverage the advantages provided by using it as the underlying engine.

## Installation

To install `pydockenv` run the following:
```
pip install --user pydockenv
```

To avoid conflicts this installs `pydockenv` to the Python user install directory. In order to run the `pydockenv` binary, you will need to have that directory in your `PATH`.

`pydockenv` supports only python >=3.6 at the moment and will use the `python` binary. In case your system has another version installed, you can use a different interpreter by specifying its path through the `PYDOCKENV_INTERPRETER` environment variable:
```
PYDOCKENV_INTERPRETER=path/to/binary pydockenv [...]
# or
export PYDOCKENV_INTERPRETER=path/to/binary
pydockenv [...]
```

## Why?

I assume that everybody landing here knows the great advantages that virtual environment brings. The reason I've started this project is that Docker provides even better isolation from the underlying system, and brings the advantage of being really portable across different systems.

In my personal experience sometimes is difficult to replicate the same local virtual environment, and eventually save it and share it with somebody else, especially if the one you want to share the environment with runs, for example, a different operating system.

Using Docker as the engine of the virtual environment makes the environment itself isolated, easily sharable, and also eventually ready-to-be-deployed given that it is still a Docker container.

## Quickstart

The installation will provide you with the `pydockenv` binary that let you create, save, load an environment and handle its dependencies.

Let's start by creating an environment!

### Let's create the environment!

To create an environment run the following command:
```
pydockenv create <env name> <project directory>
```

For example, if you are in the root of a project named `awesome-project` this could be:
```
pydockenv create awesome-project .
```

This will create a Docker container with the latest Python version installed! If you want to create an environment with a specific Python version you only just need to add the `--version=<python version>` to the previous command:
```
pydockenv create awesome-project . --version=3.6
```

As you may have noticed, to create the environment you have to set a project directory. This means that everything that is not inside the project directory is completely invisible to the environment. For example, you cannot access a Python script that resides outside your project directory. See the details in the [Advanced](#advanced) section.

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
# list packages installed in current environment
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

File: `examples/hello_world.py`

This first example just shows how different environments work. The script simply prints the "Hello World!" string followed by the Python version being used. You can run this on different environments and see how the output changes. See the following gif.

![](https://raw.githubusercontent.com/se7entyse7en/pydockenv/master/assets/hello-world.gif)

### Requests

File: `examples/requests_get.py`

This second example shows how you can install external packages and run Python scripts by passing arguments as you would do normally. See the following gif.

![](https://raw.githubusercontent.com/se7entyse7en/pydockenv/master/assets/requests-get.gif)

### Flask web app

File: `examples/flask_hello_world.py`

This third example shows how you can run a Flask web application. This example is important as it shows some caveats that make the experience of using `pydockenv` not completely identical to using a local environment. Given the environment runs inside a container, the host must be `0.0.0.0` and not `localhost`, and the port being used must be told to `pydockenv` using the `-p/--port` flag of the `run` command. See the following gif.

![](https://raw.githubusercontent.com/se7entyse7en/pydockenv/master/assets/flask-hello-world.gif)


## Commands reference

(TODO)

### Environment handling

### Packages handling

### Others

## Advanced

(TODO)

## Development

To setup you environment to develop `pydockenv` run the followings:
1. Clone the repository where you prefer:
```
git clone https://github.com/se7entyse7en/pydockenv.git <dir>
```
2. Enter in the project root directory:
```
cd <dir>
```
3. Install `pydockenv` in editable mode in another path:
```
export PYTHONPATH=<prefix>/lib/python3.7/site-packages
mkdir -p <prefix>/lib/python3.7/site-packages
pip install --prefix <prefix> -e .
```
I personally use `~/.local-dev` as `<prefix>`.

4. Rename `pydockvenv` into `dev-pydockenv` or whatever you want:
```
mv <prefix>/bin/{,dev-}pydockenv
```
5. Add `<prefix>/bin` to you `$PATH`:
```
export PATH=<prefix>/bin:$PATH
```

Now you have `dev-pydockenv` that runs the development version of `pydockenv`!
