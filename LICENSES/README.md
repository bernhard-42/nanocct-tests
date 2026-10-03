# Licenses

| Path                                                                  | License                                                                                                              | Why                                                                                                 |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `tests/`                                                              | GNU LGPL 2.1 (`LGPL-2.1.txt`) with the Open CASCADE exception 1.0 (`OCCT-LGPL-exception-1.0.txt`)                    | Python translations of the GTests in Open CASCADE Technology's sources, which are under these terms |
| `patches/build123d-nanocct.patch`                                     | Apache License 2.0 (`build123d-LICENSE.txt`, notice in `build123d-NOTICE.txt`)                                       | Changes to build123d's sources                                                                      |
| `patches/ocpsvg-0.7.0.patch`                                          | Apache License 2.0 (`ocpsvg-LICENSE.txt`)                                                                            | Changes to ocpsvg's sources                                                                         |
| `patches/ocp_gordon-0.3.1.patch`                                      | Apache License 2.0 (`ocp_gordon-LICENSE.txt`)                                                                        | Changes to ocp_gordon's sources                                                                     |
| `patches/ocp_tessellate-3.5.3.patch` | Apache License 2.0 (`ocp_tessellate-LICENSE.txt`) | Changes to ocp_tessellate's sources |
| `patches/ocp_viewer_core-1.0.13.patch` | Apache License 2.0 (`ocp_viewer_core-LICENSE.txt`) | Changes to ocp_viewer_core's sources |
| `patches/bd_materials-0.2.4.patch`                                    | Apache License 2.0 (`bd_materials-LICENSE.txt`, from the repository at commit `ec5b6a5`; the 0.2.4 sdist ships none) | Changes to bd_materials' sources                                                                    |
| everything else (`Makefile`, `scripts/`, `pytest.ini`, documentation) | GNU LGPL 2.1 (`../LICENSE`)                                                                                          | The license of this repository                                                                      |

build123d and the ported packages themselves are not part of this repository: the `Makefile` clones build123d from GitHub and downloads the ports' sdists from PyPI into `sources/` (git-ignored). The license texts were copied from the pinned commits (`BUILD123D_COMMIT` in the `Makefile`) and from the sdists (`PORTS`).

The patches carry their own change record: every hunk shows the original line next to the changed one.
