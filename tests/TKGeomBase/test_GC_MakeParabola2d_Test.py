# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GC_MakeParabola2d_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GC import GC_MakeParabola2d
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d


def _check(axes, focus, sense, focal, vx, vy, param, coeffs):
    tol = 1.0e-12
    prb = GC_MakeParabola2d(axes, focus, sense)
    assert prb.Value() is not None
    parab = prb.Value().Parab2d()
    vert = parab.Location()
    assert abs(parab.Focal() - focal) <= tol
    assert abs(vert.X() - vx) <= tol
    assert abs(vert.Y() - vy) <= tol
    assert abs(parab.Parameter() - param) <= tol
    for got, exp in zip(parab.Coefficients(), coeffs):
        assert abs(got - exp) <= tol


def test_GC_MakeParabola2d_Test_OCC26747_1_ParabolaOpeningRight():
    _check(gp_Ax2d(gp_Pnt2d(0.0, 3.0), gp_Dir2d(gp_Dir2d.D.Y)), gp_Pnt2d(1.0, 3.0), True,
           0.5, 0.5, 3.0, 1.0, [0.0, 1.0, 0.0, -1.0, -3.0, 10.0])


def test_GC_MakeParabola2d_Test_OCC26747_2_ParabolaOpeningLeft():
    _check(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(gp_Dir2d.D.Y)), gp_Pnt2d(-1.0, 3.0), False,
           0.5, -0.5, 3.0, 1.0, [0.0, 1.0, 0.0, 1.0, -3.0, 10.0])


def test_GC_MakeParabola2d_Test_OCC26747_3_DegenerateParabola():
    _check(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(gp_Dir2d.D.Y)), gp_Pnt2d(0.0, 3.0), False,
           0.0, 0.0, 3.0, 0.0, [0.0, 1.0, 0.0, 0.0, -3.0, 9.0])
