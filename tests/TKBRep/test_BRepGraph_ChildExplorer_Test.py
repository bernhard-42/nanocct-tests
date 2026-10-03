# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_ChildExplorer_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest
from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_ChildExplorer,
    BRepGraph_CompoundId,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_RefId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound

K = BRepGraph_NodeId.Kind
Mode = BRepGraph_ChildExplorer.TraversalMode
LinkKind = BRepGraph_ChildExplorer.LinkKind


def _box(dx=10.0, dy=20.0, dz=30.0):
    return BRepPrimAPI_MakeBox(dx, dy, dz).Shape()


def _graph(shape=None):
    g = BRepGraph()
    g.Clear()
    if shape is None:
        shape = _box()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _compound(*shapes):
    comp = TopoDS_Compound()
    bb = BRep_Builder()
    bb.MakeCompound(comp)
    for s in shapes:
        bb.Add(comp, s)
    return comp


def _direct(g, root, kind, loc=None, ori=None):
    if loc is None:
        return BRepGraph_ChildExplorer(g, root, kind, Mode.DirectChildren)
    return BRepGraph_ChildExplorer(g, root, kind, loc, ori, Mode.DirectChildren)


def _count(exp):
    n = 0
    while exp.More():
        n += 1
        exp.Next()
    return n


def _translation(x, y, z):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(x, y, z))
    return t


def test_BRepGraph_ChildExplorerTest_Box_EdgeOccurrences_Count24():
    g = _graph()
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge)) == 24


def test_BRepGraph_ChildExplorerTest_Box_FaceOccurrences_Count6():
    g = _graph()
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Face)) == 6


def test_BRepGraph_ChildExplorerTest_Box_VertexOccurrences():
    g = _graph()
    visited = set()
    count = 0
    exp = BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Vertex)
    while exp.More():
        visited.add(exp.Current().DefId.Index)
        count += 1
        exp.Next()
    assert count > 0
    assert len(visited) == 8


def test_BRepGraph_ChildExplorerTest_Face_EdgeOccurrences_4():
    g = _graph()
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_FaceId.Start_s(), K.Edge)) == 4


def test_BRepGraph_ChildExplorerTest_InvalidRoot_Empty():
    g = _graph()
    assert not BRepGraph_ChildExplorer(g, BRepGraph_NodeId(), K.Edge).More()


def test_BRepGraph_ChildExplorerTest_RootEqualsTarget_ReturnsSelf():
    g = _graph()
    exp = BRepGraph_ChildExplorer(g, BRepGraph_FaceId.Start_s(), K.Face)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_FaceId.Start_s()
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ChildExplorerTest_AvoidKind_Shell_SkipsContainedFaces():
    g = _graph()
    exp = BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Face, K.Shell, False)
    assert not exp.More()


def test_BRepGraph_ChildExplorerTest_AvoidKind_EmitBoundary_ReturnsFacesInsteadOfEdges():
    g = _graph()
    n = 0
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge, K.Face, True):
        assert inst.DefId.NodeKind == K.Face
        n += 1
    assert n == 6


def test_BRepGraph_ChildExplorerTest_AvoidKind_SameAsTarget_IsIgnored():
    g = _graph()
    n = 0
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Face, K.Face, False):
        assert inst.DefId.NodeKind == K.Face
        n += 1
    assert n == 6


def test_BRepGraph_ChildExplorerTest_AllDescendants_Recursive_YieldsAllKinds():
    g = _graph()
    counts = {}
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s()):
        kind = inst.DefId.NodeKind
        assert kind in (K.Shell, K.Face, K.Wire, K.CoEdge, K.Edge, K.Vertex)
        counts[kind] = counts.get(kind, 0) + 1
    assert counts[K.Shell] == 1
    assert counts[K.Face] == 6
    assert counts[K.Wire] == 6
    assert counts[K.CoEdge] == 24
    assert counts[K.Edge] == 24
    assert counts[K.Vertex] == 48


def test_BRepGraph_ChildExplorerTest_AllDescendants_AvoidFaceBoundary_StopsBelowFaces():
    g = _graph()
    shells = 0
    faces = 0
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Face, True):
        if inst.DefId.NodeKind == K.Shell:
            shells += 1
            continue
        assert inst.DefId.NodeKind == K.Face
        faces += 1
    assert shells == 1
    assert faces == 6


def test_BRepGraph_ChildExplorerTest_NoCumLoc_IdentityLocation():
    g = _graph()
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge, False, True):
        assert inst.Location.IsIdentity()


