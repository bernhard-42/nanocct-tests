# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_RelatedIterator_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest
from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CompoundId,
    BRepGraph_CompoundIterator,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_RelatedIterator,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_VertexId,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Trsf, gp_Vec
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound

Rel = BRepGraph_RelatedIterator.RelationKind


def _has_related_node(g, source, node, relation):
    it = BRepGraph_RelatedIterator(g, source)
    while it.More():
        if it.Current() == node and it.CurrentRelation() == relation:
            return True
        it.Next()
    return False


def _count_relations(g, node, relation):
    n = 0
    it = BRepGraph_RelatedIterator(g, node)
    while it.More():
        if it.CurrentRelation() == relation:
            n += 1
        it.Next()
    return n


def _related(g, node, relation):
    out = []
    it = BRepGraph_RelatedIterator(g, node)
    while it.More():
        if it.CurrentRelation() == relation:
            out.append(it.Current())
        it.Next()
    return out


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def test_BRepGraph_RelatedIteratorTest_FaceOfBox_ReturnsBoundaryEdgesAndOuterWire(graph):
    face = BRepGraph_NodeId(BRepGraph_FaceId(0))
    assert _count_relations(graph, face, Rel.BoundaryEdge) == 4
    assert _count_relations(graph, face, Rel.AdjacentFace) == 4
    assert _count_relations(graph, face, Rel.OuterWire) == 1
    assert _has_related_node(graph, face, BRepGraph_NodeId(BRepGraph_WireId.Start_s()), Rel.OuterWire)


def test_BRepGraph_RelatedIteratorTest_EdgeOfBox_ReturnsIncidentVerticesAndFaces(graph):
    edge = BRepGraph_NodeId(BRepGraph_EdgeId(0))
    assert _count_relations(graph, edge, Rel.IncidentVertex) == 2
    assert _count_relations(graph, edge, Rel.ReferencedByFace) == 2


def test_BRepGraph_RelatedIteratorTest_AssemblyNodes_YieldNoRelations(graph):
    products = graph.Editor().Products()
    part = products.Add(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    products.AppendDocumentRoot(part)
    root = products.Add()
    products.AppendDocumentRoot(root)
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    occ = products.Append(root, part, TopLoc_Location(t))
    assert occ.IsValid()
    assert not BRepGraph_RelatedIterator(graph, BRepGraph_NodeId(root)).More()
    assert not BRepGraph_RelatedIterator(graph, BRepGraph_NodeId(occ)).More()


def test_BRepGraph_RelatedIteratorTest_InvalidNode_ReturnsEmpty(graph):
    assert not BRepGraph_RelatedIterator(graph, BRepGraph_NodeId()).More()


def test_BRepGraph_RelatedIteratorTest_EdgeReferencedByFace_RemovedFaceIsSkipped(graph):
    edge = BRepGraph_EdgeId(0)
    face_it = graph.Topo().Edges().FacesOf(edge)
    assert face_it.More()
    removed = face_it.CurrentId()
    face_it.Next()
    assert face_it.More()
    survivor = face_it.CurrentId()
    face_it.Next()
    assert not face_it.More()

    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(removed))

    edge_node = BRepGraph_NodeId(edge)
    assert _count_relations(graph, edge_node, Rel.ReferencedByFace) == 1
    assert _has_related_node(graph, edge_node, BRepGraph_NodeId(survivor), Rel.ReferencedByFace)


def test_BRepGraph_RelatedIteratorTest_ContainerNodes_YieldNoRelations(graph):
    assert not BRepGraph_RelatedIterator(graph, BRepGraph_NodeId(BRepGraph_SolidId.Start_s())).More()
    assert not BRepGraph_RelatedIterator(graph, BRepGraph_NodeId(BRepGraph_ShellId.Start_s())).More()


def test_BRepGraph_RelatedIteratorTest_WireOfBox_ReturnsCoEdges(graph):
    assert _count_relations(graph, BRepGraph_NodeId(BRepGraph_WireId(0)), Rel.WireCoEdge) == 4


def test_BRepGraph_RelatedIteratorTest_WireOfBox_ReturnsOwningFace(graph):
    assert _count_relations(graph, BRepGraph_NodeId(BRepGraph_WireId(0)), Rel.OwningFace) == 1


def test_BRepGraph_RelatedIteratorTest_VertexOfBox_ReturnsIncidentEdges(graph):
    assert _count_relations(graph, BRepGraph_NodeId(BRepGraph_VertexId(0)), Rel.IncidentEdge) == 3


def test_BRepGraph_RelatedIteratorTest_CoEdgeOfBox_ReturnsParentEdgeAndOwningFace(graph):
    coedge = BRepGraph_NodeId(BRepGraph_CoEdgeId(0))
    assert _count_relations(graph, coedge, Rel.ParentEdge) == 1
    assert _count_relations(graph, coedge, Rel.OwningFace) == 1


def test_BRepGraph_RelatedIteratorStandalone_Compound_YieldsNoRelations():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    bb.Add(comp, BRepPrimAPI_MakeBox(20.0, 20.0, 20.0).Shape())
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(comp)
    assert not g.IsEmpty()

    compound = BRepGraph_CompoundId()
    it = BRepGraph_CompoundIterator(g)
    if it.More():
        compound = it.CurrentId()
    assert compound.IsValid()
    assert not BRepGraph_RelatedIterator(g, BRepGraph_NodeId(compound)).More()


def test_BRepGraph_RelatedIteratorTest_RangeFor_WorksCorrectly(graph):
    n = 0
    for node in BRepGraph_RelatedIterator(graph, BRepGraph_NodeId(BRepGraph_FaceId(0))):
        assert node.IsValid()
        n += 1
    assert n >= 9


def test_BRepGraph_RelatedIteratorTest_EdgeOfBox_AllRelationsSequential(graph):
    edge = BRepGraph_NodeId(BRepGraph_EdgeId(0))
    faces = _related(graph, edge, Rel.ReferencedByFace)
    vertices = _related(graph, edge, Rel.IncidentVertex)
    assert len(faces) == 2
    assert len(vertices) == 2
    assert faces[0] != faces[1]
    assert vertices[0] != vertices[1]


def test_BRepGraph_RelatedIteratorTest_EdgeOfBox_RemovedFace_CorrectTransition(graph):
    edge = BRepGraph_EdgeId(0)
    face_it = graph.Topo().Edges().FacesOf(edge)
    assert face_it.More()
    removed = face_it.CurrentId()
    face_it.Next()
    assert face_it.More()
    face_it.Next()
    assert not face_it.More()
    graph.Editor().Gen().RemoveNode(removed)

    edge_node = BRepGraph_NodeId(edge)
    assert _count_relations(graph, edge_node, Rel.ReferencedByFace) == 1
    assert _count_relations(graph, edge_node, Rel.IncidentVertex) == 2


def test_BRepGraph_RelatedIteratorTest_VertexOfBox_AllParentEdgesYielded(graph):
    edges = _related(graph, BRepGraph_NodeId(BRepGraph_VertexId(0)), Rel.IncidentEdge)
    assert len(edges) == 3
    for i in range(len(edges)):
        for j in range(i + 1, len(edges)):
            assert edges[i] != edges[j]
