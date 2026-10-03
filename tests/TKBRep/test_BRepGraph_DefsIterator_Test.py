# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_DefsIterator_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CompSolidId,
    BRepGraph_DefsChildOfCompound,
    BRepGraph_DefsCoEdgeOfWire,
    BRepGraph_DefsEdgeOfWire,
    BRepGraph_DefsFaceOfShell,
    BRepGraph_DefsOccurrenceOfProduct,
    BRepGraph_DefsShellOfSolid,
    BRepGraph_DefsSolidOfCompSolid,
    BRepGraph_DefsVertexOfEdge,
    BRepGraph_DefsWireOfFace,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Plane
from nanocct.gp import gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_INTERNAL
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Face, TopoDS_Vertex, TopoDS_Wire

K = BRepGraph_NodeId.Kind


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


def _make_edge_with_internal_vertex():
    bb = BRep_Builder()
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0)).Edge()
    internal = TopoDS_Vertex()
    bb.MakeVertex(internal, gp_Pnt(5, 0, 0), Precision.Confusion_s())
    bb.Add(edge, internal.Oriented(TopAbs_INTERNAL))
    return edge


def _wrap_edge_in_face(edge):
    bb = BRep_Builder()
    plane = Geom_Plane(gp_Pln())
    face = TopoDS_Face()
    bb.MakeFace(face, plane, Precision.Confusion_s())
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    bb.Add(wire, edge)
    bb.Add(face, wire)
    return face


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g



def test_BRepGraph_DefsIteratorTest_BoxHierarchy_TraversesSingleLevelChildren(graph):
    assert _count(BRepGraph_DefsShellOfSolid(graph, BRepGraph_SolidId.Start_s())) == 1
    assert _count(BRepGraph_DefsFaceOfShell(graph, BRepGraph_ShellId.Start_s())) == 6
    assert _count(BRepGraph_DefsWireOfFace(graph, BRepGraph_FaceId.Start_s())) == 1
    assert _count(BRepGraph_DefsEdgeOfWire(graph, BRepGraph_WireId.Start_s())) == 4
    assert _count(BRepGraph_DefsCoEdgeOfWire(graph, BRepGraph_WireId.Start_s())) == 4
    assert _count(BRepGraph_DefsVertexOfEdge(graph, BRepGraph_EdgeId.Start_s())) == 2


def test_BRepGraph_DefsIteratorTest_EdgeOfWire_YieldsEdgeDefinitions(graph):
    it = BRepGraph_DefsEdgeOfWire(graph, BRepGraph_WireId.Start_s())
    assert it.More()
    edge = it.CurrentId()
    coedge = it.CurrentRefId()
    assert edge.IsValid(graph.Topo().Edges().Nb())
    assert coedge.IsValid(graph.Topo().CoEdges().Nb())
    assert graph.Topo().CoEdges().Definition(coedge).ChildEdgeId == edge
    assert it.Current().StartVertexRefId.IsValid()
    assert it.Current().EndVertexRefId.IsValid()


def test_BRepGraph_DefsIteratorTest_CoEdgeOfWire_YieldsCoEdgeDefinitions(graph):
    it = BRepGraph_DefsCoEdgeOfWire(graph, BRepGraph_WireId.Start_s())
    assert it.More()
    assert it.CurrentId().IsValid(graph.Topo().CoEdges().Nb())
    assert it.CurrentRefId() == it.CurrentId()
    assert it.Current().ChildEdgeId.IsValid(graph.Topo().Edges().Nb())


def test_BRepGraph_DefsIteratorTest_VertexOfEdge_ExposesBoundaryVertexRef(graph):
    it = BRepGraph_DefsVertexOfEdge(graph, BRepGraph_EdgeId.Start_s())
    assert it.More()
    vertex = it.CurrentId()
    ref = it.CurrentRefId()
    assert vertex.IsValid(graph.Topo().Vertices().Nb())
    assert ref.IsValid(graph.Refs().Vertices().Nb())
    assert graph.Refs().Vertices().Entry(ref).ChildVertexId == vertex


