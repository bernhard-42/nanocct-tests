# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_LayerTopoSupplement_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# LayerRegistry().Ensure<T>() / FindLayer<T>() are templates (not bound): FindLayer(T.GetID_s()) plus
# RegisterLayer(T()) when absent. A null Entry* from FindByUid is None.

from nanocct import TopAbs
from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CompoundId,
    BRepGraph_CompSolidId,
    BRepGraph_Copy,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_LayerTopoSupplement,
    BRepGraph_NodeId,
    BRepGraph_RefsVertexOfEdge,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_SupplementEditor,
    BRepGraph_SupplementIterator,
    BRepGraph_VertexId,
)
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.TopoDS import (
    TopoDS_Compound,
    TopoDS_CompSolid,
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Iterator,
    TopoDS_Shell,
    TopoDS_Solid,
    TopoDS_Vertex,
    TopoDS_Wire,
)

AK = BRepGraph_LayerTopoSupplement.AttachmentKind
NKind = BRepGraph_NodeId.Kind


def _find_layer(g):
    return g.LayerRegistry().FindLayer(BRepGraph_LayerTopoSupplement.GetID_s())


def _ensure_layer(g):
    layer = _find_layer(g)
    if layer is None:
        layer = BRepGraph_LayerTopoSupplement()
        g.LayerRegistry().RegisterLayer(layer)
    return layer


def _options_no_product():
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = False
    return opts


def _vertex(p):
    v = TopoDS_Vertex()
    BRep_Builder().MakeVertex(v, p, 1.0e-7)
    return v


def _edge_with_supplement_vertices():
    bb = BRep_Builder()
    start = _vertex(gp_Pnt(0.0, 0.0, 0.0))
    extra_fwd = _vertex(gp_Pnt(2.0, 0.0, 0.0))
    internal = _vertex(gp_Pnt(5.0, 0.0, 0.0))
    external = _vertex(gp_Pnt(7.0, 0.0, 0.0))
    end = _vertex(gp_Pnt(10.0, 0.0, 0.0))

    edge = TopoDS_Edge()
    bb.MakeEdge(edge)
    bb.Add(edge, extra_fwd.Oriented(TopAbs.TopAbs_FORWARD))
    bb.Add(edge, start.Oriented(TopAbs.TopAbs_FORWARD))
    bb.Add(edge, internal.Oriented(TopAbs.TopAbs_INTERNAL))
    bb.Add(edge, external.Oriented(TopAbs.TopAbs_EXTERNAL))
    bb.Add(edge, end.Oriented(TopAbs.TopAbs_REVERSED))
    return edge


def _plain_face(loose_vertex=False):
    bb = BRep_Builder()
    pts = [gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0), gp_Pnt(10.0, 10.0, 0.0), gp_Pnt(0.0, 10.0, 0.0)]
    vs = [_vertex(p) for p in pts]
    edges = []
    for i in range(4):
        e = TopoDS_Edge()
        bb.MakeEdge(e)
        bb.Add(e, vs[i].Oriented(TopAbs.TopAbs_FORWARD))
        bb.Add(e, vs[(i + 1) % 4].Oriented(TopAbs.TopAbs_REVERSED))
        edges.append(e)
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    for e in edges:
        bb.Add(wire, e)
    wire.Closed(True)

    face = TopoDS_Face()
    bb.MakeFace(face)
    bb.Add(face, wire)
    if loose_vertex:
        bb.Add(face, _vertex(gp_Pnt(5.0, 5.0, 0.0)).Oriented(TopAbs.TopAbs_INTERNAL))
    return face


def _face_with_supplement_vertex():
    return _plain_face(loose_vertex=True)


def _plain_shell():
    bb = BRep_Builder()
    shell = TopoDS_Shell()
    bb.MakeShell(shell)
    bb.Add(shell, _plain_face())
    return shell


def _plain_solid():
    bb = BRep_Builder()
    solid = TopoDS_Solid()
    bb.MakeSolid(solid)
    bb.Add(solid, _plain_shell())
    return solid


