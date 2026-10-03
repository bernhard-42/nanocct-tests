# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_RefId_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_ChildRefId,
    BRepGraph_CoEdgeId,
    BRepGraph_CompoundId,
    BRepGraph_CompoundIterator,
    BRepGraph_CompSolidIterator,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceIterator,
    BRepGraph_FaceRefId,
    BRepGraph_NodeId,
    BRepGraph_RefId,
    BRepGraph_RefsShellsOfFace,
    BRepGraph_RefUID,
    BRepGraph_ShellIterator,
    BRepGraph_ShellRefId,
    BRepGraph_SolidIterator,
    BRepGraph_SolidRefId,
    BRepGraph_VertexRefId,
    BRepGraph_WireIterator,
    BRepGraph_WireRefId,
)
from nanocct.BRepGraphInc import ParityOrientation
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED

RefKind = BRepGraph_RefId.Kind


def _box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    return g


def _ids(iterator_cls, g):
    it = iterator_cls(g)
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _count_inline_face_refs(g):
    return sum(len(g.Refs().Faces().IdsOf(s)) for s in _ids(BRepGraph_ShellIterator, g))


def _count_inline_wire_refs(g):
    return sum(len(g.Refs().Wires().IdsOf(f)) for f in _ids(BRepGraph_FaceIterator, g))


def _count_inline_coedges(g):
    return sum(len(g.Topo().Wires().Relations(w).CoEdgeIds) for w in _ids(BRepGraph_WireIterator, g))


def _count_inline_vertex_refs(g):
    nb = 0
    for edge in BRepGraph_EdgeIterator(g):
        if edge.StartVertexRefId.IsValid():
            nb += 1
        if edge.EndVertexRefId.IsValid():
            nb += 1
    return nb


def _count_inline_shell_refs(g):
    return sum(len(g.Refs().Shells().IdsOf(s)) for s in _ids(BRepGraph_SolidIterator, g))


def _count_inline_solid_refs(g):
    return sum(len(g.Refs().Solids().IdsOf(c)) for c in _ids(BRepGraph_CompSolidIterator, g))


def _count_inline_child_refs(g):
    # ChildRefsOfParent is empty for every non-compound parent.
    return sum(len(g.Refs().Children().IdsOf(c)) for c in _ids(BRepGraph_CompoundIterator, g))


def test_BRepGraph_RefIdTest_DefaultRefId_IsInvalid():
    assert not BRepGraph_RefId().IsValid()


def test_BRepGraph_RefIdTest_TypedRefId_ConvertsToUntyped():
    untyped = BRepGraph_RefId(BRepGraph_FaceRefId(3))
    assert untyped.RefKind == RefKind.Face
    assert untyped.Index == 3


def test_BRepGraph_RefIdTest_UntypedArithmetic_PreservesKindAndIndex():
    # ++ is not bound; the +/- offset operators are.
    ref = BRepGraph_RefId(RefKind.Face, 3)
    advanced = ref + 4
    assert advanced.RefKind == RefKind.Face
    assert advanced.Index == 7
    retreated = advanced - 6
    assert retreated.RefKind == RefKind.Face
    assert retreated.Index == 1


def test_BRepGraph_RefIdTest_TypedArithmetic_PreservesKindAndIndex():
    face_ref = BRepGraph_FaceRefId(3)
    advanced = face_ref + 4
    assert advanced.Index == 7
    retreated = advanced - 6
    assert retreated.Index == 1
    ref = BRepGraph_RefId(advanced)
    assert ref.RefKind == RefKind.Face
    assert ref.Index == 7


def test_BRepGraph_RefIdTest_TypedArithmetic_IndexZeroBoundary():
    vertex_ref = BRepGraph_VertexRefId(0)
    assert vertex_ref.IsValid()
    vertex_ref = vertex_ref + 1
    assert vertex_ref.Index == 1
    zero = vertex_ref - 1
    assert zero.Index == 0
    assert zero.IsValid()
    invalid = zero - 1
    assert invalid.Index == BRepGraph_VertexRefId.THE_INVALID_INDEX
    assert not invalid.IsValid()


def test_BRepGraph_RefIdTest_FromRefId_WrongKindReturnsInvalid():
    wire = BRepGraph_WireRefId.FromRefId_s(BRepGraph_RefId(RefKind.Face, 3))
    assert not wire.IsValid()
    assert wire.Index == BRepGraph_WireRefId.THE_INVALID_INDEX


def test_BRepGraph_RefIdTest_RefUID_Default_IsInvalid():
    assert not BRepGraph_RefUID().IsValid()


def test_BRepGraph_RefIdTest_RefUID_Equality_IgnoresGeneration():
    assert BRepGraph_RefUID(RefKind.Face, 42) == BRepGraph_RefUID(RefKind.Face, 42)


