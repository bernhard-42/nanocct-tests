# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Convenience_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CompoundId,
    BRepGraph_CompSolidId,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_NodeId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
    BRepGraph_VertexId,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def test_BRepGraph_ConvenienceTest_NodeId_Factories_CorrectKindAndIndex():
    K = BRepGraph_NodeId.Kind
    cases = [
        (BRepGraph_SolidId(3), K.Solid, 3),
        (BRepGraph_ShellId(5), K.Shell, 5),
        (BRepGraph_FaceId.Start_s(), K.Face, 0),
        (BRepGraph_WireId(2), K.Wire, 2),
        (BRepGraph_EdgeId(7), K.Edge, 7),
        (BRepGraph_VertexId(1), K.Vertex, 1),
        (BRepGraph_CompoundId.Start_s(), K.Compound, 0),
        (BRepGraph_CompSolidId.Start_s(), K.CompSolid, 0),
    ]
    for typed, kind, index in cases:
        node = BRepGraph_NodeId(typed)
        assert node.NodeKind == kind
        assert node.Index == index


def test_BRepGraph_ConvenienceTest_NodeId_Factories_EqualToConstructor():
    assert BRepGraph_FaceId(3) == BRepGraph_NodeId(BRepGraph_NodeId.Kind.Face, 3)
    assert BRepGraph_EdgeId.Start_s() == BRepGraph_NodeId(BRepGraph_NodeId.Kind.Edge, 0)


def test_BRepGraph_ConvenienceTest_EdgeDef_StartVertex_Valid(graph):
    assert graph.Topo().Edges().Nb() > 0
    assert BRepGraph_Tool.Edge.StartVertexId_s(graph, BRepGraph_EdgeId(0)).IsValid()


def test_BRepGraph_ConvenienceTest_EdgeDef_EndVertex_Valid(graph):
    assert graph.Topo().Edges().Nb() > 0
    assert BRepGraph_Tool.Edge.EndVertexId_s(graph, BRepGraph_EdgeId(0)).IsValid()


def test_BRepGraph_ConvenienceTest_EdgeDef_StartEnd_DifferForNonClosed(graph):
    eid = BRepGraph_EdgeId(0)
    if not BRepGraph_Tool.Edge.IsClosed_s(graph, eid):
        assert BRepGraph_Tool.Edge.StartVertexId_s(graph, eid) != BRepGraph_Tool.Edge.EndVertexId_s(graph, eid)


def test_BRepGraph_ConvenienceTest_EdgeDef_RefIds_AreValid(graph):
    edge = graph.Topo().Edges().Definition(BRepGraph_EdgeId(0))
    assert edge.StartVertexRefId.IsValid()
    assert edge.EndVertexRefId.IsValid()


def _usages(graph, eid):
    start = BRepGraph_Tool.Vertex.Usage_s(graph, BRepGraph_Tool.Edge.StartVertexId_s(graph, eid))
    end = BRepGraph_Tool.Vertex.Usage_s(graph, BRepGraph_Tool.Edge.EndVertexId_s(graph, eid))
    assert start.IsValid()
    assert end.IsValid()
    return start, end


def test_BRepGraph_ConvenienceTest_EdgeOps_FindByVertices_FindsDirectedEdge(graph):
    eid = BRepGraph_EdgeId(0)
    start, end = _usages(graph, eid)
    assert BRepGraph_Tool.Edge.FindByVertices_s(graph, start.DefId, end.DefId) == eid


def test_BRepGraph_ConvenienceTest_EdgeOps_FindByVertices_ReverseRequiresExplicitFlag(graph):
    eid = BRepGraph_EdgeId(0)
    start, end = _usages(graph, eid)
    assert start.DefId != end.DefId
    assert not BRepGraph_Tool.Edge.FindByVertices_s(graph, end.DefId, start.DefId).IsValid()
    assert BRepGraph_Tool.Edge.FindByVertices_s(graph, end.DefId, start.DefId, True) == eid


def test_BRepGraph_ConvenienceTest_FaceSurface_Valid(graph):
    assert graph.Topo().Faces().Nb() > 0
    assert graph.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SurfaceRepId.IsValid()


def test_BRepGraph_ConvenienceTest_FaceSurface_AllBoxFaces(graph):
    count = 0
    for face in BRepGraph_FaceIterator(graph):
        assert face.SurfaceRepId.IsValid()
        count += 1
    assert count == 6


def test_BRepGraph_ConvenienceTest_FindPCurveCoEdgeId_ValidPair(graph):
    edge_ids = _ids(BRepGraph_EdgeIterator(graph))
    for fid in _ids(BRepGraph_FaceIterator(graph)):
        for eid in edge_ids:
            ceid = BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(graph, eid, fid)
            if ceid.IsValid():
                assert graph.Topo().CoEdges().Definition(ceid).Curve2DRepId.IsValid()
                return


def test_BRepGraph_ConvenienceTest_FindPCurveCoEdgeId_InvalidPair_ReturnsNull(graph):
    ceid = BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(graph, BRepGraph_EdgeId.Start_s(), BRepGraph_FaceId(9999))
    assert not ceid.IsValid()


def test_BRepGraph_ConvenienceTest_ShellFaceRefs_Box_SixFaces(graph):
    assert graph.Topo().Shells().Nb() == 1
    assert graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s()).Size() == 6


def test_BRepGraph_ConvenienceTest_ShellFaceRefs_AllValid(graph):
    refs = graph.Refs()
    ids = refs.Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert ids.Size() == 6
    for ref_id in ids:
        assert refs.Faces().Entry(ref_id).ChildFaceId.IsValid()


def test_BRepGraph_ConvenienceTest_ShellFaceRefs_InvalidShell_Empty(graph):
    assert graph.Refs().Faces().IdsOf(BRepGraph_ShellId(100)).Size() == 0


def test_BRepGraph_ConvenienceTest_ShapesView_RemoveShape_RemovesFoundNode(graph):
    assert graph.Topo().Faces().Nb() > 0
    fid = BRepGraph_FaceId.Start_s()
    face = graph.Shapes().Original(fid)
    assert not face.IsNull()
    assert graph.Shapes().FindNode(face).IsValid()
    assert graph.Shapes().RemoveShape(face)
    assert not graph.Shapes().FindNode(face).IsValid()
    assert graph.Topo().Gen().IsRemoved(fid)
    assert not graph.Shapes().RemoveShape(face)


def test_BRepGraph_ConvenienceTest_FindPCurveCoEdgeId_WithOrientation_SeamEdge():
    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    assert res.IsOk()
    topo = g.Topo()
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ceid in topo.Edges().CoEdges(eid):
            if not BRepGraph_Tool.CoEdge.IsSeam_s(g, ceid):
                continue
            fid = topo.CoEdges().Definition(ceid).FaceId
            pcf = BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, fid, TopAbs_FORWARD)
            pcr = BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, fid, TopAbs_REVERSED)
            assert pcf.IsValid()
            assert pcr.IsValid()
            assert pcf != pcr
            return
    pytest.fail("no seam edge found on cylinder")
