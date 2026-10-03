# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_OffsetSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import (
    Geom_ConicalSurface,
    Geom_CylindricalSurface,
    Geom_OffsetSurface,
    Geom_Plane,
    Geom_RectangularTrimmedSurface,
    Geom_SphericalSurface,
    Geom_ToroidalSurface,
)
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pln, gp_Pnt, gp_Vec
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()
ATOL = 1e-10
PI = math.pi


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


def frange(start, stop, step, inclusive):
    # mirrors the C++ `for (double x = start; x <= / < stop; x += step)` accumulation
    x = start
    while (x <= stop) if inclusive else (x < stop):
        yield x
        x += step


def vec_eq(v1, v2, tol=ATOL):
    return (v1 - v2).Magnitude() < tol


def z_ax3(x=0.0, y=0.0, z=0.0):
    return gp_Ax3(gp_Pnt(x, y, z), gp_Dir(0, 0, 1))


@pytest.fixture
def original():
    plane = Geom_Plane(gp_Pln(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))))
    return Geom_OffsetSurface(plane, 3.0)


# --- evaluation helpers --------------------------------------------------------------------------


def ad_d0(a, u, v):
    p = gp_Pnt()
    a.D0(u, v, p)
    return p


def d1(s, u, v):
    p, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
    s.D1(u, v, p, du, dv)
    return p, du, dv


def d2(s, u, v):
    p = gp_Pnt()
    vs = [gp_Vec() for _ in range(5)]
    s.D2(u, v, p, *vs)
    return (p, *vs)  # P, D1U, D1V, D2U, D2V, D2UV


def d3(s, u, v):
    p = gp_Pnt()
    vs = [gp_Vec() for _ in range(9)]
    s.D3(u, v, p, *vs)
    return (p, *vs)  # P, D1U, D1V, D2U, D2V, D2UV, D3U, D3V, D3UUV, D3UVV


def adaptors(off):
    equiv = off.Surface()
    assert equiv is not None
    return GeomAdaptor_Surface(off), GeomAdaptor_Surface(equiv)


def check_adaptor_consistency(a1, a2, u, v, orders):
    where = f"u={u}, v={v}"
    if 0 in orders:
        assert ad_d0(a1, u, v).IsEqual(ad_d0(a2, u, v), ATOL), f"D0 {where}"
    if 1 in orders:
        r1, r2 = d1(a1, u, v), d1(a2, u, v)
        assert r1[0].IsEqual(r2[0], ATOL), f"D1 point {where}"
        assert vec_eq(r1[1], r2[1]), f"D1U {where}"
        assert vec_eq(r1[2], r2[2]), f"D1V {where}"
    if 2 in orders:
        r1, r2 = d2(a1, u, v), d2(a2, u, v)
        assert r1[0].IsEqual(r2[0], ATOL), f"D2 point {where}"
        for i, n in ((3, "D2U"), (4, "D2V"), (5, "D2UV")):
            assert vec_eq(r1[i], r2[i]), f"{n} {where}"
    if 3 in orders:
        r1, r2 = d3(a1, u, v), d3(a2, u, v)
        assert r1[0].IsEqual(r2[0], ATOL), f"D3 point {where}"
        for i, n in ((6, "D3U"), (7, "D3V"), (8, "D3UUV"), (9, "D3UVV")):
            assert vec_eq(r1[i], r2[i]), f"{n} {where}"


# --- copy tests ----------------------------------------------------------------------------------


def test_Geom_OffsetSurface_Test_CopyConstructorBasicProperties(original):
    copy = Geom_OffsetSurface(original)
    deq(original.Offset(), copy.Offset())
    assert original.IsUPeriodic() == copy.IsUPeriodic()
    assert original.IsVPeriodic() == copy.IsVPeriodic()
    assert original.IsUClosed() == copy.IsUClosed()
    assert original.IsVClosed() == copy.IsVClosed()


def test_Geom_OffsetSurface_Test_CopyConstructorBasisSurface(original):
    copy = Geom_OffsetSurface(original)
    orig_basis = original.BasisSurface()
    copy_basis = copy.BasisSurface()
    assert orig_basis is not copy_basis
    b1 = orig_basis.Bounds()
    b2 = copy_basis.Bounds()
    for x, y in zip(b1, b2):
        deq(x, y)


