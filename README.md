- - -

# Test harness — not affiliated with the projects it tests

- This repository exists only to test [nanocct](https://github.com/bernhard-42/nanocct) against third-party libraries.
- The patches to build123d, ocpsvg and ocp_gordon and the Python translations of Open CASCADE Technology's GTests are unofficial work of the nanocct project. They are not affiliated with, reviewed, endorsed or supported by the authors of those projects.
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
uv pip install ~/Development/CAD/vscode-ocp-cad-viewer      # optional: the viewer
```

On Windows (Git Bash): `source .venv/Scripts/activate`. The environment holds nanocct, the patched build123d (installed editable from `sources/`), the dual-binding ports of build123d's dependencies and the dual-binding versions of bd_materials and the viewer's core, so `from build123d import *` runs on nanocct, and `ocp_vscode` shows its objects (it imports no `OCP` itself and finds its core, `ocp_viewer_core` with the `cli` extra, already installed). Until a release of `ocp_vscode` accepts the dual-binding viewer core, it is installed from its local checkout: `ocp_vscode` 4.1.0 from PyPI asks for `ocp-viewer-core<1.1.0`, and uv would replace the dual-binding viewer core and `ocp_tessellate` by their OCP-only releases. `make env` recreates `.venv` from scratch, so run it again after copying a new wheel into `wheels/` (and re-activate).

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

One uv environment, `.venv` (Python `3.14`, `make PYTHON=3.13 ...` for another one), runs all three suites: nanocct, build123d and the packages below are resolved together, so every suite sees the same package versions. `make env` and `make tests` recreate it; a single suite target (`make build123d-tests`, ...) uses the existing one.

There is no `OCP` in the environment, not even the `cadquery-ocp-novtk` compatibility shim: importing `OCP` patches nanocct's classes in place, which changes nanocct for every caller in the process, build123d included. build123d's dependencies that import `OCP` are installed from their PyPI sdists (verified against PyPI's sha256) with a patch each, which lets them run on `OCP` or nanocct (nanocct wherever it is installed, so that they always share build123d's binding):

- `ocpsvg` 0.7.0 (`patches/ocpsvg-0.7.0.patch`)
- `ocp_gordon` 0.3.1 (`patches/ocp_gordon-0.3.1.patch`)

bd_materials and the viewer's core run on `OCP` or nanocct (nanocct wherever it is installed). Their dual-binding versions are not released yet, so they are installed unchanged from local checkouts in `DUAL_DIR` (default `~/Development/CAD`, `make DUAL_DIR=... env` for another one) and rebuilt on every `make env`:

- `ocp-tessellate`
- `ocp-viewer-core`, with its `cli` extra
- `bd_materials`

`make env` fails if `OCP` is importable afterwards. The environment also holds `vtk` from PyPI, for build123d's two VTK test modules (`test_jupyter.py`, `test_vtk_poly_data.py`), which skip themselves without it. 

## Which nanocct is tested

- By default, the latest [nanocct release on PyPI](https://pypi.org/project/nanocct/).
- To test another build, copy its wheel into `wheels/` (git-ignored). The highest nanocct version there that this Python accepts is installed instead (`scripts/wheels.py`), and a wheel replaced under the same name is picked up too.
- To go back to PyPI, empty `wheels/`.

## Upstream sources

Everything upstream lands in `sources/` (git-ignored). build123d is cloned once and checked out at the pinned commits (`BUILD123D_COMMIT` in the `Makefile`); the ports' sdists are downloaded once into `sources/sdist`. When a patch changes, the sources are reset to their original state and the patches are applied again. `make clean` removes `sources/` and `.venv/`.

## License

This repository is under the GNU LGPL 2.1 (`LICENSE`); the GTest translations additionally carry the Open CASCADE exception, the patches are under the licenses of the projects they change. Details in `LICENSES/README.md`.