def test_BRepGraph_ChildExplorerTest_NoCumOri_ForwardOrientation():
    g = _graph()
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge, True, False):
        assert inst.Orientation == TopAbs_FORWARD


def test_BRepGraph_ChildExplorerTest_GlobalLocation_Box_Identity():
    g = _graph()
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge):
        assert inst.Location.IsIdentity()


def test_BRepGraph_ChildExplorerTest_GlobalOrientation_BoxEdges_ForwardOrReversed():
    g = _graph()
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge):
        assert inst.Orientation in (TopAbs_FORWARD, TopAbs_REVERSED)


def test_BRepGraph_ChildExplorerTest_Compound_FaceCount():
    g = _graph(_compound(_box(10, 10, 10), _box(20, 20, 20)))
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_CompoundId.Start_s(), K.Face)) == 12


def test_BRepGraph_ChildExplorerTest_NodeOf_Kind_Face():
    g = _graph()
    exp = BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge)
    assert exp.More()
    face = exp.NodeOf(K.Face)
    assert face.IsValid()
    assert face.NodeKind == K.Face


def test_BRepGraph_ChildExplorerTest_DeepCompound_NoStackOverflow():
    inner = _box(1, 1, 1)
    for _ in range(100):
        inner = _compound(inner)
    g = _graph(inner)
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_CompoundId.Start_s(), K.Face)) == 6


def test_BRepGraph_ChildExplorerTest_Recreate_ResetAndReexplore():
    g = _graph()
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Face)) == 6
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Edge)) == 24


def test_BRepGraph_ChildExplorerTest_CoEdgeTarget_Reachable():
    g = _graph()
    n = 0
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.CoEdge):
        assert inst.DefId.NodeKind == K.CoEdge
        n += 1
    assert n == 24


def test_BRepGraph_ChildExplorerTest_CoEdgeTarget_FromFace_Count4():
    g = _graph()
    n = 0
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_FaceId.Start_s(), K.CoEdge):
        assert inst.DefId.NodeKind == K.CoEdge
        n += 1
    assert n == 4


def test_BRepGraph_ChildExplorerTest_DirectChildren_ShellFaces_CountAndOrder():
    g = _graph()
    shell = BRepGraph_ShellId(0)
    expected = []
    for ref_id in g.Refs().Faces().IdsOf(shell):
        ref = g.Refs().Faces().Entry(ref_id)
        if not ref_id.IsRemoved(g):
            expected.append(ref.ChildFaceId.Index)
    actual = []
    exp = _direct(g, shell, K.Face)
    while exp.More():
        assert exp.Current().DefId.NodeKind == K.Face
        actual.append(exp.Current().DefId.Index)
        exp.Next()
    assert actual == expected


def test_BRepGraph_ChildExplorerTest_DirectChildren_ShellFaces_ExposeParentAndRef():
    g = _graph()
    shell = BRepGraph_ShellId(0)
    ordinal = 0
    exp = _direct(g, shell, K.Face)
    while exp.More():
        face_ref = g.Refs().Faces().IdsOf(shell).Value(ordinal)
        assert exp.CurrentParent() == BRepGraph_NodeId(shell)
        assert exp.CurrentLinkKind() == LinkKind.Reference
        assert exp.CurrentRef() == BRepGraph_RefId(face_ref)
        exp.Next()
        ordinal += 1


def test_BRepGraph_ChildExplorerTest_DirectChildren_ProductShapeRoot_ViaOccurrenceRef():
    g = _graph()
    product = g.Editor().Products().Add(BRepGraph_SolidId.Start_s())
    g.Editor().Products().AppendDocumentRoot(product)
    assert product.IsValid()
    it = BRepGraph_ChildExplorer(g, product, Mode.DirectChildren)
    assert it.More()
    assert it.Current().DefId.NodeKind == K.Occurrence
    assert it.CurrentParent() == BRepGraph_NodeId(product)
    assert it.CurrentRef().IsValid()
    it.Next()
    assert not it.More()


def test_BRepGraph_ChildExplorerTest_RootEqualsTarget_LinkKindNone():
    g = _graph()
    exp = BRepGraph_ChildExplorer(g, BRepGraph_FaceId.Start_s(), K.Face)
    assert exp.More()
    assert exp.CurrentLinkKind() == LinkKind.None_
    assert not exp.CurrentParent().IsValid()
    assert not exp.CurrentRef().IsValid()


