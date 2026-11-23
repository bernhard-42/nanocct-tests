# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepTools_GTrsfModification_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepTools import BRepTools_GTrsfModification, BRepTools_Modifier
from nanocct.Geom import Geom_BezierCurve, Geom_BezierSurface
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp_Ax2d, gp_Dir, gp_Dir2d, gp_GTrsf, gp_Mat, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec, gp_XYZ
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Poly import Poly_Polygon3D, Poly_PolygonOnTriangulation, Poly_Triangle, Poly_Triangulation
from nanocct.Precision import Precision
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Edge, TopoDS_Face, TopoDS_Vertex


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def _triangulation(has_normals):
    tri = Poly_Triangulation(3, 1, False, has_normals)
    tri.SetNode(1, gp_Pnt(0.0, 0.0, 0.0))
    tri.SetNode(2, gp_Pnt(1.0, 0.0, 0.0))
    tri.SetNode(3, gp_Pnt(0.0, 1.0, 1.0))
    tri.SetTriangle(1, Poly_Triangle(1, 2, 3))
    tri.Deflection(0.25)
    if has_normals is True:
        normal = gp_Dir(0.0, -1.0, 1.0)
        for i in range(1, 4):
            tri.SetNormal(i, normal)
    return tri


def _gtrsf(*m):
    g = gp_GTrsf()
    g.SetVectorialPart(gp_Mat(*m))
    return g


def _near(actual, expected):
    assert actual.Distance(expected) < 1.0e-12, (actual.Coord(), expected.Coord())


def _scale(factor, center=(0.0, 0.0, 0.0)):
    t = gp_Trsf()
    t.SetScale(gp_Pnt(*center), factor)
    return t


def _translation(*v):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(*v))
    return t


def _face_of(tri):
    face = TopoDS_Face()
    BRep_Builder().MakeFace(face, tri)
    return face


def _transformed(g, point):
    p = gp_Pnt(point.XYZ())
    g.Transforms(p.ChangeCoord())
    return p


def test_BRepTools_GTrsfModificationTest_Triangulation_ReflectionPreservesWindingAndNormals():
    source = _triangulation(True)
    source.UpdateCachedMinMax()
    assert source.HasCachedMinMax() is True
    face = _face_of(source)
    modification = BRepTools_GTrsfModification(_gtrsf(-2.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 4.0))
    ok, result = modification.NewTriangulation(face)
    assert ok is True
    assert result is not None
    assert result.HasCachedMinMax() is False
    assert source.HasCachedMinMax() is True
    assert result.Triangle(1).Get() == (1, 3, 2)
    expected_normal = gp_Dir(0.0, -1.0 / 3.0, 1.0 / 4.0)
    for i in range(1, 4):
        assert result.Normal(i).Angle(expected_normal) < 1.0e-6
    assert result.Deflection() == _eq(1.0)
    assert source.Deflection() == _eq(0.25)
    _near(source.Node(2), gp_Pnt(1.0, 0.0, 0.0))


def test_BRepTools_GTrsfModificationTest_Triangulation_NegativeUniformScalePreservesOrientation():
    face = _face_of(_triangulation(True))
    modification = BRepTools_GTrsfModification(gp_GTrsf(_scale(-2.0)))
    ok, result = modification.NewTriangulation(face)
    assert ok is True
    assert result.Triangle(1).Get() == (1, 3, 2)
    assert result.Normal(1).Angle(gp_Dir(0.0, 1.0, -1.0)) < 1.0e-6
    assert result.Deflection() == _eq(0.5)


def test_BRepTools_GTrsfModificationTest_Triangulation_NormalTransformationIsScaleInvariant():
    source = _triangulation(True)
    face = _face_of(source)
    for scale in (Precision.PConfusion_s(), Precision.Infinite_s()):
        modification = BRepTools_GTrsfModification(_gtrsf(scale, 0.0, 0.0, 0.0, scale, 0.0, 0.0, 0.0, scale))
        ok, result = modification.NewTriangulation(face)
        assert ok is True, scale
        assert result.Normal(1).Angle(source.Normal(1)) < 1.0e-6, scale


