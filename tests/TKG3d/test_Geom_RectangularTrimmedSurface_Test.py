# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_RectangularTrimmedSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: SingleDirectionTrimInitializesState constructs the surface by placement new into storage filled with
# ones, so that uninitialized trim flags would show (raw memory); the bounds and the evaluation it then checks are.
import pytest

from nanocct.Geom import Geom_CylindricalSurface, Geom_OffsetSurface, Geom_RectangularTrimmedSurface
from nanocct.gp import gp_Ax3


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def test_Geom_RectangularTrimmedSurface_SingleDirectionTrimInitializesState():
    cylinder = Geom_CylindricalSurface(gp_Ax3(), 5.0)
    for is_offset in (False, True):
        basis = Geom_OffsetSurface(cylinder, 1.0) if is_offset else cylinder
        for is_u_trim in (False, True):
            where = (is_offset, is_u_trim)
            trim = Geom_RectangularTrimmedSurface(basis, 0.5, 1.5, is_u_trim, True)
            u1, u2, v1, v2 = trim.Bounds()
            bu1, bu2, bv1, bv2 = basis.Bounds()
            assert u1 == _eq(0.5 if is_u_trim else bu1), where
            assert u2 == _eq(1.5 if is_u_trim else bu2), where
            assert v1 == _eq(bv1 if is_u_trim else 0.5), where
            assert v2 == _eq(bv2 if is_u_trim else 1.5), where
            assert trim.EvalD0(1.0, 1.0).Distance(basis.EvalD0(1.0, 1.0)) == pytest.approx(0.0, abs=1e-12), where


def test_Geom_RectangularTrimmedSurface_ComplementaryTrimAndCopyPreserveBounds():
    cylinder = Geom_CylindricalSurface(gp_Ax3(), 5.0)
    for is_u_trim in (False, True):
        first = Geom_RectangularTrimmedSurface(cylinder, 0.5, 1.5, is_u_trim, True)
        copy = first.Copy()
        assert isinstance(copy, Geom_RectangularTrimmedSurface)
        copy.SetTrim(2.0, 3.0, not is_u_trim, True)
        nested = Geom_RectangularTrimmedSurface(first, 2.0, 3.0, not is_u_trim, True)
        for trim in (copy, nested):
            u1, u2, v1, v2 = trim.Bounds()
            assert u1 == _eq(0.5 if is_u_trim else 2.0), is_u_trim
            assert u2 == _eq(1.5 if is_u_trim else 3.0), is_u_trim
            assert v1 == _eq(2.0 if is_u_trim else 0.5), is_u_trim
            assert v2 == _eq(3.0 if is_u_trim else 1.5), is_u_trim
