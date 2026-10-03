# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Geom2dAPI_Interpolate_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom2dAPI import Geom2dAPI_Interpolate
from nanocct.gp import gp_Pnt2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1, NCollection_HArray1
from nanocct.Precision import Precision


def test_Geom2dAPI_InterpolateTest_OCC28594_InterpolateWithAndWithoutTangentScale():
    pts = [gp_Pnt2d(-30.4, 8), gp_Pnt2d(-16.689912, 17.498217), gp_Pnt2d(-23.803064, 24.748543),
           gp_Pnt2d(-16.907466, 32.919615), gp_Pnt2d(-8.543829, 26.549421), gp_Pnt2d(0, 39.200000)]
    points = NCollection_HArray1[gp_Pnt2d](1, 6)
    for i, p in enumerate(pts, 1):
        points.SetValue(i, p)

    tangents = NCollection_Array1[gp_Vec2d](1, 6)
    for i, v in enumerate([gp_Vec2d(0.3, 0.4), gp_Vec2d(0, 0), gp_Vec2d(0, 0), gp_Vec2d(0, 0),
                           gp_Vec2d(0, 0), gp_Vec2d(1, 0)], 1):
        tangents.SetValue(i, v)

    flags = NCollection_HArray1[bool](1, 6)
    for i, f in enumerate([True, False, False, False, False, True], 1):
        flags.SetValue(i, f)

    with_scale = Geom2dAPI_Interpolate(points, False, Precision.Confusion_s())
    with_scale.Load(tangents, flags)
    with_scale.Perform()
    assert with_scale.IsDone()
    curve_with = with_scale.Curve()
    assert curve_with is not None

    without_scale = Geom2dAPI_Interpolate(points, False, Precision.Confusion_s())
    without_scale.Load(tangents, flags, False)
    without_scale.Perform()
    assert without_scale.IsDone()
    assert without_scale.Curve() is not None

    tol = Precision.Confusion_s() * 10
    for idx in range(1, points.Length() + 1):
        on = curve_with.EvalD0(curve_with.Knot(idx))
        p = pts[idx - 1]
        assert abs(p.X() - on.X()) <= tol
        assert abs(p.Y() - on.Y()) <= tol
