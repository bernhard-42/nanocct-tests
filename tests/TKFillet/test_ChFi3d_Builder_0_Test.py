# Translated from OCCT src/ModelingAlgorithms/TKFillet/GTests/ChFi3d_Builder_0_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakePolygon
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepFilletAPI import BRepFilletAPI_MakeFillet
from nanocct.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder
from nanocct.ChFi3d import ChFi3d_PerformElSpine, ChFi3d_Rational
from nanocct.ChFiDS import ChFiDS_Closed, ChFiDS_ElSpine, ChFiDS_Spine
from nanocct.GC import GC_MakeArcOfCircle
from nanocct.Geom import Geom_BSplineSurface
from nanocct.GeomAbs import GeomAbs_BSplineSurface, GeomAbs_C1, GeomAbs_Circle, GeomAbs_Torus
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Elips, gp_Pnt
from nanocct.NCollection import NCollection_IndexedMap
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE
from nanocct.TopExp import TopExp
from nanocct.TopoDS import TopoDS_Shape, TopoDS_Vertex
from nanocct.TopTools import TopTools_ShapeMapHasher


def _map(shape, kind):
    m = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(shape, kind, m)
    return m


def _rectangle(width, depth, z):
    polygon = BRepBuilderAPI_MakePolygon()
    polygon.Add(gp_Pnt(-width / 2.0, -depth / 2.0, z))
    polygon.Add(gp_Pnt(width / 2.0, -depth / 2.0, z))
    polygon.Add(gp_Pnt(width / 2.0, depth / 2.0, z))
    polygon.Add(gp_Pnt(-width / 2.0, depth / 2.0, z))
    polygon.Close()
    return polygon.Wire()


def _z_range(edge):
    first, last = TopoDS_Vertex(), TopoDS_Vertex()
    TopExp.Vertices_s(edge, first, last)
    z1, z2 = BRep_Tool.Pnt_s(first).Z(), BRep_Tool.Pnt_s(last).Z()
    return min(z1, z2), max(z1, z2)


def _spans_height(edge, height):
    lo, hi = _z_range(edge)
    return lo < Precision.Confusion_s() and hi > height - Precision.Confusion_s()


def _lies_on_bottom(edge):
    lo, hi = _z_range(edge)
    return abs(lo) < Precision.Confusion_s() and abs(hi) < Precision.Confusion_s()


def _count_c0_bspline_faces(shape):
    count = 0
    faces = _map(shape, TopAbs_FACE)
    for i in range(1, faces.Extent() + 1):
        surface = BRep_Tool.Surface_s(TopoDS.Face(faces.FindKey(i)))
        if isinstance(surface, Geom_BSplineSurface) is False:
            continue
        has_c0 = any(surface.UMultiplicity(k) >= surface.UDegree() for k in range(2, surface.NbUKnots()))
        if has_c0 is False:
            has_c0 = any(surface.VMultiplicity(k) >= surface.VDegree() for k in range(2, surface.NbVKnots()))
        if has_c0 is True:
            count += 1
    return count


def test_BRepFilletAPI_MakeFilletTest_PeriodicAnalyticSpineKeepsParticularSurface():
    shapes = (BRepPrimAPI_MakeCylinder(20.0, 50.0).Shape(), BRepPrimAPI_MakeCone(25.0, 12.0, 50.0).Shape())
    for shape_index, shape in enumerate(shapes, 1):
        edges = _map(shape, TopAbs_EDGE)
        circular = 0
        for i in range(1, edges.Extent() + 1):
            edge = TopoDS.Edge(edges.FindKey(i))
            if BRepAdaptor_Curve(edge).GetType() != GeomAbs_Circle:
                continue
            circular += 1
            where = (shape_index, circular)
            fillet = BRepFilletAPI_MakeFillet(shape, ChFi3d_Rational)
            fillet.Add(4.0, edge)
            fillet.Build()
            assert fillet.IsDone() is True, where
            result = fillet.Shape()
            assert result.IsNull() is False, where
            assert BRepCheck_Analyzer(result).IsValid() is True, where
            faces = _map(result, TopAbs_FACE)
            types = [BRepAdaptor_Surface(TopoDS.Face(faces.FindKey(j))).GetType() for j in range(1, faces.Extent() + 1)]
            assert types.count(GeomAbs_Torus) == 1, where
            assert types.count(GeomAbs_BSplineSurface) == 0, where
        assert circular == 2, shape_index


