# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_LayerHistory_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Not translated: the tests driven by Editor().Gen().ApplyModification (a C++ lambda modifier; not bound).
# LayerRegistry().Ensure<BRepGraph_LayerHistory>() maps to FindLayer(GetID_s()) (+ RegisterLayer when absent).

import pytest

from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_LayerHistory,
    BRepGraph_NodeId,
    BRepGraph_Tool,
    BRepGraph_UID,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.BRepTools import BRepTools_History
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_DataMap
from nanocct.TCollection import TCollection_AsciiString
from nanocct.TopoDS import TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher

Kind = BRepGraph_NodeId.Kind
HKind = BRepGraph_LayerHistory.Kind


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _hist(g):
    reg = g.LayerRegistry()
    layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    if layer is None:
        layer = BRepGraph_LayerHistory()
        reg.RegisterLayer(layer)
    return layer


def _arr(T, items):
    if len(items) == 0:
        return NCollection_Array1[T]()
    a = NCollection_Array1[T](0, len(items) - 1)
    for i, v in enumerate(items):
        a[i] = v
    return a


def _nodes(*items):
    return _arr(BRepGraph_NodeId, list(items))


def _uids(*items):
    return _arr(BRepGraph_UID, list(items))


def _shape_map():
    return NCollection_DataMap[TopoDS_Shape, BRepGraph_NodeId, TopTools_ShapeMapHasher]()


def _vertex_shape(x, y, z):
    return BRepBuilderAPI_MakeVertex(gp_Pnt(x, y, z)).Shape()


def _wires_of_edge(g, eid):
    out = []
    it = g.Topo().Edges().WiresOf(eid)
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def test_BRepGraph_LayerHistoryTest_FindOriginal_UnmodifiedNode_ReturnsSelf(graph):
    face = BRepGraph_NodeId(Kind.Face, 0)
    orig = _hist(graph).FindOriginal(face)
    assert orig.IsValid()
    assert orig == face


def test_BRepGraph_LayerHistoryTest_FindDerived_UnmodifiedNode_ReturnsEmpty(graph):
    assert len(_hist(graph).FindDerived(BRepGraph_NodeId(Kind.Face, 0))) == 0


def test_BRepGraph_LayerHistoryTest_Disabled_RecordHistory_NoRecordStored(graph):
    h = _hist(graph)
    nb_before = h.NbRecords()
    h.SetEnabled(False)
    h.Record("Disabled", BRepGraph_NodeId(Kind.Edge, 0), _nodes(BRepGraph_NodeId(Kind.Edge, 1)))
    assert h.NbRecords() == nb_before


def test_BRepGraph_LayerHistoryTest_ReEnabled_RecordsAfterReEnable(graph):
    h = _hist(graph)
    h.SetEnabled(False)
    assert not h.IsEnabled()
    h.SetEnabled(True)
    assert h.IsEnabled()
    nb_before = h.NbRecords()
    h.Record("ReEnabled", BRepGraph_NodeId(Kind.Edge, 0), _nodes(BRepGraph_NodeId(Kind.Edge, 1)))
    assert h.NbRecords() == nb_before + 1


def test_BRepGraph_LayerHistoryTest_RecordHistory_EmptyReplacements_Stored(graph):
    h = _hist(graph)
    nb_before = h.NbRecords()
    h.Record("Erase", BRepGraph_NodeId(Kind.Edge, 0), _nodes())
    assert h.NbRecords() == nb_before + 1


def test_BRepGraph_LayerHistoryTest_HistoryRecord_SequenceNumber_Monotonic(graph):
    h = _hist(graph)
    e0 = BRepGraph_NodeId(Kind.Edge, 0)
    e1 = BRepGraph_NodeId(Kind.Edge, 1)
    e2 = BRepGraph_NodeId(Kind.Edge, 2)
    h.Record("Op1", e0, _nodes(e1))
    h.Record("Op2", e1, _nodes(e2))
    nb = h.NbRecords()
    assert nb >= 2
    assert h.Record(nb - 2).SequenceNumber < h.Record(nb - 1).SequenceNumber


