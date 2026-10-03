# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomHash_SurfaceHasher_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import (
    Geom_BezierSurface,
    Geom_BSplineSurface,
    Geom_Circle,
    Geom_ConicalSurface,
    Geom_CylindricalSurface,
    Geom_Line,
    Geom_OffsetSurface,
    Geom_Plane,
    Geom_RectangularTrimmedSurface,
    Geom_SphericalSurface,
    Geom_SurfaceOfLinearExtrusion,
    Geom_SurfaceOfRevolution,
    Geom_ToroidalSurface,
)
from nanocct.GeomHash import GeomHash_SurfaceHasher
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Ax3, gp_Dir, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2


def _ax3(p=(0.0, 0.0, 0.0), d=(0.0, 0.0, 1.0)):
    return gp_Ax3(gp_Pnt(*p), gp_Dir(*d))


def _reals(*vals):
    arr = NCollection_Array1[float](1, len(vals))
    for i, v in enumerate(vals, start=1):
        arr[i] = float(v)
    return arr


def _ints(*vals):
    arr = NCollection_Array1[int](1, len(vals))
    for i, v in enumerate(vals, start=1):
        arr[i] = v
    return arr


def _poles22(z22=1.0):
    a = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    a[1, 1] = gp_Pnt(0.0, 0.0, 0.0)
    a[1, 2] = gp_Pnt(1.0, 0.0, 0.0)
    a[2, 1] = gp_Pnt(0.0, 1.0, 0.0)
    a[2, 2] = gp_Pnt(1.0, 1.0, z22)
    return a


def _weights22(w22):
    w = NCollection_Array2[float](1, 2, 1, 2)
    w[1, 1] = 1.0
    w[1, 2] = 1.0
    w[2, 1] = 1.0
    w[2, 2] = w22
    return w


def _assert_same(h, a, b):
    assert h(a) == h(b)
    assert h(a, b)


def _assert_diff(h, a, b):
    assert h(a) != h(b)
    assert not h(a, b)


def test_GeomHash_SurfaceHasherTest_Plane_CopiedPlanes_SameHash():
    h = GeomHash_SurfaceHasher()
    p1 = Geom_Plane(_ax3())
    _assert_same(h, p1, p1.Copy())


def test_GeomHash_SurfaceHasherTest_Plane_DifferentPlanes_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(h, Geom_Plane(_ax3()), Geom_Plane(_ax3(p=(0.0, 0.0, 1.0))))


def test_GeomHash_SurfaceHasherTest_CylindricalSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    c1 = Geom_CylindricalSurface(_ax3(), 5.0)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_SurfaceHasherTest_CylindricalSurface_DifferentRadius_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(h, Geom_CylindricalSurface(_ax3(), 5.0), Geom_CylindricalSurface(_ax3(), 10.0))


def test_GeomHash_SurfaceHasherTest_ConicalSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    c1 = Geom_ConicalSurface(_ax3(), math.pi / 6.0, 5.0)
    _assert_same(h, c1, c1.Copy())


def test_GeomHash_SurfaceHasherTest_ConicalSurface_DifferentAngle_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(
        h, Geom_ConicalSurface(_ax3(), math.pi / 6.0, 5.0), Geom_ConicalSurface(_ax3(), math.pi / 4.0, 5.0)
    )


def test_GeomHash_SurfaceHasherTest_SphericalSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_SphericalSurface(_ax3(), 5.0)
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_SphericalSurface_DifferentRadius_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(h, Geom_SphericalSurface(_ax3(), 5.0), Geom_SphericalSurface(_ax3(), 10.0))


def test_GeomHash_SurfaceHasherTest_ToroidalSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    t1 = Geom_ToroidalSurface(_ax3(), 10.0, 3.0)
    _assert_same(h, t1, t1.Copy())


def test_GeomHash_SurfaceHasherTest_ToroidalSurface_DifferentRadii_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(h, Geom_ToroidalSurface(_ax3(), 10.0, 3.0), Geom_ToroidalSurface(_ax3(), 10.0, 5.0))


def test_GeomHash_SurfaceHasherTest_BezierSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BezierSurface(_poles22())
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_BezierSurface_DifferentPoles_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    assert not h(Geom_BezierSurface(_poles22(1.0)), Geom_BezierSurface(_poles22(2.0)))


