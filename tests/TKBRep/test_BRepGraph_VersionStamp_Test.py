# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_VersionStamp_Test.cxx (LGPL-2.1 with the OCCT exception)

import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_FaceRefId,
    BRepGraph_ItemId,
    BRepGraph_NodeId,
    BRepGraph_ProductId,
    BRepGraph_RefId,
    BRepGraph_Tool,
    BRepGraph_VersionStamp,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Standard import Standard_GUID


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    return g


def _bump_face_tolerance(g):
    f0 = BRepGraph_FaceId.Start_s()
    g.Editor().Faces().SetTolerance(f0, BRepGraph_Tool.Face.Tolerance_s(g, f0) + 0.01)


def _rebuild(g):
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()


def test_BRepGraph_VersionStampBasicTest_DefaultStamp_IsInvalid():
    assert not BRepGraph_VersionStamp().IsValid()


def test_BRepGraph_VersionStampTest_StampOf_ValidNode_ReturnsValidStamp(graph):
    f0 = BRepGraph_FaceId(0)
    assert f0.IsValid(graph.Topo().Faces().Nb())
    stamp = graph.UIDs().StampOf(f0)
    assert stamp.IsValid()
    assert stamp.myNodeUID.IsValid()
    assert stamp.myMutationGen == 0
    assert stamp.myGeneration == graph.UIDs().Generation()


def test_BRepGraph_VersionStampTest_StampOf_InvalidNode_ReturnsInvalid(graph):
    assert not graph.UIDs().StampOf(BRepGraph_NodeId()).IsValid()


def test_BRepGraph_VersionStampTest_IsStale_UnmutatedNode_ReturnsFalse(graph):
    stamp = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    assert not graph.UIDs().IsStale(stamp)


def test_BRepGraph_VersionStampTest_IsStale_MutatedNode_ReturnsTrue(graph):
    stamp = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    _bump_face_tolerance(graph)
    assert graph.UIDs().IsStale(stamp)


def test_BRepGraph_VersionStampTest_IsStale_RemovedNode_ReturnsTrue(graph):
    stamp = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    graph.Editor().Gen().RemoveNode(BRepGraph_FaceId.Start_s())
    assert graph.UIDs().IsStale(stamp)


def test_BRepGraph_VersionStampTest_IsStale_DifferentGeneration_ReturnsTrue(graph):
    stamp = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    _rebuild(graph)
    assert graph.UIDs().IsStale(stamp)


def test_BRepGraph_VersionStampTest_IsStale_DeferredMode_TracksCorrectly(graph):
    stamp = graph.UIDs().StampOf(BRepGraph_EdgeId.Start_s())
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    graph.Editor().EndDeferredInvalidation()
    assert graph.UIDs().IsStale(stamp)


def test_BRepGraph_VersionStampTest_IsStale_InvalidStamp_ReturnsTrue(graph):
    assert graph.UIDs().IsStale(BRepGraph_VersionStamp())


def test_BRepGraph_VersionStampTest_StampIdentity_SameNode_Equal(graph):
    s1 = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    s2 = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    assert s1 == s2


def test_BRepGraph_VersionStampTest_StampIdentity_DifferentNodes_NotEqual(graph):
    s1 = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    s2 = graph.UIDs().StampOf(BRepGraph_FaceId(1))
    assert s1 != s2


def test_BRepGraph_VersionStampTest_IsSameItem_SameVersion_ReturnsTrue(graph):
    s1 = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    s2 = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    assert s1.IsSameItem(s2)


def test_BRepGraph_VersionStampTest_IsSameItem_DifferentVersion_StillSameItem(graph):
    before = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    _bump_face_tolerance(graph)
    after = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    assert before != after
    assert before.IsSameItem(after)


def test_BRepGraph_VersionStampTest_StampOf_AssemblyNodes_WorksForProductsAndOccurrences(graph):
    assert graph.Topo().Products().Nb() > 0
    stamp = graph.UIDs().StampOf(BRepGraph_ProductId.Start_s())
    assert stamp.IsValid()
    assert not graph.UIDs().IsStale(stamp)


