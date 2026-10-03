# Third-party test suites run against a nanocct wheel: build123d and OCCT's GTests translated to Python.
#
#   make build123d-tests   build123d at BUILD123D_COMMIT + patches/build123d-nanocct.patch
#   make occt-tests        tests/ (OCCT's GTests in Python, one directory per toolkit)
#   make tests             all three, one after the other
#   make env               only (re)install the environment .venv
#   make clean             remove sources/ and .venv/ (wheels/ is kept)
#
# One uv environment (.venv) runs all three suites: nanocct, build123d and the native ports of build123d's
# dependencies are resolved together, so every suite sees the same package versions. `make env` and `make tests`
# recreate it; a single suite target uses the existing one.
#
# No OCP in the environment, not even the cadquery-ocp-novtk shim: importing OCP patches nanocct's classes in place,
# which changes nanocct for every caller in the process (build123d imports ocpsvg and ocp_gordon). build123d's
# dependencies that import OCP are therefore installed as native ports (PORTS), and `make env` fails if OCP is
# importable afterwards.
#
# The nanocct wheel comes from wheels/. When it holds no wheel, the latest GitHub release's wheel for this platform is
# downloaded there first. To test another build, copy its wheel into wheels/: the highest nanocct version this Python
# accepts wins (scripts/wheels.py); a wheel replaced under the same name is picked up too.

SHELL := bash
.SHELLFLAGS := -euo pipefail -c
.DEFAULT_GOAL := help

# Python version of the environment (uv venv --python)
PYTHON ?= 3.14

BUILD123D_REPO   := https://github.com/gumyr/build123d.git
BUILD123D_COMMIT := 2aec5679ae2c33b663ff452bc8930d0ece564a96

# Native nanocct ports of the packages that import OCP -- build123d's dependencies and the viewer's core (ocp_tessellate,
# ocp_viewer_core: `uv pip install ocp_vscode` then needs nothing else): name-version|sha256|url of the PyPI sdist (PyPI's
# own digest, https://pypi.org/pypi/<name>/<version>/json), patched with patches/<name-version>.patch
PORTS := \
    ocpsvg-0.7.0|e8a03495e873943398df61e1cd02bd0d6f0f206665a2c9f86430b75bd2ecc152|https://files.pythonhosted.org/packages/77/93/6731a317aca67604914e69f4d92d544c5637c89d8fd54e5dde9ddbc93561/ocpsvg-0.7.0.tar.gz \
    ocp_gordon-0.3.1|e55e695fd421e4dc10fe91636e7f2fa376ad81572faaf74e7bbed4b78c7918b7|https://files.pythonhosted.org/packages/35/b2/66ed6601660648ad5bf84a571460cd57e9db4b28c6833c55e229211a418d/ocp_gordon-0.3.1.tar.gz \
    bd_materials-0.2.4|daea82953c18cef04be9f8519c75518d230df1b78457f4a92a7da8725e533bb8|https://files.pythonhosted.org/packages/19/28/940946d9cc9f1489c3d3f0c6a8f2acaf2a1240ba1cf24df69ac385f9c0d7/bd_materials-0.2.4.tar.gz \
    ocp_tessellate-3.5.3|3f627da7099cd078081432b26db179b7f225241d1ca9474ce959e714f6cac564|https://files.pythonhosted.org/packages/ef/59/f5affe69a54587413b03b22020b0353fba1b4aeb3a281912eb6eaeef9347/ocp_tessellate-3.5.3.tar.gz \
    ocp_viewer_core-1.0.13|57ccbfff31a03fdd6c78e1dc5f05ff55d49f959df956d450f211ec7b06bf91ca|https://files.pythonhosted.org/packages/d2/99/6c36e0fda14e44e66e2fccc04420be7650f813f9e6556cb27e5470171bb8/ocp_viewer_core-1.0.13.tar.gz
PORT_NAMES := $(foreach p,$(PORTS),$(firstword $(subst |, ,$(p))))
# what `make env` installs of them: ocp_viewer_core with its [cli] extra, which ocp_vscode asks for
PORT_INSTALL := $(foreach n,$(PORT_NAMES),"sources/ports/$(n)$(if $(filter ocp_viewer_core-%,$(n)),[cli])")

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
# tags this interpreter accepts (its stdout is only the wheel path).
env: sources/build123d/.patched sources/ports/.patched
	uv venv --quiet --clear --python $(PYTHON) .venv
	uv pip install --quiet --python $(VENV_PY) packaging
	nanocct=$$($(VENV_PY) scripts/wheels.py); \
	echo "env: $$(basename "$$nanocct")"; \
	uv pip install --python $(VENV_PY) "$$nanocct" $(PORT_INSTALL) \
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