def test_BRepGraph_LayerHistoryTest_HistoryRecord_OperationName_Stored(graph):
    h = _hist(graph)
    h.Record("MyCustomOp", BRepGraph_NodeId(Kind.Edge, 0), _nodes(BRepGraph_NodeId(Kind.Edge, 1)))
    assert h.Record(h.NbRecords() - 1).OperationName.IsEqual("MyCustomOp")


def test_BRepGraph_LayerHistoryTest_NbHistoryRecords_AfterMultipleOps_Correct(graph):
    h = _hist(graph)
    nb_before = h.NbRecords()
    e0 = BRepGraph_NodeId(Kind.Edge, 0)
    repl = _nodes(BRepGraph_NodeId(Kind.Edge, 1))
    h.Record("A", e0, repl)
    h.Record("B", e0, repl)
    h.Record("C", e0, repl)
    assert h.NbRecords() == nb_before + 3


def test_BRepGraph_LayerHistoryTest_SplitEdge_RewritesAllContainingWires(graph):
    assert graph.Topo().Edges().Nb() > 0
    eid = BRepGraph_EdgeId(0)
    first, last = BRepGraph_Tool.Edge.Range_s(graph, eid)
    split_param = 0.5 * (first + last)

    nb_vertices_before = graph.Topo().Vertices().Nb()
    split_vertex = graph.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 1.0e-7)
    assert split_vertex.IsValid()
    assert graph.Topo().Vertices().Nb() == nb_vertices_before + 1

    wires = _wires_of_edge(graph, eid)
    assert len(wires) > 0

    nb_edges_before = graph.Topo().Edges().Nb()
    nb_active_before = graph.Topo().Edges().NbActive()

    sub_a = BRepGraph_EdgeId()
    sub_b = BRepGraph_EdgeId()
    graph.Editor().Edges().Split(eid, split_vertex, split_param, sub_a, sub_b)

    assert sub_a.IsValid()
    assert sub_b.IsValid()
    assert graph.Topo().Edges().Nb() == nb_edges_before + 2
    assert graph.Topo().Edges().NbActive() == nb_active_before + 1

    for wid in wires:
        coedges = list(graph.Topo().Wires().Relations(wid).CoEdgeIds)
        has_old = False
        ord_a = None
        ord_b = None
        for idx, ce in enumerate(coedges):
            node = BRepGraph_NodeId(graph.Topo().CoEdges().Definition(ce).ChildEdgeId)
            if node == BRepGraph_NodeId(eid):
                has_old = True
            elif node == BRepGraph_NodeId(sub_a):
                ord_a = idx
            elif node == BRepGraph_NodeId(sub_b):
                ord_b = idx
        assert not has_old
        assert ord_a is not None
        assert ord_b is not None
        distance = abs(ord_a - ord_b)
        assert distance == 1 or distance + 1 == len(coedges)


def test_BRepGraph_LayerHistoryTest_SplitEdge_IgnoresRemovedCoEdgeEntries(graph):
    assert graph.Topo().Edges().Nb() > 0
    eid = BRepGraph_EdgeId(0)
    first, last = BRepGraph_Tool.Edge.Range_s(graph, eid)
    split_param = 0.5 * (first + last)

    wires = _wires_of_edge(graph, eid)
    assert len(wires) > 1
    wid = wires[0]
    coedges_before = list(graph.Topo().Wires().Relations(wid).CoEdgeIds)
    assert len(coedges_before) > 0

    to_remove = BRepGraph_CoEdgeId()
    for ce in coedges_before:
        if graph.Topo().CoEdges().Definition(ce).ChildEdgeId == eid:
            to_remove = ce
            break
    assert to_remove.IsValid(graph.Topo().CoEdges().Nb())

    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(to_remove))
    assert to_remove.IsRemoved(graph)

    nb_active_before = len(graph.Topo().Wires().Relations(wid).CoEdgeIds)

    split_vertex = graph.Editor().Vertices().Add(gp_Pnt(4.0, 5.0, 6.0), 1.0e-7)
    assert split_vertex.IsValid()

    sub_a = BRepGraph_EdgeId()
    sub_b = BRepGraph_EdgeId()
    graph.Editor().Edges().Split(eid, split_vertex, split_param, sub_a, sub_b)
    assert sub_a.IsValid()
    assert sub_b.IsValid()

    assert to_remove.IsRemoved(graph)
    assert len(graph.Topo().Wires().Relations(wid).CoEdgeIds) == nb_active_before
    assert graph.Topo().CoEdges().Definition(to_remove).ChildEdgeId == eid

    has_a = False
    has_b = False
    for i in range(graph.Topo().CoEdges().Nb()):
        ce = BRepGraph_CoEdgeId(i)
        if ce.IsRemoved(graph):
            continue
        node = BRepGraph_NodeId(graph.Topo().CoEdges().Definition(ce).ChildEdgeId)
        if node == BRepGraph_NodeId(sub_a):
            has_a = True
        if node == BRepGraph_NodeId(sub_b):
            has_b = True
    assert has_a
    assert has_b


