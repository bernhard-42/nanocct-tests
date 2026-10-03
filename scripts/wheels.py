"""Pick the nanocct wheel the test environment installs, downloading the latest release's first when wheels/ is empty.

    python scripts/wheels.py            prints the path of the nanocct wheel

The highest version among the nanocct wheels in wheels/ whose tags this interpreter accepts (packaging.tags), so a
wheel copied into wheels/ by hand wins over an older downloaded one. Run it with the interpreter the environment is
built for: the platform and ABI tags are this interpreter's.
"""

import json
import sys
import urllib.request
from pathlib import Path

from packaging.tags import sys_tags
from packaging.utils import parse_wheel_filename

REPO = "bernhard-42/nanocct"
WHEELS = Path(__file__).resolve().parent.parent / "wheels"


def compatible(name: str) -> bool:
    _, _, _, tags = parse_wheel_filename(name)
    supported = set(sys_tags())
    return len(tags & supported) > 0


def download_latest() -> None:
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    with urllib.request.urlopen(url) as response:
        release = json.load(response)
    wanted = [a for a in release["assets"]
              if a["name"].startswith("nanocct-") and a["name"].endswith(".whl") and compatible(a["name"])]
    if len(wanted) == 0:
        sys.exit(f"wheels.py: release {release['tag_name']} has no nanocct wheel for this interpreter")
    WHEELS.mkdir(exist_ok=True)
    for asset in wanted:
        target = WHEELS / asset["name"]
        print(f"wheels.py: downloading {asset['name']} ({asset['size'] / 1e6:.1f} MB) from {release['tag_name']}",
              file=sys.stderr)
        partial = target.with_suffix(".part")
        urllib.request.urlretrieve(asset["browser_download_url"], partial)
        if partial.stat().st_size != asset["size"]:
            sys.exit(f"wheels.py: {asset['name']}: got {partial.stat().st_size} bytes, expected {asset['size']}")
        partial.rename(target)


def main() -> None:
    if WHEELS.is_dir() is False or len(list(WHEELS.glob("*.whl"))) == 0:
        download_latest()
    candidates = [p for p in WHEELS.glob("nanocct-*.whl") if compatible(p.name)]
    if len(candidates) == 0:
        found = ", ".join(sorted(p.name for p in WHEELS.glob("*.whl")))
        sys.exit(f"wheels.py: no nanocct wheel for this interpreter in {WHEELS} (found: {found}); copy one there, "
                 f"or empty the folder to download the latest release")
    print(max(candidates, key=lambda p: parse_wheel_filename(p.name)[1]))


if __name__ == "__main__":
    main()
