# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_CircleTool_Test.cxx (LGPL-2.1 with the OCCT exception)
import math
import random

import pytest

from nanocct.BRepMesh import BRepMesh_Circle, BRepMesh_CircleInspector, BRepMesh_CircleTool
from nanocct.gp import gp_XY
from nanocct.NCollection import NCollection_IncAllocator
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


def test_BRepMesh_CircleToolTest_CircumcircleKeepsPointsBeyondSecantOutside():
    points = (gp_XY(12.463211482361567, 1.9738661904523815e-06),
              gp_XY(12.463212204366371, 4.7372788570857157e-06),
              gp_XY(12.361816737261172, 0.025871858931497457))
    translations = (gp_XY(0.0, 0.0), gp_XY(16.0, -8.0), gp_XY(-32.0, 64.0))
    inspector = BRepMesh_CircleInspector(Precision.PConfusion_s(), 1, NCollection_IncAllocator())
    for scale in (0.25, 1.0, 4.0):
        for translation in translations:
            p1, p2, p3 = (p * scale + translation for p in points)
            center = gp_XY()
            ok, radius = BRepMesh_CircleTool.MakeCircle_s(p1, p2, p3, center)
            assert ok is True
            inspector.Bind(1, BRepMesh_Circle(center, radius))
            for point in (p1, p2, p3):
                inspector.SetPoint(point)
                inspector.Inspect(1)
                assert inspector.GetShotCircles().IsEmpty() is False
            # A point beyond an endpoint of a secant is outside the circle.
            inspector.SetPoint(p1 + (p1 - p2) * 0.5)
            inspector.Inspect(1)
            assert inspector.GetShotCircles().IsEmpty() is True


def test_BRepMesh_CircleToolTest_TranslatedRightTrianglesHaveAnalyticCircumcircles():
    legs = (gp_XY(1.0, 1.0), gp_XY(1.0, 1.0e-6), gp_XY(1.0e-3, 1.0e-4))
    translations = (gp_XY(0.0, 0.0), gp_XY(16.0, -8.0), gp_XY(-32.0, 64.0))
    pc = Precision.PConfusion_s()
    for leg in legs:
        for scale in (0.25, 1.0, 4.0):
            for translation in translations:
                p2 = translation + gp_XY(leg.X() * scale, 0.0)
                p3 = translation + gp_XY(0.0, leg.Y() * scale)
                expected_center = translation + leg * (0.5 * scale)
                expected_radius = (leg * (0.5 * scale)).Modulus()
                center = gp_XY()
                ok, radius = BRepMesh_CircleTool.MakeCircle_s(translation, p2, p3, center)
                assert ok is True
                assert center.X() == pytest.approx(expected_center.X(), abs=pc)
                assert center.Y() == pytest.approx(expected_center.Y(), abs=pc)
                assert radius == pytest.approx(expected_radius, abs=pc)


def test_BRepMesh_CircleToolTest_CircumcircleRejectsDegenerateEdges():
    points = (gp_XY(0.0, 0.0), gp_XY(1.0, 0.0), gp_XY(0.0, 1.0))
    for i in range(3):
        triangle = [gp_XY(p.X(), p.Y()) for p in points]
        triangle[(i + 1) % 3] = triangle[i] + gp_XY(0.5 * Precision.PConfusion_s(), 0.0)
        ok, _ = BRepMesh_CircleTool.MakeCircle_s(triangle[0], triangle[1], triangle[2], gp_XY())
        assert ok is False, i
    ok, _ = BRepMesh_CircleTool.MakeCircle_s(gp_XY(0.0, 0.0), gp_XY(1.0, 0.0), gp_XY(2.0, 0.0), gp_XY())
    assert ok is False