def _plain_compsolid():
    bb = BRep_Builder()
    cs = TopoDS_CompSolid()
    bb.MakeCompSolid(cs)
    bb.Add(cs, _plain_solid())
    return cs


def _add_empty_compsolid(g):
    return g.Editor().CompSolids().Add(NCollection_Array1[BRepGraph_SolidId]())


def _count_direct_children(shape, shape_type, orientation):
    count = 0
    for child in TopoDS_Iterator(shape, False, False):
        if child.ShapeType() == shape_type and child.Orientation() == orientation:
            count += 1
    return count


def test_BRepGraph_LayerTopoSupplementTest_AttachAndRemoveVertexSupplement():
    g = BRepGraph()
    owner = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)

    editor = BRepGraph_SupplementEditor(g)
    uid = editor.AttachToVertex(owner, _vertex(gp_Pnt(1.0, 2.0, 3.0)))
    assert uid != 0

    layer = _find_layer(g)
    assert layer is not None

    attached = layer.AttachedTo(BRepGraph_NodeId(owner))
    assert len(attached) == 1
    assert attached.First() == uid

    entry = layer.FindByUid(uid)
    assert entry is not None
    assert entry.BaseOwner == BRepGraph_NodeId(owner)
    assert entry.Kind == AK.VertexSupplementShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_VERTEX

    assert editor.RemoveAttachment(uid)
    assert len(layer.AttachedTo(BRepGraph_NodeId(owner))) == 0
    assert layer.FindByUid(uid) is None


def test_BRepGraph_LayerTopoSupplementTest_SupplementIteratorPreservesOwnerOrderAndUidLookup():
    g = BRepGraph()
    owner = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)

    editor = BRepGraph_SupplementEditor(g)
    first = editor.AttachToVertex(owner, _vertex(gp_Pnt(1.0, 0.0, 0.0)))
    second = editor.AttachToVertex(owner, _vertex(gp_Pnt(2.0, 0.0, 0.0)))
    assert first != 0
    assert second != 0

    seen = []
    it = BRepGraph_SupplementIterator(g, BRepGraph_NodeId(owner))
    while it.More():
        seen.append(it.Uid())
        assert it.Value().BaseOwner == BRepGraph_NodeId(owner)
        assert it.Value().Shape.ShapeType() == TopAbs.TopAbs_VERTEX
        it.Next()

    assert seen == [first, second]

    layer = _find_layer(g)
    assert layer is not None
    assert layer.FindByUid(first) is not None
    assert layer.FindByUid(second) is not None


def test_BRepGraph_LayerTopoSupplementTest_OnNodeReplacedMigratesAttachments():
    g = BRepGraph()
    old_owner = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    new_owner = g.Editor().Vertices().Add(gp_Pnt(5.0, 0.0, 0.0), 1.0e-7)

    editor = BRepGraph_SupplementEditor(g)
    uid = editor.AttachToVertex(old_owner, _vertex(gp_Pnt(0.0, 1.0, 0.0)))
    assert uid != 0

    layer = _find_layer(g)
    assert layer is not None
    layer.OnNodeReplaced(BRepGraph_NodeId(old_owner), BRepGraph_NodeId(new_owner))

    assert len(layer.AttachedTo(BRepGraph_NodeId(old_owner))) == 0
    attached_new = layer.AttachedTo(BRepGraph_NodeId(new_owner))
    assert len(attached_new) == 1
    assert attached_new.First() == uid

    entry = layer.FindByUid(uid)
    assert entry is not None
    assert entry.BaseOwner == BRepGraph_NodeId(new_owner)


def test_BRepGraph_LayerTopoSupplementTest_RemoveNodeDropsOwnedAttachments():
    g = BRepGraph()
    owner = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)

    editor = BRepGraph_SupplementEditor(g)
    uid = editor.AttachToVertex(owner, _vertex(gp_Pnt(0.0, 1.0, 0.0)))
    assert uid != 0

    layer = _find_layer(g)
    assert layer is not None
    assert len(layer.AttachedTo(BRepGraph_NodeId(owner))) == 1

    g.Editor().Gen().RemoveNode(owner)

    assert len(layer.AttachedTo(BRepGraph_NodeId(owner))) == 0
    assert layer.FindByUid(uid) is None


