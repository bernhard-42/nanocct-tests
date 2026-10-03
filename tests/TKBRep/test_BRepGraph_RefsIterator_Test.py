# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_RefsIterator_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgesOfWire,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_RefsChildOfCompound,
    BRepGraph_RefsFaceOfShell,
    BRepGraph_RefsOccurrenceOfProduct,
    BRepGraph_RefsShellOfSolid,
    BRepGraph_RefsVertexOfEdge,
    BRepGraph_RefsWireOfFace,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Plane
from nanocct.gp import gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_INTERNAL, TopAbs_REVERSED
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Face, TopoDS_Vertex, TopoDS_Wire

K = BRepGraph_NodeId.Kind


def _count(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def _node_array(items):
    arr = NCollection_Array1[BRepGraph_NodeId](0, len(items) - 1)
    for i, item in enumerate(items):
        arr.SetValue(i, BRepGraph_NodeId(item))
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
    face = TopoDS_Face()
    bb.MakeFace(face, Geom_Plane(gp_Pln()), Precision.Confusion_s())
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


def test_BRepGraph_RefsIteratorTest_BoxHierarchy_YieldsReferenceIds(graph):
    assert _count(BRepGraph_RefsShellOfSolid(graph, BRepGraph_SolidId.Start_s())) == 1
    assert _count(BRepGraph_RefsFaceOfShell(graph, BRepGraph_ShellId.Start_s())) == 6
    assert _count(BRepGraph_RefsWireOfFace(graph, BRepGraph_FaceId.Start_s())) == 1
    assert _count(BRepGraph_CoEdgesOfWire(graph, BRepGraph_WireId.Start_s())) == 4
    assert _count(BRepGraph_RefsVertexOfEdge(graph, BRepGraph_EdgeId.Start_s())) == 2


def test_BRepGraph_RefsIteratorTest_CurrentId_ResolvesToExpectedEntry(graph):
    it = BRepGraph_RefsWireOfFace(graph, BRepGraph_FaceId.Start_s())
    assert it.More()
    wire_ref = graph.Refs().Wires().Entry(it.CurrentId())
    assert wire_ref.ChildWireId.IsValid(graph.Topo().Wires().Nb())


def test_BRepGraph_RefsIteratorTestStandalone_VertexOfEdge_ExposesBoundaryVertexRefsOnly():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(_wrap_edge_in_face(_make_edge_with_internal_vertex()))

    found_internal = False
    n = 0
    it = BRepGraph_RefsVertexOfEdge(g, BRepGraph_EdgeId.Start_s())
    while it.More():
        n += 1
        vertex_ref = g.Refs().Vertices().Entry(it.CurrentId())
        # C++ compares through ParityOrientation's implicit TopAbs_Orientation conversion.
        ori = TopAbs_REVERSED if vertex_ref.Orientation.IsReversed else TopAbs_FORWARD
        if ori == TopAbs_INTERNAL:
            found_internal = True
        it.Next()
    assert n == 2
    assert not found_internal


def test_BRepGraph_RefsIteratorTest_ChildOfCompound_EnumeratesChildRefs(graph):
    loose = graph.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.01)
    assert loose.IsValid()
    compound = graph.Editor().Compounds().Add(_node_array([BRepGraph_SolidId.Start_s(), loose]))
    assert compound.IsValid()
    it = BRepGraph_RefsChildOfCompound(graph, compound)
    assert it.More()
    assert graph.Refs().Children().Entry(it.CurrentId()).ChildNodeId.NodeKind == K.Solid
    it.Next()
    assert it.More()
    assert graph.Refs().Children().Entry(it.CurrentId()).ChildNodeId.NodeKind == K.Vertex


def test_BRepGraph_RefsIteratorTest_ChildOfCompound_SkipsOutOfRangeChildNode(graph):
    loose = graph.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.01)
    assert loose.IsValid()
    compound = graph.Editor().Compounds().Add(_node_array([BRepGraph_SolidId.Start_s(), loose, loose]))
    assert compound.IsValid()

    rel = graph.Topo().Compounds().Relations(compound)
    child_refs = rel.ChildRefIds
    assert child_refs.Size() == 3
    bad_ref = graph.Editor().Gen().MutChildRef(child_refs.Value(1))
    bad_ref.Internal().ChildNodeId = BRepGraph_NodeId(K.Vertex, graph.Topo().Vertices().Nb())
    del bad_ref

    n = 0
    it = BRepGraph_RefsChildOfCompound(graph, compound)
    while it.More():
        child = graph.Refs().Children().Entry(it.CurrentId()).ChildNodeId
        assert graph.Topo().Gen().IsActive(child)
        n += 1
        it.Next()
    assert n == 2


def test_BRepGraph_RefsIteratorTest_ChildOfCompound_SkipsRemovedChildNode(graph):
    loose = graph.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.01)
    assert loose.IsValid()
    compound = graph.Editor().Compounds().Add(_node_array([BRepGraph_SolidId.Start_s(), loose]))
    assert compound.IsValid()
    graph.Editor().Gen().RemoveNode(loose)
    assert BRepGraph_RefsChildOfCompound(graph, compound).More()
    assert _count(BRepGraph_RefsChildOfCompound(graph, compound)) == 1


def test_BRepGraph_RefsIteratorTest_OccurrenceOfProduct_EnumeratesOccurrenceRefs(graph):
    products = graph.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()
    assert products.Append(assembly, part, TopLoc_Location()).IsValid()
    assert products.Append(assembly, part, TopLoc_Location()).IsValid()
    assert _count(BRepGraph_RefsOccurrenceOfProduct(graph, assembly)) == 2


def test_BRepGraph_RefsIteratorTest_RemovedWireRef_IsSkipped(graph):
    wire_refs = graph.Refs().Wires().IdsOf(BRepGraph_FaceId.Start_s())
    assert wire_refs.Size() == 1
    graph.Editor().Gen().RemoveRef(wire_refs.Value(0))
    assert _count(BRepGraph_RefsWireOfFace(graph, BRepGraph_FaceId.Start_s())) == 0
