"""Pick what the test environment installs as nanocct: a local wheel from wheels/, else nanocct from PyPI.

    python scripts/wheels.py            prints the path of the nanocct wheel, or "nanocct" for PyPI's latest release

To test another build, copy its wheel into wheels/: the highest version among the nanocct wheels there whose tags this
interpreter accepts (packaging.tags) is installed instead of PyPI's. Run it with the interpreter the environment is
built for: the platform and ABI tags are this interpreter's.
"""

import sys
from pathlib import Path

from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename

WHEELS = Path(__file__).resolve().parent.parent / "wheels"


def compatible(name: str) -> bool:
    _, _, _, tags = parse_wheel_filename(name)
    supported = set(sys_tags())
    return len(tags & supported) > 0


def main() -> None:
    wheels = sorted(WHEELS.glob("*.whl")) if WHEELS.is_dir() else []
    if len(wheels) == 0:
        print("nanocct")
        return
    candidates = [p for p in wheels if p.name.startswith("nanocct-") and compatible(p.name)]
    if len(candidates) == 0:
        found = ", ".join(p.name for p in wheels)
        sys.exit(f"wheels.py: no nanocct wheel for this interpreter in {WHEELS} (found: {found}); copy one there, "
                 f"or empty the folder to install nanocct from PyPI")
    print(max(candidates, key=lambda p: parse_wheel_filename(p.name)[1]))


if __name__ == "__main__":
    main()
