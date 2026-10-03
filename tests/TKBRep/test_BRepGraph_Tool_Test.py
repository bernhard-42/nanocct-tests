# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Tool_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_ShellId,
    BRepGraph_Tool,
    BRepGraph_VertexId,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.Poly import Poly_PolygonOnTriangulation, Poly_Triangulation
from nanocct.Precision import Precision


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    return g


@pytest.fixture
def box_graph():
    return _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())


@pytest.fixture
def cyl_graph():
    return _graph(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())


def test_BRepGraph_QuerySurfaceTest_Face_NbWires_BoxFaceHasOneWire(box_graph):
    for i in range(box_graph.Topo().Faces().Nb()):
        assert BRepGraph_Tool.Face.NbWires_s(box_graph, BRepGraph_FaceId(i)) == 1


def test_BRepGraph_QuerySurfaceTest_Face_Bounds_BoxFaceHasFiniteBounds(box_graph):
    u_min, u_max, v_min, v_max = BRepGraph_Tool.Face.Bounds_s(box_graph, BRepGraph_FaceId(0))
    assert u_min < u_max
    assert v_min < v_max
    assert u_min < Precision.Infinite_s()
    assert v_min < Precision.Infinite_s()


def test_BRepGraph_QuerySurfaceTest_Face_Bounds_CylinderFaceReturnsSurfaceBounds(cyl_graph):
    for i in range(cyl_graph.Topo().Faces().Nb()):
        fid = BRepGraph_FaceId(i)
        if not BRepGraph_Tool.Face.HasSurface_s(cyl_graph, fid):
            continue
        bounds = BRepGraph_Tool.Face.Bounds_s(cyl_graph, fid)
        expected = BRepGraph_Tool.Face.Surface_s(cyl_graph, fid).Bounds()
        assert tuple(bounds) == tuple(expected)


def test_BRepGraph_QuerySurfaceTest_Wire_FaceOf_ReturnsValidFace(box_graph):
    assert BRepGraph_Tool.Wire.FaceOf_s(box_graph, BRepGraph_WireId(0)).IsValid()


def test_BRepGraph_QuerySurfaceTest_Wire_IsOuter_FirstWireOfBoxFaceIsOuter(box_graph):
    outer = BRepGraph_Tool.Face.OuterWire_s(box_graph, BRepGraph_FaceId(0))
    assert outer.IsValid()
    assert BRepGraph_Tool.Wire.IsOuter_s(box_graph, outer)


def test_BRepGraph_QuerySurfaceTest_Edge_NbFaces_BoxEdgeHasExactlyTwoFaces(box_graph):
    for i in range(box_graph.Topo().Edges().Nb()):
        assert BRepGraph_Tool.Edge.NbFaces_s(box_graph, BRepGraph_EdgeId(i)) == 2


def test_BRepGraph_QuerySurfaceTest_Edge_IsManifold_BoxEdgesAreManifold(box_graph):
    for i in range(box_graph.Topo().Edges().Nb()):
        eid = BRepGraph_EdgeId(i)
        assert BRepGraph_Tool.Edge.IsManifold_s(box_graph, eid)
        assert not BRepGraph_Tool.Edge.IsBoundary_s(box_graph, eid)


def test_BRepGraph_QuerySurfaceTest_Edge_IsClosed_BoxEdgesAreOpen(box_graph):
    nb = box_graph.Topo().Edges().Nb()
    assert nb > 0
    for i in range(nb):
        assert not BRepGraph_Tool.Edge.IsClosed_s(box_graph, BRepGraph_EdgeId(i))


def test_BRepGraph_QuerySurfaceTest_Edge_IsClosed_DerivedFromVertexTopology(box_graph):
    eid = BRepGraph_EdgeId(0)
    assert eid.IsValid(box_graph.Topo().Edges().Nb())
    assert not BRepGraph_Tool.Edge.IsClosed_s(box_graph, eid)


