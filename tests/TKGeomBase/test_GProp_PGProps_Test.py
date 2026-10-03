# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GProp_PGProps_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Pnt
from nanocct.GProp import GProp_PGProps
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _pnts(*xyz):
    a = NCollection_Array1[gp_Pnt](1, len(xyz))
    for i, p in enumerate(xyz, 1):
        a[i] = gp_Pnt(*p)
    return a


def _com(props, x, y, z):
    c = props.CentreOfMass()
    assert abs(c.X() - x) <= CONF
    assert abs(c.Y() - y) <= CONF
    assert abs(c.Z() - z) <= CONF


def test_GProp_PGPropsTest_EmptySet():
    assert abs(GProp_PGProps().Mass()) <= CONF


def test_GProp_PGPropsTest_SinglePoint():
    pr = GProp_PGProps()
    pr.AddPoint(gp_Pnt(1, 2, 3))
    assert abs(pr.Mass() - 1.0) <= CONF
    _com(pr, 1, 2, 3)


def test_GProp_PGPropsTest_TwoPoints_Barycentre():
    pr = GProp_PGProps()
    pr.AddPoint(gp_Pnt(0, 0, 0))
    pr.AddPoint(gp_Pnt(2, 4, 6))
    assert abs(pr.Mass() - 2.0) <= CONF
    _com(pr, 1, 2, 3)


def test_GProp_PGPropsTest_WeightedPoints():
    pr = GProp_PGProps()
    pr.AddPoint(gp_Pnt(0, 0, 0), 1.0)
    pr.AddPoint(gp_Pnt(4, 0, 0), 3.0)
    assert abs(pr.Mass() - 4.0) <= CONF
    _com(pr, 3, 0, 0)


def test_GProp_PGPropsTest_ArrayConstructor():
    pr = GProp_PGProps(_pnts((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)))
    assert abs(pr.Mass() - 4.0) <= CONF
    _com(pr, 0, 0, 0)


def test_GProp_PGPropsTest_StaticBarycentre():
    g = GProp_PGProps.Barycentre_s(_pnts((0, 0, 0), (3, 0, 0), (0, 6, 0)))
    assert abs(g.X() - 1.0) <= CONF
    assert abs(g.Y() - 2.0) <= CONF
    assert abs(g.Z()) <= CONF


def test_GProp_PGPropsTest_MatrixOfInertia_SymmetricPoints():
    m = GProp_PGProps(_pnts((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0))).MatrixOfInertia()
    for (r, c), exp in {(1, 1): 2.0, (2, 2): 2.0, (3, 3): 4.0, (1, 2): 0.0, (1, 3): 0.0, (2, 3): 0.0}.items():
        assert abs(m.Value(r, c) - exp) <= CONF