def test_BRepGraph_LayerHistoryTest_FindGenerated_PerKindLookup_ReturnsOnlyGenerated(graph):
    h = _hist(graph)
    orig = BRepGraph_NodeId(Kind.Edge, 0)
    repl = BRepGraph_NodeId(Kind.Edge, 1)
    h.Record("Generate", orig, _nodes(repl), HKind.Generated)

    gen = h.FindGenerated(orig)
    assert gen is not None
    assert len(gen) == 1
    assert gen[0] == repl
    assert h.FindModified(orig) is None


def test_BRepGraph_LayerHistoryTest_RecordDeleted_MarksNodesAsDeleted(graph):
    h = _hist(graph)
    ea = BRepGraph_NodeId(Kind.Edge, 0)
    eb = BRepGraph_NodeId(Kind.Edge, 1)
    nb_before = h.NbRecords()
    h.RecordDeleted("DeleteEdges", _nodes(ea, eb))
    assert h.NbRecords() == nb_before + 1
    assert h.IsDeleted(ea)
    assert h.IsDeleted(eb)
    deleted = h.DeletedNodes()
    assert deleted.Contains(ea)
    assert deleted.Contains(eb)


def test_BRepGraph_LayerHistoryTest_RecordDeleted_EmptyList_IsNoop(graph):
    h = _hist(graph)
    nb_before = h.NbRecords()
    h.RecordDeleted("Noop", _nodes())
    assert h.NbRecords() == nb_before


def test_BRepGraph_LayerHistoryTest_Record_EmptyReplacements_AutoDeleted(graph):
    h = _hist(graph)
    orig = BRepGraph_NodeId(Kind.Edge, 0)
    h.Record("Consumed", orig, _nodes(), HKind.Generated)
    assert h.IsDeleted(orig)
    assert h.NbRecords() == 1
    assert h.Record(0).RecordKind == HKind.Deleted


def test_BRepGraph_LayerHistoryTest_RecordBatch_ExplicitGeneratedKind_StoredCorrectly(graph):
    h = _hist(graph)
    orig = BRepGraph_NodeId(Kind.Edge, 0)
    repl = BRepGraph_NodeId(Kind.Edge, 1)
    h.RecordBatch("BatchGen", _nodes(orig), _nodes(repl), TCollection_AsciiString(), HKind.Generated)
    assert h.NbRecords() == 1
    assert h.Record(0).RecordKind == HKind.Generated
    assert h.FindGenerated(orig) is not None
    assert h.FindModified(orig) is None


def test_BRepGraph_LayerHistoryTest_Record_ExplicitModifiedKind_DefaultMatches(graph):
    h = _hist(graph)
    nb_before = h.NbRecords()
    h.Record(
        "ExplicitMod",
        BRepGraph_NodeId(Kind.Edge, 0),
        _nodes(BRepGraph_NodeId(Kind.Edge, 1)),
        HKind.Modified,
    )
    assert h.NbRecords() == nb_before + 1
    assert h.Record(nb_before).RecordKind == HKind.Modified


def test_BRepGraph_LayerHistoryTest_IsDeleted_UnrelatedNode_ReturnsFalse(graph):
    assert not _hist(graph).IsDeleted(BRepGraph_NodeId(Kind.Edge, 0))


