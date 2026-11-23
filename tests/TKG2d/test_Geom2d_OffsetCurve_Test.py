# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_OffsetCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Adaptor2d import Adaptor2d_OffsetCurve
from nanocct.Geom2d import Geom2d_BezierCurve, Geom2d_Circle, Geom2d_Ellipse, Geom2d_OffsetCurve
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1


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


def test_Geom2dOffsetCurveTest_EvalD3_RegularAndSmallEllipse_AgreesWithLowerOrders():
    for scale in (1.0, 1.0e-45):
        ellipse = Geom2d_Ellipse(gp_Ax2d(), 2.0 * scale, scale)
        offset = Geom2d_OffsetCurve(ellipse, 0.25 * scale)
        adaptor = Adaptor2d_OffsetCurve(Geom2dAdaptor_Curve(ellipse), 0.25 * scale)
        for t in (0.0, 0.37, 1.2):
            d2 = offset.EvalD2(t)
            d3 = offset.EvalD3(t)
            a3 = adaptor.EvalD3(t)
            assert d3.D2.X() / scale == pytest.approx(d2.D2.X() / scale, abs=1e-12), (scale, t)
            assert d3.D2.Y() / scale == pytest.approx(d2.D2.Y() / scale, abs=1e-12), (scale, t)
            assert a3.D2.X() / scale == pytest.approx(d2.D2.X() / scale, abs=1e-12), (scale, t)
            assert a3.D2.Y() / scale == pytest.approx(d2.D2.Y() / scale, abs=1e-12), (scale, t)
            assert a3.D3.X() / scale == pytest.approx(d3.D3.X() / scale, abs=1e-12), (scale, t)
            assert a3.D3.Y() / scale == pytest.approx(d3.D3.Y() / scale, abs=1e-12), (scale, t)
        assert offset.EvalD3(0.0).D2.X() / scale == pytest.approx(-3.0, abs=1e-12), scale
        assert offset.EvalD3(0.0).D3.Y() / scale == pytest.approx(-6.0, abs=1e-12), scale


def test_Geom2dOffsetCurveTest_ScaledParabolaHasFiniteThirdNormalDerivative():
    for scale in (1.0, 1.0e-45, 1.0e-53, 1.0e53):
        pts = NCollection_Array1[gp_Pnt2d](3)
        pts[0] = gp_Pnt2d(0, 0)
        pts[1] = gp_Pnt2d(0.5 * scale, 0)
        pts[2] = gp_Pnt2d(scale, scale)
        offset = Geom2d_OffsetCurve(Geom2d_BezierCurve(pts), 0.25)
        at_zero = offset.EvalD3(0)
        assert at_zero.D3.X() == pytest.approx(-6.0, abs=1e-12), scale
        assert at_zero.D3.Y() == pytest.approx(0.0, abs=1e-12), scale
        at_one = offset.EvalD3(1)
        denominator = 25 * math.sqrt(5.0)
        assert at_one.D3.X() == pytest.approx(18 / denominator, abs=1e-12), scale
        assert at_one.D3.Y() == pytest.approx(12 / denominator, abs=1e-12), scale
        d2 = offset.EvalD2(0)
        assert at_zero.D2.Y() == pytest.approx(d2.D2.Y(), abs=1e-12 * max(1.0, scale)), scale
