# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Compact_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Bnd import Bnd_Box
from nanocct.BRep import BRep_Builder
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Cut
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy, BRepBuilderAPI_MakeEdge
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_Compact,
    BRepGraph_Deduplicate,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceRefId,
    BRepGraph_ItemId,
    BRepGraph_ItemUID,
    BRepGraph_LayerHistory,
    BRepGraph_NodeId,
    BRepGraph_RefId,
    BRepGraph_RefsFaceOfShell,
    BRepGraph_RefsShellOfSolid,
    BRepGraph_ShellId,
    BRepGraph_ShellIterator,
    BRepGraph_ShellRefId,
    BRepGraph_SolidId,
    BRepGraph_SolidIterator,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_VertexId,
    BRepGraph_VertexIterator,
    BRepGraph_VertexRefId,
    BRepGraph_WireId,
    BRepGraph_WireIterator,
    BRepGraph_WireRefId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.gp import gp, gp_Ax2, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.TCollection import TCollection_AsciiString
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound

Kind = BRepGraph_NodeId.Kind


def _compound(*shapes):
    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)
    for s in shapes:
        builder.Add(comp, s)
    return comp


def _make_two_copied_faces():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    face = TopExp_Explorer(box, TopAbs_FACE).Current()
    return _compound(BRepBuilderAPI_Copy(face, True).Shape(), BRepBuilderAPI_Copy(face, True).Shape())


def _make_box_with_loose_edge():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(100.0, 0.0, 0.0), gp_Pnt(120.0, 0.0, 0.0)).Edge()
    return _compound(box, edge)


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _box_graph():
    return _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())


def _history(g):
    # C++: theGraph.LayerRegistry().Ensure<BRepGraph_LayerHistory>()
    reg = g.LayerRegistry()
    layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    if layer is None:
        reg.RegisterLayer(BRepGraph_LayerHistory())
        layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    return layer


def _count_history_records_by_op(g, op):
    history = g.LayerRegistry().FindLayer(BRepGraph_LayerHistory.GetID_s())
    if history is None:
        return 0
    return sum(1 for i in range(history.NbRecords()) if history.Record(i).OperationName.ToCString() == op)


def _graph_bounds(g):
    box = Bnd_Box()
    it = BRepGraph_VertexIterator(g)
    while it.More():
        box.Add(g.Topo().Vertices().Definition(it.CurrentId()).Point)
        it.Next()
    return box


def _expect_box_near(left, right, tol):
    assert not left.IsVoid()
    assert not right.IsVoid()
    for a, b in zip(left.Get__float__float__float__float__float__float(), right.Get__float__float__float__float__float__float()):
        assert abs(a - b) <= tol


def _loose_edge(g):
    it = BRepGraph_EdgeIterator(g)
    while it.More():
        if not g.Topo().Edges().FacesOf(it.CurrentId()).More():
            return it.CurrentId()
        it.Next()
    return BRepGraph_EdgeId()


def _merge_opts():
    opts = BRepGraph_Deduplicate.Options()
    opts.MergeEntitiesWhenSafe = True
    return opts


def test_BRepGraph_CompactTest_NoRemovedNodes_Noop():
    g = _box_graph()
    nv = g.Topo().Vertices().Nb()
    ne = g.Topo().Edges().Nb()
    nf = g.Topo().Faces().Nb()

    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbRemovedVertices == 0
    assert res.NbRemovedEdges == 0
    assert res.NbRemovedFaces == 0
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Vertices().Nb() == nv
    assert g.Topo().Edges().Nb() == ne
    assert g.Topo().Faces().Nb() == nf


def test_BRepGraph_CompactTest_AfterDeduplicate_RemovesNodes():
    g = _graph(_make_two_copied_faces())
    BRepGraph_Deduplicate.Perform_s(g)
    opts = BRepGraph_Compact.Options()
    opts.HistoryMode = False
    res = BRepGraph_Compact.Perform_s(g, opts)
    assert res.NbRemovedSurfaces == 0
    assert res.NbRemovedCurves == 0
    assert res.NbNodesAfter == res.NbNodesBefore