def test_BRepFilletAPI_MakeFilletTest_PeriodicSpine_TangentCurvatureJump_DoesNotCreateC0Surface():
    height = 30.0
    growth = 2.0 * height * math.tan(10.0 * math.pi / 180.0)
    loft = BRepOffsetAPI_ThruSections(True, True)
    loft.AddWire(_rectangle(50.0, 70.0, 0.0))
    loft.AddWire(_rectangle(50.0 + growth, 70.0 + growth, height))
    loft.Build()
    assert loft.IsDone() is True
    vertical = BRepFilletAPI_MakeFillet(loft.Shape())
    loft_edges = _map(loft.Shape(), TopAbs_EDGE)
    nb_vertical = 0
    for i in range(1, loft_edges.Extent() + 1):
        edge = TopoDS.Edge(loft_edges.FindKey(i))
        if _spans_height(edge, height) is True:
            vertical.Add(10.0, edge)
            nb_vertical += 1
    assert nb_vertical == 4
    vertical.Build()
    assert vertical.IsDone() is True
    rounded = _map(vertical.Shape(), TopAbs_EDGE)
    bottom = [TopoDS.Edge(rounded.FindKey(i)) for i in range(1, rounded.Extent() + 1)
              if _lies_on_bottom(TopoDS.Edge(rounded.FindKey(i))) is True]
    assert len(bottom) == 8
    for seed, edge in enumerate(bottom, 1):
        fillet = BRepFilletAPI_MakeFillet(vertical.Shape(), ChFi3d_Rational)
        fillet.SetParams(1.0e-2, 1.0e-4, 1.0e-5, 1.0e-4, 1.0e-5, 1.0e-3)
        fillet.SetContinuity(GeomAbs_C1, 1.0e-2)
        fillet.Add(5.0, edge)
        fillet.Build()
        assert fillet.IsDone() is True, seed
        result = fillet.Shape()
        assert result.IsNull() is False, seed
        assert BRepCheck_Analyzer(result).IsValid() is True, seed
        assert _map(result, TopAbs_FACE).Extent() == 18, seed
        assert _map(result, TopAbs_EDGE).Extent() == 40, seed
        assert _count_c0_bspline_faces(result) == 0, seed


def _perform_periodic_spine(edges, tolerance):
    spine = ChFiDS_Spine(tolerance)
    for edge in edges:
        spine.SetEdges(edge)
    spine.SetFirstStatus(ChFiDS_Closed)
    spine.SetLastStatus(ChFiDS_Closed)
    spine.Load()
    el_spine = ChFiDS_ElSpine()
    el_spine.FirstParameter(spine.FirstParameter())
    el_spine.LastParameter(spine.LastParameter())
    el_spine.SetPeriodic(True)
    ChFi3d_PerformElSpine(el_spine, spine, GeomAbs_C1, tolerance)
    return el_spine.BSpline()


def _stadium_edges(scale):
    radius, length = 10.0 * scale, 50.0 * scale
    p1, p2 = gp_Pnt(0.0, radius, 0.0), gp_Pnt(length, radius, 0.0)
    p3, p4 = gp_Pnt(length, -radius, 0.0), gp_Pnt(0.0, -radius, 0.0)
    return [BRepBuilderAPI_MakeEdge(p1, p2).Edge(),
            BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(p2, gp_Pnt(length + radius, 0.0, 0.0), p3).Value()).Edge(),
            BRepBuilderAPI_MakeEdge(p3, p4).Edge(),
            BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(p4, gp_Pnt(-radius, 0.0, 0.0), p1).Value()).Edge()]


def _split_circle_edges():
    circle = gp_Circ(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 20.0)
    return [BRepBuilderAPI_MakeEdge(circle, a * math.pi, (a + 0.5) * math.pi).Edge() for a in (0.0, 0.5, 1.0, 1.5)]


def _split_ellipse_edges(scale):
    ellipse = gp_Elips(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 30.0 * scale, 20.0 * scale)
    return [BRepBuilderAPI_MakeEdge(ellipse, 0.0, math.pi).Edge(),
            BRepBuilderAPI_MakeEdge(ellipse, math.pi, 2.0 * math.pi).Edge()]


def test_ChFi3d_PerformElSpineTest_ExactMultiEdgeCircle_NoApproximation_KeepsClosureMultiplicity():
    curve = _perform_periodic_spine(_split_circle_edges(), 1.0e-4)
    assert curve is not None
    assert curve.IsPeriodic() is True
    # An exact periodic guide must retain the OCC22163 guarded behavior.
    assert curve.Multiplicity(1) == curve.Degree()


def test_ChFi3d_PerformElSpineTest_ExactMultiEdgeEllipse_NoApproximation_KeepsClosureMultiplicity():
    for scale in (1.0, 1.0e4):
        curve = _perform_periodic_spine(_split_ellipse_edges(scale), 1.0e-4)
        assert curve is not None, scale
        assert curve.IsPeriodic() is True, scale
        assert curve.Multiplicity(1) == curve.Degree(), scale


def test_ChFi3d_PerformElSpineTest_TangentCurvatureJump_ScaledGuide_ReducesClosureMultiplicity():
    for scale in (1.0, 1.0e4):
        curve = _perform_periodic_spine(_stadium_edges(scale), 1.0e-4)
        assert curve is not None, scale
        assert curve.IsPeriodic() is True, scale
        assert curve.Multiplicity(1) <= curve.Degree() - 2, scale
