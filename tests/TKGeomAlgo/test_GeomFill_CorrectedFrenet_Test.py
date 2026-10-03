# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomFill_CorrectedFrenet_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepAdaptor import BRepAdaptor_CompCurve
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.GC import GC_MakeSegment
from nanocct.Geom import Geom_BSplineCurve
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.GeomFill import GeomFill_CorrectedFrenet
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.ShapeExtend import ShapeExtend_WireData


def _bspline(points, mult, degree):
    poles = NCollection_Array1[gp_Pnt](1, len(points))
    for i, p in enumerate(points, 1):
        poles.SetValue(i, p)
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, mult)
    mults.SetValue(2, mult)
    return Geom_BSplineCurve(poles, knots, mults, degree)


def test_GeomFill_CorrectedFrenet_EndlessLoopPrevention():
    curve = _bspline([gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1.0, 0.0, 0.0), gp_Pnt(1.0, 1.0, 0.0), gp_Pnt(0.0, 1.0, 0.0)], 4, 3)
    adaptor = GeomAdaptor_Curve(curve)
    cf = GeomFill_CorrectedFrenet(False)
    cf.SetCurve(adaptor)
    t1, n1, b1 = gp_Vec(), gp_Vec(), gp_Vec()
    t2, n2, b2 = gp_Vec(), gp_Vec(), gp_Vec()
    cf.D0(0.0, t1, n1, b1)
    cf.D0(1.0, t2, n2, b2)
    for v in (t1, n1, b1, t2, n2, b2):
        assert v.Magnitude() > 1e-10


def test_GeomFill_CorrectedFrenet_SmallStepHandling():
    curve = _bspline([gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1e-10, 0.0, 0.0)], 2, 1)
    adaptor = GeomAdaptor_Curve(curve)
    cf = GeomFill_CorrectedFrenet(False)
    cf.SetCurve(adaptor)
    cf.D0(0.5, gp_Vec(), gp_Vec(), gp_Vec())


def test_GeomFill_CorrectedFrenet_ParameterProgressionGuarantee():
    curve = _bspline([gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(0.5, 0.5, 0.0), gp_Pnt(1.0, 0.0, 0.0)], 3, 2)
    adaptor = GeomAdaptor_Curve(curve)
    cf = GeomFill_CorrectedFrenet(False)
    cf.SetCurve(adaptor)
    param = 0.1
    while param <= 0.9:
        t, n, b = gp_Vec(), gp_Vec(), gp_Vec()
        cf.D0(param, t, n, b)
        assert t.Magnitude() > 1e-12
        assert n.Magnitude() > 1e-12
        assert b.Magnitude() > 1e-12
        param += 0.1


def test_GeomFill_CorrectedFrenet_ActualReproducerCase():
    pts = [gp_Pnt(-1, -1, 0), gp_Pnt(0, -2, 0), gp_Pnt(0, -2, -1), gp_Pnt(0, -1, -1)]
    wd = ShapeExtend_WireData()
    for i in range(1, len(pts)):
        seg = GC_MakeSegment(pts[i - 1], pts[i]).Value()
        wd.Add(BRepBuilderAPI_MakeEdge(seg).Edge())
    wire = wd.WireAPIMake()
    adaptor = BRepAdaptor_CompCurve(wire)
    cf = GeomFill_CorrectedFrenet(False)
    cf.SetCurve(adaptor.ShallowCopy())
    t, n, b = gp_Vec(), gp_Vec(), gp_Vec()
    cf.D0(0.0, t, n, b)
    cf.D0(0.5, t, n, b)
    cf.D0(1.0, t, n, b)
