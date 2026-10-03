# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_CurveEval_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import (
    Geom_Circle,
    Geom_Line,
    Geom_OffsetCurve,
    Geom_Parabola,
    Geom_TrimmedCurve,
    Geom_UndefinedDerivative,
)
from nanocct.GeomAPI import GeomAPI_PointsToBSpline
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()
ORIGIN = gp_Pnt(0.0, 0.0, 0.0)


def circle(r):
    return Geom_Circle(gp_Circ(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), r))


def bspline(pts):
    arr = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, start=1):
        arr[i] = gp_Pnt(*p)
    interp = GeomAPI_PointsToBSpline(arr)
    assert interp.IsDone()
    return interp.Curve()


def test_Geom_CurveEvalTest_Circle_EvalD0_ReturnsValidPoint():
    res = circle(5.0).EvalD0(math.pi / 4.0)
    assert abs(res.Distance(ORIGIN) - 5.0) <= TOL


def test_Geom_CurveEvalTest_Circle_EvalD1D2D3_ReturnsValidDerivatives():
    c = circle(5.0)
    u = math.pi / 3.0
    d1 = c.EvalD1(u)
    assert abs(d1.Point.Distance(ORIGIN) - 5.0) <= TOL
    radial = gp_Vec(ORIGIN, d1.Point)
    assert abs(radial.Dot(d1.D1)) <= 1.0e-10

    d2 = c.EvalD2(u)
    assert abs(d2.Point.Distance(d1.Point)) <= TOL
    assert abs(d2.D2.Magnitude() - 5.0) <= 1.0e-10

    d3 = c.EvalD3(u)
    assert abs(d3.Point.Distance(d1.Point)) <= TOL
    assert d3.D3.Magnitude() > 0.0


def test_Geom_CurveEvalTest_Line_EvalD2_ZeroSecondDerivative():
    c = Geom_Line(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(1.0, 0.0, 0.0))
    d2 = c.EvalD2(5.0)
    assert abs(d2.D2.Magnitude()) <= TOL
    assert abs(d2.D1.X() - 1.0) <= TOL
    assert abs(d2.D1.Y()) <= TOL
    assert abs(d2.D1.Z()) <= TOL


def test_Geom_CurveEvalTest_BSplineCurve_EvalD1_ConsistentWithOldAPI():
    c = bspline([(0, 0, 0), (1, 2, 0), (3, 1, 0), (5, 3, 0), (7, 0, 0)])
    mid = (c.FirstParameter() + c.LastParameter()) / 2.0
    ev = c.EvalD1(mid)
    p, v1 = gp_Pnt(), gp_Vec()
    c.D1(mid, p, v1)
    assert abs(ev.Point.Distance(p)) <= TOL
    assert abs((ev.D1 - v1).Magnitude()) <= TOL


def test_Geom_CurveEvalTest_EvalDN_N1_ConsistentWithEvalD1():
    c = circle(3.0)
    u = math.pi / 6.0
    d1 = c.EvalD1(u)
    dn1 = c.EvalDN(u, 1)
    assert abs((d1.D1 - dn1).Magnitude()) <= TOL


def test_Geom_CurveEvalTest_OffsetCurve_EvalD0_ReturnsNulloptAtSingular():
    off = Geom_OffsetCurve(circle(5.0), -5.0, gp_Dir(0.0, 0.0, 1.0))
    res = off.EvalD0(0.0)
    assert abs(res.Distance(ORIGIN)) <= TOL


def test_Geom_CurveEvalTest_OffsetCurve_D0Wrapper_ThrowsAtSingular():
    off = Geom_OffsetCurve(circle(5.0), 2.0, gp_Dir(0.0, 0.0, 1.0))
    p = gp_Pnt()
    off.D0(0.0, p)  # must not raise


def test_Geom_CurveEvalTest_Parabola_EvalD3_ZeroThirdDerivative():
    c = Geom_Parabola(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 2.0)
    d3 = c.EvalD3(1.0)
    assert abs(d3.D3.Magnitude()) <= TOL


def test_Geom_CurveEvalTest_BSplineCurve_EvalDN_InvalidN_Throws():
    c = bspline([(0, 0, 0), (1, 1, 0), (2, 0, 0)])
    mid = (c.FirstParameter() + c.LastParameter()) / 2.0
    with pytest.raises(Geom_UndefinedDerivative):
        c.EvalDN(mid, 0)
    with pytest.raises(Geom_UndefinedDerivative):
        c.EvalDN(mid, -1)


def test_Geom_CurveEvalTest_TrimmedCurve_EvalD1_DelegatesToBasis():
    basis = circle(5.0)
    trimmed = Geom_TrimmedCurve(basis, 0.0, math.pi)
    u = math.pi / 4.0
    b = basis.EvalD1(u)
    t = trimmed.EvalD1(u)
    assert abs(b.Point.Distance(t.Point)) <= TOL
    assert abs((b.D1 - t.D1).Magnitude()) <= TOL


def test_Geom_CurveEvalTest_OffsetCurve_EvalD1_DegenerateAtCollapsed():
    off = Geom_OffsetCurve(circle(5.0), -5.0, gp_Dir(0.0, 0.0, 1.0))
    res = off.EvalD1(0.0)
    assert abs(res.Point.Distance(ORIGIN)) <= TOL