def test_BRepGraph_RefIdTest_RefsView_AfterBuild_HasFaceRefs():
    g = _box_graph()
    nb = g.Refs().Faces().Nb()
    assert nb >= 0
    if nb > 0:
        face_ref = BRepGraph_FaceRefId(0)
        g.Refs().Faces().Entry(face_ref)
        assert face_ref.IsValid(nb)
    else:
        assert not g.UIDs().Of(BRepGraph_FaceRefId.Start_s()).IsValid()


def test_BRepGraph_RefIdTest_RefDomain_StampGUIDGeneration_IfSupported():
    g = _box_graph()
    assert g.Refs().Faces().Nb() > 0
    stamp = g.UIDs().StampOf(BRepGraph_FaceRefId.Start_s())
    assert stamp.IsValid()
    assert stamp.IsRefStamp()
    graph_guid = g.UIDs().GraphGUID()
    guid1 = stamp.ToGUID(graph_guid)
    guid2 = stamp.ToGUID(graph_guid)
    assert guid1 == guid2


def test_BRepGraph_RefIdTest_RefsView_AfterBuild_CountsDoNotExceedInlineStorage():
    g = _box_graph()
    refs = g.Refs()
    assert refs.Faces().Nb() <= _count_inline_face_refs(g)
    assert refs.Wires().Nb() <= _count_inline_wire_refs(g)
    assert _count_inline_coedges(g) > 0
    assert g.Topo().CoEdges().Nb() == _count_inline_coedges(g)
    assert refs.Vertices().Nb() <= _count_inline_vertex_refs(g)
    assert refs.Shells().Nb() <= _count_inline_shell_refs(g)
    assert refs.Solids().Nb() <= _count_inline_solid_refs(g)
    assert refs.Children().Nb() <= _count_inline_child_refs(g)


def _check_ref_roundtrip(g, typed_id, nb, entry_of, child_of, child_count):
    while typed_id.IsValid(nb):
        ref = BRepGraph_RefId(typed_id)
        uid = g.UIDs().Of(ref)
        assert uid.IsValid()
        assert g.UIDs().RefIdFrom(uid) == ref
        entry = entry_of(typed_id)
        if child_count is None:
            assert child_of(entry).IsValid()
        else:
            assert child_of(entry).IsValid(child_count)
        typed_id = typed_id + 1


def test_BRepGraph_RefIdTest_RefsView_AfterBuild_UIDRoundtripAndParentKinds():
    g = _box_graph()
    refs = g.Refs()
    topo = g.Topo()

    face_ref = BRepGraph_FaceRefId.Start_s()
    while face_ref.IsValid(refs.Faces().Nb()):
        ref = BRepGraph_RefId(face_ref)
        uid = g.UIDs().Of(ref)
        stamp = g.UIDs().StampOf(ref)
        assert uid.IsValid()
        assert g.UIDs().RefIdFrom(uid) == ref
        assert g.UIDs().Has(uid)
        assert stamp.IsValid()
        assert stamp.IsRefStamp()
        assert not g.UIDs().IsStale(stamp)
        assert refs.Faces().Entry(face_ref).ChildFaceId.IsValid(topo.Faces().Nb())
        face_ref = face_ref + 1

    _check_ref_roundtrip(g, BRepGraph_WireRefId.Start_s(), refs.Wires().Nb(), refs.Wires().Entry,
                         lambda e: e.ChildWireId, topo.Wires().Nb())

    coedge = BRepGraph_CoEdgeId.Start_s()
    while coedge.IsValid(topo.CoEdges().Nb()):
        uid = g.UIDs().Of(BRepGraph_NodeId(coedge))
        assert uid.IsValid()
        assert g.UIDs().NodeIdFrom(uid) == BRepGraph_NodeId(coedge)
        assert topo.CoEdges().Definition(coedge).ChildEdgeId.IsValid(topo.Edges().Nb())
        coedge = coedge + 1

    _check_ref_roundtrip(g, BRepGraph_ShellRefId.Start_s(), refs.Shells().Nb(), refs.Shells().Entry,
                         lambda e: e.ChildShellId, topo.Shells().Nb())
    _check_ref_roundtrip(g, BRepGraph_VertexRefId.Start_s(), refs.Vertices().Nb(), refs.Vertices().Entry,
                         lambda e: e.ChildVertexId, topo.Vertices().Nb())
    _check_ref_roundtrip(g, BRepGraph_SolidRefId.Start_s(), refs.Solids().Nb(), refs.Solids().Entry,
                         lambda e: e.ChildSolidId, topo.Solids().Nb())
    _check_ref_roundtrip(g, BRepGraph_ChildRefId.Start_s(), refs.Children().Nb(), refs.Children().Entry,
                         lambda e: e.ChildNodeId, None)


