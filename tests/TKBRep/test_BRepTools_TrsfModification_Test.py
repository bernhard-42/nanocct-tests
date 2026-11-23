# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepTools_TrsfModification_Test.cxx (LGPL-2.1 with the OCCT exception)
# Open (nanocct, R-OUT): the check that a refused NewTriangulation leaves its in/out handle argument untouched -- the
# handle& is bound as a result only, like ChFi3d_PerformElSpine's. IsCopyMesh() = true is SetIsCopyMesh(True).
import pytest

from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepTools import BRepTools_TrsfModification
from nanocct.Geom import Geom_Plane
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp_Ax2d, gp_Dir, gp_Dir2d, gp_Pln, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Poly import Poly_Polygon3D, Poly_PolygonOnTriangulation, Poly_Triangle, Poly_Triangulation
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Edge, TopoDS_Face


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def _triangulation(has_normals=False):
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


def _scale(factor):
    t = gp_Trsf()
    t.SetScale(gp_Pnt(0.0, 0.0, 0.0), factor)
    return t


def _translation(*v):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(*v))
    return t


def _near(actual, expected):
    assert actual.Distance(expected) < 1.0e-12, (actual.Coord(), expected.Coord())


def test_BRepTools_TrsfModificationTest_CopyMeshFlag_SkipsCachedMeshOnGeometricFace():
    builder = BRep_Builder()
    face = TopoDS_Face()
    triangulation = _triangulation()
    builder.MakeFace(face, Geom_Plane(gp_Pln()), 0.1)
    builder.UpdateFace(face, triangulation)
    modification = BRepTools_TrsfModification(_scale(2.0))
    ok, result = modification.NewTriangulation(face)
    assert ok is False
    modification.SetIsCopyMesh(True)
    ok, result = modification.NewTriangulation(face)
    assert ok is True
    _near(result.Node(2), gp_Pnt(2.0, 0.0, 0.0))
    assert result.Deflection() == _eq(0.5)
    _near(triangulation.Node(2), gp_Pnt(1.0, 0.0, 0.0))


def test_BRepTools_TrsfModificationTest_Polygon3D_DistinctRepresentationLocation():
    nodes = NCollection_Array1[gp_Pnt](1, 2)
    nodes[1], nodes[2] = gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 5.0, 6.0)
    polygon = Poly_Polygon3D(nodes)
    builder = BRep_Builder()
    edge = TopoDS_Edge()
    builder.MakeEdge(edge)
    builder.UpdateEdge(edge, polygon, TopLoc_Location(_translation(10.0, 0.0, 0.0)))
    edge.Location(TopLoc_Location(_translation(0.0, 20.0, 0.0)))
    modification = BRepTools_TrsfModification(_scale(2.0))
    modification.SetIsCopyMesh(True)
    ok, result = modification.NewPolygon(edge)
    assert ok is True
    source_location = TopLoc_Location()
    assert BRep_Tool.Polygon3D_s(edge, source_location) is not None
    for i in range(1, result.NbNodes() + 1):
        expected = polygon.Nodes()[i].Transformed(source_location.Transformation())
        expected.Transform(_scale(2.0))
        _near(result.Nodes()[i].Transformed(edge.Location().Transformation()), expected)


def test_BRepTools_TrsfModificationTest_ParameterlessPolygonOnTriangulationDoesNotThrow():
    builder = BRep_Builder()
    face, edge = TopoDS_Face(), TopoDS_Edge()
    triangulation = _triangulation()
    builder.MakeFace(face, Geom_Plane(gp_Pln()), 0.1)
    builder.UpdateFace(face, triangulation)
    nodes = NCollection_Array1[int](1, 2)
    nodes[1], nodes[2] = 1, 2
    polygon = Poly_PolygonOnTriangulation(nodes)
    polygon.Deflection(0.25)
    builder.MakeEdge(edge, polygon, triangulation)
    builder.UpdateEdge(edge, Geom2d_Line(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0))), face, 0.1)
    builder.Range(edge, face, 0.0, 1.0)
    modification = BRepTools_TrsfModification(_scale(2.0))
    modification.SetIsCopyMesh(True)
    ok, result = modification.NewPolygonOnTriangulation(edge, face)
    assert ok is True
    assert result is not None
    assert result.HasParameters() is False
    assert result.Deflection() == _eq(0.5)


def test_BRepTools_TrsfModificationTest_NegativeScaleUpdatesWindingNormalsAndDeflection():
    face = TopoDS_Face()
    BRep_Builder().MakeFace(face, _triangulation(True))
    modification = BRepTools_TrsfModification(_scale(-2.0))
    modification.SetIsCopyMesh(True)
    ok, result = modification.NewTriangulation(face)
    assert ok is True
    assert result.Triangle(1).Get() == (1, 3, 2)
    assert result.Normal(1).Angle(gp_Dir(0.0, 1.0, -1.0)) < 1.0e-6
    assert result.Deflection() == _eq(0.5)
