# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomGridEval_Hyperbola_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_Hyperbola
from nanocct.GeomGridEval import GeomGridEval_Hyperbola
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
    return Geom_Hyperbola(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 3.0, 2.0)


def test_GeomGridEval_HyperbolaTest_BasicEvaluation():
    crv = _curve()
    ev = GeomGridEval_Hyperbola(crv)
    assert ev.Geometry() is not None
    params = _uniform(-2.0, 2.0, 9)
    grid = ev.EvaluateGrid(params)
    assert grid.Size() == 9
    for i in range(1, 9 + 1):
        assert grid.Value(i).Distance(crv.Value(params.Value(i))) <= TOL


def test_GeomGridEval_HyperbolaTest_DerivativeD1():
    crv = _curve()
    ev = GeomGridEval_Hyperbola(crv)
    params = _uniform(-2.0, 2.0, 9)
    grid = ev.EvaluateGridD1(params)
    for i in range(1, 10):
        p, d1 = gp_Pnt(), gp_Vec()
        crv.D1(params.Value(i), p, d1)
        assert grid.Value(i).Point.Distance(p) <= TOL
        assert (grid.Value(i).D1 - d1).Magnitude() <= TOL


def test_GeomGridEval_HyperbolaTest_DerivativeD2():
    crv = _curve()
    ev = GeomGridEval_Hyperbola(crv)
    params = _uniform(-2.0, 2.0, 9)
    grid = ev.EvaluateGridD2(params)
    for i in range(1, 10):
        p, d1, d2 = gp_Pnt(), gp_Vec(), gp_Vec()
        crv.D2(params.Value(i), p, d1, d2)
        assert grid.Value(i).Point.Distance(p) <= TOL
        assert (grid.Value(i).D1 - d1).Magnitude() <= TOL
        assert (grid.Value(i).D2 - d2).Magnitude() <= TOL


def test_GeomGridEval_HyperbolaTest_DerivativeD3():
    crv = _curve()
    ev = GeomGridEval_Hyperbola(crv)
    params = _uniform(-2.0, 2.0, 9)
    grid = ev.EvaluateGridD3(params)
    for i in range(1, 10):
        p, d1, d2, d3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
        crv.D3(params.Value(i), p, d1, d2, d3)
        assert grid.Value(i).Point.Distance(p) <= TOL
        assert (grid.Value(i).D1 - d1).Magnitude() <= TOL
        assert (grid.Value(i).D2 - d2).Magnitude() <= TOL
        assert (grid.Value(i).D3 - d3).Magnitude() <= TOL
