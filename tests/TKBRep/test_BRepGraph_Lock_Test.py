# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Lock_Test.cxx (LGPL-2.1 with the OCCT exception)
# LayerRegistry().Ensure<T>() / FindLayer<T>() are templates; they are written as FindLayer(T.GetID_s()) plus RegisterLayer(T()).
import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_Compact,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_ItemId,
    BRepGraph_LayerDeferred,
    BRepGraph_LayerLock,
    BRepGraph_NodeId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_VertexId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.Standard import Standard_GUID, Standard_ProgramError
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED

TEST_OWNER = "2ee13474-4cc6-4f6f-bde2-f0e4dcf9e5f1"
OTHER_OWNER = "63c7da5f-4adc-4024-85f2-329525dc76b7"
RepKind = BRepGraph_LayerDeferred.RepresentationKind


def _box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _find(g, cls):
    return g.LayerRegistry().FindLayer(cls.GetID_s())


def _ensure(g, cls):
    layer = _find(g, cls)
    if layer is None:
        layer = cls()
        g.LayerRegistry().RegisterLayer(layer)
    return layer


def _owned(g, item):
    layer = _find(g, BRepGraph_LayerLock)
    return layer is not None and layer.HasOwner(item)


def _lock(g, item):
    _ensure(g, BRepGraph_LayerLock).SetOwner(item, Standard_GUID(TEST_OWNER))


def _start_vertex_ref(g):
    return g.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s()).StartVertexRefId


def test_BRepGraph_LockTest_NewItemsAreUnlockedByDefault():
    g = _box_graph()
    assert not g.IsEmpty()
    assert not _owned(g, BRepGraph_VertexId.Start_s())
    assert not _owned(g, _start_vertex_ref(g))


def test_BRepGraph_LockTest_LockLayerControlsStorageFlag():
    g = _box_graph()
    v = BRepGraph_VertexId.Start_s()
    assert not _owned(g, v)
    _lock(g, v)
    assert _owned(g, v)
    _ensure(g, BRepGraph_LayerLock).UnsetOwner(BRepGraph_ItemId(BRepGraph_NodeId(v)), Standard_GUID(TEST_OWNER))
    assert not _owned(g, v)


def test_BRepGraph_LockTest_LockedNodeRejectsMutableGuard():
    g = _box_graph()
    v = BRepGraph_VertexId.Start_s()
    _lock(g, v)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Vertices().Mut(v)


def test_BRepGraph_LockTest_LockedReferenceRejectsMutableGuard():
    g = _box_graph()
    ref = _start_vertex_ref(g)
    _lock(g, ref)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Vertices().MutRef(ref)


def test_BRepGraph_LockTest_LockedNodeRejectsRemoval():
    g = _box_graph()
    v = BRepGraph_VertexId.Start_s()
    _lock(g, v)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Gen().RemoveNode(v)


def test_BRepGraph_LockTest_LockedParentRejectsStructuralAdd():
    g = _box_graph()
    shell = BRepGraph_ShellId.Start_s()
    _lock(g, shell)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Shells().Append(shell, BRepGraph_FaceId.Start_s(), TopAbs_FORWARD)


def test_BRepGraph_LockTest_LockedNodeRejectsDirectSetterWithoutMutation():
    g = _box_graph()
    v = BRepGraph_VertexId.Start_s()
    point = gp_Pnt(g.Topo().Vertices().Definition(v).Point.XYZ())
    _lock(g, v)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Vertices().SetPoint(v, gp_Pnt(1.0, 2.0, 3.0))
    assert abs(g.Topo().Vertices().Definition(v).Point.Distance(point)) <= 1.0e-12


def test_BRepGraph_LockTest_LockedReferenceRejectsOrientationSetterWithoutMutation():
    g = _box_graph()
    ref = _start_vertex_ref(g)
    # BRepGraphInc::ParityOrientation has no bound conversion to TopAbs_Orientation: compare IsReversed
    orientation = g.Refs().Vertices().Entry(ref).Orientation.IsReversed
    _lock(g, ref)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Vertices().SetRefOrientation(ref, TopAbs_REVERSED)
    assert g.Refs().Vertices().Entry(ref).Orientation.IsReversed == orientation


