# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dAPI_InterCurveCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom2d import Geom2d_Ellipse
from nanocct.Geom2dAPI import Geom2dAPI_InterCurveCurve
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Elips2d, gp_Pnt2d
from nanocct.math import math_NewtonFunctionRoot, math_TrigonometricEquationFunction
from nanocct.Standard import Standard_NullObject, Standard_OutOfRange


def test_Geom2dAPI_InterCurveCurve_Test_OCC29289_EllipseIntersectionNewtonRoot():
    e1 = gp_Elips2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(gp_Dir2d.D.X)), 2.0, 1.0)
    ge1 = Geom2d_Ellipse(e1)
    e2 = gp_Elips2d(gp_Ax2d(gp_Pnt2d(0.5, 0.5), gp_Dir2d(1.0, 1.0)), 2.0, 1.0)
    ge2 = Geom2d_Ellipse(e2)

    inter = Geom2dAPI_InterCurveCurve()
    inter.Init(ge1, ge2, 1.0e-7)
    assert inter.NbPoints() > 0

    my_f = math_TrigonometricEquationFunction(1.875, -0.75, -0.5, -0.25, -0.25)
    tol1 = 1.0e-15
    eps = 1.5e-12
    nit = [5, 6, 7, 6]

    teta_prev = 0.0
    gi = inter.Intersector()
    for i in range(1, inter.NbPoints() + 1):
        teta = gi.Point(i).ParamOnFirst()
        x = teta - 0.1 * (teta - teta_prev)
        teta_prev = teta
        resol = math_NewtonFunctionRoot(my_f, x, tol1, eps, nit[i - 1])
        assert resol.IsDone()
        assert abs(teta - resol.Root()) <= 1.0e-7


def test_Geom2dAPI_InterCurveCurve_Test_PointRejectsZeroIndex():
    c1 = Geom2d_Ellipse(gp_Elips2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 2.0, 1.0))
    c2 = Geom2d_Ellipse(gp_Elips2d(gp_Ax2d(gp_Pnt2d(0.5, 0.5), gp_Dir2d(1.0, 1.0)), 2.0, 1.0))
    inter = Geom2dAPI_InterCurveCurve(c1, c2, 1.0e-7)
    assert inter.NbPoints() > 0
    with pytest.raises(Standard_OutOfRange):
        inter.Point(0)


def test_Geom2dAPI_InterCurveCurve_Test_Init_NullHandle_RaisesException():
    valid = Geom2d_Ellipse(gp_Elips2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 2.0, 1.0))
    with pytest.raises(Standard_NullObject):
        Geom2dAPI_InterCurveCurve(None, None, 1.0e-7)
    with pytest.raises(Standard_NullObject):
        Geom2dAPI_InterCurveCurve(None, valid, 1.0e-7)
    with pytest.raises(Standard_NullObject):
        Geom2dAPI_InterCurveCurve(valid, None, 1.0e-7)
    inter = Geom2dAPI_InterCurveCurve()
    with pytest.raises(Standard_NullObject):
        inter.Init(None, 1.0e-7)
