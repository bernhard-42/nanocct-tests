# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_BezierCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_BezierCurve
from nanocct.GeomGridEval import GeomGridEval_BezierCurve
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-10


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _cubic():
    poles = NCollection_Array1[gp_Pnt](1, 4)
    poles.SetValue(1, gp_Pnt(0, 0, 0))
    poles.SetValue(2, gp_Pnt(1, 2, 0))
    poles.SetValue(3, gp_Pnt(3, 2, 0))
    poles.SetValue(4, gp_Pnt(4, 0, 0))
    return Geom_BezierCurve(poles)


def _quarter_circle():
    poles = NCollection_Array1[gp_Pnt](1, 3)
    weights = NCollection_Array1[float](1, 3)
    poles.SetValue(1, gp_Pnt(1, 0, 0))
    poles.SetValue(2, gp_Pnt(1, 1, 0))
    poles.SetValue(3, gp_Pnt(0, 1, 0))
    weights.SetValue(1, 1.0)
    weights.SetValue(2, 1.0 / math.sqrt(2.0))
    weights.SetValue(3, 1.0)
    return Geom_BezierCurve(poles, weights)


def test_GeomGridEval_BezierCurveTest_BasicEvaluation():
    bez = _cubic()
    ev = GeomGridEval_BezierCurve(bez)
    assert ev.Geometry() is not None
    params = NCollection_Array1[float](1, 3)
    params.SetValue(1, 0.0)
    params.SetValue(2, 0.5)
    params.SetValue(3, 1.0)
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == 3
    for i in range(1, 4):
        assert grid.Value(i).Distance(bez.Value(params.Value(i))) <= TOL


def test_GeomGridEval_BezierCurveTest_DerivativeD1():
    bez = _cubic()
    ev = GeomGridEval_BezierCurve(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD1(params)
    for i in range(1, 6):
        p, d1 = gp_Pnt(), gp_Vec()
        bez.D1(params.Value(i), p, d1)
        r = grid.Value(i)
        assert r.Point.Distance(p) <= TOL
        assert (r.D1 - d1).Magnitude() <= TOL


def test_GeomGridEval_BezierCurveTest_DerivativeD2():
    bez = _cubic()
    ev = GeomGridEval_BezierCurve(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD2(params)
    for i in range(1, 6):
        p, d1, d2 = gp_Pnt(), gp_Vec(), gp_Vec()
        bez.D2(params.Value(i), p, d1, d2)
        r = grid.Value(i)
        assert r.Point.Distance(p) <= TOL
        assert (r.D1 - d1).Magnitude() <= TOL
        assert (r.D2 - d2).Magnitude() <= TOL


def test_GeomGridEval_BezierCurveTest_DerivativeD3():
    bez = _cubic()
    ev = GeomGridEval_BezierCurve(bez)
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridD3(params)
    for i in range(1, 6):
        p, d1, d2, d3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
        bez.D3(params.Value(i), p, d1, d2, d3)
        r = grid.Value(i)
        assert r.Point.Distance(p) <= TOL
        assert (r.D1 - d1).Magnitude() <= TOL
        assert (r.D2 - d2).Magnitude() <= TOL
        assert (r.D3 - d3).Magnitude() <= TOL


def test_GeomGridEval_BezierCurveTest_RationalEvaluation():
    bez = _quarter_circle()
    ev = GeomGridEval_BezierCurve(bez)
    params = _uniform(0.0, 1.0, 11)
    grid = ev.EvaluateGrid(params)
    for i in range(1, 12):
        assert grid.Value(i).Distance(bez.Value(params.Value(i))) <= TOL


def _check_dn(bez, n_params, order):
    ev = GeomGridEval_BezierCurve(bez)
    params = _uniform(0.0, 1.0, n_params)
    grid = ev.EvaluateGridDN(params, order)
    for i in range(1, n_params + 1):
        expected = bez.DN(params.Value(i), order)
        assert (grid.Value(i) - expected).Magnitude() <= TOL


def test_GeomGridEval_BezierCurveTest_DerivativeDN_Order1():
    _check_dn(_cubic(), 5, 1)


def test_GeomGridEval_BezierCurveTest_DerivativeDN_Order2():
    _check_dn(_cubic(), 5, 2)


def test_GeomGridEval_BezierCurveTest_DerivativeDN_Order3():
    _check_dn(_cubic(), 5, 3)


def test_GeomGridEval_BezierCurveTest_DerivativeDN_BeyondDegree():
    ev = GeomGridEval_BezierCurve(_cubic())
    params = _uniform(0.0, 1.0, 5)
    grid = ev.EvaluateGridDN(params, 4)
    for i in range(1, 6):
        assert grid.Value(i).Magnitude() <= TOL


def test_GeomGridEval_BezierCurveTest_DerivativeDN_RationalCurve():
    bez = _quarter_circle()
    for order in (1, 2):
        _check_dn(bez, 11, order)
