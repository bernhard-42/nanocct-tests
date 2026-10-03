# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomConvert_CompCurveToBSplineCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_BSplineCurve, Geom_Circle, Geom_TrimmedCurve
from nanocct.GeomConvert import GeomConvert_CompCurveToBSplineCurve
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _arr(typ, values):
    a = NCollection_Array1[typ](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


def _bspline(pts, knots=(0.0, 1.0), mults=(4, 4)):
    poles = _arr(gp_Pnt, [p if isinstance(p, gp_Pnt) else gp_Pnt(*p) for p in pts])
    return Geom_BSplineCurve(poles, _arr(float, list(knots)), _arr(int, list(mults)), 3)


def _dist(p, xyz):
    return p.Distance(gp_Pnt(*xyz))


def test_GeomConvert_CompCurveToBSplineCurveTest_ConcatenateClampedBSplines():
    c1 = _bspline([(0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0)])
    c2 = _bspline([(3, 0, 0), (4, -1, 0), (5, -1, 0), (6, 0, 0)])
    cc = GeomConvert_CompCurveToBSplineCurve(c1)
    assert cc.Add(c2, CONF)
    r = cc.BSplineCurve()
    assert r is not None
    assert _dist(r.StartPoint(), (0, 0, 0)) <= CONF
    assert _dist(r.EndPoint(), (6, 0, 0)) <= CONF


def test_GeomConvert_CompCurveToBSplineCurveTest_ConcatenateTrimmedCircleArcs():
    circ = Geom_Circle(gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5.0))
    a1 = Geom_TrimmedCurve(circ, 0.0, math.pi / 2.0)
    a2 = Geom_TrimmedCurve(circ, math.pi / 2.0, math.pi)
    assert a1.EndPoint().Distance(a2.StartPoint()) <= CONF
    cc = GeomConvert_CompCurveToBSplineCurve(a1)
    assert cc.Add(a2, CONF)
    r = cc.BSplineCurve()
    assert r is not None
    assert _dist(r.StartPoint(), (5, 0, 0)) <= CONF
    assert _dist(r.EndPoint(), (-5, 0, 0)) <= CONF


def test_GeomConvert_CompCurveToBSplineCurveTest_ConcatenateWithReversal():
    c1 = _bspline([(0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0)])
    c2 = _bspline([(6, 0, 0), (5, -1, 0), (4, -1, 0), (3, 0, 0)])
    cc = GeomConvert_CompCurveToBSplineCurve(c1)
    assert cc.Add(c2, CONF)
    r = cc.BSplineCurve()
    assert r is not None
    assert _dist(r.StartPoint(), (0, 0, 0)) <= CONF
    assert _dist(r.EndPoint(), (6, 0, 0)) <= CONF


def test_GeomConvert_CompCurveToBSplineCurveTest_FailsForDisjointCurves():
    c1 = _bspline([(0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0)])
    c2 = _bspline([(10, 0, 0), (11, 1, 0), (12, 1, 0), (13, 0, 0)])
    assert not GeomConvert_CompCurveToBSplineCurve(c1).Add(c2, CONF)


def test_GeomConvert_CompCurveToBSplineCurveTest_ConcatenateNonClampedBSpline_Bug30007():
    c1 = _bspline([(0, 0, 0), (1, 2, 0), (2, 2, 0), (3, 2, 0), (4, 2, 0), (5, 0, 0)],
                  (0.0, 0.33, 0.67, 1.0), (4, 1, 1, 4))
    c2 = _bspline([c1.EndPoint(), (6, -1, 0), (7, -1, 0), (8, 0, 0)])
    cc = GeomConvert_CompCurveToBSplineCurve(c1)
    assert cc.Add(c2, CONF)
    r = cc.BSplineCurve()
    assert r is not None
    assert r.StartPoint().Distance(c1.StartPoint()) <= CONF
    assert _dist(r.EndPoint(), (8, 0, 0)) <= CONF


def test_GeomConvert_CompCurveToBSplineCurveTest_PrependCurve():
    c1 = _bspline([(3, 0, 0), (4, 1, 0), (5, 1, 0), (6, 0, 0)])
    c2 = _bspline([(0, 0, 0), (1, -1, 0), (2, -1, 0), (3, 0, 0)])
    cc = GeomConvert_CompCurveToBSplineCurve(c1)
    assert cc.Add(c2, CONF)
    r = cc.BSplineCurve()
    assert r is not None
    assert _dist(r.StartPoint(), (0, 0, 0)) <= CONF
    assert _dist(r.EndPoint(), (6, 0, 0)) <= CONF


def test_GeomConvert_CompCurveToBSplineCurveTest_EmptyInitialCurve():
    cc = GeomConvert_CompCurveToBSplineCurve()
    assert cc.Add(_bspline([(0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0)]), CONF)
    assert cc.BSplineCurve() is not None


def test_GeomConvert_CompCurveToBSplineCurveTest_ClearAndReuse():
    c = _bspline([(0, 0, 0), (1, 1, 0), (2, 1, 0), (3, 0, 0)])
    cc = GeomConvert_CompCurveToBSplineCurve(c)
    assert cc.BSplineCurve() is not None
    cc.Clear()
    assert cc.BSplineCurve() is None
    assert cc.Add(c, CONF)
    assert cc.BSplineCurve() is not None