def test_BRepTools_GTrsfModificationTest_Triangulation_SingularAffinityHandlesNormals():
    source = _triangulation(True)
    face = _face_of(source)
    rank_two = BRepTools_GTrsfModification(_gtrsf(2.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 0.0))
    ok, result = rank_two.NewTriangulation(face)
    assert ok is True
    assert result.HasNormals() is True
    assert result.Normal(1).Angle(gp_Dir(0.0, 0.0, 1.0)) < 1.0e-6
    rank_one = BRepTools_GTrsfModification(_gtrsf(2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
    ok, result = rank_one.NewTriangulation(face)
    assert ok is True
    assert result.HasNormals() is True
    assert result.Normal(1).Angle(source.Normal(1)) < 1.0e-6


def test_BRepTools_GTrsfModificationTest_Surface_LocatedBezierTransformsEvaluatedGeometry():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0.0, 0.0, 0.0))
    poles.SetValue(2, 1, gp_Pnt(2.0, 0.0, 1.0))
    poles.SetValue(1, 2, gp_Pnt(0.0, 3.0, 1.0))
    poles.SetValue(2, 2, gp_Pnt(2.0, 3.0, 2.0))
    surface = Geom_BezierSurface(poles)
    location_trsf = _translation(4.0, -2.0, 5.0)
    face = TopoDS_Face()
    BRep_Builder().MakeFace(face, surface, TopLoc_Location(location_trsf), 0.2)
    g = gp_GTrsf(gp_Mat(2.0, 0.5, 0.0, 0.0, 3.0, 0.25, 0.0, 0.0, 4.0), gp_XYZ(7.0, 8.0, 9.0))
    modification = BRepTools_GTrsfModification(g)
    result_location = TopLoc_Location()
    ok, result, tolerance, reverse_wires, reverse_face = modification.NewSurface(face, result_location)
    assert ok is True
    assert result is not None
    assert result_location.IsIdentity() is True
    assert reverse_wires is False
    assert reverse_face is False
    _near(result.Value(0.35, 0.65), _transformed(g, surface.Value(0.35, 0.65).Transformed(location_trsf)))
    _near(surface.Pole(2, 2), gp_Pnt(2.0, 3.0, 2.0))
    assert tolerance == _eq(0.8)
    scale = _scale(-2.0)
    modification.GTrsf().SetTrsf(scale)
    ok, result, tolerance, reverse_wires, reverse_face = modification.NewSurface(face, result_location)
    assert ok is True
    assert reverse_face is True
    assert tolerance == _eq(0.4)
    _near(result.Value(0.35, 0.65), surface.Value(0.35, 0.65).Transformed(location_trsf).Transformed(scale))


def test_BRepTools_GTrsfModificationTest_Curve_LocatedBezierPreservesRangeAndSource():
    poles = NCollection_Array1[gp_Pnt](1, 3)
    poles[1], poles[2], poles[3] = gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1.0, 2.0, 0.0), gp_Pnt(3.0, 2.0, 1.0)
    curve = Geom_BezierCurve(poles)
    location_trsf = _translation(-3.0, 4.0, 2.0)
    builder = BRep_Builder()
    edge = TopoDS_Edge()
    builder.MakeEdge(edge, curve, TopLoc_Location(location_trsf), 0.1)
    builder.Range(edge, 0.2, 0.8)
    g = gp_GTrsf(gp_Mat(1.0, 0.5, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 3.0), gp_XYZ(2.0, -1.0, 5.0))
    modification = BRepTools_GTrsfModification(g)
    result_location = TopLoc_Location()
    ok, result, tolerance = modification.NewCurve(edge, result_location)
    assert ok is True
    assert result is not None
    assert result_location.IsIdentity() is True
    assert result.FirstParameter() == _eq(0.2)
    assert result.LastParameter() == _eq(0.8)
    _near(result.Value(0.4), _transformed(g, curve.Value(0.4).Transformed(location_trsf)))
    _near(curve.Pole(2), gp_Pnt(1.0, 2.0, 0.0))
    scale = _scale(-2.0)
    modification.GTrsf().SetTrsf(scale)
    ok, result, tolerance = modification.NewCurve(edge, result_location)
    assert ok is True
    assert tolerance == _eq(0.2)
    _near(result.Value(0.4), curve.Value(0.4).Transformed(location_trsf).Transformed(scale))


