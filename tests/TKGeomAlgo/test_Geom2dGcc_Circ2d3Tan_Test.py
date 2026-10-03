# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dGcc_Circ2d3Tan_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom2d import Geom2d_Circle
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.Geom2dGcc import Geom2dGcc, Geom2dGcc_Circ2d3Tan
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Pnt2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def _circ(x, y, r):
    return gp_Circ2d(gp_Ax2d(gp_Pnt2d(x, y), gp_Dir2d(1, 0)), r)


def _qualified(x, y, r):
    adaptor = Geom2dAdaptor_Curve(Geom2d_Circle(_circ(x, y, r)))
    return Geom2dGcc.Unqualified_s(adaptor)


def _verify_tangency(sol, circles, tol=1e-6):
    c = sol.Location()
    r = sol.Radius()
    for circ in circles:
        d = c.Distance(circ.Location())
        ext = r + circ.Radius()
        inner = abs(r - circ.Radius())
        assert abs(d - ext) <= tol or abs(d - inner) <= tol


def _verify_validity(sol, min_x=-10000.0, max_x=10000.0, min_y=-10000.0, max_y=10000.0, max_r=100000.0):
    assert 0 < sol.Radius() < max_r
    c = sol.Location()
    assert min_x < c.X() < max_x
    assert min_y < c.Y() < max_y


def _solve(specs, tol=TOL):
    q1, q2, q3 = (_qualified(*s) for s in specs)
    return Geom2dGcc_Circ2d3Tan(q1, q2, q3, tol, 0, 0, 0)


def test_Geom2dGcc_Circ2d3TanTest_BUC60622_RegressionCase():
    specs = [(500.0, 1800.0, 500.0), (500.0, 1900.0, 400.0), (700.0, 1900.0, 200.0)]
    solver = _solve(specs)
    assert solver.IsDone()
    n = solver.NbSolutions()
    assert n == 3
    circles = [_circ(*s) for s in specs]
    for i in range(1, n + 1):
        sol = solver.ThisSolution(i)
        _verify_validity(sol, -1000.0, 2000.0, 1000.0, 3000.0, 10000.0)
        _verify_tangency(sol, circles)
    if n >= 3:
        sol1 = solver.ThisSolution(1)
        assert abs(sol1.Location().X() - 500.0) <= 1.0
        assert abs(sol1.Location().Y() - 1900.0) <= 1.0
        assert abs(sol1.Radius() - 400.0) <= 1.0


def test_Geom2dGcc_Circ2d3TanTest_ToleranceImpact_Analysis():
    specs = [(500.0, 1800.0, 500.0), (500.0, 1900.0, 400.0), (700.0, 1900.0, 200.0)]
    default_count = 0
    for tol in [TOL, 1e-12, 1e-10, 1e-8]:
        solver = _solve(specs, tol)
        assert solver.IsDone()
        n = solver.NbSolutions()
        if tol == TOL:
            default_count = n
            assert n >= 1
        else:
            assert n >= 1
            assert n <= default_count + 2
        for i in range(1, n + 1):
            _verify_validity(solver.ThisSolution(i), -1000.0, 2000.0, 1000.0, 3000.0, 10000.0)


def _generic(specs, validity=(), tang_tol=1e-6):
    solver = _solve(specs)
    assert solver.IsDone()
    n = solver.NbSolutions()
    assert n >= 1
    circles = [_circ(*s) for s in specs]
    for i in range(1, n + 1):
        sol = solver.ThisSolution(i)
        _verify_validity(sol, *validity)
        _verify_tangency(sol, circles, tang_tol)


def test_Geom2dGcc_Circ2d3TanTest_Simple_ThreeCircle_Case():
    _generic([(0.0, 0.0, 2.0), (10.0, 0.0, 2.0), (5.0, 8.0, 2.0)])


def test_Geom2dGcc_Circ2d3TanTest_Concentric_Circles_EdgeCase():
    solver = _solve([(0.0, 0.0, 1.0), (0.0, 0.0, 3.0), (10.0, 0.0, 2.0)])
    assert solver.IsDone()
    assert solver.NbSolutions() == 0


def test_Geom2dGcc_Circ2d3TanTest_SmallCircles_PrecisionTest():
    _generic([(0.0, 0.0, 0.01), (0.1, 0.0, 0.01), (0.05, 0.08, 0.01)], (-10.0, 10.0, -10.0, 10.0, 10.0), 1e-3)


def test_Geom2dGcc_Circ2d3TanTest_LargeCircles_ScalingTest():
    _generic([(0.0, 0.0, 1000.0), (5000.0, 0.0, 1500.0), (2500.0, 4000.0, 800.0)],
             (-10000.0, 10000.0, -10000.0, 10000.0, 50000.0), 1.0)


def test_Geom2dGcc_Circ2d3TanTest_LinearConfiguration_GeometricTest():
    _generic([(0.0, 0.0, 1.0), (5.0, 0.0, 1.5), (10.0, 0.0, 1.2)])


def test_Geom2dGcc_Circ2d3TanTest_TouchingCircles_DegenerateCase():
    _generic([(0.0, 0.0, 2.0), (4.0, 0.0, 2.0), (2.0, 5.0, 1.5)])