def test_Geom_OffsetSurface_Test_CopyMethodUsesOptimizedConstructor(original):
    copy = original.Copy()
    assert isinstance(copy, Geom_OffsetSurface)
    deq(original.Offset(), copy.Offset())
    for u in frange(-5.0, 5.0, 2.5, True):
        for v in frange(-5.0, 5.0, 2.5, True):
            assert original.Value(u, v).IsEqual(copy.Value(u, v), 1e-10)


def test_Geom_OffsetSurface_Test_CopyIndependence(original):
    copy = Geom_OffsetSurface(original)
    orig_offset = copy.Offset()
    original.SetOffsetValue(15.0)
    deq(copy.Offset(), orig_offset)
    assert copy.Offset() != original.Offset()


# --- equivalent surface --------------------------------------------------------------------------


def test_Geom_OffsetSurface_EquivalentSurface_Plane_ReturnsTranslatedPlane():
    plane = Geom_Plane(z_ax3(1.0, 2.0, 3.0))
    off = Geom_OffsetSurface(plane, 5.0)
    equiv = off.Surface()
    assert isinstance(equiv, Geom_Plane)
    o, e = plane.Location(), equiv.Location()
    assert abs(e.Z() - o.Z() - 5.0) <= TOL
    assert abs(e.X() - o.X()) <= TOL
    assert abs(e.Y() - o.Y()) <= TOL


def _check_cylinder_equiv(radius, offset, expected):
    off = Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), radius), offset)
    equiv = off.Surface()
    assert isinstance(equiv, Geom_CylindricalSurface)
    assert abs(equiv.Radius() - expected) <= TOL


def test_Geom_OffsetSurface_EquivalentSurface_Cylinder_PositiveOffset_ReturnsLargerCylinder():
    _check_cylinder_equiv(10.0, 3.0, 13.0)


def test_Geom_OffsetSurface_EquivalentSurface_Cylinder_NegativeOffset_ReturnsSmallerCylinder():
    _check_cylinder_equiv(10.0, -3.0, 7.0)


def test_Geom_OffsetSurface_EquivalentSurface_Cylinder_NegativeRadiusFlip_ReturnsFlippedCylinder():
    _check_cylinder_equiv(5.0, -8.0, 3.0)


def test_Geom_OffsetSurface_EquivalentSurface_Sphere_PositiveOffset_ReturnsLargerSphere():
    sphere = Geom_SphericalSurface(z_ax3(1, 2, 3), 10.0)
    equiv = Geom_OffsetSurface(sphere, 5.0).Surface()
    assert isinstance(equiv, Geom_SphericalSurface)
    assert abs(equiv.Radius() - 15.0) <= TOL
    assert equiv.Location().IsEqual(sphere.Location(), TOL)


def test_Geom_OffsetSurface_EquivalentSurface_Sphere_NegativeRadiusFlip_ReturnsFlippedSphere():
    equiv = Geom_OffsetSurface(Geom_SphericalSurface(z_ax3(), 5.0), -8.0).Surface()
    assert isinstance(equiv, Geom_SphericalSurface)
    assert abs(equiv.Radius() - 3.0) <= TOL


def test_Geom_OffsetSurface_EquivalentSurface_Cone_PositiveOffset_ReturnsOffsetCone():
    semi, ref = PI / 6.0, 10.0
    equiv = Geom_OffsetSurface(Geom_ConicalSurface(z_ax3(), semi, ref), 2.0).Surface()
    assert isinstance(equiv, Geom_ConicalSurface)
    assert abs(equiv.SemiAngle() - semi) <= TOL
    assert abs(equiv.RefRadius() - (ref + 2.0 * math.cos(semi))) <= TOL


def _check_torus_equiv(minor, offset, expected_minor):
    equiv = Geom_OffsetSurface(Geom_ToroidalSurface(z_ax3(), 20.0, minor), offset).Surface()
    assert isinstance(equiv, Geom_ToroidalSurface)
    assert abs(equiv.MajorRadius() - 20.0) <= TOL
    assert abs(equiv.MinorRadius() - expected_minor) <= TOL


def test_Geom_OffsetSurface_EquivalentSurface_Torus_PositiveOffset_ReturnsLargerTorus():
    _check_torus_equiv(5.0, 2.0, 7.0)


def test_Geom_OffsetSurface_EquivalentSurface_Torus_NegativeOffset_ReturnsSmallerTorus():
    _check_torus_equiv(5.0, -2.0, 3.0)


def test_Geom_OffsetSurface_EquivalentSurface_Torus_NegativeMinorRadiusFlip_ReturnsFlippedTorus():
    _check_torus_equiv(3.0, -5.0, 2.0)


