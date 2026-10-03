# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_PermissionUpdate_Test.cxx (LGPL-2.1 with the OCCT exception)
# A C++ scope end of a MutGuard is written as `del guard`.
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_Copy,
    BRepGraph_EdgeIterator,
    BRepGraph_NodeId,
    BRepGraph_OccurrenceId,
    BRepGraph_OccurrenceRefId,
    BRepGraph_OccurrencesOfChild,
    BRepGraph_RefId,
    BRepGraph_RefsFaceOfShell,
    BRepGraph_RefsShellOfSolid,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_SolidIterator,
    BRepGraph_SolidsOfShell,
    BRepGraph_Transform,
    BRepGraph_VertexId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Line
from nanocct.gp import gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED
from nanocct.TopLoc import TopLoc_Location


def _box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    return g


def _array1(cls, items):
    a = NCollection_Array1[cls](1, len(items))
    for i, x in enumerate(items, start=1):
        a.SetValue(i, x)
    return a


def _current_ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _occurrences_of(g, node):
    return _current_ids(BRepGraph_OccurrencesOfChild(g, g.Topo().Gen().OccurrenceRefIds(node)))


def _self_loop_edge(g):
    v = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    return g.Editor().Edges().Add(v, v, line, 0.0, 1.0, 1.0e-7)


def _parent_child(g, extra=0):
    prods = g.Editor().Products()
    ids = []
    for _ in range(2 + extra):
        p = prods.Add()
        prods.AppendDocumentRoot(p)
        assert p.IsValid()
        ids.append(p)
    return ids


def test_BRepGraph_PermissionUpdateTest_RemoveRef_FaceRef_InvalidatesOwningShellBeforeUnbind():
    g = _box_graph()
    refs = BRepGraph_RefsFaceOfShell(g, BRepGraph_ShellId.Start_s())
    assert refs.More()
    face_ref = refs.CurrentId()
    before = g.Topo().Shells().Definition(BRepGraph_ShellId.Start_s()).SubtreeGen
    assert g.Editor().Gen().RemoveRef(face_ref)
    assert face_ref.IsRemoved(g)
    assert g.Topo().Shells().Definition(BRepGraph_ShellId.Start_s()).SubtreeGen > before
    assert g.ValidateRelations()


def test_BRepGraph_PermissionUpdateTest_RemoveShell_SameSolidSiblingRef_PreservesRelations():
    g = _box_graph()
    solid = BRepGraph_SolidId.Start_s()
    refs = BRepGraph_RefsShellOfSolid(g, solid)
    assert refs.More()
    first = refs.CurrentId()
    shell = g.Refs().Shells().Entry(first).ChildShellId
    second = g.Editor().Solids().Append(solid, shell, TopAbs_REVERSED)
    assert second.IsValid()
    assert second != first

    def solids_of_shell():
        return _current_ids(BRepGraph_SolidsOfShell(g, g.Topo().Shells().Relations(shell).ParentShellRefIds))

    assert solid in solids_of_shell()
    assert g.Editor().Solids().RemoveShell(solid, first)
    assert first.IsRemoved(g)
    assert not second.IsRemoved(g)
    assert solid in solids_of_shell()
    assert g.ValidateRelations()


def test_BRepGraph_PermissionUpdateTest_RemoveRef_OccurrenceRef_PreservesProductToOccurrencesIndex():
    g = _box_graph()
    parent, child = _parent_child(g)
    occ_ref = BRepGraph_OccurrenceRefId()
    occ = g.Editor().Products().Append(parent, child, TopLoc_Location(), BRepGraph_OccurrenceId(), occ_ref)
    assert occ.IsValid()
    assert occ_ref.IsValid()
    assert occ in _occurrences_of(g, BRepGraph_NodeId(child))
    assert g.Editor().Gen().RemoveRef(BRepGraph_RefId(occ_ref))
    assert occ not in _occurrences_of(g, BRepGraph_NodeId(child))
    assert occ not in _occurrences_of(g, BRepGraph_NodeId(parent))