def test_BRepGraph_CompactTest_IndexDensity_NoGaps():
    g = _graph(_make_two_copied_faces())
    BRepGraph_Deduplicate.Perform_s(g)
    BRepGraph_Compact.Perform_s(g)

    for i in range(g.Topo().Vertices().Nb()):
        assert not BRepGraph_VertexId(i).IsRemoved(g)
    for i in range(g.Topo().Edges().Nb()):
        assert not BRepGraph_EdgeId(i).IsRemoved(g)
    for i in range(g.Topo().Faces().Nb()):
        assert not BRepGraph_FaceId(i).IsRemoved(g)
    for i in range(g.Topo().Wires().Nb()):
        assert not BRepGraph_WireId(i).IsRemoved(g)


def test_BRepGraph_CompactTest_CrossReferences_Valid():
    g = _graph(_make_two_copied_faces())
    BRepGraph_Deduplicate.Perform_s(g)
    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_CompactTest_HistoryMode_RecordsMapping():
    g = _graph(_make_two_copied_faces())
    BRepGraph_Deduplicate.Perform_s(g, _merge_opts())
    opts = BRepGraph_Compact.Options()
    opts.HistoryMode = True
    BRepGraph_Compact.Perform_s(g, opts)
    assert _count_history_records_by_op(g, "Compact:Remap") >= 1


def test_BRepGraph_CompactTest_FullPipeline_Deduplicate_Compact_Validate():
    g = _graph(_make_two_copied_faces())
    BRepGraph_Deduplicate.Perform_s(g)
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesAfter == res.NbNodesBefore
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_CompactTest_RemovalCompact_PreservesBounds_AndDoesNotGrowTopology():
    g = _box_graph()
    assert g.Topo().CoEdges().Nb() > 0
    assert g.Topo().Faces().Nb() > 2

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId(2)))
    coedges_before = g.Topo().CoEdges().Nb()
    box_before = _graph_bounds(g)

    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore >= res.NbNodesAfter
    assert g.Topo().CoEdges().Nb() <= coedges_before

    _expect_box_near(_graph_bounds(g), box_before, Precision.Confusion_s())
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_CompactTest_RemovalCompact_PreservesClosedTopologyAndValidShape():
    g = _graph(_make_box_with_loose_edge())
    loose = _loose_edge(g)
    assert loose.IsValid()

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(loose))
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore > res.NbNodesAfter

    assert g.Topo().Shells().Nb() == 1
    it = BRepGraph_WireIterator(g)
    while it.More():
        assert BRepGraph_Tool.Wire.IsClosed_s(g, it.CurrentId())
        it.Next()
    assert BRepGraph_Tool.Shell.IsClosed_s(g, BRepGraph_ShellId.Start_s())

    root_shape = g.Shapes().Reconstruct(BRepGraph_NodeId(g.RootProductIds().Value(0)))
    assert not root_shape.IsNull()
    assert BRepCheck_Analyzer(root_shape).IsValid()
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_CompactTest_AuditMode_PassesAfterDedupCompact():
    g = _graph(_make_two_copied_faces())
    assert BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Mode.Audit).IsValid()
    BRepGraph_Deduplicate.Perform_s(g)
    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Mode.Audit).IsValid()


def test_BRepGraph_CompactTest_AuditMode_PassesAfterRemovalCompact():
    g = _graph(_make_box_with_loose_edge())
    loose = _loose_edge(g)
    assert loose.IsValid()
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(loose))
    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Mode.Audit).IsValid()


def test_BRepGraph_CompactTest_Compact_PreservesTopologyUIDs():
    g = _graph(_make_two_copied_faces())
    topo = g.Topo()
    kinds = [
        (Kind.Vertex, lambda: topo.Vertices().Nb()),
        (Kind.Edge, lambda: topo.Edges().Nb()),
        (Kind.Wire, lambda: topo.Wires().Nb()),
        (Kind.Face, lambda: topo.Faces().Nb()),
        (Kind.Shell, lambda: topo.Shells().Nb()),
        (Kind.Solid, lambda: topo.Solids().Nb()),
        (Kind.Compound, lambda: topo.Compounds().Nb()),
        (Kind.CompSolid, lambda: topo.CompSolids().Nb()),
    ]

    originals = {}
    for kind, count in kinds:
        uids = set()
        for i in range(count()):
            uid = g.UIDs().Of(BRepGraph_NodeId(kind, i))
            assert uid.IsValid()
            uids.add(uid)
        originals[kind] = uids

    gen_before = g.UIDs().Generation()
    BRepGraph_Deduplicate.Perform_s(g)
    BRepGraph_Compact.Perform_s(g)
    assert g.UIDs().Generation() == gen_before

    topo = g.Topo()
    for kind, count in kinds:
        for i in range(count()):
            new_id = BRepGraph_NodeId(kind, i)
            new_uid = g.UIDs().Of(new_id)
            assert new_uid.IsValid()
            assert new_uid in originals[kind]
            assert g.UIDs().NodeIdFrom(new_uid) == new_id
            assert g.UIDs().Has(new_uid)
    assert g.Topo().Faces().Nb() > 0


