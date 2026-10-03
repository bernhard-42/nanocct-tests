# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_OffsetCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom import Geom_Circle, Geom_OffsetCurve
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt


@pytest.fixture
def original():
    circ = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5.0)
    return Geom_OffsetCurve(Geom_Circle(circ), 2.0, gp_Dir(0, 0, 1))


def test_Geom_OffsetCurve_Test_CopyConstructorBasicProperties(original):
    cp = Geom_OffsetCurve(original)
    assert original.Offset() == cp.Offset()
    assert original.Direction().IsEqual(cp.Direction(), 1e-10)
    assert original.IsPeriodic() == cp.IsPeriodic()
    assert original.IsClosed() == cp.IsClosed()


def test_Geom_OffsetCurve_Test_CopyConstructorBasisCurve(original):
    cp = Geom_OffsetCurve(original)
    b0 = original.BasisCurve()
    b1 = cp.BasisCurve()
    assert b0 is not b1
    assert b0.FirstParameter() == b1.FirstParameter()
    assert b0.LastParameter() == b1.LastParameter()


def test_Geom_OffsetCurve_Test_CopyMethodUsesOptimizedConstructor(original):
    cp = original.Copy()
    assert isinstance(cp, Geom_OffsetCurve)
    assert original.Offset() == cp.Offset()
    u0 = original.FirstParameter()
    u1 = original.LastParameter()
    step = (u1 - u0) / 4.0
    u = u0
    while u <= u1:
        assert original.Value(u).IsEqual(cp.Value(u), 1e-10)
        u += step


def test_Geom_OffsetCurve_Test_CopyIndependence(original):
    cp = Geom_OffsetCurve(original)
    orig_offset = cp.Offset()
    original.SetOffsetValue(10.0)
    assert cp.Offset() == orig_offset
    assert cp.Offset() != original.Offset()