def test_BRepGraph_LayerTopoSupplementTest_LegacyEdgeInternalVertexWriterUsesSupplementLayer():
    g = BRepGraph()
    start = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    end = g.Editor().Vertices().Add(gp_Pnt(10.0, 0.0, 0.0), 1.0e-7)
    edge = g.Editor().Edges().Add(start, end, None, 0.0, 1.0, 1.0e-7)
    assert edge.IsValid()

    layer = _find_layer(g)
    if layer is not None:
        assert len(layer.AttachedTo(BRepGraph_NodeId(edge))) == 0

    nb_core_refs = 0
    it = BRepGraph_RefsVertexOfEdge(g, edge)
    while it.More():
        nb_core_refs += 1
        it.Next()
    assert nb_core_refs == 2


def test_BRepGraph_LayerTopoSupplementTest_AddAndReconstructPreservesSupplementEdgeVertices():
    g = BRepGraph()
    assert _ensure_layer(g) is not None

    res = g.Shapes().Add(_edge_with_supplement_vertices(), _options_no_product())
    assert res.IsOk()
    assert res.TopologyRoot.NodeKind == NKind.Edge

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(res.TopologyRoot)
    assert len(attached) == 3

    nb_internal = 0
    nb_external = 0
    nb_forward = 0
    for uid in attached:
        entry = layer.FindByUid(uid)
        assert entry is not None
        assert entry.Kind == AK.EdgeInternalVertex
        ori = entry.Shape.Orientation()
        if ori == TopAbs.TopAbs_INTERNAL:
            nb_internal += 1
        elif ori == TopAbs.TopAbs_EXTERNAL:
            nb_external += 1
        elif ori == TopAbs.TopAbs_FORWARD:
            nb_forward += 1
    assert nb_internal == 1
    assert nb_external == 1
    assert nb_forward == 1

    round_trip = g.Shapes().Reconstruct(res.TopologyRoot)
    assert round_trip.ShapeType() == TopAbs.TopAbs_EDGE

    counts = {}
    for child in TopoDS_Iterator(round_trip, False, False):
        assert child.ShapeType() == TopAbs.TopAbs_VERTEX
        counts[child.Orientation()] = counts.get(child.Orientation(), 0) + 1
    assert counts.get(TopAbs.TopAbs_FORWARD, 0) == 2
    assert counts.get(TopAbs.TopAbs_REVERSED, 0) == 1
    assert counts.get(TopAbs.TopAbs_INTERNAL, 0) == 1
    assert counts.get(TopAbs.TopAbs_EXTERNAL, 0) == 1


def test_BRepGraph_LayerTopoSupplementTest_AddAndReconstructPreservesSupplementFaceVertex():
    g = BRepGraph()
    assert _ensure_layer(g) is not None

    res = g.Shapes().Add(_face_with_supplement_vertex(), _options_no_product())
    assert res.IsOk()
    assert res.TopologyRoot.NodeKind == NKind.Face

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(res.TopologyRoot)
    assert len(attached) == 1

    entry = layer.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == AK.FaceDirectVertex
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_VERTEX
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    round_trip = g.Shapes().Reconstruct(res.TopologyRoot)
    assert round_trip.ShapeType() == TopAbs.TopAbs_FACE

    nb_wires = 0
    nb_internal_vertices = 0
    for child in TopoDS_Iterator(round_trip, False, False):
        if child.ShapeType() == TopAbs.TopAbs_WIRE:
            nb_wires += 1
            continue
        if child.ShapeType() == TopAbs.TopAbs_VERTEX and child.Orientation() == TopAbs.TopAbs_INTERNAL:
            nb_internal_vertices += 1
    assert nb_wires == 1
    assert nb_internal_vertices == 1