def test_BRepGraph_PermissionUpdateTest_RemoveRef_CoEdge_PreservesEdgeToWireWhenSiblingPresent():
    g = BRepGraph()
    g.Clear()
    v1 = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    v2 = g.Editor().Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    line = Geom_Line(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    edge = g.Editor().Edges().Add(v1, v2, line, 0.0, 1.0, 1.0e-7)
    assert edge.IsValid()
    coedges = [g.Editor().CoEdges().Add(edge, TopAbs_FORWARD), g.Editor().CoEdges().Add(edge, TopAbs_REVERSED)]
    wire = g.Editor().Wires().Add(_array1(BRepGraph_CoEdgeId, coedges))
    assert wire.IsValid()
    assert g.ValidateRelations()
    rel = g.Topo().Wires().Relations(wire)
    assert rel.CoEdgeIds.Size() == 2
    first = rel.CoEdgeIds.First()
    assert first.IsValid()

    def contains_wire():
        return any(w == wire for w in _current_ids(g.Topo().Edges().WiresOf(edge)))

    assert contains_wire()
    assert g.Editor().Wires().RemoveCoEdge(wire, first)
    assert g.ValidateRelations()
    assert contains_wire()


def test_BRepGraph_PermissionUpdateTest_SetRefChildVertexId_SelfLoopSibling_KeepsRevIndexValid():
    g = _box_graph()
    edge = _self_loop_edge(g)
    assert edge.IsValid()
    assert g.ValidateRelations()
    start_ref = g.Topo().Edges().Definition(edge).StartVertexRefId
    assert start_ref.IsValid()
    new_v = g.Editor().Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    g.Editor().Vertices().SetRefChildVertexId(start_ref, new_v)
    assert g.ValidateRelations()
    end_ref = g.Topo().Edges().Definition(edge).EndVertexRefId
    old_v = g.Refs().Vertices().Entry(end_ref).ChildVertexId if end_ref.IsValid() else BRepGraph_VertexId()
    assert old_v.IsValid()
    assert any(e == edge for e in g.Topo().Vertices().Edges(old_v))


def test_BRepGraph_PermissionUpdateTest_CopyNode_SelfReferencingCompound_Terminates():
    g = _box_graph()
    v = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    root = g.Editor().Compounds().Add(_array1(BRepGraph_NodeId, [BRepGraph_NodeId(v)]))
    assert root.IsValid()
    rel = g.Topo().Compounds().Relations(root)
    assert not rel.ChildRefIds.IsEmpty()
    child_ref = rel.ChildRefIds.First()
    g.Editor().Gen().SetChildRefChildNodeId(child_ref, BRepGraph_NodeId(root))
    copy = BRepGraph()
    root_id = BRepGraph_Copy.CopyNode_s(
        g, copy, BRepGraph_NodeId(root), BRepGraph_Copy.GeomPolicy.Copy, BRepGraph_Copy.MeshPolicy.Drop
    )
    assert root_id.IsValid()
    assert not copy.IsEmpty()
    assert copy.ValidateRelations()


def _translation():
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(1.0, 0.0, 0.0))
    return t


def test_BRepGraph_PermissionUpdateTest_TransformNode_AssemblyWithCopyGeom_Rejected():
    g = _box_graph()
    prod = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(prod)
    assert prod.IsValid()
    result = BRepGraph()
    root = BRepGraph_Transform.TransformNode_s(
        g, result, BRepGraph_NodeId(prod), _translation(), BRepGraph_Copy.GeomPolicy.Copy, BRepGraph_Copy.MeshPolicy.Drop
    )
    assert not root.IsValid()


def test_BRepGraph_PermissionUpdateTest_TransformNode_OccurrenceWithCopyGeom_Rejected():
    g = _box_graph()
    parent, child = _parent_child(g)
    occ = g.Editor().Products().Append(parent, child, TopLoc_Location())
    assert occ.IsValid()
    result = BRepGraph()
    root = BRepGraph_Transform.TransformNode_s(
        g, result, BRepGraph_NodeId(occ), _translation(), BRepGraph_Copy.GeomPolicy.Copy, BRepGraph_Copy.MeshPolicy.Drop
    )
    assert not root.IsValid()


def test_BRepGraph_PermissionUpdateTest_LinkProducts_OutOccurrenceRefId_Populated():
    g = _box_graph()
    parent, child = _parent_child(g)
    occ_ref = BRepGraph_OccurrenceRefId()
    occ = g.Editor().Products().Append(parent, child, TopLoc_Location(), BRepGraph_OccurrenceId(), occ_ref)
    assert occ.IsValid()
    assert occ_ref.IsValid()
    assert g.Refs().Occurrences().Entry(occ_ref).ChildOccurrenceId == occ
    occ2 = g.Editor().Products().Append(parent, child, TopLoc_Location())
    assert occ2.IsValid()


