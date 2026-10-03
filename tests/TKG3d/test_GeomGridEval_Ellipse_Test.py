# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_Ellipse_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_Ellipse
from nanocct.GeomGridEval import GeomGridEval_Ellipse
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-10


def _uniform(first, last, n):
    arr = NCollection_Array1[float](1, n)
    step = (last - first) / (n - 1)
    for i in range(1, n + 1):
        arr.SetValue(i, first + (i - 1) * step)
    return arr


def _curve():
    return Geom_Ellipse(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 3.0, 2.0)


def test_GeomGridEval_EllipseTest_BasicEvaluation():
    crv = _curve()
    ev = GeomGridEval_Ellipse(crv)
    assert ev.Geometry() is not None
    params = NCollection_Array1[float](1, 5)
    for i, t in enumerate((0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi), start=1):
        params.SetValue(i, t)
    grid = ev.EvaluateGrid(params)
    for i, (x, y) in enumerate(((3.0, 0.0), (0.0, 2.0), (-3.0, 0.0), (0.0, -2.0), (3.0, 0.0)), start=1):
        assert abs(grid.Value(i).X() - x) <= TOL
        assert abs(grid.Value(i).Y() - y) <= TOL


def test_GeomGridEval_EllipseTest_DerivativeD1():
    crv = _curve()
    ev = GeomGridEval_Ellipse(crv)
    params = _uniform(0.0, 2 * math.pi, 9)
    grid = ev.EvaluateGridD1(params)
    for i in range(1, 10):
        p, d1 = gp_Pnt(), gp_Vec()
        crv.D1(params.Value(i), p, d1)
        assert grid.Value(i).Point.Distance(p) <= TOL
        assert (grid.Value(i).D1 - d1).Magnitude() <= TOL


def test_GeomGridEval_EllipseTest_DerivativeD2():
    crv = _curve()
    ev = GeomGridEval_Ellipse(crv)
    params = _uniform(0.0, 2 * math.pi, 9)
    grid = ev.EvaluateGridD2(params)
    for i in range(1, 10):
        p, d1, d2 = gp_Pnt(), gp_Vec(), gp_Vec()
        crv.D2(params.Value(i), p, d1, d2)
        assert grid.Value(i).Point.Distance(p) <= TOL
        assert (grid.Value(i).D1 - d1).Magnitude() <= TOL
        assert (grid.Value(i).D2 - d2).Magnitude() <= TOL


def test_GeomGridEval_EllipseTest_DerivativeD3():
    crv = _curve()
    ev = GeomGridEval_Ellipse(crv)
    params = _uniform(0.0, 2 * math.pi, 9)
    grid = ev.EvaluateGridD3(params)
    for i in range(1, 10):
        p, d1, d2, d3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
        crv.D3(params.Value(i), p, d1, d2, d3)
        assert grid.Value(i).Point.Distance(p) <= TOL
        assert (grid.Value(i).D1 - d1).Magnitude() <= TOL
        assert (grid.Value(i).D2 - d2).Magnitude() <= TOL
        assert (grid.Value(i).D3 - d3).Magnitude() <= TOL