def test_BRepTools_GTrsfModificationTest_Polygon3D_RepresentationLocationTransformsToEdgeFrame():
    nodes = NCollection_Array1[gp_Pnt](1, 2)
    nodes[1], nodes[2] = gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 5.0, 6.0)
    params = NCollection_Array1[float](1, 2)
    params[1], params[2] = 0.25, 0.75
    polygon = Poly_Polygon3D(nodes, params)
    polygon.Deflection(0.5)
    builder = BRep_Builder()
    edge = TopoDS_Edge()
    builder.MakeEdge(edge)
    builder.UpdateEdge(edge, polygon, TopLoc_Location(_translation(10.0, 0.0, 0.0)))
    edge.Location(TopLoc_Location(_translation(0.0, 20.0, 0.0)))
    g = _gtrsf(2.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 4.0)
    modification = BRepTools_GTrsfModification(g)
    ok, result = modification.NewPolygon(edge)
    assert ok is True
    assert result is not None
    source_location = TopLoc_Location()
    assert BRep_Tool.Polygon3D_s(edge, source_location) is not None
    for i in range(1, result.NbNodes() + 1):
        expected = _transformed(g, polygon.Nodes()[i].Transformed(source_location.Transformation()))
        _near(result.Nodes()[i].Transformed(edge.Location().Transformation()), expected)
        assert result.Parameters()[i] == _eq(params[i])
    assert result.Deflection() == _eq(2.0)
    assert polygon.Deflection() == _eq(0.5)


def test_BRepTools_GTrsfModificationTest_MissingPolygonRepresentationsReturnFalse():
    edge = TopoDS_Edge()
    BRep_Builder().MakeEdge(edge)
    face = _face_of(_triangulation(False))
    modification = BRepTools_GTrsfModification(gp_GTrsf())
    ok, polygon3d = modification.NewPolygon(edge)
    assert ok is False
    assert polygon3d is None
    ok, polygon_on_tri = modification.NewPolygonOnTriangulation(edge, face)
    assert ok is False
    assert polygon_on_tri is None


def test_BRepTools_GTrsfModificationTest_Curve2dAndVertexParameterPreserveParametrization():
    surface_poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    surface_poles.SetValue(1, 1, gp_Pnt(0.0, 0.0, 0.0))
    surface_poles.SetValue(2, 1, gp_Pnt(1.0, 0.0, 0.0))
    surface_poles.SetValue(1, 2, gp_Pnt(0.0, 1.0, 0.0))
    surface_poles.SetValue(2, 2, gp_Pnt(1.0, 1.0, 0.0))
    surface = Geom_BezierSurface(surface_poles)
    curve_poles = NCollection_Array1[gp_Pnt](1, 2)
    curve_poles[1], curve_poles[2] = gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1.0, 0.0, 0.0)
    curve = Geom_BezierCurve(curve_poles)
    builder = BRep_Builder()
    face, edge, vertex = TopoDS_Face(), TopoDS_Edge(), TopoDS_Vertex()
    builder.MakeFace(face, surface, 0.05)
    builder.MakeEdge(edge, curve, 0.05)
    builder.Range(edge, 0.2, 0.8)
    pcurve = Geom2d_Line(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)))
    builder.UpdateEdge(edge, pcurve, face, 0.05)
    builder.Range(edge, face, 0.2, 0.8)
    builder.MakeVertex(vertex, curve.Value(0.25), 0.02)
    builder.Add(edge, vertex)
    builder.UpdateVertex(vertex, 0.25, edge, 0.02)
    source_curve, source_first, source_last = BRep_Tool.CurveOnSurface_s(edge, face)
    assert source_curve is not None
    modification = BRepTools_GTrsfModification(_gtrsf(2.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 1.0))
    ok, result_curve, tolerance = modification.NewCurve2d(edge, face, TopoDS_Edge(), TopoDS_Face())
    assert ok is True
    assert result_curve is not None
    assert result_curve.FirstParameter() == _eq(source_first)
    assert result_curve.LastParameter() == _eq(source_last)
    assert result_curve.Value(0.4).Distance(pcurve.Value(0.4)) < 1.0e-12
    assert tolerance == _eq(0.15)
    ok, parameter, tolerance = modification.NewParameter(vertex, edge)
    assert ok is True
    assert parameter == _eq(0.25)
    assert tolerance == _eq(0.06)


