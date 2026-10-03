# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_ReverseIterator_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgesOfEdge,
    BRepGraph_CompoundsOfChild,
    BRepGraph_CompoundsOfCoEdge,
    BRepGraph_CompoundsOfCompound,
    BRepGraph_CompoundsOfCompSolid,
    BRepGraph_CompoundsOfEdge,
    BRepGraph_CompoundsOfFace,
    BRepGraph_CompoundsOfShell,
    BRepGraph_CompoundsOfSolid,
    BRepGraph_CompoundsOfVertex,
    BRepGraph_CompoundsOfWire,
    BRepGraph_EdgeId,
    BRepGraph_EdgesOfVertex,
    BRepGraph_FaceId,
    BRepGraph_FacesOfWire,
    BRepGraph_NodeId,
    BRepGraph_OccurrencesOfChild,
    BRepGraph_RefsEdgesOfVertex,
    BRepGraph_RefsShellsOfFace,
    BRepGraph_ShellId,
    BRepGraph_ShellsOfFace,
    BRepGraph_SolidId,
    BRepGraph_SolidsOfShell,
    BRepGraph_VertexId,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.TopAbs import TopAbs_FORWARD
from nanocct.TopLoc import TopLoc_Location


def _count(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def _array(item_type, items):
    arr = NCollection_Array1[item_type](0, len(items) - 1)
    for i, item in enumerate(items):
        arr.SetValue(i, item)
    return arr


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def test_BRepGraph_ReverseIteratorTest_FacesOfEdge_BoxEdgeSharedByTwoFaces(graph):
    assert _count(graph.Topo().Edges().FacesOf(BRepGraph_EdgeId(0))) == 2


def test_BRepGraph_ReverseIteratorTest_EdgesOfVertex_BoxVertexSharedByThreeEdges(graph):
    edges = graph.Topo().Vertices().Edges(BRepGraph_VertexId(0))
    assert _count(BRepGraph_EdgesOfVertex(graph, edges)) == 3


def test_BRepGraph_ReverseIteratorTest_SolidsOfShell_BoxShellHasOneSolid(graph):
    rel = graph.Topo().Shells().Relations(BRepGraph_ShellId(0))
    refs = rel.ParentShellRefIds
    assert _count(BRepGraph_SolidsOfShell(graph, refs)) == 1


def test_BRepGraph_ReverseIteratorTest_ShellsOfFace_BoxFaceHasOneShell(graph):
    rel = graph.Topo().Faces().Relations(BRepGraph_FaceId(0))
    refs = rel.ParentFaceRefIds
    assert _count(BRepGraph_ShellsOfFace(graph, refs)) == 1


def test_BRepGraph_ReverseIteratorTest_FacesOfWire_BoxWireHasOneFace(graph):
    rel = graph.Topo().Wires().Relations(BRepGraph_WireId(0))
    refs = rel.ParentWireRefIds
    assert _count(BRepGraph_FacesOfWire(graph, refs)) == 1


def test_BRepGraph_ReverseIteratorTest_WiresOfEdge_BoxEdgeBelongsToTwoWires(graph):
    assert _count(graph.Topo().Edges().WiresOf(BRepGraph_EdgeId(0))) == 2


def test_BRepGraph_ReverseIteratorTest_SequentialIteration_SkipsRemovedParent(graph):
    edge = BRepGraph_EdgeId(0)
    faces = graph.Topo().Edges().FacesOf(edge)
    assert faces.More()
    first = faces.CurrentId()
    assert _count(graph.Topo().Edges().FacesOf(edge)) == 2
    graph.Editor().Gen().RemoveNode(first)
    assert _count(graph.Topo().Edges().FacesOf(edge)) == 1


def test_BRepGraph_ReverseIteratorTest_IndexedAccess_TracksActiveReverseBucket(graph):
    edge = BRepGraph_EdgeId(0)
    faces = graph.Topo().Edges().FacesOf(edge)
    assert faces.More()
    first = faces.CurrentId()
    assert _count(graph.Topo().Edges().FacesOf(edge)) == 2
    graph.Editor().Gen().RemoveNode(first)

    it = graph.Topo().Edges().FacesOf(edge)
    assert it.More()
    assert it.CurrentId().IsValid(graph.Topo().Faces().Nb())
    it.Next()
    assert not it.More()


def test_BRepGraph_ReverseIteratorTest_RangeFor_WorksCorrectly(graph):
    n = 0
    for face in graph.Topo().Edges().FacesOf(BRepGraph_EdgeId(0)):
        assert face.IsValid(graph.Topo().Faces().Nb())
        n += 1
    assert n == 2


def test_BRepGraph_ReverseIteratorTest_RefsShellsOfFace_ReturnsValidRefId(graph):
    rel = graph.Topo().Faces().Relations(BRepGraph_FaceId(0))
    refs = rel.ParentFaceRefIds
    it = BRepGraph_RefsShellsOfFace(graph, refs)
    assert it.More()
    assert it.CurrentParentId() == BRepGraph_ShellId(0)
    assert it.CurrentRefId().IsValid()


def test_BRepGraph_ReverseIteratorTest_RefsEdgesOfVertex_ReturnsValidRefId(graph):
    vertex = BRepGraph_VertexId(0)
    n = 0
    # Keep the edge vector alive: the Python binding returns a copy that the iterator only references.
    edges = graph.Topo().Vertices().Edges(vertex)
    it = BRepGraph_RefsEdgesOfVertex(graph, edges, vertex)
    while it.More():
        assert it.CurrentParentId().IsValid(graph.Topo().Edges().Nb())
        assert it.CurrentRefId().IsValid()
        n += 1
        it.Next()
    assert n == 3


def test_BRepGraph_ReverseIteratorTest_CoEdgesOfEdge_BoxEdgeHasCoEdges(graph):
    coedges = graph.Topo().Edges().CoEdges(BRepGraph_EdgeId(0))  # held: iterator references it
    assert _count(BRepGraph_CoEdgesOfEdge(graph, coedges)) == 2


def test_BRepGraph_ReverseIteratorTest_WiresOfCoEdge_BoxCoEdgeBelongsToOneWire(graph):
    assert graph.Topo().CoEdges().Wire(BRepGraph_CoEdgeId(0)).IsValid()


def test_BRepGraph_ReverseIteratorTest_Definition_ReturnsFaceDefinition(graph):
    it = graph.Topo().Edges().FacesOf(BRepGraph_EdgeId(0))
    assert it.More()
    face = it.CurrentId()
    assert not it.CurrentId().IsRemoved(graph)
    assert graph.Topo().Faces().Relations(face).WireRefIds.Size() >= 1


def test_BRepGraph_ReverseIteratorTest_Definition_ReturnsEdgeDefinition(graph):
    edges = graph.Topo().Vertices().Edges(BRepGraph_VertexId(0))
    it = BRepGraph_EdgesOfVertex(graph, edges)
    assert it.More()
    edge_def = it.Definition()
    assert not it.CurrentId().IsRemoved(graph)
    assert edge_def.StartVertexRefId.IsValid()
    assert edge_def.EndVertexRefId.IsValid()


def test_BRepGraph_ReverseIteratorTest_SkipsRemovedParent_EdgesOfVertex(graph):
    edges = graph.Topo().Vertices().Edges(BRepGraph_VertexId(0))
    assert edges.Size() == 3
    graph.Editor().Gen().RemoveNode(edges.Value(0))
    assert _count(BRepGraph_EdgesOfVertex(graph, edges)) == 2


def test_BRepGraph_ReverseIteratorTest_SkipsRemovedParent_AllRemoved(graph):
    edge = BRepGraph_EdgeId(0)
    faces = graph.Topo().Edges().FacesOf(edge)
    assert faces.More()
    first = faces.CurrentId()
    faces.Next()
    assert faces.More()
    second = faces.CurrentId()
    assert _count(graph.Topo().Edges().FacesOf(edge)) == 2
    graph.Editor().Gen().RemoveNode(first)
    graph.Editor().Gen().RemoveNode(second)
    assert _count(graph.Topo().Edges().FacesOf(edge)) == 0


def test_BRepGraph_ReverseIteratorTest_StartingIndex_SkipsToPosition(graph):
    edges = graph.Topo().Vertices().Edges(BRepGraph_VertexId(0))
    assert edges.Size() == 3
    assert _count(BRepGraph_EdgesOfVertex(graph, edges, 1)) == 2


def _expect_single_parent_of(cls, g, refs, expected):
    # refs must stay referenced while iterating (the iterator does not keep it alive)
    it = cls(g, refs)
    assert it.More()
    assert it.CurrentId() == expected
    it.Next()
    assert not it.More()


def test_BRepGraph_ReverseIteratorTest_CompoundsOfChild_AllTopologyKinds(graph):
    g = BRepGraph()
    g.Clear()
    ed = g.Editor()
    v0 = ed.Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    v1 = ed.Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    assert v0.IsValid()
    assert v1.IsValid()

    edge = ed.Edges().Add(v0, v1, None, 0.0, 1.0, 1.0e-7)
    assert edge.IsValid()

    wire = ed.Wires().Add(_array(BRepGraph_CoEdgeId, [ed.CoEdges().Add(edge, TopAbs_FORWARD)]))
    assert wire.IsValid()
    assert g.Topo().Edges().CoEdges(edge).Size() == 1
    coedge = g.Topo().Edges().CoEdges(edge).First()

    face = ed.Faces().Add(None, wire, NCollection_Array1[BRepGraph_WireId](), 1.0e-7)
    assert face.IsValid()
    shell = ed.Shells().Add()
    assert shell.IsValid()
    assert ed.Shells().Append(shell, face).IsValid()
    solid = ed.Solids().Add()
    assert solid.IsValid()
    assert ed.Solids().Append(solid, shell).IsValid()

    compsolid = ed.CompSolids().Add(_array(BRepGraph_SolidId, [solid]))
    assert compsolid.IsValid()

    nested = ed.Compounds().Add(_array(BRepGraph_NodeId, [BRepGraph_NodeId(solid)]))
    assert nested.IsValid()

    children = [v0, coedge, edge, wire, face, shell, solid, compsolid, nested]
    compound = ed.Compounds().Add(_array(BRepGraph_NodeId, [BRepGraph_NodeId(c) for c in children]))
    assert compound.IsValid()

    gen = g.Topo().Gen()
    _expect_single_parent_of(BRepGraph_CompoundsOfVertex, g, gen.CompoundRefIds(BRepGraph_NodeId(v0)), compound)
    _expect_single_parent_of(BRepGraph_CompoundsOfCoEdge, g, gen.CompoundRefIds(BRepGraph_NodeId(coedge)), compound)
    _expect_single_parent_of(BRepGraph_CompoundsOfEdge, g, gen.CompoundRefIds(BRepGraph_NodeId(edge)), compound)
    _expect_single_parent_of(BRepGraph_CompoundsOfWire, g, gen.CompoundRefIds(BRepGraph_NodeId(wire)), compound)
    _expect_single_parent_of(BRepGraph_CompoundsOfFace, g, gen.CompoundRefIds(BRepGraph_NodeId(face)), compound)
    _expect_single_parent_of(BRepGraph_CompoundsOfShell, g, gen.CompoundRefIds(BRepGraph_NodeId(shell)), compound)

    solid_refs = gen.CompoundRefIds(BRepGraph_NodeId(solid))
    solid_parents = BRepGraph_CompoundsOfSolid(g, solid_refs)
    assert solid_parents.More()
    assert solid_parents.CurrentId() == nested
    solid_parents.Next()
    assert solid_parents.More()
    assert solid_parents.CurrentId() == compound
    solid_parents.Next()
    assert not solid_parents.More()

    _expect_single_parent_of(BRepGraph_CompoundsOfCompSolid, g, gen.CompoundRefIds(BRepGraph_NodeId(compsolid)), compound)
    _expect_single_parent_of(BRepGraph_CompoundsOfCompound, g, gen.CompoundRefIds(BRepGraph_NodeId(nested)), compound)
    _expect_single_parent_of(BRepGraph_CompoundsOfChild, g, gen.CompoundRefIds(coedge), compound)
    _expect_single_parent_of(BRepGraph_FacesOfWire, g, g.Topo().Wires().Relations(wire).ParentWireRefIds, face)


def test_BRepGraph_ReverseIteratorTest_OccurrencesOfChild_ProductAndTopologyChildren(graph):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape())
    assert not g.IsEmpty()

    compound = g.Editor().Compounds().Add(
        _array(BRepGraph_NodeId, [BRepGraph_NodeId(BRepGraph_SolidId.Start_s())])
    )
    assert compound.IsValid()

    products = g.Editor().Products()
    part = products.Add(compound)
    products.AppendDocumentRoot(part)
    assert part.IsValid()
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert assembly.IsValid()
    part_occ = products.Append(assembly, part, TopLoc_Location())
    assert part_occ.IsValid()

    occ_refs = g.Topo().Gen().OccurrenceRefIds(compound)
    topo_occs = BRepGraph_OccurrencesOfChild(g, occ_refs)
    assert topo_occs.More()
    compound_occ = topo_occs.CurrentId()
    assert compound_occ.IsValid()
    assert g.Topo().Occurrences().Definition(compound_occ).ChildNodeId == BRepGraph_NodeId(compound)
    topo_occs.Next()
    assert not topo_occs.More()

    _expect_single_parent_of(BRepGraph_OccurrencesOfChild, g, g.Topo().Gen().OccurrenceRefIds(part), part_occ)