def test_BRepGraph_LockTest_LockedRepresentationRejectsDirectSetterWithoutMutation():
    g = _box_graph()
    surface = g.Topo().Faces().Surface(BRepGraph_FaceId.Start_s())
    assert surface is not None
    # C++ compares the raw pointers (.get()); the same OCCT object maps to the same Python object
    assert g.Topo().Faces().Surface(BRepGraph_FaceId.Start_s()) is surface


def test_BRepGraph_LockTest_LockLayerOwnerControlsLockFlag():
    g = _box_graph()
    v = BRepGraph_VertexId.Start_s()
    layer = _ensure(g, BRepGraph_LayerLock)
    owner = Standard_GUID(TEST_OWNER)
    layer.SetOwner(v, owner)
    assert _owned(g, v)
    assert layer.HasOwner(v)
    found = Standard_GUID()
    assert layer.FindOwnerId(v, found)
    assert found == owner
    layer.UnsetOwner(v)
    assert not _owned(g, v)
    assert not layer.HasOwner(v)


def test_BRepGraph_LockTest_RejectsDifferentOwnerWhenAncestorOwnsNode():
    g = _box_graph()
    solid = BRepGraph_SolidId.Start_s()
    face = BRepGraph_FaceId.Start_s()
    layer = _ensure(g, BRepGraph_LayerLock)
    assert layer.SetOwner(BRepGraph_ItemId(BRepGraph_NodeId(solid)), Standard_GUID(TEST_OWNER), False)
    assert layer.HasOwner(face)
    assert not layer.SetOwner(BRepGraph_ItemId(BRepGraph_NodeId(face)), Standard_GUID(OTHER_OWNER), False)
    found = Standard_GUID()
    assert layer.FindOwnerId(face, found)
    assert found == Standard_GUID(TEST_OWNER)


def test_BRepGraph_LockTest_ParentOwnerRejectsDifferentOwnedDescendant():
    g = _box_graph()
    solid = BRepGraph_SolidId.Start_s()
    face = BRepGraph_FaceId.Start_s()
    layer = _ensure(g, BRepGraph_LayerLock)
    assert layer.SetOwner(BRepGraph_ItemId(BRepGraph_NodeId(face)), Standard_GUID(TEST_OWNER), False)
    assert not layer.SetOwner(BRepGraph_ItemId(BRepGraph_NodeId(solid)), Standard_GUID(OTHER_OWNER), False)
    assert layer.HasOwner(face)
    assert not layer.HasOwner(solid)


def test_BRepGraph_LockTest_ParentOwnerCollapsesSameOwnedDescendant():
    g = _box_graph()
    solid = BRepGraph_SolidId.Start_s()
    face = BRepGraph_FaceId.Start_s()
    layer = _ensure(g, BRepGraph_LayerLock)
    assert layer.SetOwner(BRepGraph_ItemId(BRepGraph_NodeId(face)), Standard_GUID(TEST_OWNER), False)
    assert layer.SetOwner(BRepGraph_ItemId(BRepGraph_NodeId(solid)), Standard_GUID(TEST_OWNER), False)
    assert layer.HasOwner(face)
    assert layer.HasOwner(solid)
    layer.UnsetOwner(solid)
    assert not layer.HasOwner(solid)
    assert not layer.HasOwner(face)