def test_BRepGraph_CompactTest_Compact_PreservesRepresentationUIDs():
    g = _box_graph()
    rep_id = g.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SurfaceRepId
    assert rep_id.IsValid()
    BRepGraph_Compact.Perform_s(g)
    compacted = g.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SurfaceRepId
    assert compacted.IsValid()
    assert compacted == rep_id


def test_BRepGraph_CompactTest_OwnGen_SurvivesCompact():
    mutated_tol = 0.2
    expected_gen = 2
    g = _graph(_make_two_copied_faces())
    g.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.1)
    g.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), mutated_tol)
    assert g.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s()).OwnGen == expected_gen

    BRepGraph_Deduplicate.Perform_s(g)
    BRepGraph_Compact.Perform_s(g)

    found = False
    for i in range(g.Topo().Edges().Nb()):
        edge = g.Topo().Edges().Definition(BRepGraph_EdgeId(i))
        if abs(edge.Tolerance - mutated_tol) < Precision.Confusion_s():
            assert edge.OwnGen == expected_gen
            found = True
            break
    assert found


def test_BRepGraph_CompactTest_UIDRoundTrip_AfterCompaction():
    g = _box_graph()
    assert g.Topo().Faces().Nb() >= 3
    assert g.Topo().Edges().Nb() >= 3

    def uid(typed_id):
        return g.UIDs().Of(BRepGraph_NodeId(typed_id))

    face_uid0 = uid(BRepGraph_FaceId.Start_s())
    face_uid1 = uid(BRepGraph_FaceId(1))
    face_uid2 = uid(BRepGraph_FaceId(2))
    edge_uid0 = uid(BRepGraph_EdgeId.Start_s())
    edge_uid1 = uid(BRepGraph_EdgeId(1))
    for u in (face_uid0, face_uid1, face_uid2, edge_uid0, edge_uid1):
        assert u.IsValid()

    removed_uid = uid(BRepGraph_FaceId(2))
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId(2)))

    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbRemovedFaces >= 1

    for u in (face_uid0, face_uid1, edge_uid0, edge_uid1):
        assert g.UIDs().NodeIdFrom(u).IsValid()
    assert not g.UIDs().NodeIdFrom(removed_uid).IsValid()


def _first_coedge_of_face1(g):
    rel = g.Topo().Faces().Relations(BRepGraph_FaceId(1))
    if rel.WireRefIds.IsEmpty():
        return BRepGraph_CoEdgeId()
    wire_ref = g.Refs().Wires().Entry(rel.WireRefIds.First())
    wire_rel = g.Topo().Wires().Relations(wire_ref.ChildWireId)
    if wire_rel.CoEdgeIds.IsEmpty():
        return BRepGraph_CoEdgeId()
    return wire_rel.CoEdgeIds.First()


def test_BRepGraph_CompactTest_CoEdgeUID_AfterCompaction():
    g = _box_graph()
    assert g.Topo().Wires().Nb() >= 1
    assert g.Topo().Faces().Nb() >= 2
    assert not g.Topo().Faces().Relations(BRepGraph_FaceId(1)).WireRefIds.IsEmpty()
    coedge_id = _first_coedge_of_face1(g)
    assert coedge_id.IsValid()

    coedge_uid = g.UIDs().Of(BRepGraph_NodeId(coedge_id))
    assert coedge_uid.IsValid()

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore > res.NbNodesAfter

    resolved = g.UIDs().NodeIdFrom(coedge_uid)
    assert resolved.IsValid()
    assert resolved.NodeKind == Kind.CoEdge


