# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GProp_PEquation_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.GProp import GProp_PEquation
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _pnts(*xyz):
    a = NCollection_Array1[gp_Pnt](1, len(xyz))
    for i, p in enumerate(xyz, 1):
        a[i] = gp_Pnt(*p)
    return a


def test_GProp_PEquationTest_CoincidentPoints():
    eq = GProp_PEquation(_pnts((1, 2, 3), (1, 2, 3), (1, 2, 3)), 1e-6)
    assert eq.IsPoint()
    p = eq.Point()
    assert abs(p.X() - 1.0) <= CONF
    assert abs(p.Y() - 2.0) <= CONF
    assert abs(p.Z() - 3.0) <= CONF


def test_GProp_PEquationTest_CollinearPoints():
    eq = GProp_PEquation(_pnts((0, 0, 0), (1, 0, 0), (2, 0, 0)), 1e-6)
    assert eq.IsLinear()
    assert abs(abs(eq.Line().Direction().X()) - 1.0) <= CONF


def test_GProp_PEquationTest_CoplanarPoints():
    eq = GProp_PEquation(_pnts((0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)), 1e-6)
    assert eq.IsPlanar()
    assert abs(abs(eq.Plane().Axis().Direction().Z()) - 1.0) <= CONF


def test_GProp_PEquationTest_SpacePoints():
    eq = GProp_PEquation(_pnts((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)), 1e-6)
    assert eq.IsSpace()
    p, v1, v2, v3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
    eq.Box(p, v1, v2, v3)
    assert v1.Magnitude() > CONF
    assert v2.Magnitude() > CONF
    assert v3.Magnitude() > CONF
