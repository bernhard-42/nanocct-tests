# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_CompBezierCurvesToBSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Convert import Convert_CompBezierCurves2dToBSplineCurve2d, Convert_CompBezierCurvesToBSplineCurve
from nanocct.gp import gp_Pnt, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1


def _poles(pts):
    a = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, 1):
        a[i] = gp_Pnt(*p)
    return a


def _poles2d(pts):
    a = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, p in enumerate(pts, 1):
        a[i] = gp_Pnt2d(*p)
    return a


def test_Convert_CompBezierCurvesToBSplineCurveTest_SingleLinearBezier():
    conv = Convert_CompBezierCurvesToBSplineCurve()
    conv.AddCurve(_poles([(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)]))
    conv.Perform()
    assert conv.Degree() >= 1
    assert conv.NbPoles() == 2
    assert conv.NbKnots() == 2
    res = NCollection_Array1[gp_Pnt](1, conv.NbPoles())
    conv.Poles(res)
    assert abs(res[1].X() - 0.0) <= 1.0e-15
    assert abs(res[2].X() - 1.0) <= 1.0e-15


def test_Convert_CompBezierCurvesToBSplineCurveTest_SingleCubicBezier():
    conv = Convert_CompBezierCurvesToBSplineCurve()
    conv.AddCurve(_poles([(0.0, 0.0, 0.0), (1.0, 2.0, 0.0), (3.0, 2.0, 0.0), (4.0, 0.0, 0.0)]))
    conv.Perform()
    assert conv.Degree() == 3
    assert conv.NbPoles() == 4
    assert conv.NbKnots() == 2


def test_Convert_CompBezierCurvesToBSplineCurveTest_TwoAdjacentBeziers_C0():
    conv = Convert_CompBezierCurvesToBSplineCurve()
    conv.AddCurve(_poles([(0.0, 0.0, 0.0), (1.0, 1.0, 0.0)]))
    conv.AddCurve(_poles([(1.0, 1.0, 0.0), (2.0, 0.0, 0.0)]))
    conv.Perform()
    assert conv.Degree() >= 1
    assert conv.NbKnots() == 3
    res = NCollection_Array1[gp_Pnt](1, conv.NbPoles())
    knots = NCollection_Array1[float](1, conv.NbKnots())
    mults = NCollection_Array1[int](1, conv.NbKnots())
    conv.Poles(res)
    conv.KnotsAndMults(knots, mults)
    assert mults[1] == conv.Degree() + 1
    assert mults[conv.NbKnots()] == conv.Degree() + 1


def test_Convert_CompBezierCurvesToBSplineCurveTest_TwoAdjacentBeziers_C1():
    conv = Convert_CompBezierCurvesToBSplineCurve()
    conv.AddCurve(_poles([(0.0, 0.0, 0.0), (1.0, 1.0, 0.0), (2.0, 1.0, 0.0), (3.0, 0.0, 0.0)]))
    conv.AddCurve(_poles([(3.0, 0.0, 0.0), (4.0, -1.0, 0.0), (5.0, -1.0, 0.0), (6.0, 0.0, 0.0)]))
    conv.Perform()
    assert conv.Degree() == 3
    assert conv.NbKnots() == 3
    mults = NCollection_Array1[int](1, conv.NbKnots())
    knots = NCollection_Array1[float](1, conv.NbKnots())
    conv.KnotsAndMults(knots, mults)
    assert mults[2] == conv.Degree() - 1


def test_Convert_CompBezierCurvesToBSplineCurveTest_MixedDegreeBeziers():
    conv = Convert_CompBezierCurvesToBSplineCurve()
    conv.AddCurve(_poles([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]))
    conv.AddCurve(_poles([(1.0, 0.0, 0.0), (2.0, 1.0, 0.0), (3.0, 1.0, 0.0), (4.0, 0.0, 0.0)]))
    conv.Perform()
    assert conv.Degree() == 3


def test_Convert_CompBezierCurves2dToBSplineCurve2dTest_SingleLinear2d():
    conv = Convert_CompBezierCurves2dToBSplineCurve2d()
    conv.AddCurve(_poles2d([(0.0, 0.0), (1.0, 1.0)]))
    conv.Perform()
    assert conv.Degree() >= 1
    assert conv.NbPoles() == 2
    assert conv.NbKnots() == 2
    res = NCollection_Array1[gp_Pnt2d](1, conv.NbPoles())
    conv.Poles(res)
    assert abs(res[1].X() - 0.0) <= 1.0e-15
    assert abs(res[2].X() - 1.0) <= 1.0e-15


def test_Convert_CompBezierCurves2dToBSplineCurve2dTest_TwoAdjacent2d_C1():
    conv = Convert_CompBezierCurves2dToBSplineCurve2d()
    conv.AddCurve(_poles2d([(0.0, 0.0), (1.0, 1.0), (2.0, 1.0), (3.0, 0.0)]))
    conv.AddCurve(_poles2d([(3.0, 0.0), (4.0, -1.0), (5.0, -1.0), (6.0, 0.0)]))
    conv.Perform()
    assert conv.Degree() == 3
    assert conv.NbKnots() == 3
    mults = NCollection_Array1[int](1, conv.NbKnots())
    knots = NCollection_Array1[float](1, conv.NbKnots())
    conv.KnotsAndMults(knots, mults)
    assert mults[2] == conv.Degree() - 1