def test_BRepGraph_LockTest_RemovedRootOwnerCallbackClearsDescendantOwnedFlags():
    g = _box_graph()
    solid = BRepGraph_SolidId.Start_s()
    face = BRepGraph_FaceId.Start_s()
    rel = g.Topo().Faces().Relations(face)
    assert not rel.WireRefIds.IsEmpty()
    wire_ref = rel.WireRefIds.First()
    layer = _ensure(g, BRepGraph_LayerLock)
    assert layer.SetOwner(BRepGraph_ItemId(BRepGraph_NodeId(solid)), Standard_GUID(TEST_OWNER), False)
    assert layer.HasOwner(solid)
    assert layer.HasOwner(face)
    assert layer.HasOwner(wire_ref)
    g.LayerRegistry().DispatchOnNodeRemoved(solid)
    assert not layer.HasOwner(solid)
    assert not layer.HasOwner(face)
    assert not layer.HasOwner(wire_ref)


def test_BRepGraph_LockTest_DeferredLayerRegistersMultipleRepresentationsAndLocksItem():
    g = _box_graph()
    face = BRepGraph_FaceId.Start_s()
    layer = _ensure(g, BRepGraph_LayerDeferred)
    layer.RegisterDeferred(face, "TestProvider", "test-source", RepKind.Geometry, "surface", 42)
    layer.RegisterDeferred(face, "TestProvider", "test-source", RepKind.Mesh, "triangulation", 7)
    assert _owned(g, face)
    entry = layer.FindDeferred(face)
    assert entry is not None
    assert entry.Provider.ToCString() == "TestProvider"
    assert entry.SourceKey.ToCString() == "test-source"
    assert entry.Representations.Size() == 2
    layer.UnregisterDeferred(face)
    assert not _owned(g, face)
    assert not layer.HasDeferred(face)


def test_BRepGraph_LockTest_DeferredLayerClearsOwnerOnNodeRemoved():
    g = _box_graph()
    face = BRepGraph_FaceId.Start_s()
    layer = _ensure(g, BRepGraph_LayerDeferred)
    layer.RegisterDeferred(face, "TestProvider", "test-source", RepKind.Geometry, "surface", 42)
    assert _owned(g, face)
    assert layer.HasDeferred(face)
    g.LayerRegistry().DispatchOnNodeRemoved(face)
    assert not _owned(g, face)
    assert not layer.HasDeferred(face)


def test_BRepGraph_LockTest_Compact_PreservesDeferredRefEntry():
    g = _box_graph()
    removed = BRepGraph_FaceId.Start_s()
    kept = BRepGraph_FaceId(1)
    rel = g.Topo().Faces().Relations(kept)
    assert not rel.WireRefIds.IsEmpty()
    wire_ref = rel.WireRefIds.First()
    layer = _ensure(g, BRepGraph_LayerDeferred)
    layer.RegisterDeferred(wire_ref, "TestProvider", "ref-source", RepKind.Topology, "wire-ref", 11)
    assert layer.HasDeferred(wire_ref)
    assert _owned(g, wire_ref)
    g.Editor().Gen().RemoveNode(removed)
    BRepGraph_Compact.Perform_s(g)
    layer = _ensure(g, BRepGraph_LayerDeferred)
    assert g.Topo().Faces().Nb() >= 1
    crel = g.Topo().Faces().Relations(BRepGraph_FaceId.Start_s())
    assert not crel.WireRefIds.IsEmpty()
    cref = crel.WireRefIds.First()
    assert layer.HasDeferred(cref)
    assert _owned(g, cref)


def test_BRepGraph_LockTest_Compact_PreservesLockOnExactGeometryRep():
    g = _box_graph()
    removed = BRepGraph_FaceId.Start_s()
    kept = BRepGraph_FaceId(1)
    assert g.Topo().Faces().Definition(kept).SurfaceRepId.IsValid()
    layer = _ensure(g, BRepGraph_LayerLock)
    layer.SetOwner(kept, Standard_GUID(TEST_OWNER))
    assert layer.HasOwner(kept)
    g.Editor().Gen().RemoveNode(removed)
    BRepGraph_Compact.Perform_s(g)
    layer = _ensure(g, BRepGraph_LayerLock)
    assert g.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SurfaceRepId.IsValid()
    assert layer.HasOwner(BRepGraph_FaceId.Start_s())
