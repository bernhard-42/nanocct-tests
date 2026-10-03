# Translated from OCCT src/ModelingAlgorithms/TKHelix/GTests/HelixGeom_BuilderHelix_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.HelixGeom import HelixGeom_BuilderHelix

TOL = 1.0e-4


def _z_ax2():
    return gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0))


def test_HelixGeom_BuilderHelix_Test_SingleCoil():
    b = HelixGeom_BuilderHelix()
    b.SetPosition(_z_ax2())
    b.SetTolerance(TOL)
    b.SetCurveParameters(0.0, 2.0 * math.pi, 10.0, 5.0, 0.0, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    assert b.Curves().Length() == 1


def test_HelixGeom_BuilderHelix_Test_MultipleCoils():
    b = HelixGeom_BuilderHelix()
    b.SetPosition(_z_ax2())
    b.SetTolerance(TOL)
    b.SetCurveParameters(0.0, 6.0 * math.pi, 10.0, 5.0, 0.0, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    assert b.Curves().Length() == 3


def test_HelixGeom_BuilderHelix_Test_PositionGetterSetter():
    b = HelixGeom_BuilderHelix()
    pos = gp_Ax2(gp_Pnt(10.0, 20.0, 30.0), gp_Dir(1.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0))
    b.SetPosition(pos)
    got = b.Position()
    assert got.Location().IsEqual(pos.Location(), 1e-15)
    assert got.Direction().IsEqual(pos.Direction(), 1e-15)
    assert got.XDirection().IsEqual(pos.XDirection(), 1e-15)


def test_HelixGeom_BuilderHelix_Test_ParameterManagement():
    b = HelixGeom_BuilderHelix()
    params = (1.0, 7.0, 15.0, 4.0, 0.2, False)
    b.SetCurveParameters(*params)
    assert b.CurveParameters() == params