def test_BRepGraph_ChildExplorerTest_DirectChildren_ProductOccurrences_ExposeOccurrenceRefs():
    g = _graph()
    products = g.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()
    occ0 = products.Append(assembly, part, TopLoc_Location())
    occ1 = products.Append(assembly, part, TopLoc_Location())
    assert occ0.IsValid()
    assert occ1.IsValid()
    occ_refs = g.Refs().Occurrences().IdsOf(assembly)
    assert occ_refs.Size() == 2
    ordinal = 0
    it = BRepGraph_ChildExplorer(g, assembly, Mode.DirectChildren)
    while it.More():
        assert it.CurrentParent() == BRepGraph_NodeId(assembly)
        assert it.CurrentRef() == BRepGraph_RefId(occ_refs.Value(ordinal))
        it.Next()
        ordinal += 1
    assert ordinal == 2


def test_BRepGraph_ChildExplorerTest_DirectChildren_RemovedFaceRef_IsSkipped():
    g = _graph()
    shell = BRepGraph_ShellId(0)
    face_refs = g.Refs().Faces().IdsOf(shell)
    assert face_refs.Size() > 0
    nb_before = face_refs.Size()
    removed_ref = face_refs.Value(0)
    removed_face = g.Refs().Faces().Entry(removed_ref).ChildFaceId
    g.Editor().Gen().RemoveRef(removed_ref)
    n = 0
    exp = _direct(g, shell, K.Face)
    while exp.More():
        assert exp.Current().DefId != BRepGraph_NodeId(removed_face)
        n += 1
        exp.Next()
    assert n == nb_before - 1


def test_BRepGraph_ChildExplorerTest_DirectChildren_WireChildren_AreCoEdges():
    g = _graph()
    face = BRepGraph_FaceId(0)
    wire_refs = g.Refs().Wires().IdsOf(face)
    assert wire_refs.Size() > 0
    wire = g.Refs().Wires().Entry(wire_refs.Value(0)).ChildWireId
    coedges = g.Topo().Wires().Relations(wire).CoEdgeIds
    n = 0
    exp = _direct(g, wire, K.CoEdge)
    while exp.More():
        assert exp.Current().DefId.NodeKind == K.CoEdge
        n += 1
        exp.Next()
    assert n == coedges.Size()


def test_BRepGraph_ChildExplorerTest_DirectChildren_CompoundChildren_Basic():
    g = _graph(_compound(_box(10, 10, 10), _box(20, 20, 20)))
    n = 0
    exp = _direct(g, BRepGraph_CompoundId.Start_s(), K.Solid)
    while exp.More():
        assert BRepGraph_NodeId.IsTopologyKind_s(exp.Current().DefId.NodeKind)
        n += 1
        exp.Next()
    assert n == 2


def test_BRepGraph_ChildExplorerTest_DirectChildren_ChainedTraversal_ParityWithRecursiveTraversal():
    box = _box()
    box.Move(TopLoc_Location(_translation(100.0, 0.0, 0.0)))
    g = _graph(_compound(box))

    expected_loc = {}
    expected_ori = {}
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_CompoundId.Start_s(), K.Face):
        idx = inst.DefId.Index
        if idx not in expected_loc:
            expected_loc[idx] = inst.Location
            expected_ori[idx] = inst.Orientation

    visited = 0
    solid_it = _direct(g, BRepGraph_CompoundId.Start_s(), K.Solid)
    while solid_it.More():
        solid = solid_it.Current()
        shell_it = _direct(g, solid.DefId, K.Shell, solid.Location, solid.Orientation)
        while shell_it.More():
            shell = shell_it.Current()
            face_it = _direct(g, shell.DefId, K.Face, shell.Location, shell.Orientation)
            while face_it.More():
                face = face_it.Current()
                assert face.DefId.NodeKind == K.Face
                idx = face.DefId.Index
                assert idx in expected_loc
                assert face.Location.IsEqual(expected_loc[idx])
                assert face.Orientation == expected_ori[idx]
                visited += 1
                face_it.Next()
            shell_it.Next()
        solid_it.Next()
    assert visited == len(expected_loc)


def test_BRepGraph_ChildExplorerTest_Recursive_SharedProduct_ChildrenHaveDistinctContexts():
    g = _graph()
    products = g.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()
    occ1 = products.Append(assembly, part, TopLoc_Location(_translation(10.0, 0.0, 0.0)))
    occ2 = products.Append(assembly, part, TopLoc_Location(_translation(20.0, 0.0, 0.0)))
    assert occ1.IsValid()
    assert occ2.IsValid()

    locs = []
    for inst in BRepGraph_ChildExplorer(g, assembly, K.Solid):
        assert inst.DefId == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
        locs.append(inst.Location)
    assert len(locs) == 2
    assert not locs[0].IsEqual(locs[1])


