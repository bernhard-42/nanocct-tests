# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomFill_CoonsAlgPatch_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.GC import GC_MakeSegment
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.GeomFill import GeomFill_CoonsAlgPatch, GeomFill_SimpleBound
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.Precision import Precision


def _eq(value):
    # ASSERT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def _bound(p1, p2):
    """A segment boundary with its native arc-length parameter range."""
    return GeomFill_SimpleBound(GeomAdaptor_Curve(GC_MakeSegment(p1, p2).Value()), Precision.Confusion_s(), Precision.Angular_s())


def test_GeomFill_CoonsAlgPatchTest_ValueUsesUForTheUDirectionBoundaries():
    # The four boundaries of a planar square, in the order the constructor expects: B1 and B3 run along U, B2 and B4
    # along V. Value(U, V) must sample B1 and B3 at U, as D1U and D1V do.
    p00, p10, p11, p01 = gp_Pnt(0., 0., 0.), gp_Pnt(10., 0., 0.), gp_Pnt(10., 10., 0.), gp_Pnt(0., 10., 0.)
    b1, b2, b3, b4 = _bound(p00, p10), _bound(p10, p11), _bound(p01, p11), _bound(p00, p01)
    patch = GeomFill_CoonsAlgPatch(b1, b2, b3, b4)
    # The patch is parametrized on the boundaries' own ranges, U on B1's and V on B2's.
    u_min, u_max = b1.Bounds()
    v_min, v_max = b2.Bounds()
    tol = Precision.Confusion_s()
    assert patch.Value(u_min, v_min).Distance(p00) == pytest.approx(0., abs=tol)
    assert patch.Value(u_max, v_min).Distance(p10) == pytest.approx(0., abs=tol)
    assert patch.Value(u_max, v_max).Distance(p11) == pytest.approx(0., abs=tol)
    assert patch.Value(u_min, v_max).Distance(p01) == pytest.approx(0., abs=tol)
    u_mid, v_mid = 0.5 * (u_min + u_max), 0.5 * (v_min + v_max)
    assert patch.Value(u_max, v_mid).Distance(gp_Pnt(10., 5., 0.)) == pytest.approx(0., abs=tol)
    assert patch.Value(u_min, v_mid).Distance(gp_Pnt(0., 5., 0.)) == pytest.approx(0., abs=tol)
    assert patch.Value(u_mid, v_min).Distance(gp_Pnt(5., 0., 0.)) == pytest.approx(0., abs=tol)
    assert patch.Value(u_mid, v_max).Distance(gp_Pnt(5., 10., 0.)) == pytest.approx(0., abs=tol)
    assert patch.Value(3., 7.).Distance(gp_Pnt(3., 7., 0.)) == pytest.approx(0., abs=tol)


def test_GeomFill_CoonsAlgPatchTest_ValueUsesIndependentUAndVRanges():
    b1 = _bound(gp_Pnt(-3., 2., 5.), gp_Pnt(7., 2., 5.))
    b2 = _bound(gp_Pnt(7., 2., 5.), gp_Pnt(7., 6., 5.))
    b3 = _bound(gp_Pnt(-3., 6., 5.), gp_Pnt(7., 6., 5.))
    b4 = _bound(gp_Pnt(-3., 2., 5.), gp_Pnt(-3., 6., 5.))
    # Opposite boundaries share a range, while U and V have different, nonzero lower bounds.
    b1.Reparametrize(2., 5., False, False, 1., 1., False)
    b3.Reparametrize(2., 5., False, False, 1., 1., False)
    b2.Reparametrize(-3., -1., False, False, 1., 1., False)
    b4.Reparametrize(-3., -1., False, False, 1., 1., False)
    for bound, is_u in ((b1, True), (b2, False), (b3, True), (b4, False)):
        first, last = bound.Bounds()
        assert first == _eq(2. if is_u else -3.)
        assert last == _eq(5. if is_u else -1.)
    patch = GeomFill_CoonsAlgPatch(b1, b2, b3, b4)
    for u in (2., 2.9, 5.):
        for v in (-3., -1.6, -1.):
            expected = gp_Pnt(-3. + 10. * (u - 2.) / 3., 2. + 4. * (v + 3.) / 2., 5.)
            assert patch.Value(u, v).Distance(expected) == pytest.approx(0., abs=Precision.Confusion_s()), (u, v)


def test_GeomFill_CoonsAlgPatchTest_ValueAgreesWithPartialDerivatives():
    bounds = (_bound(gp_Pnt(0., 0., 0.), gp_Pnt(10., 0., 2.)), _bound(gp_Pnt(10., 0., 2.), gp_Pnt(10., 10., 0.)),
              _bound(gp_Pnt(0., 10., 1.), gp_Pnt(10., 10., 0.)), _bound(gp_Pnt(0., 0., 0.), gp_Pnt(0., 10., 1.)))
    for bound in bounds:
        bound.Reparametrize(0., 1., False, False, 1., 1., False)
        first, last = bound.Bounds()
        assert first == _eq(0.)
        assert last == _eq(1.)
    patch = GeomFill_CoonsAlgPatch(*bounds)
    # For straight boundaries the patch is bilinear: (10 U, 10 V, 2 U + V - 3 U V).
    # The step and derivative tolerance allow subtraction roundoff for coordinates near 10.
    step, dtol = 1.e-5, 1.e-7
    for u in (0.2, 0.3, 0.8):
        for v in (0.1, 0.7, 0.9):
            expected = gp_Pnt(10. * u, 10. * v, 2. * u + v - 3. * u * v)
            assert patch.Value(u, v).Distance(expected) == pytest.approx(0., abs=Precision.Confusion_s()), (u, v)
            num_u = (patch.Value(u + step, v).XYZ() - patch.Value(u - step, v).XYZ()) / (2. * step)
            num_v = (patch.Value(u, v + step).XYZ() - patch.Value(u, v - step).XYZ()) / (2. * step)
            d1u, d1v = patch.D1U(u, v), patch.D1V(u, v)
            assert (num_u - d1u.XYZ()).Modulus() == pytest.approx(0., abs=dtol), (u, v)
            assert (num_v - d1v.XYZ()).Modulus() == pytest.approx(0., abs=dtol), (u, v)
            assert (d1u - gp_Vec(10., 0., 2. - 3. * v)).Magnitude() == pytest.approx(0., abs=dtol), (u, v)
            assert (d1v - gp_Vec(0., 10., 1. - 3. * u)).Magnitude() == pytest.approx(0., abs=dtol), (u, v)