def test_Geom_OffsetSurface_EquivalentSurface_ZeroOffset_ReturnsBasisSurface():
    off = Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), 0.0)
    equiv = off.Surface()
    assert equiv is not None
    assert equiv is off.BasisSurface()
    assert isinstance(equiv, Geom_CylindricalSurface)
    assert abs(equiv.Radius() - 10.0) <= TOL


def test_Geom_OffsetSurface_EquivalentSurface_TrimmedPlane_ReturnsTrimmedTranslatedPlane():
    trimmed = Geom_RectangularTrimmedSurface(Geom_Plane(z_ax3()), 0.0, 10.0, 0.0, 5.0)
    equiv = Geom_OffsetSurface(trimmed, 3.0).Surface()
    assert isinstance(equiv, Geom_RectangularTrimmedSurface)
    u1, u2, v1, v2 = equiv.Bounds()
    assert abs(u1 - 0.0) <= TOL
    assert abs(u2 - 10.0) <= TOL
    assert abs(v1 - 0.0) <= TOL
    assert abs(v2 - 5.0) <= TOL


def test_Geom_OffsetSurface_EquivalentSurface_DegenerateCylinder_ReturnsNull():
    off = Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 1.0), -1.0 + 0.5 * TOL)
    assert off.Surface() is None


def test_Geom_OffsetSurface_EquivalentSurface_EquivalentSurface_EvaluationConsistency():
    off = Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), 3.0)
    equiv = off.Surface()
    assert equiv is not None
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(-5.0, 5.0, 2.5, True):
            assert off.Value(u, v).IsEqual(equiv.Value(u, v), TOL), f"u={u}, v={v}"


# --- derivatives: offset adaptor vs equivalent adaptor ------------------------------------------


def test_Geom_OffsetSurface_Derivatives_Plane_D0D1D2D3_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_Plane(z_ax3(1.0, 2.0, 3.0)), 5.0))
    for u in frange(-5.0, 5.0, 2.5, True):
        for v in frange(-5.0, 5.0, 2.5, True):
            check_adaptor_consistency(a1, a2, u, v, {0, 1, 2})


def test_Geom_OffsetSurface_Derivatives_Cylinder_D0D1D2D3_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), 3.0))
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(-5.0, 5.0, 2.5, True):
            check_adaptor_consistency(a1, a2, u, v, {0, 1, 2, 3})


def test_Geom_OffsetSurface_Derivatives_Sphere_D0D1D2D3_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_SphericalSurface(z_ax3(1, 2, 3), 10.0), 5.0))
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(-PI / 3.0, PI / 3.0, PI / 6.0, True):
            check_adaptor_consistency(a1, a2, u, v, {0, 1, 2})


def test_Geom_OffsetSurface_Derivatives_Cone_D0D1D2_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_ConicalSurface(z_ax3(), PI / 6.0, 10.0), 2.0))
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(1.0, 10.0, 3.0, True):
            check_adaptor_consistency(a1, a2, u, v, {0, 1, 2})


def test_Geom_OffsetSurface_Derivatives_Torus_D0D1D2D3_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_ToroidalSurface(z_ax3(), 20.0, 5.0), 2.0))
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(0.0, 2.0 * PI, PI / 4.0, False):
            check_adaptor_consistency(a1, a2, u, v, {0, 1, 2, 3})


def test_Geom_OffsetSurface_Derivatives_Cylinder_DN_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), 3.0))
    u, v = PI / 3.0, 2.5
    for nu in range(4):
        for nv in range(4):
            if nu + nv == 0 or nu + nv > 3:
                continue
            assert vec_eq(a1.DN(u, v, nu, nv), a2.DN(u, v, nu, nv)), f"Nu={nu}, Nv={nv}"


def test_Geom_OffsetSurface_Derivatives_NegativeOffset_Cylinder_D0D1D2_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), -3.0))
    for u in frange(0.0, 2.0 * PI, PI / 3.0, False):
        for v in frange(-3.0, 3.0, 2.0, True):
            check_adaptor_consistency(a1, a2, u, v, {1})


def test_Geom_OffsetSurface_Derivatives_FlippedCylinder_D0D1_Consistency():
    a1, a2 = adaptors(Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 5.0), -8.0))
    for u in frange(0.0, 2.0 * PI, PI / 3.0, False):
        for v in frange(-3.0, 3.0, 2.0, True):
            check_adaptor_consistency(a1, a2, u, v, {1})


# --- three-way: direct surface vs offset adaptor vs equivalent adaptor ---------------------------