def test_BRepGraph_LayerTopoSupplementTest_ShellReconstructionReplaysFaceSupplementVertex():
    bb = BRep_Builder()
    shell = TopoDS_Shell()
    bb.MakeShell(shell)
    bb.Add(shell, _face_with_supplement_vertex())

    g = BRepGraph()
    g.Clear()
    _ensure_layer(g)
    res = g.Shapes().Add(shell, _options_no_product())
    assert res.TopologyRoot.IsValid()

    round_trip = g.Shapes().Reconstruct(res.TopologyRoot)
    assert not round_trip.IsNull()
    assert round_trip.ShapeType() == TopAbs.TopAbs_SHELL

    nb_faces = 0
    nb_internal_vertices = 0
    for face in TopoDS_Iterator(round_trip, False, False):
        if face.ShapeType() != TopAbs.TopAbs_FACE:
            continue
        nb_faces += 1
        nb_internal_vertices += _count_direct_children(face, TopAbs.TopAbs_VERTEX, TopAbs.TopAbs_INTERNAL)
    assert nb_faces == 1
    assert nb_internal_vertices == 1


def test_BRepGraph_LayerTopoSupplementTest_SolidAddChild_ReconstructPreservesSupplementEdge():
    g = BRepGraph()
    assert _ensure_layer(g) is not None

    res = g.Shapes().Add(_plain_solid(), _options_no_product())
    assert res.IsOk()
    assert res.TopologyRoot.NodeKind == NKind.Solid

    assert g.Topo().Edges().Nb() > 0
    assert BRepGraph_EdgeId.Start_s().IsValid()

    layer = _find_layer(g)
    assert layer is not None
    assert len(layer.AttachedTo(res.TopologyRoot)) == 0


def test_BRepGraph_LayerTopoSupplementTest_ShellOwner_IsAcceptedBySupplementLayer():
    g = BRepGraph()
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()

    layer = _ensure_layer(g)
    uid = layer.AddAttachment(BRepGraph_NodeId(shell), AK.ShellAuxShape, _vertex(gp_Pnt(1.0, 2.0, 3.0)))
    assert uid != 0
    assert len(layer.AttachedTo(BRepGraph_NodeId(shell))) == 1


def test_BRepGraph_LayerTopoSupplementTest_CompSolidOwner_IsAcceptedBySupplementLayer():
    g = BRepGraph()
    cs = _add_empty_compsolid(g)
    assert cs.IsValid()

    layer = _ensure_layer(g)
    assert layer.AddAttachment(BRepGraph_NodeId(cs), AK.CompSolidAuxShape, _plain_solid()) != 0
    assert layer.AddAttachment(BRepGraph_NodeId(cs), AK.GenericSupplementShape, _vertex(gp_Pnt(1.0, 2.0, 3.0))) != 0
    assert len(layer.AttachedTo(BRepGraph_NodeId(cs))) == 2


def test_BRepGraph_LayerTopoSupplementTest_ShellAddFace_Internal_RoutedToSupplement():
    g = BRepGraph()
    shell_res = g.Shapes().Add(_plain_shell(), _options_no_product())
    assert shell_res.IsOk()
    assert shell_res.TopologyRoot.NodeKind == NKind.Shell

    shell_id = BRepGraph_ShellId(shell_res.TopologyRoot)
    nb_faces_before = g.Topo().Faces().Nb()
    internal_face = _plain_face()
    internal_face.Orientation(TopAbs.TopAbs_INTERNAL)

    add_res = g.Shapes().Add(internal_face, BRepGraph_NodeId(shell_id))
    assert add_res.IsOk()
    assert not add_res.TopologyRoot.IsValid()
    assert not add_res.InsertedRef.IsValid()
    assert g.Topo().Faces().Nb() == nb_faces_before

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(BRepGraph_NodeId(shell_id))
    assert len(attached) >= 1

    entry = layer.FindByUid(attached.Last())
    assert entry is not None
    assert entry.Kind == AK.ShellAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_FACE
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    round_trip = g.Shapes().Reconstruct(BRepGraph_NodeId(shell_id))
    assert _count_direct_children(round_trip, TopAbs.TopAbs_FACE, TopAbs.TopAbs_INTERNAL) == 1


