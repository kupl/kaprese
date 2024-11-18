# kaprese

Collection of APR tools by SAL (Software Analysis Lab) at Korea University.

## Quick Start

You can run `kaprese` by following the steps below.

### Prerequisites

`kaprese` requires the following software to be installed:

- Python 3.12 or higher (required)
- Docker 24 or higher (recommended, we did not test it on other versions)

### Installation

`kaprese` can be installed via `pip`:

```bash
pip install kaprese
```

### Usage

You can run `saver` engine on `flint-1` benchmark as follows:

```bash
kaprese benchmark preset c
kaprese engine preset saver
kaprese run -b flint-1 spearmint-1 -e saver
# See the logs. If you want to see more logs set LOV_LEVEL environment variable to INFO, e.g.,
# LOG_LEVEL=info kaprese run -b flint-1 spearmint-1 -e saver
```

## Options

`kaprese` provides the following options:

| Benchmarks | Repository                                                                                |
| :--------- | :---------------------------------------------------------------------------------------- |
| `benchmark`        | command to do something about benchmark     |
| `engine`    | command to do something about engine |
| `run`    | command to run APR tools on benchmarks |
| `-h`, `--help`    | command to show help |

## Benchmarks and Engines
`kaprese` provides a set of benchmarks and engines.
You can register them by calling `kaprese benchmark preset <language>` and `kaprese engine preset <engine>`.
The following table shows the list of supported benchmarks and engines.

### Benchmarks
| Benchmarks | Repository                                                                                |
| :--------- | :---------------------------------------------------------------------------------------- |
| `c`        | C benchmarks in [kupl/starlab-benchmarks](https://github.com/kupl/starlab-benchmarks)     |
| `ocaml`    | OCaml benchmarks in [kupl/starlab-benchmarks](https://github.com/kupl/starlab-benchmarks) |

### Engines
| Engines | Repository                                                |
| :------ | :-------------------------------------------------------- |
| `saver` | [kupl/SAVER_public](https://github.com/kupl/Saver_public) |
| `cafe`  | [kupl/LearnML](https://github.com/kupl/LearnML)           |

## How to Add Your Own

All benchmarks and engines are registered to the global registry (by default, registry is located in `~/.kaprese`).
You can add your own benchmarks and engines by registering them with a small python code.

### Add a Benchmark
A benchmark is an instance of `kaprese.core.benchmark.Benchmark`.
You can initialize a benchmark with the following 4 parameters:
- `name`: name of the benchmark (must be unique).
- `image`: docker image name, e.g., `ghcr.io/kupl/starlab-benchmarks/c:flint-1`.
- `language_command` or `_language`: command to find the language of the benchmark, if you set `_language`, `language_command` is ignored.
    the command will be run inside the docker container from `image`.
- `workdir_command` or `_workdir`: command to find the working directory of the benchmark, if you set `_workdir`, `workdir_command` is ignored.
    the command will be run inside the docker container from `image`.
Then by calling `register` method of `Benchmark`, you can register the benchmark to the global registry.

For example, the following code defines a benchmark named `flint-1`:
```python
from kaprese.core.benchmark import Benchmark

flint_1 = Benchmark(
    name="flint-1",
    image="ghcr.io/kupl/starlab-benchmarks/c:flint-1",
    language_command="cat metadata.json | jq -r .language", # c
    workdir_command="cd $(cat metadata.json | jq -r .buggyPath) && pwd", # /workspace/buggy
)
flint_1.register()

```

### Add an Engine
An engine is an instance of `kaprese.core.engine.Engine`.
You can initialize an engine with the following 6 parameters:
- `name`: name of the engine (must be unique).
- `supported_languages`: list of supported languages, e.g., `["c", "java"]`.
- `supported_os`: list of supported operating systems, e.g., `["ubuntu:20.04", "debian:12"]`.
- `location`: location to the docker context directory of the engine, e.g., `~/saver`.
- `build_args`: arguments to pass to `docker build` command to fill `ARG` variables in the Dockerfile, e.g., `{"SOME_ARG": "some_value"}`.
- `exec_commands`: list of commands to execute the engine, e.g., `["saver ...", "cp ..."]`,
    all commands are joined with `;`, in other words, all commands are executed and the return code of the last command is returned.
Note that, your dockerfile **MUST** gets the benchmark image as an argument and starts build from it, e.g.,
```dockerfile
ARG BENCHMARK_IMAGE
FROM ${BENCHMARK_IMAGE}
...
```
In the same way, you **MUST** specify the benchmark image as an argument when you build the engine image, e.g.,
```python
from kaprese.core.engine import Engine

saver = Engine(
    "saver",
    supported_languages=["c"],
    supported_os=["ubuntu:20.04"],
    location="https://github.com/kupl/kaprese-engines#main:context/saver/starlab-benchmarks", # location of saver context for preset benchmarks
    build_args={"BENCHMARK_IMAGE": "ghcr.io/kupl/starlab-benchmarks/c:flint-1"},
    exec_commands= ["saver ...", "cp ..."], # see kaprese/engines/saver.py
)
```
Then by calling `register` method of `Engine`, you can register the engine to the global registry.
```
saver.register()
```

## How to Contribute
Any contributions are welcome!
You can leave an [issue](https://github.com/kupl/kaprese/issues) or make a [pull request](https://github.com/kupl/kaprese/pulls).
