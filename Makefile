# Third-party test suites run against a nanocct wheel: build123d and OCCT's GTests translated to Python.
#
#   make build123d-tests   build123d at BUILD123D_COMMIT + patches/build123d-nanocct.patch
#   make occt-tests        tests/ (OCCT's GTests in Python, one directory per toolkit)
#   make tests             all three, one after the other
#   make env               only (re)install the environment .venv
#   make clean             remove sources/ and .venv/ (wheels/ is kept)
#
# One uv environment (.venv) runs all three suites: nanocct, build123d and the ports of build123d's
# dependencies are resolved together, so every suite sees the same package versions. `make env` and `make tests`
# recreate it; a single suite target uses the existing one.
#
# No OCP in the environment, not even the cadquery-ocp-novtk shim: importing OCP patches nanocct's classes in place,
# which changes nanocct for every caller in the process (build123d imports ocpsvg and ocp_gordon). build123d's
# dependencies that import OCP are therefore installed as ports (PORTS) or in their dual-binding versions
# (DUAL), and `make env` fails if OCP is importable afterwards.
#
# nanocct comes from PyPI (its latest release), unless wheels/ holds a wheel: to test another build, copy its wheel into
# wheels/, and the highest nanocct version there that this Python accepts is installed instead (scripts/wheels.py); a
# wheel replaced under the same name is picked up too. Empty wheels/ to go back to PyPI.

SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

# Python version of the environment (uv venv --python)
PYTHON ?= 3.14

BUILD123D_REPO   := https://github.com/gumyr/build123d.git
BUILD123D_COMMIT := 2aec5679ae2c33b663ff452bc8930d0ece564a96

# Ports of build123d's dependencies that import OCP, patched to run on OCP or nanocct (nanocct wherever it is
# installed): name-version|sha256|url of the PyPI sdist (PyPI's own digest,
# https://pypi.org/pypi/<name>/<version>/json), patched with patches/<name-version>.patch
PORTS := \
    ocpsvg-0.7.0|e8a03495e873943398df61e1cd02bd0d6f0f206665a2c9f86430b75bd2ecc152|https://files.pythonhosted.org/packages/77/93/6731a317aca67604914e69f4d92d544c5637c89d8fd54e5dde9ddbc93561/ocpsvg-0.7.0.tar.gz \
    ocp_gordon-0.3.1|e55e695fd421e4dc10fe91636e7f2fa376ad81572faaf74e7bbed4b78c7918b7|https://files.pythonhosted.org/packages/35/b2/66ed6601660648ad5bf84a571460cd57e9db4b28c6833c55e229211a418d/ocp_gordon-0.3.1.tar.gz
PORT_NAMES := $(foreach p,$(PORTS),$(firstword $(subst |, ,$(p))))
PORT_INSTALL := $(foreach n,$(PORT_NAMES),"sources/ports/$(n)")

# The packages that run on OCP or nanocct, whichever is installed -- bd_materials and the viewer's core (ocp_tessellate,
# ocp_viewer_core with its [cli] extra: ocp_vscode then needs nothing else). Not released yet, so they are installed
# from local checkouts in DUAL_DIR, rebuilt on every `make env` (--reinstall-package), so an edit there is picked up.
DUAL_DIR ?= $(HOME)/Development/CAD
DUAL := ocp-tessellate ocp-viewer-core bd_materials
DUAL_INSTALL := "$(DUAL_DIR)/ocp-tessellate" "$(DUAL_DIR)/ocp-viewer-core[cli]" "$(DUAL_DIR)/bd_materials" \
    $(foreach d,$(DUAL),--reinstall-package $(d))

ifeq ($(OS),Windows_NT)
VENV_PY := $(CURDIR)/.venv/Scripts/python.exe
else
VENV_PY := $(CURDIR)/.venv/bin/python
endif

# $(1) checkout dir, $(2) repository, $(3) commit, $(4) patches: a pristine checkout of the commit with the patches
# applied. Cloned once; later runs reset the clone, so an edited patch is applied to the original sources again.
define checkout
	if [ ! -d $(1)/.git ]; then git clone --quiet --filter=blob:none $(2) $(1); fi
	git -C $(1) checkout --quiet --force $(3)
	git -C $(1) clean --quiet -fdx
	for p in $(4); do git -C $(1) apply --whitespace=nowarn $(CURDIR)/$$p; done
	touch $(1)/.patched
endef

.PHONY: help tests build123d-tests occt-tests env clean

help:
	@sed -n '3,8p' Makefile | sed 's/^# //'

tests: env build123d-tests occt-tests

sources/build123d/.patched: patches/build123d-nanocct.patch
	$(call checkout,sources/build123d,$(BUILD123D_REPO),$(BUILD123D_COMMIT),patches/build123d-nanocct.patch)

# Each sdist is downloaded once into sources/sdist and verified; the tree in sources/ports is unpacked and patched anew
sources/ports/.patched: $(PORT_NAMES:%=patches/%.patch)
	mkdir -p sources/sdist sources/ports
	for entry in $(foreach p,$(PORTS),'$(p)'); do \
	    IFS='|' read -r pkg sha url <<< "$$entry"; \
	    tarball="sources/sdist/$$pkg.tar.gz"; \
	    if [ ! -f "$$tarball" ]; then curl -fsSL -o "$$tarball.part" "$$url" && mv "$$tarball.part" "$$tarball"; fi; \
	    echo "$$sha  $$tarball" | shasum -a 256 -c --quiet -; \
	    rm -rf "sources/ports/$${pkg:?}"; \
	    tar -xzf "$$tarball" -C sources/ports; \
	    patch -p1 --forward --quiet -d "sources/ports/$$pkg" < "patches/$$pkg.patch"; \
	done
	touch $@

# vtk: build123d's VTK tests (test_jupyter.py, test_vtk_poly_data.py) skip themselves without it.
# Recreated (--clear), so nothing of an earlier install survives. packaging first: scripts/wheels.py reads the wheel
# tags this interpreter accepts (its stdout is only the wheel path, or "nanocct" for PyPI).
env: sources/build123d/.patched sources/ports/.patched
	for d in $(DUAL); do \
	    if [ ! -f "$(DUAL_DIR)/$$d/pyproject.toml" ]; then echo "env: no checkout of $$d in $(DUAL_DIR) (DUAL_DIR=...)" >&2; exit 1; fi; \
	done
	uv venv --quiet --clear --python $(PYTHON) .venv
	uv pip install --quiet --python $(VENV_PY) packaging
	nanocct=$$($(VENV_PY) scripts/wheels.py); \
	if [ "$$nanocct" = "nanocct" ]; then echo "env: nanocct from PyPI"; else echo "env: $$(basename "$$nanocct")"; fi; \
	uv pip install --python $(VENV_PY) "$$nanocct" $(PORT_INSTALL) $(DUAL_INSTALL) \
	    -e "sources/build123d[development]" vtk pytest
	$(VENV_PY) -c "import nanocct.all"
	$(VENV_PY) -c 'import importlib.util, sys; sys.exit("OCP is importable in .venv" if importlib.util.find_spec("OCP") is not None else 0)'

# -c: the upstream config file explicitly, or pytest walks up to this directory's pytest.ini (measured).
# Serial, benchmarks included.
build123d-tests: 
	cd sources/build123d && $(VENV_PY) -m pytest -c pyproject.toml



occt-tests: 
	$(VENV_PY) -m pytest tests

clean:
	rm -rf sources .venv