def test_BRepGraph_LayerTopoSupplementTest_SolidAddShell_Internal_RoutedToSupplement():
    g = BRepGraph()
    solid_res = g.Shapes().Add(_plain_solid(), _options_no_product())
    assert solid_res.IsOk()
    assert solid_res.TopologyRoot.NodeKind == NKind.Solid

    solid_id = BRepGraph_SolidId(solid_res.TopologyRoot)
    nb_shells_before = g.Topo().Shells().Nb()
    internal_shell = _plain_shell()
    internal_shell.Orientation(TopAbs.TopAbs_INTERNAL)

    add_res = g.Shapes().Add(internal_shell, BRepGraph_NodeId(solid_id))
    assert add_res.IsOk()
    assert not add_res.TopologyRoot.IsValid()
    assert not add_res.InsertedRef.IsValid()
    assert g.Topo().Shells().Nb() == nb_shells_before

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(BRepGraph_NodeId(solid_id))
    assert len(attached) >= 1

    entry = layer.FindByUid(attached.Last())
    assert entry is not None
    assert entry.Kind == AK.SolidAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_SHELL
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    round_trip = g.Shapes().Reconstruct(BRepGraph_NodeId(solid_id))
    assert _count_direct_children(round_trip, TopAbs.TopAbs_SHELL, TopAbs.TopAbs_INTERNAL) == 1


def test_BRepGraph_LayerTopoSupplementTest_CompSolidAddSolid_Internal_RoutedToSupplement():
    g = BRepGraph()
    cs_res = g.Shapes().Add(_plain_compsolid(), _options_no_product())
    assert cs_res.IsOk()
    assert cs_res.TopologyRoot.NodeKind == NKind.CompSolid

    cs_id = BRepGraph_CompSolidId(cs_res.TopologyRoot)
    nb_solids_before = g.Topo().Solids().Nb()
    internal_solid = _plain_solid()
    internal_solid.Orientation(TopAbs.TopAbs_INTERNAL)

    add_res = g.Shapes().Add(internal_solid, BRepGraph_NodeId(cs_id))
    assert add_res.IsOk()
    assert not add_res.TopologyRoot.IsValid()
    assert not add_res.InsertedRef.IsValid()
    assert g.Topo().Solids().Nb() == nb_solids_before

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(BRepGraph_NodeId(cs_id))
    assert len(attached) == 1

    entry = layer.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == AK.CompSolidAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_SOLID
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    round_trip = g.Shapes().Reconstruct(BRepGraph_NodeId(cs_id))
    assert _count_direct_children(round_trip, TopAbs.TopAbs_SOLID, TopAbs.TopAbs_INTERNAL) == 1


def test_BRepGraph_LayerTopoSupplementTest_CompoundAddChild_MixedOrientations_CoreRefAndSupplement():
    g = BRepGraph()
    bb = BRep_Builder()
    compound = TopoDS_Compound()
    bb.MakeCompound(compound)
    comp_res = g.Shapes().Add(compound, _options_no_product())
    assert comp_res.IsOk()
    comp_id = BRepGraph_CompoundId(comp_res.TopologyRoot)

    fwd_face = _plain_face()
    fwd_face.Orientation(TopAbs.TopAbs_FORWARD)
    fwd_res = g.Shapes().Add(fwd_face, BRepGraph_NodeId(comp_id))
    assert fwd_res.IsOk()
    assert fwd_res.InsertedRef.IsValid()

    int_face = _plain_face()
    int_face.Orientation(TopAbs.TopAbs_INTERNAL)
    int_res = g.Shapes().Add(int_face, BRepGraph_NodeId(comp_id))
    assert int_res.IsOk()
    assert not int_res.InsertedRef.IsValid()

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(BRepGraph_NodeId(comp_id))
    assert len(attached) == 1
    entry = layer.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == AK.CompoundAuxShape


