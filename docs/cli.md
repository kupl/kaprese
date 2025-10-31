# CLI Reference

This document provides a comprehensive reference for all `kaprese` CLI commands, their options, and usage examples.

## Table of Contents

- [Global Options](#global-options)
- [Main Commands](#main-commands)
  - [config](#config)
  - [benchmark](#benchmark)
  - [engine](#engine)
  - [run](#run)
  - [eval](#eval)

---

## Global Options

These options are available for all `kaprese` commands:

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `-v`, `--version` | Show program's version number and exit | - |
| `--kaprese-config <dir>` | Path to kaprese config directory | `~/.kaprese` |

### Example

```bash
# Show version
kaprese --version

# Use custom config directory
kaprese --kaprese-config /path/to/config run -b flint-1 -e saver
```

---

## Main Commands

### config

Configure kaprese settings.

#### Subcommands

##### config show

Display current configuration settings.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `-k [KEY ...]`, `--key [KEY ...]` | Specific configuration key(s) to show | All keys |

**Example:**

```bash
# Show all configuration
kaprese config show

# Show specific configuration keys
kaprese config show -k CONFIG_PATH
```

**Sample Output:**

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ key                      ┃ value                                ┃ description                             ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ CONFIG_PATH              │ ~/.kaprese                           │ Path to kaprese config directory        │
└──────────────────────────┴──────────────────────────────────────┴─────────────────────────────────────────┘
```

##### config set

Set configuration values.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `<key>=<value>` | Configuration key-value pair to set | - |

**Example:**

```bash
# Set a configuration value
kaprese config set SOME_KEY=some_value
```

---

### benchmark

Manage benchmarks in kaprese.

#### Subcommands

##### benchmark list

List all registered benchmarks.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `-d`, `--detail` | Show detailed information (may take some time) | `False` |
| `-q`, `--quiet` | Only show names of benchmarks | `False` |

**Example:**

```bash
# List all benchmarks
kaprese benchmark list

# List benchmarks with details
kaprese benchmark list --detail

# List only benchmark names
kaprese benchmark list --quiet
```

**Sample Output (basic):**

```
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ name          ┃ image                                                           ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ flint-1       │ ghcr.io/kupl/starlab-benchmarks/c:flint-1                       │
│ spearmint-1   │ ghcr.io/kupl/starlab-benchmarks/c:spearmint-1                   │
└───────────────┴─────────────────────────────────────────────────────────────────┘
```

##### benchmark preset

Add or manage preset benchmarks for specific languages.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `--overwrite` | Overwrite existing benchmarks | `False` |
| `<preset>` | Preset language to add (choices: all, ocaml, c) | Required |

**Example:**

```bash
# Add C language benchmarks
kaprese benchmark preset c

# Add OCaml benchmarks
kaprese benchmark preset ocaml

# Add all preset benchmarks
kaprese benchmark preset all

# Overwrite existing benchmarks
kaprese benchmark preset c --overwrite
```

##### benchmark prepare

Prepare benchmarks by pulling their Docker images.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `-f`, `--force` | Force prepare benchmarks (re-download) | `False` |
| `<benchmark>` | Benchmark name(s) to prepare (use 'all' for all benchmarks) | Required |

**Example:**

```bash
# Prepare specific benchmarks
kaprese benchmark prepare flint-1 spearmint-1

# Force re-download
kaprese benchmark prepare flint-1 --force

# Prepare all benchmarks
kaprese benchmark prepare all
```

**Sample Output:**

```
👍 Done!
Run the following command to see the detailed list of benchmarks:
    kaprese benchmark list -d
```

##### benchmark cleanup

Clean up benchmark images and cached data.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `-d`, `--delete-image` | Delete Docker images from registry | `False` |
| `<benchmark>` | Benchmark name(s) to clean up (use 'all' for all benchmarks) | Required |

**Example:**

```bash
# Clean up specific benchmarks
kaprese benchmark cleanup flint-1

# Clean up and delete Docker images
kaprese benchmark cleanup flint-1 --delete-image

# Clean up all benchmarks
kaprese benchmark cleanup all
```

**Sample Output:**

```
👍 Done! 2 benchmarks cleaned up
```

---

### engine

Manage APR engines in kaprese.

#### Subcommands

##### engine list

List all registered engines.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `-q`, `--quiet` | Only show names of engines | `False` |

**Example:**

```bash
# List all engines
kaprese engine list

# List only engine names
kaprese engine list --quiet
```

**Sample Output:**

```
┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ name   ┃ supported languages   ┃ supported os     ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ saver  │ c                     │ ubuntu:20.04     │
│ cafe   │ ocaml                 │ ubuntu:22.04     │
└────────┴───────────────────────┴──────────────────┘
```

##### engine inspect

Inspect detailed information about a specific engine.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `<engine>` | Engine name to inspect | Required |

**Example:**

```bash
# Inspect saver engine
kaprese engine inspect saver
```

**Sample Output:**

```json
{
    "name": "saver",
    "supported_languages": ["c"],
    "supported_os": ["ubuntu:20.04"],
    "location": "https://github.com/kupl/kaprese-engines#main:context/saver/starlab-benchmarks",
    "build_args": {},
    "exec_commands": ["..."]
}
```

##### engine preset

Register preset engines.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `--overwrite` | Overwrite existing engines | `False` |
| `<preset>` | Preset engine name to add (choices: saver, cafe) | Required |

**Example:**

```bash
# Register saver engine
kaprese engine preset saver

# Register cafe engine
kaprese engine preset cafe

# Overwrite existing engine
kaprese engine preset saver --overwrite
```

**Sample Output:**

```
preset engine "saver" registered
```

---

### run

Run APR engines on benchmarks. This is the main command for executing automatic program repair tools.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `--delete-runner` | Delete runner Docker image after running | `False` |
| `--rebuild-runner` | Rebuild runner Docker image | `False` |
| `-o OUTPUT`, `--output OUTPUT` | Output directory for results | `kaprese-out` |
| `-e [ENGINE ...]`, `--engine [ENGINE ...]` | Engine(s) to run (see `kaprese engine list`) | Required |
| `-b [BENCHMARK ...]`, `--benchmark [BENCHMARK ...]` | Benchmark(s) to run (see `kaprese benchmark list`) | All registered benchmarks |
| `extra_args` | Extra arguments to pass to the engine (use `--` separator) | - |

**Example:**

```bash
# Run saver engine on flint-1 benchmark
kaprese run -b flint-1 -e saver

# Run multiple engines on multiple benchmarks
kaprese run -b flint-1 spearmint-1 -e saver

# Run with custom output directory
kaprese run -b flint-1 -e saver -o /path/to/output

# Run with verbose logging
LOG_LEVEL=info kaprese run -b flint-1 -e saver

# Pass extra arguments to the engine
kaprese run -b flint-1 -e saver -- -j4

# Rebuild runner before running
kaprese run -b flint-1 -e saver --rebuild-runner

# Delete runner after execution
kaprese run -b flint-1 -e saver --delete-runner
```

**Sample Output:**

```
┏━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ #    ┃ Engine   ┃ Benchmark   ┃ Status           ┃ Output directory                ┃ Elapsed time   ┃
┡━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 1    │ saver    │ flint-1     │ OK               │ kaprese-out/saver/flint-1       │ 0:02:15.42     │
│ 2    │ saver    │ spearmint-1 │ OK               │ kaprese-out/saver/spearmint-1   │ 0:01:58.31     │
└──────┴──────────┴─────────────┴──────────────────┴─────────────────────────────────┴────────────────┘
```

**Notes:**

- At least one engine must be specified with `-e` for the command to run.
- If no benchmarks are specified with `-b`, all registered benchmarks will be used.
- The command checks if engines support the benchmark's language and OS before running.
- Progress is shown in a live table format with status updates.
- Output is saved to the specified directory (default: `kaprese-out`).
- Use `LOG_LEVEL` environment variable to control logging verbosity (`info`, `debug`, etc.).

---

### eval

Evaluate results from APR engine runs.

**Options:**

| Option | Description | Default |
|--------|-------------|---------|
| `-h`, `--help` | Show help message and exit | - |
| `-e [ENGINE ...]`, `--engine [ENGINE ...]` | Engine(s) to evaluate (choices: cafe) | Required |
| `-o OUTPUT`, `--output OUTPUT` | Output directory to read results from | `kaprese-out` |

**Example:**

```bash
# Evaluate cafe engine results
kaprese eval -e cafe

# Evaluate with custom output directory
kaprese eval -e cafe -o /path/to/output
```

**Sample Output:**

```
┏━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Total   ┃ Correct   ┃ Accuracy   ┃
┡━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 100     │ 85        │ 85.00%     │
└─────────┴───────────┴────────────┘
```

**Notes:**

- At least one engine must be specified with `-e` for the command to run.
- The `eval` command analyzes the output from previous `run` commands.
- Currently, only the `cafe` engine has evaluation support.
- The command reads from the output directory specified by `-o` (default: `kaprese-out`).

---

## Common Workflows

### Initial Setup

```bash
# 1. Register benchmarks and engines
kaprese benchmark preset c
kaprese engine preset saver

# 2. Prepare benchmarks (download Docker images)
kaprese benchmark prepare all

# 3. List available benchmarks and engines
kaprese benchmark list
kaprese engine list
```

### Running Experiments

```bash
# Run a single experiment
kaprese run -b flint-1 -e saver

# Run multiple experiments
kaprese run -b flint-1 spearmint-1 -e saver

# Run with verbose logging
LOG_LEVEL=info kaprese run -b flint-1 -e saver
```

### Evaluating Results

```bash
# Evaluate results
kaprese eval -e cafe -o kaprese-out
```

### Cleanup

```bash
# Clean up specific benchmarks
kaprese benchmark cleanup flint-1

# Clean up all benchmarks and delete images
kaprese benchmark cleanup all --delete-image
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity level (`debug`, `info`, `warning`, `error`) | `warning` |

**Example:**

```bash
# Enable info-level logging
LOG_LEVEL=info kaprese run -b flint-1 -e saver

# Enable debug-level logging
LOG_LEVEL=debug kaprese benchmark prepare flint-1
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error (missing arguments, command not found, etc.) |

---

## Additional Resources

- **GitHub Repository**: [https://github.com/kupl/kaprese](https://github.com/kupl/kaprese)
- **Issue Tracker**: [https://github.com/kupl/kaprese/issues](https://github.com/kupl/kaprese/issues)
- **README**: [../README.md](../README.md)
