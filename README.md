# py-geth

[![Join the conversation on Discord](https://img.shields.io/discord/809793915578089484?color=blue&label=chat&logo=discord&logoColor=white)](https://discord.gg/GHryRvPB84)
[![Build Status](https://circleci.com/gh/ethereum/py-geth.svg?style=shield)](https://circleci.com/gh/ethereum/py-geth)
[![PyPI version](https://badge.fury.io/py/py-geth.svg)](https://badge.fury.io/py/py-geth)
[![Python versions](https://img.shields.io/pypi/pyversions/py-geth.svg)](https://pypi.python.org/pypi/py-geth)

Python wrapper around running `geth` as a subprocess

## System Dependency

This library requires the `geth` executable to be present.

> If managing your own bundled version of geth, set the path to the binary using the `GETH_BINARY` environment variable.

## Installation

Installation

```bash
python -m pip install py-geth
```

## Quickstart

To run geth connected to the mainnet

```python
>>> from geth import LiveGethProcess
>>> geth = LiveGethProcess()
>>> geth.start()
```

Or a private local chain for testing.  These require you to give them a name.

```python
>>> from geth import DevGethProcess
>>> geth = DevGethProcess('testing')
>>> geth.start()
```

By default the `DevGethProcess` sets up test chains in the default `datadir`
used by `geth`.  If you would like to change the location for these test
chains, you can specify an alternative `base_dir`.

```python
>>> geth = DevGethProcess('testing', '/tmp/some-other-base-dir/')
>>> geth.start()
```

Each instance has a few convenient properties.

```python
>>> geth.data_dir
"~/.ethereum"
>>> geth.rpc_port
8545
>>> geth.ipc_path
"~/.ethereum/geth.ipc"
>>> geth.accounts
['0xd3cda913deb6f67967b99d67acdfa1712c293601']
>>> geth.is_alive
False
>>> geth.is_running
False
>>> geth.is_stopped
False
>>> geth.start()
>>> geth.is_alive
True  # indicates that the subprocess hasn't exited
>>> geth.is_running
True  # indicates that `start()` has been called (but `stop()` hasn't)
>>> geth.is_stopped
False
>>> geth.stop()
>>> geth.is_alive
False
>>> geth.is_running
False
>>> geth.is_stopped
True
```

When testing it can be nice to see the logging output produced by the `geth`
process.  `py-geth` provides a mixin class that can be used to log the stdout
and stderr output to a logfile.

```python
>>> from geth import LoggingMixin, DevGethProcess
>>> class MyGeth(LoggingMixin, DevGethProcess):
...     pass
>>> geth = MyGeth()
>>> geth.start()
```

All logs will be written to logfiles in `./logs/` in the current directory.

The underlying `geth` process can take additional time to open the RPC or IPC
connections, as well as to start mining if it needs to generate the DAG.  You
can use the following interfaces to query whether these are ready.

```python
>>> geth.is_rpc_ready
True
>>> geth.wait_for_rpc(timeout=30)  # wait up to 30 seconds for the RPC connection to open
>>> geth.is_ipc_ready
True
>>> geth.wait_for_ipc(timeout=30)  # wait up to 30 seconds for the IPC socket to open
>>> geth.is_dag_generated
True
>>> geth.is_mining
True
>>> geth.wait_for_dag(timeout=600)  # wait up to 10 minutes for the DAG to generate.
```

> The DAG functionality currently only applies to the DAG for epoch 0.

## Installing specific versions of `geth`

> This feature is experimental and subject to breaking changes.

Versions of `geth` dating back to v1.11.0 can be installed using `py-geth`.
See [install.py](https://github.com/ethereum/py-geth/blob/master/geth/install.py) for
the current list of supported versions.

Installation can be done via the command line:

```bash
$ python -m geth.install v1.13.7
```

Or from python using the `install_geth` function.

```python
>>> from geth import install_geth
>>> install_geth('v1.13.7')
```

The installed binary can be found in the `$HOME/.py-geth` directory, under your
home directory.  The `v1.13.7` binary would be located at
`$HOME/.py-geth/geth-v1.13.7/bin/geth`.

## About `DevGethProcess`

The `DevGethProcess` is designed to facilitate testing.  In that regard, it is
preconfigured as follows.

- A single account is created and allocated 1 billion ether.
- All APIs are enabled on both `rpc` and `ipc` interfaces.
- Account 0 is unlocked
- Networking is configured to not look for or connect to any peers.
- The `networkid` of `1234` is used.
- Verbosity is set to `5` (DEBUG)
- Mining is enabled with a single thread.
- The RPC interface *tries* to bind to 8545 but will find an open port if this
  port is not available.
- The DevP2P interface *tries* to bind to 30303 but will find an open port if this
  port is not available.

## Gotchas

If you are running with `mining` enabled, which is default for `DevGethProcess`,
then you will likely need to generate the `DAG` manually.  If you do not, then
it will auto-generate the first time you run the process and this takes a
while.

To generate it manually:

```sh
$ geth makedag 0 ~/.ethash
```

This is especially important in CI environments like Travis-CI where your
process will likely timeout during generation.

## Development

Clone the repository:

```shell
$ git clone git@github.com:ethereum/py-geth.git
```

Next, run the following from the newly-created `py-geth` directory:

```sh
$ python -m pip install -e ".[dev]"
```

### Running the tests

You can run the tests with:

```sh
pytest tests
```

## Developer Setup

If you would like to hack on py-geth, please check out the [Snake Charmers
Tactical Manual](https://github.com/ethereum/snake-charmers-tactical-manual)
for information on how we do:

- Testing
- Pull Requests
- Documentation

We use [pre-commit](https://pre-commit.com/) to maintain consistent code style. Once
installed, it will run automatically with every commit. You can also run it manually
with `make lint`. If you need to make a commit that skips the `pre-commit` checks, you
can do so with `git commit --no-verify`.

### Development Environment Setup

You can set up your dev environment with:

```sh
git clone git@github.com:ethereum/py-geth.git
cd py-geth
virtualenv -p python3 venv
. venv/bin/activate
python -m pip install -e ".[dev]"
pre-commit install
```

### Release setup

To release a new version:

```sh
make release bump=$$VERSION_PART_TO_BUMP$$
```

#### How to bumpversion

The version format for this repo is `{major}.{minor}.{patch}` for stable, and
`{major}.{minor}.{patch}-{stage}.{devnum}` for unstable (`stage` can be alpha or beta).

To issue the next version in line, specify which part to bump,
like `make release bump=minor` or `make release bump=devnum`. This is typically done from the
master branch, except when releasing a beta (in which case the beta is released from master,
and the previous stable branch is released from said branch).

If you are in a beta version, `make release bump=stage` will switch to a stable.

To issue an unstable version when the current version is stable, specify the
new version explicitly, like `make release bump="--new-version 4.0.0-alpha.1 devnum"`

## Adding Support For New Geth Versions

There is an automation script to facilitate adding support for new geth versions: `update_geth.py`

To add support for a geth version, run the following line from the py-geth directory, substituting
the version for the one you wish to add support for. Note that the `v` in the versioning is
optional.

```shell
$ python update_geth.py v1_10_9
```

To introduce support for more than one version, pass in the versions in increasing order,
ending with the latest version.

```shell
$ python update_geth.py v1_10_7 v1_10_8 v1_10_9
```

Always review your changes before committing as something may cause this existing pattern to change at some point.
It is best to compare the git difference with a previous commit that introduced support for a new geth version to make
sure everything looks good.