def test_BRepGraph_DefsIteratorTestStandalone_VertexOfEdge_EnumeratesBoundaryVerticesOnly():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(_wrap_edge_in_face(_make_edge_with_internal_vertex()))

    found_split = False
    n = 0
    it = BRepGraph_DefsVertexOfEdge(g, BRepGraph_EdgeId.Start_s())
    while it.More():
        n += 1
        if abs(it.Current().Point.X() - 5.0) <= Precision.Confusion_s():
            found_split = True
        it.Next()
    assert n == 2
    assert not found_split


def _add_compound(g, children):
    return g.Editor().Compounds().Add(_array(BRepGraph_NodeId, [BRepGraph_NodeId(c) for c in children]))


def test_BRepGraph_DefsIteratorTest_ChildOfCompound_EnumeratesHeterogeneousChildren(graph):
    loose = graph.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.01)
    assert loose.IsValid()
    compound = _add_compound(graph, [BRepGraph_SolidId.Start_s(), loose])
    assert compound.IsValid()
    it = BRepGraph_DefsChildOfCompound(graph, compound)
    assert it.More()
    assert it.CurrentId().NodeKind == K.Solid
    it.Next()
    assert it.More()
    assert it.CurrentId().NodeKind == K.Vertex


def test_BRepGraph_DefsIteratorTest_ChildOfCompound_SkipsOutOfRangeChildNode(graph):
    loose = graph.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.01)
    assert loose.IsValid()
    compound = _add_compound(graph, [BRepGraph_SolidId.Start_s(), loose, loose])
    assert compound.IsValid()

    rel = graph.Topo().Compounds().Relations(compound)
    child_refs = rel.ChildRefIds
    assert child_refs.Size() == 3
    bad_ref = graph.Editor().Gen().MutChildRef(child_refs.Value(1))
    bad_ref.Internal().ChildNodeId = BRepGraph_NodeId(K.Vertex, graph.Topo().Vertices().Nb())
    del bad_ref

    n = 0
    it = BRepGraph_DefsChildOfCompound(graph, compound)
    while it.More():
        assert graph.Topo().Gen().IsActive(it.CurrentId())
        n += 1
        it.Next()
    assert n == 2


def test_BRepGraph_DefsIteratorTest_ChildOfCompound_SkipsRemovedChildNode(graph):
    loose = graph.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.01)
    assert loose.IsValid()
    compound = _add_compound(graph, [BRepGraph_SolidId.Start_s(), loose])
    assert compound.IsValid()
    graph.Editor().Gen().RemoveNode(loose)
    assert BRepGraph_DefsChildOfCompound(graph, compound).More()
    assert _count(BRepGraph_DefsChildOfCompound(graph, compound)) == 1


def test_BRepGraph_DefsIteratorTest_SolidOfCompSolid_EnumeratesDirectSolids(graph):
    solid_a = graph.Editor().Solids().Add()
    solid_b = graph.Editor().Solids().Add()
    assert solid_a.IsValid()
    assert solid_b.IsValid()
    compsolid = graph.Editor().CompSolids().Add(_array(BRepGraph_SolidId, [solid_a, solid_b]))
    assert isinstance(compsolid, BRepGraph_CompSolidId)
    assert compsolid.IsValid()
    assert _count(BRepGraph_DefsSolidOfCompSolid(graph, compsolid)) == 2


def test_BRepGraph_DefsIteratorTest_OccurrenceOfProduct_EnumeratesDirectOccurrences(graph):
    products = graph.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()
    assert products.Append(assembly, part, TopLoc_Location()).IsValid()
    assert products.Append(assembly, part, TopLoc_Location()).IsValid()
    assert _count(BRepGraph_DefsOccurrenceOfProduct(graph, assembly)) == 2


def test_BRepGraph_DefsIteratorTest_RemovedWireRef_IsSkipped(graph):
    wire_refs = graph.Refs().Wires().IdsOf(BRepGraph_FaceId.Start_s())
    assert wire_refs.Size() == 1
    graph.Editor().Gen().RemoveRef(wire_refs.Value(0))
    assert _count(BRepGraph_DefsWireOfFace(graph, BRepGraph_FaceId.Start_s())) == 0