def test_BRepTools_GTrsfModificationTest_Modifier_LocatedSurfaceAndMeshStayCoincident():
    poles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    poles.SetValue(1, 1, gp_Pnt(0.0, 0.0, 0.0))
    poles.SetValue(2, 1, gp_Pnt(1.0, 0.0, 0.0))
    poles.SetValue(1, 2, gp_Pnt(0.0, 1.0, 1.0))
    poles.SetValue(2, 2, gp_Pnt(1.0, 1.0, 1.0))
    surface = Geom_BezierSurface(poles)
    triangulation = _triangulation(False)
    builder = BRep_Builder()
    face = TopoDS_Face()
    builder.MakeFace(face, surface, 0.1)
    builder.UpdateFace(face, triangulation)
    location_trsf = _translation(10.0, 20.0, 30.0)
    face.Location(TopLoc_Location(location_trsf))
    g = gp_GTrsf(gp_Mat(2.0, 0.5, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 4.0), gp_XYZ(5.0, 6.0, 7.0))
    modifier = BRepTools_Modifier(face, BRepTools_GTrsfModification(g))
    assert modifier.IsDone() is True
    result_face = TopoDS.Face(modifier.ModifiedShape(face))
    assert result_face.IsNull() is False
    surface_location = TopLoc_Location()
    result_surface = BRep_Tool.Surface_s(result_face, surface_location)
    assert result_surface is not None
    _near(result_surface.Value(0.25, 0.75).Transformed(surface_location.Transformation()),
          _transformed(g, surface.Value(0.25, 0.75).Transformed(location_trsf)))
    mesh_location = TopLoc_Location()
    result_triangulation = BRep_Tool.Triangulation_s(result_face, mesh_location)
    assert result_triangulation is not None
    for i in range(1, triangulation.NbNodes() + 1):
        _near(result_triangulation.Node(i).Transformed(mesh_location.Transformation()),
              _transformed(g, triangulation.Node(i).Transformed(location_trsf)))


def test_BRepTools_GTrsfModificationTest_Triangulation_LocatedFaceUsesLocalCoordinates():
    source = _triangulation(False)
    face = _face_of(source)
    face.Location(TopLoc_Location(_translation(10.0, 20.0, 30.0)))
    g = _gtrsf(2.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 4.0)
    modification = BRepTools_GTrsfModification(g)
    ok, result = modification.NewTriangulation(face)
    assert ok is True
    result_location = TopLoc_Location()
    assert BRep_Tool.Triangulation_s(face, result_location) is not None
    for i in range(1, source.NbNodes() + 1):
        expected = _transformed(g, source.Node(i).Transformed(result_location.Transformation()))
        actual = result.Node(i).Transformed(result_location.Transformation())
        assert actual.Distance(expected) < 1.0e-12, i