def test_BRepGraph_LayerTopoSupplementTest_CopyToAllocatesFreshUidOnCollision():
    source = BRepGraph()
    target = BRepGraph()

    src_vertex = source.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    tgt_vertex = target.Editor().Vertices().Add(gp_Pnt(10.0, 0.0, 0.0), 1.0e-7)
    tgt_vertex_count = target.Topo().Vertices().Nb()

    src_layer = _ensure_layer(source)
    tgt_layer = _ensure_layer(target)
    assert src_layer.AddAttachmentWithUid(
        BRepGraph_NodeId(src_vertex), 1, AK.VertexSupplementShape, _vertex(gp_Pnt(1.0, 0.0, 0.0))
    )
    assert tgt_layer.AddAttachmentWithUid(
        BRepGraph_NodeId(tgt_vertex), 1, AK.VertexSupplementShape, _vertex(gp_Pnt(11.0, 0.0, 0.0))
    )

    assert BRepGraph_Copy.Perform_s(source, target, BRepGraph_Copy.GeomPolicy.Copy)

    tgt_layer = _find_layer(target)
    assert tgt_layer is not None
    copied = tgt_layer.AttachedTo(BRepGraph_NodeId(BRepGraph_VertexId(tgt_vertex_count)))
    assert len(copied) == 1
    assert copied.First() != 1
    assert tgt_layer.FindByUid(copied.First()) is not None


def test_BRepGraph_LayerTopoSupplementTest_SelfCopyDoesNotMutateEntriesDuringIteration():
    g = BRepGraph()
    src_vertex = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)

    layer = _ensure_layer(g)
    assert layer.AddAttachmentWithUid(
        BRepGraph_NodeId(src_vertex), 1, AK.VertexSupplementShape, _vertex(gp_Pnt(1.0, 0.0, 0.0))
    )

    copied_node = BRepGraph_Copy.CopyNode_s(g, g, BRepGraph_NodeId(src_vertex))
    assert copied_node.IsValid()
    assert copied_node.NodeKind == NKind.Vertex
    assert copied_node.Index != src_vertex.Index

    layer = _find_layer(g)
    assert layer is not None

    src_att = layer.AttachedTo(BRepGraph_NodeId(src_vertex))
    assert len(src_att) == 1
    assert src_att.First() == 1

    copied_att = layer.AttachedTo(copied_node)
    assert len(copied_att) == 1
    assert copied_att.First() != 1
    assert layer.FindByUid(copied_att.First()) is not None


def test_BRepGraph_LayerTopoSupplementTest_IncompatibleAttachmentKindIsRejected():
    g = BRepGraph()
    v0 = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    v1 = g.Editor().Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    edge = g.Editor().Edges().Add(v0, v1, None, 0.0, 1.0, 1.0e-7)
    face_res = g.Shapes().Add(_plain_face())
    face = BRepGraph_FaceId(face_res.TopologyRoot)
    assert edge.IsValid()
    assert face_res.IsOk()
    assert face.IsValid()

    layer = _ensure_layer(g)

    assert layer.AddAttachment(BRepGraph_NodeId(edge), AK.FaceDirectVertex, _vertex(gp_Pnt(1.0, 2.0, 3.0))) == 0
    assert layer.AddAttachment(BRepGraph_NodeId(face), AK.SolidAuxShape, _vertex(gp_Pnt(4.0, 5.0, 6.0))) == 0
    cs = _add_empty_compsolid(g)
    assert cs.IsValid()
    assert layer.AddAttachment(BRepGraph_NodeId(cs), AK.ShellAuxShape, _plain_shell()) == 0
    assert layer.AddAttachment(BRepGraph_NodeId(face), AK.CompSolidAuxShape, _plain_solid()) == 0

    assert len(layer.AttachedTo(BRepGraph_NodeId(edge))) == 0
    assert len(layer.AttachedTo(BRepGraph_NodeId(face))) == 0
    assert len(layer.AttachedTo(BRepGraph_NodeId(cs))) == 0


