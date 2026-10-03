# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_CurveEval_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import (
    Geom2d_Circle,
    Geom2d_Ellipse,
    Geom2d_Line,
    Geom2d_OffsetCurve,
    Geom2d_UndefinedDerivative,
)
from nanocct.Geom2dAPI import Geom2dAPI_PointsToBSpline
from nanocct.gp import gp_Ax22d, gp_Circ2d, gp_Dir2d, gp_Elips2d, gp_Pnt2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def pnts(*pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, 1):
        a[i] = gp_Pnt2d(x, y)
    return a


def test_Geom2d_CurveEvalTest_Circle_EvalD0D1_ValidResults():
    c = Geom2d_Circle(gp_Circ2d(gp_Ax22d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 4.0))
    u = math.pi / 4.0
    d0 = c.EvalD0(u)
    assert abs(d0.Distance(gp_Pnt2d(0.0, 0.0)) - 4.0) <= TOL
    r = c.EvalD1(u)
    assert abs(r.Point.Distance(d0)) <= TOL
    radial = gp_Vec2d(gp_Pnt2d(0.0, 0.0), r.Point)
    assert abs(radial.Dot(r.D1)) <= 1e-10


def test_Geom2d_CurveEvalTest_OffsetCurve_EvalD0_ValidAtDegenerateCenter():
    basis = Geom2d_Circle(gp_Circ2d(gp_Ax22d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 3.0))
    off = Geom2d_OffsetCurve(basis, -3.0)
    assert abs(off.EvalD0(0.0).Distance(gp_Pnt2d(0.0, 0.0))) <= TOL


def test_Geom2d_CurveEvalTest_BSplineCurve_EvalD1_ConsistentWithOldAPI():
    interp = Geom2dAPI_PointsToBSpline(pnts((0, 0), (1, 2), (3, 1), (5, 3), (7, 0)))
    assert interp.IsDone() is True
    c = interp.Curve()
    mid = (c.FirstParameter() + c.LastParameter()) / 2.0
    r = c.EvalD1(mid)
    p, v1 = gp_Pnt2d(), gp_Vec2d()
    c.D1(mid, p, v1)
    assert abs(r.Point.Distance(p)) <= TOL
    assert abs((r.D1 - v1).Magnitude()) <= TOL


def test_Geom2d_CurveEvalTest_Ellipse_EvalD2D3_ValidResults():
    c = Geom2d_Ellipse(gp_Elips2d(gp_Ax22d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 5.0, 3.0))
    u = math.pi / 4.0
    assert c.EvalD2(u).D2.Magnitude() > 0.0
    assert c.EvalD3(u).D3.Magnitude() > 0.0


def test_Geom2d_CurveEvalTest_Line_EvalDN_ValidResults():
    c = Geom2d_Line(gp_Pnt2d(1.0, 2.0), gp_Dir2d(1.0, 0.0))
    d1 = c.EvalDN(5.0, 1)
    assert abs(d1.X() - 1.0) <= TOL
    assert abs(d1.Y()) <= TOL
    assert abs(c.EvalDN(5.0, 2).Magnitude()) <= TOL


def test_Geom2d_CurveEvalTest_BSplineCurve_EvalDN_InvalidN_Throws():
    interp = Geom2dAPI_PointsToBSpline(pnts((0, 0), (1, 1), (2, 0)))
    assert interp.IsDone() is True
    c = interp.Curve()
    mid = (c.FirstParameter() + c.LastParameter()) / 2.0
    with pytest.raises(Geom2d_UndefinedDerivative):
        c.EvalDN(mid, 0)
    with pytest.raises(Geom2d_UndefinedDerivative):
        c.EvalDN(mid, -1)


def test_Geom2d_CurveEvalTest_OffsetCurve_EvalD1_DegenerateAtCollapsed():
    basis = Geom2d_Circle(gp_Circ2d(gp_Ax22d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 3.0))
    off = Geom2d_OffsetCurve(basis, -3.0)
    assert abs(off.EvalD1(0.0).Point.Distance(gp_Pnt2d(0.0, 0.0))) <= TOL