def test_BRepGraph_LayerHistoryTest_RecordReplaced_MapsImageAndMarksDeleted(graph):
    h = _hist(graph)
    orig = BRepGraph_NodeId(Kind.Face, 0)
    repl = BRepGraph_NodeId(Kind.Face, 1)
    h.RecordReplaced("ReplaceFace", orig, repl)

    assert h.NbRecords() == 1
    assert h.Record(0).RecordKind == HKind.Replaced
    assert h.IsDeleted(orig)

    modified = h.FindModified(orig)
    assert modified is not None
    assert len(modified) == 1
    assert modified[0] == repl

    origins = h.FindOriginals(repl)
    assert origins is not None
    assert len(origins) == 1
    assert origins[0] == orig


def test_BRepGraph_LayerHistoryTest_StructuralReplacement_DoesNotEmitSemanticHistory(graph):
    assert graph.Topo().Faces().Nb() > 1
    h = _hist(graph)
    h.Clear()

    removed = BRepGraph_FaceId(1)
    graph.Editor().Gen().ReplaceNode(removed, BRepGraph_FaceId(0))

    assert h.NbRecords() == 0
    assert not h.IsDeleted(removed)
    assert h.FindModified(removed) is None


def test_BRepGraph_LayerHistoryTest_FindOriginals_DerivedWithTwoParents_ReturnsBoth(graph):
    h = _hist(graph)
    orig_a = BRepGraph_NodeId(Kind.Face, 0)
    orig_b = BRepGraph_NodeId(Kind.Face, 1)
    derived = BRepGraph_NodeId(Kind.Edge, 0)
    h.Record("FirstParent", orig_a, _nodes(derived))
    h.Record("SecondParent", orig_b, _nodes(derived))

    origins = h.FindOriginals(derived)
    assert origins is not None
    assert len(origins) == 2
    items = list(origins)
    assert orig_a in items
    assert orig_b in items


def test_BRepGraph_LayerHistoryTest_RecordUid_Modified_AppendsAuditRecord():
    orig = BRepGraph_UID(Kind.Face, 10)
    repl = BRepGraph_UID(Kind.Face, 11)

    h = BRepGraph_LayerHistory()
    h.RecordUid("UidMod", orig, _uids(repl), HKind.Modified)

    assert h.NbRecords() == 1
    rec = h.Record(0)
    assert rec.OperationName.IsEqual("UidMod")
    assert rec.RecordKind == HKind.Modified
    assert rec.UidMapping.IsBound(orig)
    assert len(rec.UidMapping.Find(orig)) == 1
    assert rec.UidMapping.Find(orig)[0] == repl
    assert rec.Mapping.IsEmpty()
    assert h.HasKnownInput(orig)

    mod = h.FindModified(orig)
    assert mod is not None
    assert len(mod) == 1
    assert mod[0] == repl


def test_BRepGraph_LayerHistoryTest_RecordDeletedUid_AppendsAuditRecord():
    a = BRepGraph_UID(Kind.Edge, 20)
    b = BRepGraph_UID(Kind.Edge, 21)

    h = BRepGraph_LayerHistory()
    h.RecordDeletedUid("UidDelete", _uids(a, b))

    assert h.NbRecords() == 1
    rec = h.Record(0)
    assert rec.OperationName.IsEqual("UidDelete")
    assert rec.RecordKind == HKind.Deleted
    assert rec.UidMapping.IsBound(a)
    assert rec.UidMapping.IsBound(b)
    assert rec.UidMapping.Find(a).IsEmpty()
    assert rec.UidMapping.Find(b).IsEmpty()
    assert h.IsDeleted(a)
    assert h.IsDeleted(b)
    assert h.HasKnownInput(a)
    assert h.HasKnownInput(b)


def test_BRepGraph_LayerHistoryTest_Absorb_NullSource_NoOp():
    h = BRepGraph_LayerHistory()
    h.Absorb(_shape_map(), _shape_map(), None, "NullSrc")
    assert h.NbRecords() == 0


def test_BRepGraph_LayerHistoryTest_Absorb_EmptyInputs_NoOp():
    h = BRepGraph_LayerHistory()
    h.Absorb(_shape_map(), _shape_map(), BRepTools_History(), "EmptyInputs")
    assert h.NbRecords() == 0