def test_BRepGraph_QuerySurfaceTest_CoEdge_PolygonOnTriangulation_RoundTrip(box_graph):
    g = box_graph
    assert g.Topo().CoEdges().Nb() > 0
    ceid = BRepGraph_CoEdgeId(0)
    fid = BRepGraph_Tool.CoEdge.FaceOf_s(g, ceid)
    assert not g.Mesh().Persistent().CoEdges().HasPolygonOnTriangulation(ceid)
    assert g.Mesh().Persistent().CoEdges().PolygonOnTriangulation(ceid) is None

    tri = Poly_Triangulation(1, 1, False)
    g.Editor().Faces().SetPersistentTriangulation(fid, tri)
    poly = Poly_PolygonOnTriangulation(2, False)
    g.Editor().CoEdges().SetPersistentPolygonOnTri(ceid, poly)

    assert g.Mesh().Persistent().CoEdges().HasPolygonOnTriangulation(ceid)
    assert g.Mesh().Persistent().CoEdges().PolygonOnTriangulation(ceid) is poly


def test_BRepGraph_QuerySurfaceTest_Edge_PolygonOnTriangulation_ResolvesViaFace(box_graph):
    g = box_graph
    assert g.Topo().CoEdges().Nb() > 0
    ceid = BRepGraph_CoEdgeId(0)
    eid = BRepGraph_Tool.CoEdge.EdgeOf_s(g, ceid)
    fid = BRepGraph_Tool.CoEdge.FaceOf_s(g, ceid)
    assert eid.IsValid()
    assert fid.IsValid()
    assert not g.Mesh().Persistent().Edges().HasPolygonOnTriangulation(eid, fid)

    tri = Poly_Triangulation(1, 1, False)
    g.Editor().Faces().SetPersistentTriangulation(fid, tri)
    poly = Poly_PolygonOnTriangulation(2, False)
    g.Editor().CoEdges().SetPersistentPolygonOnTri(ceid, poly)

    assert g.Mesh().Persistent().Edges().HasPolygonOnTriangulation(eid, fid)
    assert g.Mesh().Persistent().Edges().PolygonOnTriangulation(eid, fid) is poly


def test_BRepGraph_QuerySurfaceTest_Face_CachedTriangulation_DefaultEmpty(box_graph):
    for i in range(box_graph.Topo().Faces().Nb()):
        fid = BRepGraph_FaceId(i)
        assert not box_graph.Mesh().Cache().Faces().Has(fid)
        assert box_graph.Mesh().Cache().Faces().Triangulation(fid) is None


def test_BRepGraph_QuerySurfaceTest_Face_CachedTriangulation_SetAndRead(box_graph):
    assert box_graph.Topo().Faces().Nb() > 0
    fid = BRepGraph_FaceId(0)
    tri = Poly_Triangulation(1, 1, False)
    box_graph.Mesh().Editor().Faces().SetCachedTriangulation(fid, tri)
    assert box_graph.Mesh().Cache().Faces().Has(fid)
    assert box_graph.Mesh().Cache().Faces().Triangulation(fid) is tri


def test_BRepGraph_QuerySurfaceTest_Vertex_NbEdges_BoxVertexHasThreeEdges(box_graph):
    for i in range(box_graph.Topo().Vertices().Nb()):
        assert BRepGraph_Tool.Vertex.NbEdges_s(box_graph, BRepGraph_VertexId(i)) == 3


def test_BRepGraph_QuerySurfaceTest_Shell_IsClosed_BoxShellIsClosed(box_graph):
    assert box_graph.Topo().Shells().Nb() >= 1
    assert BRepGraph_Tool.Shell.IsClosed_s(box_graph, BRepGraph_ShellId.Start_s())


def test_BRepGraph_QuerySurfaceTest_Shell_NbFaces_BoxShellHasSixFaces(box_graph):
    assert box_graph.Topo().Shells().Nb() >= 1
    assert BRepGraph_Tool.Shell.NbFaces_s(box_graph, BRepGraph_ShellId.Start_s()) == 6