def test_BRepGraph_LayerTopoSupplementTest_ShapesView_AddToShellRoutesInvalidChildWithoutOrphanAppend():
    g = BRepGraph()
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()

    nb_edges_before = g.Topo().Edges().Nb()
    nb_vertices_before = g.Topo().Vertices().Nb()

    edge = TopoDS_Edge()
    BRep_Builder().MakeEdge(edge)

    res = g.Shapes().Add(edge, BRepGraph_NodeId(shell))
    assert res.IsOk()
    assert not res.TopologyRoot.IsValid()
    assert not res.InsertedRef.IsValid()
    assert g.Topo().Edges().Nb() == nb_edges_before
    assert g.Topo().Vertices().Nb() == nb_vertices_before

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(BRepGraph_NodeId(shell))
    assert len(attached) == 1
    entry = layer.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == AK.ShellAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_EDGE


def test_BRepGraph_LayerTopoSupplementTest_ShapesView_AddToSolidRoutesInvalidChildWithoutOrphanAppend():
    g = BRepGraph()
    solid = g.Editor().Solids().Add()
    assert solid.IsValid()

    nb_faces_before = g.Topo().Faces().Nb()
    nb_vertices_before = g.Topo().Vertices().Nb()

    res = g.Shapes().Add(_plain_face(), BRepGraph_NodeId(solid))
    assert res.IsOk()
    assert not res.TopologyRoot.IsValid()
    assert not res.InsertedRef.IsValid()
    assert g.Topo().Faces().Nb() == nb_faces_before
    assert g.Topo().Vertices().Nb() == nb_vertices_before

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(BRepGraph_NodeId(solid))
    assert len(attached) == 1
    entry = layer.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == AK.SolidAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_FACE


def test_BRepGraph_LayerTopoSupplementTest_ShapesView_AddToFaceRejectsUnsupportedChildWithoutOrphanAppend():
    g = BRepGraph()
    face_res = g.Shapes().Add(_plain_face())
    assert face_res.IsOk()
    assert face_res.TopologyRoot.IsValid()
    assert face_res.TopologyRoot.NodeKind == NKind.Face

    nb_edges_before = g.Topo().Edges().Nb()
    nb_vertices_before = g.Topo().Vertices().Nb()

    edge = TopoDS_Edge()
    BRep_Builder().MakeEdge(edge)

    res = g.Shapes().Add(edge, face_res.TopologyRoot)
    assert not res.IsOk()
    assert not res.TopologyRoot.IsValid()
    assert not res.InsertedRef.IsValid()
    assert g.Topo().Edges().Nb() == nb_edges_before
    assert g.Topo().Vertices().Nb() == nb_vertices_before


def test_BRepGraph_LayerTopoSupplementTest_ShapesView_AddNonSolidToCompSolidRoutesInvalidChildWithoutOrphanAppend():
    g = BRepGraph()
    bb = BRep_Builder()
    cs_shape = TopoDS_CompSolid()
    bb.MakeCompSolid(cs_shape)
    bb.Add(cs_shape, _plain_solid())

    cs_res = g.Shapes().Add(cs_shape)
    assert cs_res.IsOk()
    assert cs_res.TopologyRoot.IsValid()
    assert cs_res.TopologyRoot.NodeKind == NKind.CompSolid

    nb_edges_before = g.Topo().Edges().Nb()
    nb_vertices_before = g.Topo().Vertices().Nb()

    edge = TopoDS_Edge()
    bb.MakeEdge(edge)

    res = g.Shapes().Add(edge, cs_res.TopologyRoot)
    assert res.IsOk()
    assert not res.TopologyRoot.IsValid()
    assert not res.InsertedRef.IsValid()
    assert g.Topo().Edges().Nb() == nb_edges_before
    assert g.Topo().Vertices().Nb() == nb_vertices_before

    layer = _find_layer(g)
    assert layer is not None
    attached = layer.AttachedTo(cs_res.TopologyRoot)
    assert len(attached) == 1
    entry = layer.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == AK.CompSolidAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_EDGE
