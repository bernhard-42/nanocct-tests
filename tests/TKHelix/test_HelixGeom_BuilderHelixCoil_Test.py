# Translated from OCCT src/ModelingAlgorithms/TKHelix/GTests/HelixGeom_BuilderHelixCoil_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_BSplineCurve
from nanocct.GeomAbs import GeomAbs_C2
from nanocct.gp import gp_Pnt
from nanocct.HelixGeom import HelixGeom_BuilderHelixCoil

TOL = 1.0e-4


def test_HelixGeom_BuilderHelixCoil_Test_BasicConstruction():
    b = HelixGeom_BuilderHelixCoil()
    b.SetTolerance(TOL)
    b.SetCurveParameters(0.0, 2.0 * math.pi, 5.0, 2.0, 0.0, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    curves = b.Curves()
    assert curves.Length() == 1
    curve = curves[1]
    assert curve is not None
    p1 = gp_Pnt()
    p2 = gp_Pnt()
    curve.D0(curve.FirstParameter(), p1)
    curve.D0(curve.LastParameter(), p2)
    assert abs(p1.X() - 2.0) <= TOL
    assert abs(p1.Y() - 0.0) <= TOL
    assert abs(p1.Z() - 0.0) <= TOL
    assert abs(p2.X() - 2.0) <= TOL
    assert abs(p2.Y() - 0.0) <= TOL
    assert abs(p2.Z() - 5.0) <= TOL


def test_HelixGeom_BuilderHelixCoil_Test_DefaultParameters():
    b = HelixGeom_BuilderHelixCoil()
    b.Perform()
    assert b.ErrorStatus() == 0
    cont, max_degree, max_seg = b.ApproxParameters()
    assert cont == GeomAbs_C2
    assert max_degree == 8
    assert max_seg == 150
    assert b.Tolerance() == 0.0001


def test_HelixGeom_BuilderHelixCoil_Test_ParameterSymmetry():
    b = HelixGeom_BuilderHelixCoil()
    params = (0.5, 5.5, 12.5, 3.5, 0.15, False)
    b.SetCurveParameters(*params)
    assert b.CurveParameters() == params


def test_HelixGeom_BuilderHelixCoil_Test_TaperedHelix():
    b = HelixGeom_BuilderHelixCoil()
    b.SetTolerance(TOL)
    b.SetApproxParameters(GeomAbs_C2, 8, 100)
    b.SetCurveParameters(0.0, 4.0 * math.pi, 20.0, 5.0, 0.1, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    assert b.ToleranceReached() <= TOL * 10
    curves = b.Curves()
    assert curves.Length() == 1
    curve = curves[1]
    assert isinstance(curve, Geom_BSplineCurve)
    assert curve.Degree() <= 8
    assert curve.NbPoles() > 0
