# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_CircleTool_Test.cxx (LGPL-2.1 with the OCCT exception)
import math
import random

from nanocct.BRepMesh import BRepMesh_CircleTool
from nanocct.gp import gp_XY
from nanocct.Precision import Precision


def _is_on_circle(point, center, radius):
    sq_prec = Precision.PConfusion_s() ** 2
    diff = point - center
    return diff.SquareModulus() - radius * radius < sq_prec


def test_BRepMesh_CircleTool_Test_OCC24923_CircumCirclePassesThroughAllVertices():
    # Python's RNG instead of C rand()
    rng = random.Random(42)
    sq_prec = Precision.PConfusion_s() ** 2
    min_area = 5.0 * math.pi / 180.0
    nb_tests = 100000

    nb_failed = 0
    i = 0
    while i < nb_tests:
        p = [gp_XY(rng.random(), rng.random()) for _ in range(3)]
        v1 = p[1] - p[0]
        v2 = p[2] - p[0]
        if v1.SquareModulus() <= sq_prec or v2.SquareModulus() <= sq_prec or (v1 ^ v2) <= min_area:
            continue
        i += 1
        center = gp_XY()
        ok, radius = BRepMesh_CircleTool.MakeCircle_s(p[0], p[1], p[2], center)
        if ok is False:
            continue
        if not (_is_on_circle(p[0], center, radius) and _is_on_circle(p[1], center, radius)
                and _is_on_circle(p[2], center, radius)):
            nb_failed += 1

    assert nb_failed / nb_tests <= 0.01
