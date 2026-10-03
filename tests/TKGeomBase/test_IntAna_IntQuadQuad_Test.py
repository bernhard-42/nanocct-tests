# Translated from OCCT src/ModelingData/TKGeomBase/GTests/IntAna_IntQuadQuad_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.gp import gp_Ax3, gp_Cone, gp_Cylinder, gp_Dir, gp_Lin, gp_Pln, gp_Pnt, gp_Sphere
from nanocct.IntAna import IntAna_IntQuadQuad, IntAna_Line, IntAna_Point, IntAna_QuadQuadGeo, IntAna_Quadric
from nanocct.Standard import Standard_DomainError, Standard_OutOfRange

Z = gp_Dir.D.Z
X = gp_Dir.D.X
Y = gp_Dir.D.Y


def _ax(p=(0, 0, 0), z=Z, x=X):
    return gp_Ax3(gp_Pnt(*p), gp_Dir(z), gp_Dir(x))


def _sphere1():
    return gp_Sphere(_ax(), 5.0)


def _cylinder1():
    return gp_Cylinder(_ax(), 3.0)


def _cyl_vs_sphere():
    return IntAna_IntQuadQuad(_cylinder1(), IntAna_Quadric(_sphere1()), 1e-7)


def test_IntAna_IntQuadQuad_Test_CylinderVsSphereIntersection():
    it = _cyl_vs_sphere()
    assert it.IsDone()
    assert not it.IdenticalElements()
    assert it.NbCurve() > 0
    for i in range(1, it.NbCurve() + 1):
        it.Curve(i)


def test_IntAna_IntQuadQuad_Test_NextCurveMethodCorrectness():
    it = _cyl_vs_sphere()
    assert it.IsDone()
    for i in range(1, it.NbCurve() + 1):
        if it.HasNextCurve(i):
            nxt, _opposite = it.NextCurve(i)
            assert 0 < nxt <= it.NbCurve()
            assert nxt != i


def test_IntAna_IntQuadQuad_Test_NextCurveBoundaryConditions():
    it = _cyl_vs_sphere()
    assert it.IsDone()
    with pytest.raises(Standard_OutOfRange):
        it.HasNextCurve(0)
    with pytest.raises(Standard_OutOfRange):
        it.HasNextCurve(it.NbCurve() + 1)
    for i in range(1, it.NbCurve() + 1):
        if not it.HasNextCurve(i):
            with pytest.raises(Standard_DomainError):
                it.NextCurve(i)


def test_IntAna_IntQuadQuad_Test_ConnectedCurvesScenario():
    ax1 = _ax((0, 0, 0))
    ax2 = _ax((3, 0, 0))
    it = IntAna_IntQuadQuad()
    it.Perform(gp_Cylinder(ax1, 2.0), IntAna_Quadric(gp_Sphere(ax2, 2.0)), 1e-7)
    assert it.IsDone()
    assert not it.IdenticalElements()
    for i in range(1, it.NbCurve() + 1):
        if it.HasNextCurve(i):
            nxt, _ = it.NextCurve(i)
            assert 0 < nxt <= it.NbCurve()
            if it.HasNextCurve(nxt):
                back, _ = it.NextCurve(nxt)
                assert 0 < back <= it.NbCurve()


def test_IntAna_IntQuadQuad_Test_IndexingConsistencyTest():
    it = _cyl_vs_sphere()
    assert it.IsDone()
    for i in range(1, it.NbCurve() + 1):
        if it.HasNextCurve(i):
            nxt, _ = it.NextCurve(i)
            assert 0 < nxt <= it.NbCurve()


def test_IntAna_IntQuadQuad_Test_CylinderCylinderNearTangent_CollapsesToSingleLine():
    inter = IntAna_QuadQuadGeo(gp_Cylinder(_ax((0, 0, 0)), 1.0), gp_Cylinder(_ax((2.0 - 1.0e-9, 0, 0)), 1.0), 1.0e-4)
    assert inter.IsDone()
    assert inter.TypeInter() == IntAna_Line
    assert inter.NbSolutions() == 1


def test_IntAna_IntQuadQuad_Test_CylinderCylinderNonTangent_HasTwoLines():
    inter = IntAna_QuadQuadGeo(gp_Cylinder(_ax((0, 0, 0)), 1.0), gp_Cylinder(_ax((1.8, 0, 0)), 1.0), 1.0e-7)
    assert inter.IsDone()
    assert inter.TypeInter() == IntAna_Line
    assert inter.NbSolutions() == 2


def test_IntAna_IntQuadQuad_Test_CylinderCylinderSkewExternallyTangent_HasPoint():
    r1, r2 = 3.0, 2.0
    c1 = gp_Cylinder(_ax((0, 0, 0), Z, X), r1)
    c2 = gp_Cylinder(_ax((0, r1 + r2, 0), X, Y), r2)
    inter = IntAna_QuadQuadGeo(c1, c2, 1.0e-7)
    assert inter.IsDone()
    assert inter.TypeInter() == IntAna_Point
    assert inter.NbSolutions() == 1
    p = inter.Point(1)
    assert abs(gp_Lin(c1.Axis()).Distance(p) - r1) <= 1.0e-7
    assert abs(gp_Lin(c2.Axis()).Distance(p) - r2) <= 1.0e-7