def test_GeomHash_SurfaceHasherTest_BSplineSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BSplineSurface(_poles22(), _reals(0.0, 1.0), _reals(0.0, 1.0), _ints(2, 2), _ints(2, 2), 1, 1)
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_SurfaceOfRevolution_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    line = Geom_Line(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    r1 = Geom_SurfaceOfRevolution(line, gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    _assert_same(h, r1, r1.Copy())


def test_GeomHash_SurfaceHasherTest_SurfaceOfLinearExtrusion_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    e1 = Geom_SurfaceOfLinearExtrusion(line, gp_Dir(0.0, 0.0, 1.0))
    _assert_same(h, e1, e1.Copy())


def test_GeomHash_SurfaceHasherTest_RectangularTrimmedSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    t1 = Geom_RectangularTrimmedSurface(Geom_Plane(_ax3()), 0.0, 10.0, 0.0, 10.0)
    _assert_same(h, t1, t1.Copy())


def test_GeomHash_SurfaceHasherTest_RectangularTrimmedSurface_DifferentBounds_DifferentHash():
    h = GeomHash_SurfaceHasher()
    plane = Geom_Plane(_ax3())
    _assert_diff(
        h,
        Geom_RectangularTrimmedSurface(plane, 0.0, 10.0, 0.0, 10.0),
        Geom_RectangularTrimmedSurface(plane, 0.0, 20.0, 0.0, 10.0),
    )


def test_GeomHash_SurfaceHasherTest_OffsetSurface_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    o1 = Geom_OffsetSurface(Geom_Plane(_ax3()), 5.0)
    _assert_same(h, o1, o1.Copy())


def test_GeomHash_SurfaceHasherTest_OffsetSurface_DifferentOffset_DifferentHash():
    h = GeomHash_SurfaceHasher()
    plane = Geom_Plane(_ax3())
    _assert_diff(h, Geom_OffsetSurface(plane, 5.0), Geom_OffsetSurface(plane, 10.0))


def test_GeomHash_SurfaceHasherTest_DifferentTypes_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    assert not h(Geom_Plane(_ax3()), Geom_SphericalSurface(_ax3(), 5.0))


def test_GeomHash_SurfaceHasherTest_NullSurfaces_HandledCorrectly():
    h = GeomHash_SurfaceHasher()
    plane = Geom_Plane(_ax3())
    assert h(None) == 0
    assert h(None, None)
    assert not h(plane, None)


def test_GeomHash_SurfaceHasherTest_SameObject_Equal():
    h = GeomHash_SurfaceHasher()
    plane = Geom_Plane(_ax3())
    assert h(plane, plane)


def test_GeomHash_SurfaceHasherTest_BSplineSurface_Weighted_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BSplineSurface(
        _poles22(), _weights22(2.0), _reals(0.0, 1.0), _reals(0.0, 1.0), _ints(2, 2), _ints(2, 2), 1, 1
    )
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_BSplineSurface_DifferentWeights_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BSplineSurface(
        _poles22(), _weights22(2.0), _reals(0.0, 1.0), _reals(0.0, 1.0), _ints(2, 2), _ints(2, 2), 1, 1
    )
    s2 = Geom_BSplineSurface(
        _poles22(), _weights22(3.0), _reals(0.0, 1.0), _reals(0.0, 1.0), _ints(2, 2), _ints(2, 2), 1, 1
    )
    assert not h(s1, s2)


def test_GeomHash_SurfaceHasherTest_BezierSurface_Weighted_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BezierSurface(_poles22(), _weights22(2.0))
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_Plane_DifferentNormal_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(h, Geom_Plane(_ax3()), Geom_Plane(_ax3(d=(0.0, 1.0, 0.0))))


def test_GeomHash_SurfaceHasherTest_CylindricalSurface_DifferentAxis_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(
        h, Geom_CylindricalSurface(_ax3(), 5.0), Geom_CylindricalSurface(_ax3(d=(1.0, 0.0, 0.0)), 5.0)
    )


def test_GeomHash_SurfaceHasherTest_SurfaceOfRevolution_DifferentBasisCurve_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    axis = gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    l1 = Geom_Line(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    l2 = Geom_Line(gp_Pnt(2.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    assert not h(Geom_SurfaceOfRevolution(l1, axis), Geom_SurfaceOfRevolution(l2, axis))


def test_GeomHash_SurfaceHasherTest_SurfaceOfLinearExtrusion_DifferentDirection_DifferentHash():
    h = GeomHash_SurfaceHasher()
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    _assert_diff(
        h,
        Geom_SurfaceOfLinearExtrusion(line, gp_Dir(0.0, 0.0, 1.0)),
        Geom_SurfaceOfLinearExtrusion(line, gp_Dir(0.0, 1.0, 0.0)),
    )


def test_GeomHash_SurfaceHasherTest_BSplineSurface_DifferentKnots_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BSplineSurface(_poles22(), _reals(0.0, 1.0), _reals(0.0, 1.0), _ints(2, 2), _ints(2, 2), 1, 1)
    s2 = Geom_BSplineSurface(_poles22(), _reals(0.0, 2.0), _reals(0.0, 1.0), _ints(2, 2), _ints(2, 2), 1, 1)
    assert not h(s1, s2)


def test_GeomHash_SurfaceHasherTest_Plane_Translated_DifferentHash():
    h = GeomHash_SurfaceHasher()
    p1 = Geom_Plane(_ax3())
    p2 = p1.Copy()
    p2.Translate(gp_Vec(0.0, 0.0, 1.0))
    _assert_diff(h, p1, p2)


def test_GeomHash_SurfaceHasherTest_Sphere_Scaled_DifferentHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_SphericalSurface(_ax3(), 5.0)
    s2 = s1.Copy()
    s2.Scale(gp_Pnt(0.0, 0.0, 0.0), 2.0)
    _assert_diff(h, s1, s2)


def test_GeomHash_SurfaceHasherTest_BezierSurface_UReversed_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BezierSurface(_poles22())
    assert not h(s1, s1.UReversed())


def test_GeomHash_SurfaceHasherTest_BezierSurface_VReversed_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_BezierSurface(_poles22())
    assert not h(s1, s1.VReversed())


def test_GeomHash_SurfaceHasherTest_BSplineSurface_HigherDegree_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    poles = NCollection_Array2[gp_Pnt](1, 4, 1, 4)
    for i in range(1, 5):
        for j in range(1, 5):
            poles[i, j] = gp_Pnt((i - 1) * 1.0, (j - 1) * 1.0, (i + j) * 0.1)
    s1 = Geom_BSplineSurface(poles, _reals(0.0, 1.0), _reals(0.0, 1.0), _ints(4, 4), _ints(4, 4), 3, 3)
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_Cylinder_vs_Cone_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    assert not h(Geom_CylindricalSurface(_ax3(), 5.0), Geom_ConicalSurface(_ax3(), math.pi / 6.0, 5.0))


def test_GeomHash_SurfaceHasherTest_Sphere_vs_Torus_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    assert not h(Geom_SphericalSurface(_ax3(), 5.0), Geom_ToroidalSurface(_ax3(), 5.0, 1.0))


def test_GeomHash_SurfaceHasherTest_RectangularTrimmedSurface_vs_BaseSurface_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    plane = Geom_Plane(_ax3())
    assert not h(plane, Geom_RectangularTrimmedSurface(plane, 0.0, 10.0, 0.0, 10.0))


def test_GeomHash_SurfaceHasherTest_Sphere_VerySmallRadius_CopiedSpheres_SameHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_SphericalSurface(_ax3(), 1e-10)
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_Sphere_VeryLargeRadius_CopiedSpheres_SameHash():
    h = GeomHash_SurfaceHasher()
    s1 = Geom_SphericalSurface(_ax3(), 1e10)
    _assert_same(h, s1, s1.Copy())


def test_GeomHash_SurfaceHasherTest_Plane_AtOrigin_vs_FarFromOrigin_DifferentHash():
    h = GeomHash_SurfaceHasher()
    _assert_diff(h, Geom_Plane(_ax3()), Geom_Plane(_ax3(p=(1e10, 1e10, 1e10))))


def test_GeomHash_SurfaceHasherTest_SurfaceOfRevolution_CircleBasis_CopiedSurfaces_SameHash():
    h = GeomHash_SurfaceHasher()
    circle = Geom_Circle(gp_Ax2(gp_Pnt(5.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0)), 1.0)
    r1 = Geom_SurfaceOfRevolution(circle, gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    _assert_same(h, r1, r1.Copy())


def test_GeomHash_SurfaceHasherTest_OffsetSurface_DifferentBaseSurface_DifferentComparison():
    h = GeomHash_SurfaceHasher()
    o1 = Geom_OffsetSurface(Geom_Plane(_ax3()), 5.0)
    o2 = Geom_OffsetSurface(Geom_Plane(_ax3(p=(1.0, 0.0, 0.0))), 5.0)
    assert not h(o1, o2)