def test_BRepGraph_VersionStampTest_GenericItemUID_NodeAndReferenceItems_RoundTrip(graph):
    uids = graph.UIDs()
    face_item = BRepGraph_ItemId(BRepGraph_FaceId.Start_s())
    face_uid = uids.Of(face_item)
    assert face_uid.IsValid()
    assert face_uid.IsNode()
    assert face_uid.NodeKind() == BRepGraph_NodeId.Kind.Face
    assert uids.ItemIdFrom(face_uid) == face_item
    assert uids.Has(face_uid)

    face_stamp = uids.StampOf(face_item)
    assert face_stamp.IsValid()
    assert face_stamp.IsNodeStamp()
    assert face_stamp.ItemUID() == face_uid

    ref_item = BRepGraph_ItemId(BRepGraph_FaceRefId.Start_s())
    ref_uid = uids.Of(ref_item)
    assert ref_uid.IsValid()
    assert ref_uid.IsReference()
    assert ref_uid.RefKind() == BRepGraph_RefId.Kind.Face
    assert uids.ItemIdFrom(ref_uid) == ref_item
    assert uids.Has(ref_uid)

    ref_stamp = uids.StampOf(ref_item)
    assert ref_stamp.IsValid()
    assert ref_stamp.IsRefStamp()
    assert ref_stamp.ItemUID() == ref_uid


def test_BRepGraph_VersionStampTest_StampOf_RemovedUse_ReturnsInvalidUntilReused(graph):
    f0 = BRepGraph_FaceId.Start_s()
    rep = graph.Topo().Faces().Definition(f0).SurfaceRepId
    assert rep.IsValid()

    surf = BRepGraph_Tool.Face.Surface_s(graph, f0)
    assert surf is not None
    assert graph.UIDs().StampOf(rep).IsValid()

    graph.Editor().Faces().ClearSurface(f0)
    assert not graph.UIDs().StampOf(rep).IsValid()

    graph.Editor().Faces().SetSurface(f0, surf)
    assert graph.Topo().Faces().Definition(f0).SurfaceRepId == rep
    assert graph.UIDs().StampOf(rep).IsValid()


def test_BRepGraph_VersionStampTest_GraphGUID_AfterBuild_IsValid(graph):
    assert graph.UIDs().GraphGUID() != Standard_GUID()


def test_BRepGraph_VersionStampTest_GraphGUID_Rebuild_Changes(graph):
    # copy, the C++ test copies the GUID before the rebuild
    guid1 = Standard_GUID(graph.UIDs().GraphGUID())
    _rebuild(graph)
    guid2 = graph.UIDs().GraphGUID()
    assert guid1 != guid2


def test_BRepGraph_VersionStampTest_ToGUID_Deterministic_SameInputSameOutput(graph):
    stamp = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    gguid = graph.UIDs().GraphGUID()
    assert stamp.ToGUID(gguid) == stamp.ToGUID(gguid)


def test_BRepGraph_VersionStampTest_ToGUID_DifferentMutationGen_DifferentGUID(graph):
    before = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    gguid = graph.UIDs().GraphGUID()
    guid_before = before.ToGUID(gguid)
    _bump_face_tolerance(graph)
    after = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    assert guid_before != after.ToGUID(gguid)


def test_BRepGraph_VersionStampTest_ToGUID_DifferentGraphGUID_DifferentGUID(graph):
    stamp = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    ga = Standard_GUID("a1b2c3d4-e5f6-7890-abcd-ef0123456789")
    gb = Standard_GUID("11223344-5566-7788-99aa-bbccddeeff00")
    assert stamp.ToGUID(ga) != stamp.ToGUID(gb)


def test_BRepGraph_VersionStampTest_ToGUID_DifferentNodes_DifferentGUID(graph):
    gguid = graph.UIDs().GraphGUID()
    s0 = graph.UIDs().StampOf(BRepGraph_FaceId.Start_s())
    s1 = graph.UIDs().StampOf(BRepGraph_FaceId(1))
    assert s0.ToGUID(gguid) != s1.ToGUID(gguid)
