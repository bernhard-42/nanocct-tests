# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_ReplaceVertex_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepGraph import BRepGraph, BRepGraph_EdgeId, BRepGraph_NodeId, BRepGraph_Validate
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt


def _make_box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _lightweight_ok(g):
    return BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Lightweight_s()).IsValid()


def test_BRepGraph_ReplaceVertexTest_StartVertex_SwappedToFreshVertex_AuditClean():
    g = _make_box_graph()
    assert not g.IsEmpty()
    assert g.Topo().Edges().Nb() > 0

    edge = BRepGraph_EdgeId(0)
    old_start = g.Topo().Edges().Definition(edge).StartVertexRefId
    assert old_start.IsValid()

    new_vertex = g.Editor().Vertices().Add(gp_Pnt(99.0, 99.0, 99.0), 1.0e-7)
    assert new_vertex.IsValid()

    new_ref = g.Editor().Edges().ReplaceVertex(edge, old_start, new_vertex)
    assert new_ref.IsValid()
    assert new_ref != old_start
    assert g.Topo().Edges().Definition(edge).StartVertexRefId == new_ref
    assert old_start.IsRemoved(g)
    assert g.Refs().Vertices().Entry(new_ref).ChildVertexId == new_vertex
    assert _lightweight_ok(g)


def test_BRepGraph_ReplaceVertexTest_EndVertex_SwappedToFreshVertex_PreservesOrientation():
    g = _make_box_graph()
    assert not g.IsEmpty()

    edge = BRepGraph_EdgeId(0)
    old_end = g.Topo().Edges().Definition(edge).EndVertexRefId
    assert old_end.IsValid()
    expected_reversed = g.Refs().Vertices().Entry(old_end).Orientation.IsReversed

    new_vertex = g.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 1.0e-7)
    new_ref = g.Editor().Edges().ReplaceVertex(edge, old_end, new_vertex)
    assert new_ref.IsValid()

    assert g.Refs().Vertices().Entry(new_ref).Orientation.IsReversed == expected_reversed
    assert _lightweight_ok(g)


def test_BRepGraph_ReplaceVertexTest_SameVertex_Idempotent():
    g = _make_box_graph()
    assert not g.IsEmpty()

    edge = BRepGraph_EdgeId(0)
    old_start = g.Topo().Edges().Definition(edge).StartVertexRefId
    same_vertex = g.Refs().Vertices().Entry(old_start).ChildVertexId

    result = g.Editor().Edges().ReplaceVertex(edge, old_start, same_vertex)
    assert result == old_start
    assert not old_start.IsRemoved(g)


def test_BRepGraph_ReplaceVertexTest_InactiveEdge_Rejected():
    g = _make_box_graph()
    assert not g.IsEmpty()

    edge = BRepGraph_EdgeId(0)
    old_ref = g.Topo().Edges().Definition(edge).StartVertexRefId
    new_vertex = g.Editor().Vertices().Add(gp_Pnt(5.0, 5.0, 5.0), 1.0e-7)

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(edge))

    result = g.Editor().Edges().ReplaceVertex(edge, old_ref, new_vertex)
    assert not result.IsValid()


def test_BRepGraph_ReplaceVertexTest_WrongParent_Rejected():
    g = _make_box_graph()
    assert not g.IsEmpty()
    assert g.Topo().Edges().Nb() > 1

    edge0 = BRepGraph_EdgeId(0)
    edge1_start = g.Topo().Edges().Definition(BRepGraph_EdgeId(1)).StartVertexRefId
    assert edge1_start.IsValid()

    new_vertex = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 100.0), 1.0e-7)
    result = g.Editor().Edges().ReplaceVertex(edge0, edge1_start, new_vertex)
    assert not result.IsValid()


def test_BRepGraph_ReplaceVertexTest_Relations_Rebuilt_VertexToEdge():
    g = _make_box_graph()
    assert not g.IsEmpty()

    edge = BRepGraph_EdgeId(0)
    old_ref = g.Topo().Edges().Definition(edge).StartVertexRefId
    old_vertex = g.Refs().Vertices().Entry(old_ref).ChildVertexId

    new_vertex = g.Editor().Vertices().Add(gp_Pnt(1000.0, 0.0, 0.0), 1.0e-7)
    assert g.Editor().Edges().ReplaceVertex(edge, old_ref, new_vertex).IsValid()

    assert any(e == edge for e in g.Topo().Vertices().Edges(new_vertex))
    assert not any(e == edge for e in g.Topo().Vertices().Edges(old_vertex))
    assert _lightweight_ok(g)