def test_BRepGraph_LayerHistoryTest_Absorb_ModifiedOnly_EmitsModifiedRecord():
    in_shape = _vertex_shape(0, 0, 0)
    out_shape = _vertex_shape(1, 0, 0)
    in_node = BRepGraph_NodeId(Kind.Vertex, 100)
    out_node = BRepGraph_NodeId(Kind.Vertex, 101)

    src = BRepTools_History()
    src.AddModified(in_shape, out_shape)
    inputs = _shape_map()
    inputs.Bind(in_shape, in_node)
    outputs = _shape_map()
    outputs.Bind(out_shape, out_node)

    h = BRepGraph_LayerHistory()
    h.Absorb(inputs, outputs, src, "Mod")

    assert h.NbRecords() == 1
    assert h.Record(0).RecordKind == HKind.Modified
    mod = h.FindModified(in_node)
    assert mod is not None
    assert len(mod) == 1
    assert mod[0] == out_node
    assert h.FindGenerated(in_node) is None
    assert not h.IsDeleted(in_node)


def test_BRepGraph_LayerHistoryTest_Absorb_GeneratedOnly_EmitsGeneratedRecord():
    in_shape = _vertex_shape(0, 0, 0)
    out_shape = _vertex_shape(2, 0, 0)
    in_node = BRepGraph_NodeId(Kind.Vertex, 200)
    out_node = BRepGraph_NodeId(Kind.Vertex, 201)

    src = BRepTools_History()
    src.AddGenerated(in_shape, out_shape)
    inputs = _shape_map()
    inputs.Bind(in_shape, in_node)
    outputs = _shape_map()
    outputs.Bind(out_shape, out_node)

    h = BRepGraph_LayerHistory()
    h.Absorb(inputs, outputs, src, "Gen")

    assert h.NbRecords() == 1
    assert h.Record(0).RecordKind == HKind.Generated
    gen = h.FindGenerated(in_node)
    assert gen is not None
    assert len(gen) == 1
    assert gen[0] == out_node
    assert h.FindModified(in_node) is None


def test_BRepGraph_LayerHistoryTest_Absorb_RemovedTakesPrecedenceOverModified():
    in_shape = _vertex_shape(0, 0, 0)
    ghost_out = _vertex_shape(3, 0, 0)
    in_node = BRepGraph_NodeId(Kind.Vertex, 300)
    ghost_node = BRepGraph_NodeId(Kind.Vertex, 301)

    src = BRepTools_History()
    src.AddModified(in_shape, ghost_out)
    src.Remove(in_shape)
    inputs = _shape_map()
    inputs.Bind(in_shape, in_node)
    outputs = _shape_map()
    outputs.Bind(ghost_out, ghost_node)

    h = BRepGraph_LayerHistory()
    h.Absorb(inputs, outputs, src, "RemovedWins")

    assert h.IsDeleted(in_node)
    assert h.FindModified(in_node) is None
    assert h.NbRecords() == 1
    assert h.Record(0).RecordKind == HKind.Deleted


def test_BRepGraph_LayerHistoryTest_Absorb_OutputMissingFromMap_DroppedSilently():
    in_shape = _vertex_shape(0, 0, 0)
    out_shape = _vertex_shape(4, 0, 0)
    in_node = BRepGraph_NodeId(Kind.Vertex, 400)

    src = BRepTools_History()
    src.AddModified(in_shape, out_shape)
    inputs = _shape_map()
    inputs.Bind(in_shape, in_node)

    h = BRepGraph_LayerHistory()
    h.Absorb(inputs, _shape_map(), src, "Drop")

    assert h.NbRecords() == 0
    assert h.FindModified(in_node) is None


def test_BRepGraph_LayerHistoryTest_ClearReleasesHistoryAndAllowsFreshUidRecording():
    h = BRepGraph_LayerHistory()
    for idx in range(1000):
        h.RecordUid("Stress", BRepGraph_UID(Kind.Edge, idx + 1), _uids(BRepGraph_UID(Kind.Edge, idx + 1001)))
    assert h.NbRecords() == 1000

    h.Clear()
    assert h.NbRecords() == 0

    fresh_orig = BRepGraph_UID(Kind.Face, 20)
    fresh_repl = BRepGraph_UID(Kind.Face, 21)
    h.RecordUid("AfterClear", fresh_orig, _uids(fresh_repl))

    assert h.NbRecords() == 1
    mod = h.FindModified(fresh_orig)
    assert mod is not None
    assert len(mod) == 1
    assert mod[0] == fresh_repl
    assert not h.IsDeleted(fresh_orig)