def test_BRepGraph_RefIdTest_RefUIDReverseLookupStaysCurrentAfterProgrammaticAdd():
    g = BRepGraph()
    ed = g.Editor()
    v0 = ed.Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 0.001)
    v1 = ed.Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 0.001)
    ed.Edges().Add(v0, v1, None, 0.0, 1.0, 0.001)

    first_ref = BRepGraph_RefId(BRepGraph_VertexRefId.Start_s())
    first_uid = g.UIDs().Of(first_ref)
    assert first_uid.IsValid()
    assert g.UIDs().RefIdFrom(first_uid) == first_ref

    v2 = ed.Vertices().Add(gp_Pnt(2.0, 0.0, 0.0), 0.001)
    v3 = ed.Vertices().Add(gp_Pnt(3.0, 0.0, 0.0), 0.001)
    ed.Edges().Add(v2, v3, None, 0.0, 1.0, 0.001)

    second_ref = BRepGraph_RefId(BRepGraph_VertexRefId(2))
    second_uid = g.UIDs().Of(second_ref)
    assert second_uid.IsValid()

    assert g.UIDs().RefIdFrom(first_uid) == first_ref
    assert g.UIDs().RefIdFrom(second_uid) == second_ref
    assert g.UIDs().Has(first_uid)
    assert g.UIDs().Has(second_uid)


def test_BRepGraph_RefIdTest_StaleRefUID_HasReturnsFalseAndLookupBecomesInvalidAfterRebuild():
    box1 = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
    box2 = BRepPrimAPI_MakeBox(11.0, 21.0, 31.0)
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(box1.Shape())
    assert not g.IsEmpty()
    assert g.Refs().Faces().Nb() > 0

    old_uid = g.UIDs().Of(BRepGraph_FaceRefId.Start_s())
    assert old_uid.IsValid()
    assert g.UIDs().Has(old_uid)

    g.Clear()
    g.Shapes().Add(box2.Shape())
    assert not g.UIDs().Has(old_uid)
    assert not g.UIDs().RefIdFrom(old_uid).IsValid()


def test_BRepGraph_RefIdTest_MutFaceRef_UpdatesRefStampAndParentModifiedFlag():
    g = _box_graph()
    assert g.Refs().Faces().Nb() > 0

    face_ref = BRepGraph_FaceRefId(0)
    before_reversed = g.Refs().Faces().Entry(face_ref).Orientation.IsReversed
    before_stamp = g.UIDs().StampOf(face_ref)
    assert before_stamp.IsValid()
    assert before_stamp.IsRefStamp()

    mut = g.Editor().Faces().MutRef(face_ref)
    new_ori = TopAbs_FORWARD if before_reversed else TopAbs_REVERSED
    g.Editor().Faces().SetRefOrientation(mut, ParityOrientation(new_ori))
    del mut  # end of the C++ guard scope

    after = g.Refs().Faces().Entry(face_ref)
    assert after.Orientation.IsReversed != before_reversed
    assert g.UIDs().IsStale(before_stamp)

    has_updated_parent = False
    # keep the ref vector alive: the iterator stores a pointer to it
    parent_refs = g.Topo().Faces().Relations(after.ChildFaceId).ParentFaceRefIds
    it = BRepGraph_RefsShellsOfFace(g, parent_refs)
    while it.More():
        if it.CurrentRefId() == face_ref:
            parent = g.Topo().Shells().Definition(it.CurrentParentId())
            has_updated_parent = parent.SubtreeGen > 0
            break
        it.Next()
    assert has_updated_parent


def test_BRepGraph_RefIdTest_MutFaceRef_MarkRemoved_PersistsAndInvalidatesStamp():
    g = _box_graph()
    assert g.Refs().Faces().Nb() > 0
    face_ref = BRepGraph_FaceRefId(0)
    before_stamp = g.UIDs().StampOf(face_ref)
    assert before_stamp.IsValid()
    assert before_stamp.IsRefStamp()

    g.Editor().Gen().RemoveRef(BRepGraph_RefId(face_ref))

    assert face_ref.IsRemoved(g)
    assert g.UIDs().IsStale(before_stamp)
    assert not g.UIDs().StampOf(face_ref).IsValid()


def test_BRepGraph_RefIdTest_OutOfRangeMetadataQueriesReturnFalse():
    g = _box_graph()
    face_ref = BRepGraph_FaceRefId(g.Refs().Faces().Nb())
    assert not face_ref.IsRemoved(g)
    assert not face_ref.IsOwned(g)
    wire_ref = BRepGraph_RefId(RefKind.Wire, g.Refs().Wires().Nb())
    assert not wire_ref.IsRemoved(g)
    assert not wire_ref.IsOwned(g)


def test_BRepGraph_RefIdTest_ChildRefs_CompoundEntriesAreValid():
    g = _box_graph()
    refs = g.Refs()
    for comp in _ids(BRepGraph_CompoundIterator, g):
        for child_ref in refs.Children().IdsOf(BRepGraph_CompoundId(comp)):
            assert refs.Children().Entry(child_ref).ChildNodeId.IsValid()
            assert not child_ref.IsRemoved(g)