def test_BRepGraph_CompactTest_UIDRoundTrip_RefUIDs_AfterCompaction():
    g = _box_graph()

    vertex_ref_id = BRepGraph_VertexRefId()
    edge = g.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s())
    if edge.StartVertexRefId.IsValid():
        vertex_ref_id = edge.StartVertexRefId

    coedge_id = _first_coedge_of_face1(g)

    wire_ref_id = BRepGraph_WireRefId()
    assert g.Topo().Faces().Nb() >= 2
    rel = g.Topo().Faces().Relations(BRepGraph_FaceId(1))
    if not rel.WireRefIds.IsEmpty():
        wire_ref_id = rel.WireRefIds.First()

    face_ref_id = BRepGraph_FaceRefId()
    it = BRepGraph_ShellIterator(g)
    while it.More() and not face_ref_id.IsValid():
        ref_it = BRepGraph_RefsFaceOfShell(g, it.CurrentId())
        while ref_it.More():
            fr = g.Refs().Faces().Entry(ref_it.CurrentId())
            if fr.ChildFaceId.Index != 0:
                face_ref_id = ref_it.CurrentId()
                break
            ref_it.Next()
        it.Next()

    shell_ref_id = BRepGraph_ShellRefId()
    it = BRepGraph_SolidIterator(g)
    while it.More() and not shell_ref_id.IsValid():
        ref_it = BRepGraph_RefsShellOfSolid(g, it.CurrentId())
        if ref_it.More():
            shell_ref_id = ref_it.CurrentId()
        it.Next()

    def ref_uid(ref_id):
        return g.UIDs().Of(BRepGraph_RefId(ref_id)) if ref_id.IsValid() else None

    vertex_ref_uid = ref_uid(vertex_ref_id)
    coedge_uid = g.UIDs().Of(BRepGraph_NodeId(coedge_id)) if coedge_id.IsValid() else None
    wire_ref_uid = ref_uid(wire_ref_id)
    face_ref_uid = ref_uid(face_ref_id)
    shell_ref_uid = ref_uid(shell_ref_id)

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    BRepGraph_Compact.Perform_s(g)

    for u, kind in (
        (vertex_ref_uid, BRepGraph_RefId.Kind.Vertex),
        (wire_ref_uid, BRepGraph_RefId.Kind.Wire),
        (face_ref_uid, BRepGraph_RefId.Kind.Face),
        (shell_ref_uid, BRepGraph_RefId.Kind.Shell),
    ):
        if u is not None and u.IsValid():
            resolved = g.UIDs().RefIdFrom(u)
            assert resolved.IsValid()
            assert resolved.RefKind == kind
    if coedge_uid is not None and coedge_uid.IsValid():
        resolved = g.UIDs().NodeIdFrom(coedge_uid)
        assert resolved.IsValid()
        assert resolved.NodeKind == Kind.CoEdge


def test_BRepGraph_CompactTest_FindNodeStillWorksAfterCompact():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g = _graph(box)
    face = TopExp_Explorer(box, TopAbs_FACE).Current()
    assert not face.IsNull()
    assert g.Shapes().HasNode(face)
    assert g.Shapes().FindNode(face).IsValid()

    BRepGraph_Compact.Perform_s(g)

    assert g.Shapes().HasNode(face)
    assert g.Shapes().FindNode(face).IsValid()


def test_BRepGraph_CompactTest_OwnGen_PreservedForAllTopologyKindsAfterCompact():
    expected = 3
    g = _box_graph()
    ed = g.Editor()
    v0 = BRepGraph_VertexId.Start_s()
    e0 = BRepGraph_EdgeId.Start_s()
    w0 = BRepGraph_WireId.Start_s()
    f0 = BRepGraph_FaceId.Start_s()
    sh0 = BRepGraph_ShellId.Start_s()
    so0 = BRepGraph_SolidId.Start_s()

    ed.Vertices().SetPoint(v0, gp_Pnt(11.0, 21.0, 31.0))
    ed.Vertices().SetPoint(v0, gp_Pnt(12.0, 22.0, 32.0))
    ed.Vertices().SetPoint(v0, gp_Pnt(13.0, 23.0, 33.0))
    for tol in (0.1, 0.2, 0.3):
        ed.Edges().SetTolerance(e0, tol)
    for _ in range(3):
        m = ed.Wires().Mut(w0)
        m.MarkDirty()
        del m
    for tol in (0.01, 0.02, 0.03):
        ed.Faces().SetTolerance(f0, tol)
    for _ in range(3):
        m = ed.Shells().Mut(sh0)
        m.MarkDirty()
        del m
    for _ in range(3):
        m = ed.Solids().Mut(so0)
        m.MarkDirty()
        del m

    def check():
        topo = g.Topo()
        assert topo.Vertices().Definition(v0).OwnGen == expected
        assert topo.Edges().Definition(e0).OwnGen == expected
        assert topo.Wires().Definition(w0).OwnGen == expected
        assert topo.Faces().Definition(f0).OwnGen == expected
        assert topo.Shells().Definition(sh0).OwnGen == expected
        assert topo.Solids().Definition(so0).OwnGen == expected

    check()
    BRepGraph_Compact.Perform_s(g)
    check()


