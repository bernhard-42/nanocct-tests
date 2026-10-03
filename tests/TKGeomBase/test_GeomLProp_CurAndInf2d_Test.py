# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomLProp_CurAndInf2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom2d import Geom2d_Circle, Geom2d_Ellipse, Geom2d_Hyperbola, Geom2d_Parabola
from nanocct.GeomLProp import GeomLProp_CurAndInf2d
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Elips2d, gp_Hypr2d, gp_Parab2d, gp_Pnt2d
from nanocct.LProp import LProp_MaxCur, LProp_MinCur
from nanocct.Precision import Precision


def _ax():
    return gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0))


def _circle():
    return Geom2d_Circle(gp_Circ2d(_ax(), 5.0))


def _ellipse():
    return Geom2d_Ellipse(gp_Elips2d(_ax(), 10.0, 3.0))


def _hyperbola():
    return Geom2d_Hyperbola(gp_Hypr2d(_ax(), 6.0, 3.0))


def _parabola():
    return Geom2d_Parabola(gp_Parab2d(_ax(), 2.0))


def _run(method, curve):
    a = GeomLProp_CurAndInf2d()
    getattr(a, method)(curve)
    assert a.IsDone()
    return a


def test_GeomLProp_CurAndInf2dTest_Circle_Perform_NoInflections():
    assert _run("Perform", _circle()).NbPoints() == 0


def test_GeomLProp_CurAndInf2dTest_Circle_PerformInf_NoInflections():
    assert _run("PerformInf", _circle()).NbPoints() == 0


def test_GeomLProp_CurAndInf2dTest_Circle_PerformCurExt_NoExtrema():
    assert _run("PerformCurExt", _circle()).NbPoints() == 0


def test_GeomLProp_CurAndInf2dTest_Ellipse_PerformCurExt_HasExtrema():
    assert _run("PerformCurExt", _ellipse()).NbPoints() == 4


def test_GeomLProp_CurAndInf2dTest_Ellipse_PerformCurExt_Types():
    a = _run("PerformCurExt", _ellipse())
    assert a.NbPoints() == 4
    types = [a.Type(i) for i in range(1, a.NbPoints() + 1)]
    assert types.count(LProp_MinCur) == 2
    assert types.count(LProp_MaxCur) == 2


def test_GeomLProp_CurAndInf2dTest_Ellipse_PerformCurExt_Parameters():
    a = _run("PerformCurExt", _ellipse())
    assert a.NbPoints() == 4
    for i in range(1, a.NbPoints()):
        assert a.Parameter(i) < a.Parameter(i + 1)


def test_GeomLProp_CurAndInf2dTest_Ellipse_PerformInf_NoInflections():
    assert _run("PerformInf", _ellipse()).NbPoints() == 0


def test_GeomLProp_CurAndInf2dTest_Ellipse_Perform_CombinedResult():
    assert _run("Perform", _ellipse()).NbPoints() == 4


def test_GeomLProp_CurAndInf2dTest_Ellipse_CurvatureExtremaAtExpectedParameters():
    a = _run("PerformCurExt", _ellipse())
    assert a.NbPoints() == 4
    for i, exp in enumerate([0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0], 1):
        assert abs(a.Parameter(i) - exp) <= 1e-6


def test_GeomLProp_CurAndInf2dTest_Hyperbola_PerformCurExt_VertexOnly():
    a = _run("PerformCurExt", _hyperbola())
    assert a.NbPoints() == 1
    assert abs(a.Parameter(1)) <= Precision.PConfusion_s()
    assert a.Type(1) == LProp_MinCur


def test_GeomLProp_CurAndInf2dTest_Hyperbola_PerformInf_NoInflections():
    assert _run("PerformInf", _hyperbola()).NbPoints() == 0


def test_GeomLProp_CurAndInf2dTest_Parabola_PerformCurExt_VertexOnly():
    a = _run("PerformCurExt", _parabola())
    assert a.NbPoints() == 1
    assert abs(a.Parameter(1)) <= Precision.PConfusion_s()
    assert a.Type(1) == LProp_MinCur


def test_GeomLProp_CurAndInf2dTest_PerformInf_ClearsPreviousExtrema():
    a = _run("PerformCurExt", _ellipse())
    assert a.NbPoints() == 4
    a.PerformInf(_ellipse())
    assert a.IsDone()
    assert a.NbPoints() == 0