def test_BRepTools_GTrsfModificationTest_Tolerance_TracksCurrentTransformation():
    vertex = TopoDS_Vertex()
    BRep_Builder().MakeVertex(vertex, gp_Pnt(1.0, 2.0, 3.0), 0.1)
    modification = BRepTools_GTrsfModification(gp_GTrsf())
    mutable = modification.GTrsf()
    mutable.SetVectorialPart(gp_Mat(2.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 4.0))
    point = gp_Pnt()
    ok, tolerance = modification.NewPoint(vertex, point)
    assert ok is True
    assert tolerance == _eq(0.4)
    _near(point, gp_Pnt(2.0, 6.0, 12.0))
    mutable.SetVectorialPart(gp_Mat(1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0))
    ok, tolerance = modification.NewPoint(vertex, point)
    assert ok is True
    assert tolerance == _eq(0.1)
    _near(point, gp_Pnt(3.0, 2.0, 3.0))
    c = math.sqrt(0.5)
    mutable.SetVectorialPart(gp_Mat(c, -c, 0.0, c, c, 0.0, 0.0, 0.0, 1.0))
    ok, tolerance = modification.NewPoint(vertex, point)
    assert ok is True
    assert tolerance == pytest.approx(0.1, abs=1.0e-14)
    mutable.SetTrsf(_scale(3.0))
    ok, tolerance = modification.NewPoint(vertex, point)
    assert ok is True
    assert tolerance == _eq(0.3)
    _near(point, gp_Pnt(3.0, 6.0, 9.0))


def test_BRepTools_GTrsfModificationTest_PolygonOnTriangulation_PreservesDeflection():
    triangulation = _triangulation(False)
    face = _face_of(triangulation)
    nodes = NCollection_Array1[int](1, 2)
    nodes[1], nodes[2] = 1, 2
    polygon = Poly_PolygonOnTriangulation(nodes)
    polygon.Deflection(0.25)
    edge = TopoDS_Edge()
    BRep_Builder().MakeEdge(edge, polygon, triangulation)
    modification = BRepTools_GTrsfModification(_gtrsf(2.0, 0.0, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 4.0))
    ok, result = modification.NewPolygonOnTriangulation(edge, face)
    assert ok is True
    assert result is not None
    assert result.Deflection() == _eq(0.25)


def test_BRepTools_GTrsfModificationTest_Triangulation_TransformsNormalsUnderShear():
    face = _face_of(_triangulation(True))
    modification = BRepTools_GTrsfModification(_gtrsf(2.0, 0.5, 0.25, 0.0, 3.0, 0.75, 0.0, 0.0, 4.0))
    ok, result = modification.NewTriangulation(face)
    assert ok is True
    assert result is not None
    # Cross product of the linearly transformed triangle sides (2,0,0) and (0.75,3.75,4).
    assert result.Normal(1).Angle(gp_Dir(0.0, -8.0, 7.5)) < 1.0e-6
    assert result.Triangle(1).Get() == (1, 2, 3)


def test_BRepTools_GTrsfModificationTest_Polygon3D_ParameterlessScaledLocation():
    nodes = NCollection_Array1[gp_Pnt](1, 2)
    nodes[1], nodes[2] = gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 5.0, 6.0)
    source = Poly_Polygon3D(nodes)
    target_trsf = _scale(3.0, (1.0, 1.0, 1.0))
    builder = BRep_Builder()
    edge = TopoDS_Edge()
    builder.MakeEdge(edge)
    builder.UpdateEdge(edge, source, TopLoc_Location(_scale(2.0, (3.0, 2.0, 1.0))))
    edge.Location(TopLoc_Location(target_trsf))
    g = _gtrsf(2.0, 0.5, 0.0, 0.0, 3.0, 0.0, 0.0, 0.0, 4.0)
    modification = BRepTools_GTrsfModification(g)
    ok, result = modification.NewPolygon(edge)
    assert ok is True
    assert result is not None
    assert result.HasParameters() is False
    source_location = TopLoc_Location()
    assert BRep_Tool.Polygon3D_s(edge, source_location) is source
    for i in range(1, source.NbNodes() + 1):
        expected = _transformed(g, nodes[i].Transformed(source_location.Transformation()))
        _near(result.Nodes()[i].Transformed(target_trsf), expected)
        _near(source.Nodes()[i], nodes[i])
