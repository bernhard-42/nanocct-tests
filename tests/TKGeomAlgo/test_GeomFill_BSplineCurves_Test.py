# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomFill_BSplineCurves_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepOffset import BRepOffset_MakeOffset, BRepOffset_Skin
from nanocct.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from nanocct.Geom import Geom_BezierCurve
from nanocct.Geom2dAPI import Geom2dAPI_Interpolate
from nanocct.GeomAbs import GeomAbs_Arc
from nanocct.GeomAPI import GeomAPI
from nanocct.GeomConvert import GeomConvert
from nanocct.GeomFill import GeomFill_BSplineCurves, GeomFill_CoonsStyle
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pln, gp_Pnt, gp_Pnt2d, gp_Vec2d
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_Array1, NCollection_HArray1
from nanocct.Precision import Precision
from nanocct.ShapeFix import ShapeFix_Shape
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer
from nanocct import TopoDS


def _create_occ28131_face():
    height = 8.5
    v0 = gp_Pnt(-17.6, 0.0, 0.0)
    v1 = gp_Pnt(0, 32.8, 0.0)
    bez_poles = NCollection_Array1[gp_Pnt](1, 4)
    bez_poles.SetValue(1, v0)
    bez_poles.SetValue(4, v1)
    bez_poles.SetValue(2, gp_Pnt(v0.X(), (5.4 / 13.2) * v1.Y(), 0))
    bez_poles.SetValue(3, gp_Pnt((6.0 / 6.8) * v0.X(), v1.Y(), 0))
    outline = GeomConvert.CurveToBSplineCurve_s(Geom_BezierCurve(bez_poles))

    h1 = NCollection_HArray1[gp_Pnt2d](1, 2)
    h1.SetValue(1, gp_Pnt2d(-v1.Y(), 0))
    h1.SetValue(2, gp_Pnt2d(0, height + height / 2))
    interp1 = Geom2dAPI_Interpolate(h1, False, 1e-6)
    interp1.Load(gp_Vec2d(0, 1), gp_Vec2d(1, 0))
    interp1.Perform()
    pln1 = gp_Pln(gp_Ax3(gp_Pnt(), gp_Dir(gp_Dir.D.X), gp_Dir(gp_Dir.D.NY)))
    curve1 = GeomAPI.To3d_s(interp1.Curve(), pln1)

    h2 = NCollection_HArray1[gp_Pnt2d](1, 3)
    h2.SetValue(1, gp_Pnt2d(-v0.X(), 0))
    h2.SetValue(2, gp_Pnt2d(-v0.X() - 2.6, height))
    h2.SetValue(3, gp_Pnt2d(0, height + height / 2))
    interp2 = Geom2dAPI_Interpolate(h2, False, 1e-6)
    interp2.Perform()
    pln2 = gp_Pln(gp_Ax3(gp_Pnt(), gp_Dir(gp_Dir.D.NY), gp_Dir(gp_Dir.D.NX)))
    curve2 = GeomAPI.To3d_s(interp2.Curve(), pln2)

    fill = GeomFill_BSplineCurves()
    fill.Init(outline, curve1, curve2, GeomFill_CoonsStyle)
    builder = BRepBuilderAPI_MakeFace(fill.Surface(), 0)
    assert builder.IsDone()
    return builder.Shape()


def _max_tolerance(shape):
    tol = 0.0
    for typ, cast in ((TopAbs_VERTEX, TopoDS.Vertex), (TopAbs_EDGE, TopoDS.Edge), (TopAbs_FACE, TopoDS.Face)):
        exp = TopExp_Explorer(shape, typ)
        while exp.More():
            tol = max(tol, BRep_Tool.Tolerance_s(cast(exp.Current())))
            exp.Next()
    return tol


def _surface_area(shape):
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


def test_GeomFill_BSplineCurvesTest_OCC28131_FillSurfaceFromBezierAndInterpolatedCurves():
    face = _create_occ28131_face()
    assert not face.IsNull()
    assert BRepCheck_Analyzer(face).IsValid()


def test_GeomFill_BSplineCurvesTest_OCC28131_SimpleOffsetOfFilledFace():
    face = _create_occ28131_face()
    maker = BRepOffsetAPI_MakeOffsetShape()
    maker.PerformBySimple(face, 10.0)
    assert maker.IsDone()
    result = maker.Shape()
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()
    assert abs(_max_tolerance(result) - 0.205) <= 0.205 * 0.01
    assert abs(_surface_area(result) - 1693.7) <= 1693.7 * 0.01


def test_GeomFill_BSplineCurvesTest_OCC28131_StandardOffsetOfFilledFace():
    face = _create_occ28131_face()
    maker = BRepOffset_MakeOffset()
    maker.Initialize(face, 10.0, Precision.Confusion_s(), BRepOffset_Skin, False, False, GeomAbs_Arc)
    maker.MakeOffsetShape()
    assert not maker.Shape().IsNull()
    fixer = ShapeFix_Shape(maker.Shape())
    fixer.Perform()
    result = fixer.Shape()
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()
    assert abs(_max_tolerance(result) - 0.408) <= 0.408 * 0.01
    assert abs(_surface_area(result) - 1693.76) <= 1693.76 * 0.01
