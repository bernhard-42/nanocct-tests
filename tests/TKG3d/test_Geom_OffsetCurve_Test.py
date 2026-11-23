# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_OffsetCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_BezierCurve, Geom_Circle, Geom_Ellipse, Geom_OffsetCurve
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.GeomGridEval import GeomGridEval_Curve
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1


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


def test_GeomOffsetCurveDerivativesTest_EllipseThirdOrderJetUsesNormalizedNormalDerivatives():
    basis = Geom_Ellipse(gp_Ax2(), 2, 1)
    curve = Geom_OffsetCurve(basis, 0.25, gp_Dir(0, 0, 1))
    adaptor = GeomAdaptor_Curve(curve)
    evaluator = GeomGridEval_Curve(adaptor)
    params = NCollection_Array1[float](0, 0)
    params[0] = 0.0
    grid = evaluator.EvaluateGridD3(params)
    for result in (curve.EvalD3(0), adaptor.EvalD3(0)):
        assert result.Point.X() == pytest.approx(2.25, rel=1e-15)
        assert result.D1.Y() == pytest.approx(1.5, rel=1e-15)
        assert result.D2.X() == pytest.approx(-3.0, rel=1e-15)
        assert result.D3.Y() == pytest.approx(-6.0, rel=1e-15)
    assert grid.Size() == 1
    first = grid[grid.Lower()]                      # C++ At(0): the first element, whatever the lower bound
    assert first.D2.X() == pytest.approx(-3.0, rel=1e-15)
    assert first.D3.Y() == pytest.approx(-6.0, rel=1e-15)
    assert curve.EvalD2(0).D2.X() == pytest.approx(-3.0, rel=1e-15)


def test_GeomOffsetCurveDerivativesTest_ScaledParabolaHasFiniteThirdNormalDerivative():
    for scale in (1.0, 1.0e-45, 1.0e-53, 1.0e53):
        poles = NCollection_Array1[gp_Pnt](3)
        poles[0] = gp_Pnt(0, 0, 0)
        poles[1] = gp_Pnt(0.5 * scale, 0, 0)
        poles[2] = gp_Pnt(scale, scale, 0)
        offset = Geom_OffsetCurve(Geom_BezierCurve(poles), 0.25, gp_Dir(0, 0, 1))
        at_zero = offset.EvalD3(0)
        assert at_zero.D3.X() == pytest.approx(-6.0, abs=1e-12), scale
        assert at_zero.D3.Y() == pytest.approx(0.0, abs=1e-12), scale
        at_one = offset.EvalD3(1)
        denominator = 25 * math.sqrt(5.0)
        assert at_one.D3.X() == pytest.approx(18 / denominator, abs=1e-12), scale
        assert at_one.D3.Y() == pytest.approx(12 / denominator, abs=1e-12), scale
        d2 = offset.EvalD2(0)
        assert at_zero.D2.Y() == pytest.approx(d2.D2.Y(), abs=1e-12 * max(1.0, scale)), scale