def test_BRepGraph_PermissionUpdateTest_SetOccurrenceChildNodeId_RejectsOccurrenceChild():
    g = _box_graph()
    parent, child = _parent_child(g)
    occ = g.Editor().Products().Append(parent, child, TopLoc_Location())
    assert occ.IsValid()
    old_child = g.Topo().Occurrences().Definition(occ).ChildNodeId
    g.Editor().Occurrences().SetChildNodeId(occ, BRepGraph_NodeId(occ))
    assert g.Topo().Occurrences().Definition(occ).ChildNodeId == old_child
    assert occ in _occurrences_of(g, old_child)
    assert occ not in _occurrences_of(g, BRepGraph_NodeId(occ))
    assert g.ValidateRelations()


def test_BRepGraph_PermissionUpdateTest_SetOccurrenceChildNodeId_InvalidOccurrenceNoOp():
    g = _box_graph()
    child = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(child)
    assert child.IsValid()
    g.Editor().Occurrences().SetChildNodeId(BRepGraph_OccurrenceId(100000), BRepGraph_NodeId(child))
    assert g.ValidateRelations()


def test_BRepGraph_PermissionUpdateTest_SetOccurrenceChildNodeId_MutGuardRejectsRemovedChild():
    g = _box_graph()
    parent, child, removed = _parent_child(g, extra=1)
    occ = g.Editor().Products().Append(parent, child, TopLoc_Location())
    assert occ.IsValid()
    old_child = g.Topo().Occurrences().Definition(occ).ChildNodeId
    g.Editor().Gen().RemoveNode(removed)
    guard = g.Editor().Occurrences().Mut(occ)
    g.Editor().Occurrences().SetChildNodeId(guard, BRepGraph_NodeId(removed))
    assert not guard.IsDirty()
    del guard
    assert g.Topo().Occurrences().Definition(occ).ChildNodeId == old_child
    assert occ in _occurrences_of(g, old_child)
    assert occ not in _occurrences_of(g, BRepGraph_NodeId(removed))
    assert g.ValidateRelations()


def test_BRepGraph_PermissionUpdateTest_MoveRef_ChildRefScaledTrsf_RejectedWithoutMutation():
    g = _box_graph()
    compound = g.Editor().Compounds().Add(_array1(BRepGraph_NodeId, [BRepGraph_NodeId(BRepGraph_SolidId.Start_s())]))
    assert compound.IsValid()
    ids = g.Refs().Children().IdsOf(compound)
    assert ids.Size() == 1
    child_ref = ids.First()
    scaled = gp_Trsf()
    scaled.SetScaleFactor(2.0)
    assert not BRepGraph_Transform.MoveRef_s(g, child_ref, scaled)
    assert g.Refs().Children().Entry(child_ref).LocalLocation.IsIdentity()
    trans = gp_Trsf()
    trans.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    assert BRepGraph_Transform.MoveRef_s(g, child_ref, trans)
    assert not g.Refs().Children().Entry(child_ref).LocalLocation.IsIdentity()


def test_BRepGraph_PermissionUpdateTest_RemoveSubgraph_NestedCascade_FinalStateValid():
    g = _box_graph()
    assert g.ValidateRelations()
    it = BRepGraph_SolidIterator(g)
    assert it.More()
    solid = it.CurrentId()
    assert solid.IsValid()
    g.Editor().Gen().RemoveSubgraph(BRepGraph_NodeId(solid))
    assert g.ValidateRelations()


def test_BRepGraph_PermissionUpdateTest_MutGuard_DirtyFlag_RespectsExplicitMarkAndCleanScope():
    g = _box_graph()
    it = BRepGraph_EdgeIterator(g)
    assert it.More()
    edge = it.CurrentId()
    before = g.Topo().Edges().Definition(edge).OwnGen
    # the C++ test reads aGuard->Tolerance; operator-> has no binding, a guard that is never written is the point
    guard = g.Editor().Edges().Mut(edge)
    del guard
    assert g.Topo().Edges().Definition(edge).OwnGen == before
    guard = g.Editor().Edges().Mut(edge)
    guard.MarkDirty()
    del guard
    assert g.Topo().Edges().Definition(edge).OwnGen > before