def test_BRepGraph_CompactTest_Compact_PreservesDeletedItemUidHistory():
    g = _box_graph()
    history = _history(g)
    face_id = BRepGraph_FaceId.Start_s()
    face_uid = g.UIDs().Of(BRepGraph_ItemId(face_id))
    assert face_uid.IsValid()

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(face_id))
    assert history.IsDeleted(face_uid)
    assert history.HasKnownInput(face_uid)

    BRepGraph_Compact.Perform_s(g)

    assert history.IsDeleted(face_uid)
    assert history.HasKnownInput(face_uid)
    assert history.DeletedItemUids().Contains(face_uid)


def test_BRepGraph_CompactTest_Compact_PreservesItemUidHistoryMappings():
    g = _box_graph()
    assert g.Topo().Faces().Nb() >= 2
    history = _history(g)
    orig_uid = g.UIDs().Of(BRepGraph_ItemId(BRepGraph_FaceId.Start_s()))
    repl_uid = g.UIDs().Of(BRepGraph_ItemId(BRepGraph_FaceId(1)))
    assert orig_uid.IsValid()
    assert repl_uid.IsValid()

    repl = NCollection_Array1[BRepGraph_ItemUID](0, 0)
    repl[0] = repl_uid
    history.RecordItemUid(TCollection_AsciiString("CompactItemHistory"), orig_uid, repl)
    assert history.HasKnownInput(orig_uid)

    BRepGraph_Compact.Perform_s(g)

    modified = history.FindModified(orig_uid)
    assert modified is not None
    assert modified.Size() == 1
    assert modified.Value(0) == repl_uid
    assert history.HasKnownInput(orig_uid)


def test_BRepGraph_CompactTest_Compact_AfterDedupMerge_NoBoundsErrors():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    comp = _compound(*[BRepBuilderAPI_Copy(box, True).Shape() for _ in range(3)])
    g = _graph(comp)
    BRepGraph_Deduplicate.Perform_s(g, _merge_opts())

    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesAfter != 0
    assert g.Topo().Vertices().Nb() == 8
    assert g.Topo().Edges().Nb() == 12
    assert g.Topo().Faces().Nb() == 6
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_CompactTest_Compact_FaceWithInnerWires_WireCountPreserved():
    box = BRepPrimAPI_MakeBox(20.0, 20.0, 20.0).Shape()
    cyl = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(10.0, 10.0, 0.0), gp.DZ_s()), 4.0, 25.0).Shape()
    cut = BRepAlgoAPI_Cut(box, cyl)
    assert cut.IsDone()
    comp = _compound(BRepBuilderAPI_Copy(cut.Shape(), True).Shape(), BRepBuilderAPI_Copy(cut.Shape(), True).Shape())
    g = _graph(comp)

    has_inner = any(
        g.Topo().Faces().Relations(BRepGraph_FaceId(i)).WireRefIds.Size() > 1 for i in range(g.Topo().Faces().Nb())
    )
    assert has_inner

    BRepGraph_Deduplicate.Perform_s(g, _merge_opts())
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesAfter != 0
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_CompactTest_HistorySurvivesCompactWithRemappedIds():
    comp = _compound(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    g = BRepGraph()
    g.Shapes().Add(comp)
    assert not g.IsEmpty()

    _history(g).SetEnabled(True)
    vertex_node = BRepGraph_NodeId(BRepGraph_VertexId.Start_s())
    repl = NCollection_Array1[BRepGraph_NodeId](0, 0)
    repl[0] = vertex_node
    _history(g).Record(TCollection_AsciiString("Test:Modify"), vertex_node, repl)
    nb_before = _history(g).NbRecords()
    assert nb_before > 0

    BRepGraph_Deduplicate.Perform_s(g, _merge_opts())
    opts = BRepGraph_Compact.Options()
    opts.HistoryMode = True
    BRepGraph_Compact.Perform_s(g, opts)

    assert _history(g).NbRecords() >= nb_before + 1
