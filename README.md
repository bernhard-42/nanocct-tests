- - -

# Unofficial test harness — not affiliated with the projects it tests

- This repository exists only to test [nanocct](https://github.com/bernhard-42/nanocct) against third-party libraries.
- The patches to build123d, ocpsvg, ocp_gordon, ocp_tessellate and ocp_viewer_core and the Python translations of Open CASCADE Technology's GTests are unofficial work of the nanocct project. They are not affiliated with, reviewed, endorsed or supported by the authors of those projects.
- Project names are used only to identify the software under test.
- **DO NOT USE THE PATCHES OR THE PATCHED PACKAGES FOR ANYTHING BUT THESE TESTS.**
- **DO NOT REPORT PROBLEMS FOUND HERE TO THE UPSTREAM PROJECTS:** A failure here is a nanocct issue, hence report it to [nanocct issues](https://github.com/bernhard-42/nanocct/issues).

- - -

# Third-party tests for nanocct 

Test suites that exercise a nanocct wheel from the outside:

- **OCCT's GTests**, translated to Python, in `tests/`, one directory per toolkit
- **build123d** at a pinned commit, ported to nanocct by `patches/build123d-nanocct.patch`


## Usage

Requirements
- Linux and MacOS: `uv`, `git`, `curl`, `patch`, `make` and `bash`
- Windows: `uv`, `git`, `curl`, `patch`, `make` and `Git Bash`

### 1) Try build123d on nanocct by hand

```bash
make env
source .venv/bin/activate
uv pip install ocp_vscode      # optional: the viewer
```

On Windows (Git Bash): `source .venv/Scripts/activate`. The environment holds nanocct, the patched build123d (installed editable from `sources/`) and the native ports of build123d's dependencies and of the viewer's core, so `from build123d import *` runs on nanocct, and `ocp_vscode` from PyPI shows its objects (it imports no `OCP` itself and finds its core, `ocp_viewer_core` with the `cli` extra, already installed). `make env` recreates `.venv` from scratch, so run it again after copying a new wheel into `wheels/` (and re-activate).

### 2) Run the third-party test suites

```bash
make tests  # starts with "make env"
```

or one suite at a time:

```bash
make env
make build123d-tests
make occt-tests
```

All suites run serially; build123d's benchmarks run too.

## The environment

One uv environment, `.venv` (Python `3.14`, `make PYTHON=3.13 ...` for another one), runs all three suites: nanocct, build123d and the native ports below are resolved together, so every suite sees the same package versions. `make env` and `make tests` recreate it; a single suite target (`make build123d-tests`, ...) uses the existing one.

There is no `OCP` in the environment, not even the `cadquery-ocp-novtk` compatibility shim: importing `OCP` patches nanocct's classes in place, which changes nanocct for every caller in the process, build123d included. build123d's dependencies and the viewer's core, which import `OCP`, are installed as native nanocct ports instead, from their PyPI sdists (verified against PyPI's sha256) with a patch each:

- `ocpsvg` 0.7.0 (`patches/ocpsvg-0.7.0.patch`)
- `ocp_gordon` 0.3.1 (`patches/ocp_gordon-0.3.1.patch`)
- `bd_materials` 0.2.4 (`patches/bd_materials-0.2.4.patch`)
- `ocp_tessellate` 3.5.3 (`patches/ocp_tessellate-3.5.3.patch`)
- `ocp_viewer_core` 1.0.13 (`patches/ocp_viewer_core-1.0.13.patch`), with its `cli` extra

`make env` fails if `OCP` is importable afterwards. The environment also holds `vtk` from PyPI, for build123d's two VTK test modules (`test_jupyter.py`, `test_vtk_poly_data.py`), which skip themselves without it. 

## Which nanocct is tested

The wheel comes from `wheels/` (git-ignored):

- If `wheels/` holds no wheel, this platform's nanocct wheel of the latest [nanocct release](https://github.com/bernhard-42/nanocct/releases) is downloaded there first.
- To test another build, copy its wheel into `wheels/`. The highest nanocct version this Python accepts is installed (`scripts/wheels.py`), so a newer wheel copied next to a downloaded one wins, and a wheel replaced under the same name is picked up too.
- To go back to the latest release, empty `wheels/`.

## Upstream sources

Everything upstream lands in `sources/` (git-ignored). build123d is cloned once and checked out at the pinned commits (`BUILD123D_COMMIT` in the `Makefile`); the ports' sdists are downloaded once into `sources/sdist`. When a patch changes, the sources are reset to their original state and the patches are applied again. `make clean` removes `sources/` and `.venv/`.

## License

This repository is under the GNU LGPL 2.1 (`LICENSE`); the GTest translations additionally carry the Open CASCADE exception, the patches are under the licenses of the projects they change. Details in `LICENSES/README.md`.