def test_BRepGraph_ChildExplorerTest_Recursive_ProductOccurrenceChain_ReachesNestedOccurrences():
    g = BRepGraph()
    g.Clear()
    products = g.Editor().Products()
    part = products.Add()
    sub = products.Add()
    top = products.Add()
    assert part.IsValid()
    assert sub.IsValid()
    assert top.IsValid()
    sub_occ = products.Append(top, sub, TopLoc_Location())
    part_occ = products.Append(sub, part, TopLoc_Location())
    assert sub_occ.IsValid()
    assert part_occ.IsValid()

    has_sub = False
    has_part = False
    n = 0
    for inst in BRepGraph_ChildExplorer(g, top, K.Occurrence):
        has_sub = has_sub or inst.DefId == BRepGraph_NodeId(sub_occ)
        has_part = has_part or inst.DefId == BRepGraph_NodeId(part_occ)
        n += 1
    assert n == 2
    assert has_sub
    assert has_part


def test_BRepGraph_ChildExplorerTest_Recursive_ProductPartRootContext_ComposedWithOccurrence():
    g = _graph()
    products = g.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assert part.IsValid()
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert assembly.IsValid()

    occ_trsf = _translation(10.0, 0.0, 0.0)
    occ = products.Append(assembly, part, TopLoc_Location(occ_trsf))
    assert occ.IsValid()

    root_trsf = _translation(0.0, 20.0, 0.0)
    for ref_id in g.Topo().Products().Relations(part).OccurrenceRefIds:
        occ_ref = g.Refs().Occurrences().Entry(ref_id)
        occ_def = g.Topo().Occurrences().Definition(occ_ref.ChildOccurrenceId)
        if BRepGraph_NodeId.IsTopologyKind_s(occ_def.ChildNodeId.NodeKind):
            mut_ref = g.Editor().Occurrences().MutRef(ref_id)
            g.Editor().Occurrences().SetRefLocalLocation(mut_ref, TopLoc_Location(root_trsf))
            del mut_ref
            break

    it = BRepGraph_ChildExplorer(g, assembly, K.Solid)
    assert it.More()
    assert it.Current().DefId == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    usage = it.Current()
    expected = (TopLoc_Location(occ_trsf) * TopLoc_Location(root_trsf)).Transformation()
    actual = usage.Location.Transformation()
    tol = Precision.Confusion_s()
    assert abs(actual.TranslationPart().X() - expected.TranslationPart().X()) <= tol
    assert abs(actual.TranslationPart().Y() - expected.TranslationPart().Y()) <= tol
    assert abs(actual.TranslationPart().Z() - expected.TranslationPart().Z()) <= tol
    it.Next()
    assert not it.More()


def test_BRepGraph_ChildExplorerTest_DirectChildren_HighFanout_DirectChildrenComplete():
    g = _graph(_compound(*[_box(1.0 + i, 2.0, 3.0) for i in range(80)]))
    assert _count(_direct(g, BRepGraph_CompoundId.Start_s(), K.Solid)) == 80


def test_BRepGraph_ChildExplorerTest_HighFanout_CompletesAllChildren():
    g = _graph(_compound(*[_box(1, 1, 1) for _ in range(500)]))
    assert _count(BRepGraph_ChildExplorer(g, BRepGraph_CompoundId.Start_s(), K.Face)) == 500 * 6


def test_BRepGraph_ChildExplorerTest_StructuredBindings_NodeInstance():
    box = _box()
    box.Move(TopLoc_Location(_translation(100.0, 0.0, 0.0)))
    g = _graph(_compound(box))
    n = 0
    for inst in BRepGraph_ChildExplorer(g, BRepGraph_CompoundId.Start_s(), K.Face):
        node_id, loc, ori = inst.DefId, inst.Location, inst.Orientation
        assert node_id.NodeKind == K.Face
        assert not loc.IsIdentity()
        assert ori in (TopAbs_FORWARD, TopAbs_REVERSED)
        n += 1
    assert n == 6


def test_BRepGraph_ChildExplorerTest_RangeFor_NodeInstance():
    g = _graph()
    n = 0
    for usage in BRepGraph_ChildExplorer(g, BRepGraph_SolidId.Start_s(), K.Face):
        assert usage.DefId.NodeKind == K.Face
        n += 1
    assert n == 6