def check_three_way(off, a1, a2, u, v, orders):
    where = f"u={u}, v={v}"
    if 0 in orders:
        direct = off.Value(u, v)
        p1, p2 = ad_d0(a1, u, v), ad_d0(a2, u, v)
        assert direct.IsEqual(p1, ATOL), f"D0 direct/offset {where}"
        assert direct.IsEqual(p2, ATOL), f"D0 direct/equiv {where}"
    if 1 in orders:
        rd, r1, r2 = d1(off, u, v), d1(a1, u, v), d1(a2, u, v)
        for i, n in ((1, "D1U"), (2, "D1V")):
            assert vec_eq(rd[i], r1[i]), f"{n} direct/offset {where}"
            assert vec_eq(rd[i], r2[i]), f"{n} direct/equiv {where}"
    if 2 in orders:
        rd, r1, r2 = d2(off, u, v), d2(a1, u, v), d2(a2, u, v)
        for i, n in ((3, "D2U"), (4, "D2V"), (5, "D2UV")):
            assert vec_eq(rd[i], r1[i]), f"{n} direct/offset {where}"
            assert vec_eq(rd[i], r2[i]), f"{n} direct/equiv {where}"


def test_Geom_OffsetSurface_ThreeWay_Cylinder_D0_ThreeWayConsistency():
    off = Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), 3.0)
    a1, a2 = adaptors(off)
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(-5.0, 5.0, 2.5, True):
            check_three_way(off, a1, a2, u, v, {0})
            assert ad_d0(a1, u, v).IsEqual(ad_d0(a2, u, v), ATOL)


def test_Geom_OffsetSurface_ThreeWay_Cylinder_D1_ThreeWayConsistency():
    off = Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), 3.0)
    a1, a2 = adaptors(off)
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(-5.0, 5.0, 2.5, True):
            rd, r1, r2 = d1(off, u, v), d1(a1, u, v), d1(a2, u, v)
            assert rd[0].IsEqual(r1[0], ATOL)
            assert rd[0].IsEqual(r2[0], ATOL)
            check_three_way(off, a1, a2, u, v, {1})


def test_Geom_OffsetSurface_ThreeWay_Cylinder_D2_ThreeWayConsistency():
    off = Geom_OffsetSurface(Geom_CylindricalSurface(z_ax3(), 10.0), 3.0)
    a1, a2 = adaptors(off)
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(-5.0, 5.0, 2.5, True):
            check_three_way(off, a1, a2, u, v, {2})


def test_Geom_OffsetSurface_ThreeWay_Sphere_D0D1D2_ThreeWayConsistency():
    off = Geom_OffsetSurface(Geom_SphericalSurface(z_ax3(1, 2, 3), 10.0), 5.0)
    a1, a2 = adaptors(off)
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(-PI / 3.0, PI / 3.0, PI / 6.0, True):
            check_three_way(off, a1, a2, u, v, {0, 1})


def test_Geom_OffsetSurface_ThreeWay_Plane_D0D1D2_ThreeWayConsistency():
    off = Geom_OffsetSurface(Geom_Plane(z_ax3(1.0, 2.0, 3.0)), 5.0)
    a1, a2 = adaptors(off)
    for u in frange(-5.0, 5.0, 2.5, True):
        for v in frange(-5.0, 5.0, 2.5, True):
            check_three_way(off, a1, a2, u, v, {0, 1})
            rd, r1, r2 = d2(off, u, v), d2(a1, u, v), d2(a2, u, v)
            for i in (3, 4):  # D2U, D2V (the C++ test does not check D2UV here)
                assert vec_eq(rd[i], r1[i])
                assert vec_eq(rd[i], r2[i])


def test_Geom_OffsetSurface_ThreeWay_Torus_D0D1D2_ThreeWayConsistency():
    off = Geom_OffsetSurface(Geom_ToroidalSurface(z_ax3(), 20.0, 5.0), 2.0)
    a1, a2 = adaptors(off)
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(0.0, 2.0 * PI, PI / 4.0, False):
            check_three_way(off, a1, a2, u, v, {0, 1})


def test_Geom_OffsetSurface_ThreeWay_Cone_D0D1_ThreeWayConsistency():
    off = Geom_OffsetSurface(Geom_ConicalSurface(z_ax3(), PI / 6.0, 10.0), 2.0)
    a1, a2 = adaptors(off)
    for u in frange(0.0, 2.0 * PI, PI / 4.0, False):
        for v in frange(1.0, 10.0, 3.0, True):
            check_three_way(off, a1, a2, u, v, {0, 1})
