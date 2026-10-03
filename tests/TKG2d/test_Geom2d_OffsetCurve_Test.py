# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_OffsetCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom2d import Geom2d_Circle, Geom2d_OffsetCurve
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Pnt2d


@pytest.fixture
def orig():
    basis = Geom2d_Circle(gp_Circ2d(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(gp_Dir2d.D.X)), 5.0))
    return Geom2d_OffsetCurve(basis, 2.0)


def test_Geom2d_OffsetCurve_Test_CopyConstructorBasicProperties(orig):
    c = Geom2d_OffsetCurve(orig)
    assert orig.Offset() == c.Offset()
    assert orig.IsPeriodic() == c.IsPeriodic()
    assert orig.IsClosed() == c.IsClosed()


def test_Geom2d_OffsetCurve_Test_CopyConstructorBasisCurve(orig):
    c = Geom2d_OffsetCurve(orig)
    ob, cb = orig.BasisCurve(), c.BasisCurve()
    assert ob is not cb
    assert ob.FirstParameter() == cb.FirstParameter()
    assert ob.LastParameter() == cb.LastParameter()


def test_Geom2d_OffsetCurve_Test_CopyMethodUsesOptimizedConstructor(orig):
    c = orig.Copy()
    assert isinstance(c, Geom2d_OffsetCurve)
    assert orig.Offset() == c.Offset()
    uf, ul = orig.FirstParameter(), orig.LastParameter()
    step = (ul - uf) / 4.0
    u = uf
    while u <= ul:
        assert orig.Value(u).IsEqual(c.Value(u), 1e-10)
        u += step


def test_Geom2d_OffsetCurve_Test_CopyIndependence(orig):
    c = Geom2d_OffsetCurve(orig)
    off = c.Offset()
    orig.SetOffsetValue(10.0)
    assert c.Offset() == off
    assert c.Offset() != orig.Offset()
