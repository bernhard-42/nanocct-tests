# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Copy_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy, BRepBuilderAPI_MakeEdge
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgesOfWire,
    BRepGraph_Copy,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_ItemId,
    BRepGraph_ItemUID,
    BRepGraph_LayerHistory,
    BRepGraph_LayerTopoSupplement,
    BRepGraph_NodeId,
    BRepGraph_OccurrenceId,
    BRepGraph_OccurrenceRefId,
    BRepGraph_ProductId,
    BRepGraph_RefId,
    BRepGraph_RefsWireOfFace,
    BRepGraph_SolidId,
    BRepGraph_Tool,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.gp import gp_Pnt, gp_Pnt2d
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_Array1
from nanocct.Poly import (
    Poly_Polygon2D,
    Poly_Polygon3D,
    Poly_PolygonOnTriangulation,
    Poly_Triangle,
    Poly_Triangulation,
)
from nanocct.Precision import Precision
from nanocct.TCollection import TCollection_AsciiString
from nanocct.TopAbs import TopAbs_FACE, TopAbs_INTERNAL, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Iterator, TopoDS_Vertex

Kind = BRepGraph_NodeId.Kind
GeomPolicy = BRepGraph_Copy.GeomPolicy
MeshPolicy = BRepGraph_Copy.MeshPolicy
CachePolicy = BRepGraph_Copy.CachePolicy


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _box_graph(dx=10.0, dy=20.0, dz=30.0):
    return _graph(BRepPrimAPI_MakeBox(dx, dy, dz).Shape())


def _copy(g, geom=GeomPolicy.Copy, *args):
    target = BRepGraph()
    BRepGraph_Copy.Perform_s(g, target, geom, *args)
    assert not target.IsEmpty()
    return target


def _history(g):
    reg = g.LayerRegistry()
    layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    if layer is None:
        reg.RegisterLayer(BRepGraph_LayerHistory())
        layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    return layer


def _area(shape):
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


def _edge_same_parameter(g, edge_id):
    return all(BRepGraph_Tool.CoEdge.SameParameter_s(g, c) for c in g.Topo().Edges().Relations(edge_id).CoEdgeIds)


def _edge_same_range(g, edge_id):
    return all(BRepGraph_Tool.CoEdge.SameRange_s(g, c) for c in g.Topo().Edges().Relations(edge_id).CoEdgeIds)


def _count_active(g, id_type, count):
    return sum(1 for i in range(count) if not id_type(i).IsRemoved(g))


def _make_edge_with_internal_vertex():
    bb = BRep_Builder()
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0)).Edge()
    vtx = TopoDS_Vertex()
    bb.MakeVertex(vtx, gp_Pnt(5, 0, 0), Precision.Confusion_s())
    bb.Add(edge, vtx.Oriented(TopAbs_INTERNAL))
    return edge


def _first_coedge_of_face(g, face_id):
    wire_it = BRepGraph_RefsWireOfFace(g, face_id)
    while wire_it.More():
        wire_id = g.Refs().Wires().Entry(wire_it.CurrentId()).ChildWireId
        ce_it = BRepGraph_CoEdgesOfWire(g, wire_id)
        while ce_it.More():
            ce_id = ce_it.CurrentId()
            if g.Topo().CoEdges().Definition(ce_id).FaceId == face_id:
                return ce_id
            ce_it.Next()
        wire_it.Next()
    return BRepGraph_CoEdgeId()


def _mesh_handles():
    tri = Poly_Triangulation(3, 1, False)
    p3d = Poly_Polygon3D(2, False)
    p2d = Poly_Polygon2D(2)
    pot = Poly_PolygonOnTriangulation(2, False)
    tri.SetNode(1, gp_Pnt(1.0, 2.0, 3.0))
    tri.SetNode(2, gp_Pnt(4.0, 5.0, 6.0))
    tri.SetNode(3, gp_Pnt(7.0, 8.0, 9.0))
    tri.SetTriangle(1, Poly_Triangle(1, 2, 3))
    p3d.ChangeNodes().SetValue(1, gp_Pnt(10.0, 11.0, 12.0))
    p3d.ChangeNodes().SetValue(2, gp_Pnt(13.0, 14.0, 15.0))
    p2d.ChangeNodes().SetValue(1, gp_Pnt2d(16.0, 17.0))
    p2d.ChangeNodes().SetValue(2, gp_Pnt2d(18.0, 19.0))
    pot.SetNode(1, 2)
    pot.SetNode(2, 3)
    return tri, p3d, p2d, pot


def _expect_mesh_handles_copied(copied, source):
    c_tri, c_p3d, c_p2d, c_pot = copied
    s_tri, s_p3d, s_p2d, s_pot = source
    for c in copied:
        assert c is not None
    for c, s in zip(copied, source):
        assert c is not s

    assert c_tri.NbNodes() == s_tri.NbNodes()
    assert c_tri.NbTriangles() == s_tri.NbTriangles()
    assert c_tri.Node(2).IsEqual(s_tri.Node(2), 0.0)

    assert c_p3d.NbNodes() == s_p3d.NbNodes()
    assert c_p3d.Nodes().Value(2).IsEqual(s_p3d.Nodes().Value(2), 0.0)

    assert c_p2d.NbNodes() == s_p2d.NbNodes()
    assert c_p2d.Nodes().Value(2).IsEqual(s_p2d.Nodes().Value(2), 0.0)

    assert c_pot.NbNodes() == s_pot.NbNodes()
    assert c_pot.Node(2) == s_pot.Node(2)


def _persistent_handles(g, face_id, edge_id, coedge_id):
    p = g.Mesh().Persistent()
    return (
        p.Faces().Triangulation(face_id),
        p.Edges().Polygon3D(edge_id),
        p.CoEdges().PolygonOnSurface(coedge_id),
        p.CoEdges().PolygonOnTriangulation(coedge_id),
    )


def _face_coedge_edge(g):
    face_id = BRepGraph_FaceId.Start_s()
    coedge_id = _first_coedge_of_face(g, face_id)
    assert coedge_id.IsValid(g.Topo().CoEdges().Nb())
    edge_id = g.Topo().CoEdges().Definition(coedge_id).ChildEdgeId
    assert edge_id.IsValid(g.Topo().Edges().Nb())
    return face_id, coedge_id, edge_id


def _set_persistent(g, face_id, edge_id, coedge_id, handles):
    tri, p3d, p2d, pot = handles
    g.Editor().Faces().SetPersistentTriangulation(face_id, tri)
    g.Editor().Edges().SetPersistentPolygon3D(edge_id, p3d)
    g.Editor().CoEdges().SetPersistentPolygon2D(coedge_id, p2d)
    g.Editor().CoEdges().SetPersistentPolygonOnTri(coedge_id, pot)


def test_BRepGraph_CopyTest_CopyBox_FaceCount():
    g = _box_graph()
    c = _copy(g)
    assert c.Topo().Faces().Nb() == 6
    assert c.Topo().Faces().Nb() == g.Topo().Faces().Nb()

    shape = c.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    assert not shape.IsNull()
    assert sum(1 for _ in TopExp_Explorer(shape, TopAbs_FACE)) == 6


def test_BRepGraph_CopyTest_CopyGraph_RemovedOccurrenceActiveCountsMatchFlags():
    g = _box_graph(10.0, 10.0, 10.0)
    part = BRepGraph_ProductId.Start_s()
    assembly = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(assembly)
    occ_id = g.Editor().Products().Append(assembly, part, TopLoc_Location())
    assert occ_id.IsValid()

    occ_refs = g.Refs().Occurrences().IdsOf(assembly)
    assert occ_refs.Size() == 1
    occ_ref_id = occ_refs.Value(0)

    g.Editor().Gen().RemoveSubgraph(BRepGraph_NodeId(occ_id))
    assert occ_id.IsRemoved(g)
    assert occ_ref_id.IsRemoved(g)

    c = _copy(g)
    assert occ_id.IsRemoved(c)
    assert occ_ref_id.IsRemoved(c)
    assert c.Topo().Occurrences().NbActive() == _count_active(c, BRepGraph_OccurrenceId, c.Topo().Occurrences().Nb())
    assert c.Refs().Occurrences().NbActive() == _count_active(c, BRepGraph_OccurrenceRefId, c.Refs().Occurrences().Nb())


def test_BRepGraph_CopyTest_CopyBox_AreaPreserved():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    orig_area = _area(box)
    c = _copy(_graph(box))
    shape = c.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    assert not shape.IsNull()
    copy_area = sum(abs(_area(f)) for f in TopExp_Explorer(shape, TopAbs_FACE))
    assert abs(copy_area - orig_area) <= orig_area * 0.01


def test_BRepGraph_CopyTest_CopyBox_GeometryIsIndependent():
    g = _box_graph()
    c = _copy(g)
    assert g.Topo().Faces().Nb() > 0
    assert c.Topo().Faces().Nb() > 0
    s_copy = BRepGraph_Tool.Face.Surface_s(c, BRepGraph_FaceId.Start_s())
    s_orig = BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId.Start_s())
    assert s_copy is not s_orig


def test_BRepGraph_CopyTest_CopyGraph_DropsRuntimeFaceCacheMesh():
    g = _box_graph()
    face_id = BRepGraph_FaceId.Start_s()
    assert face_id.IsValid(g.Topo().Faces().Nb())
    g.Mesh().Editor().Faces().SetCachedTriangulation(face_id, Poly_Triangulation(3, 1, False))
    assert g.Mesh().Cache().Faces().Has(face_id)

    c = _copy(g)
    assert not c.Mesh().Cache().Faces().Has(face_id)


def test_BRepGraph_CopyTest_CopyGraph_CanCopyFreshRuntimeFaceCacheMesh():
    g = _box_graph()
    face_id = BRepGraph_FaceId.Start_s()
    assert face_id.IsValid(g.Topo().Faces().Nb())
    tri = Poly_Triangulation(3, 1, False)
    g.Mesh().Editor().Faces().SetCachedTriangulation(face_id, tri)
    assert g.Mesh().Cache().Faces().Has(face_id)

    c = BRepGraph()
    assert BRepGraph_Copy.Perform_s(g, c, GeomPolicy.Copy, MeshPolicy.Copy, CachePolicy.CopyFresh)
    assert not c.IsEmpty()
    assert c.Mesh().Cache().Faces().Has(face_id)
    assert c.Mesh().Cache().Faces().Triangulation(face_id) is tri


def test_BRepGraph_CopyTest_CopyGraph_DropsRuntimeEdgeAndCoEdgeCacheMesh():
    g = _box_graph()
    face_id, coedge_id, edge_id = _face_coedge_edge(g)

    g.Editor().Faces().SetPersistentTriangulation(face_id, Poly_Triangulation(3, 1, False))
    g.Mesh().Editor().Edges().SetCachedPolygon3D(edge_id, Poly_Polygon3D(2, False))
    g.Mesh().Editor().CoEdges().SetCachedPolygon2D(coedge_id, Poly_Polygon2D(2))
    g.Mesh().Editor().CoEdges().AppendCachedPolygonOnTri(coedge_id, Poly_PolygonOnTriangulation(2, False))
    assert g.Mesh().Cache().Edges().Has(edge_id)
    assert g.Mesh().Cache().CoEdges().Has(coedge_id)

    c = _copy(g)
    assert not c.Mesh().Cache().Edges().Has(edge_id)
    assert not c.Mesh().Cache().CoEdges().Has(coedge_id)


def test_BRepGraph_CopyTest_CopyNode_CopiesPersistentMeshAndDropsCache():
    g = _box_graph()
    face_id, coedge_id, edge_id = _face_coedge_edge(g)
    handles = _mesh_handles()
    tri, p3d, p2d, pot = handles
    _set_persistent(g, face_id, edge_id, coedge_id, handles)
    g.Mesh().Editor().Faces().SetCachedTriangulation(face_id, tri)
    g.Mesh().Editor().Edges().SetCachedPolygon3D(edge_id, p3d)
    g.Mesh().Editor().CoEdges().SetCachedPolygon2D(coedge_id, p2d)
    g.Mesh().Editor().CoEdges().AppendCachedPolygonOnTri(coedge_id, pot)

    c = BRepGraph()
    BRepGraph_Copy.CopyNode_s(g, c, BRepGraph_NodeId(face_id))
    assert not c.IsEmpty()

    c_face, c_coedge, c_edge = _face_coedge_edge(c)
    assert not c.Mesh().Cache().Faces().Has(c_face)
    assert not c.Mesh().Cache().Edges().Has(c_edge)
    assert not c.Mesh().Cache().CoEdges().Has(c_coedge)

    _expect_mesh_handles_copied(_persistent_handles(c, c_face, c_edge, c_coedge), handles)


def test_BRepGraph_CopyTest_CopyGraph_CopiesPersistentMeshHandles():
    g = _box_graph()
    face_id, coedge_id, edge_id = _face_coedge_edge(g)
    handles = _mesh_handles()
    _set_persistent(g, face_id, edge_id, coedge_id, handles)

    c = BRepGraph()
    assert BRepGraph_Copy.Perform_s(g, c, GeomPolicy.Copy, MeshPolicy.Copy)
    _expect_mesh_handles_copied(_persistent_handles(c, face_id, edge_id, coedge_id), handles)


def test_BRepGraph_CopyTest_CopyGraph_NonEmptyTargetUsesSetterPathForPersistentMesh():
    source = _box_graph()
    target = _box_graph(1.0, 2.0, 3.0)
    face_id, coedge_id, edge_id = _face_coedge_edge(source)
    handles = _mesh_handles()
    _set_persistent(source, face_id, edge_id, coedge_id, handles)

    nf = target.Topo().Faces().Nb()
    ne = target.Topo().Edges().Nb()
    nce = target.Topo().CoEdges().Nb()

    assert BRepGraph_Copy.Perform_s(source, target, GeomPolicy.Copy, MeshPolicy.Copy)

    c_face = BRepGraph_FaceId(nf + face_id.Index)
    c_coedge = BRepGraph_CoEdgeId(nce + coedge_id.Index)
    c_edge = BRepGraph_EdgeId(ne + edge_id.Index)
    assert c_face.IsValid(target.Topo().Faces().Nb())
    assert c_edge.IsValid(target.Topo().Edges().Nb())
    assert c_coedge.IsValid(target.Topo().CoEdges().Nb())

    _expect_mesh_handles_copied(_persistent_handles(target, c_face, c_edge, c_coedge), handles)


def test_BRepGraph_CopyTest_CopyNode_DoesNotReviveRemovedPersistentMeshReps():
    g = _box_graph()
    face_id, coedge_id, edge_id = _face_coedge_edge(g)
    g.Editor().Faces().SetPersistentTriangulation(face_id, Poly_Triangulation(3, 1, False))
    g.Editor().Edges().SetPersistentPolygon3D(edge_id, Poly_Polygon3D(2, False))
    assert g.Mesh().Persistent().Faces().Has(face_id)
    assert g.Mesh().Persistent().Edges().Has(edge_id)

    g.Editor().Faces().ClearPersistentTriangulation(face_id)
    g.Editor().Edges().ClearPersistentPolygon3D(edge_id)
    assert not g.Mesh().Persistent().Faces().Has(face_id)
    assert not g.Mesh().Persistent().Edges().Has(edge_id)

    c = BRepGraph()
    BRepGraph_Copy.CopyNode_s(g, c, BRepGraph_NodeId(face_id))
    assert not c.IsEmpty()

    c_face, c_coedge, c_edge = _face_coedge_edge(c)
    assert not c.Mesh().Persistent().Faces().Has(c_face)
    assert not c.Mesh().Persistent().Edges().Has(c_edge)


def test_BRepGraph_CopyTest_CopyBox_SharedGeometry():
    g = _box_graph()
    c = _copy(g, GeomPolicy.Share)
    assert c.Topo().Faces().Nb() == 6
    assert g.Topo().Faces().Nb() > 0
    s_copy = BRepGraph_Tool.Face.Surface_s(c, BRepGraph_FaceId.Start_s())
    s_orig = BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId.Start_s())
    assert s_copy is s_orig


def test_BRepGraph_CopyTest_CopyGraph_PreservesSupplementAttachmentsAndUids():
    g = BRepGraph()
    g.Clear()
    reg = g.LayerRegistry()
    if reg.FindLayer(BRepGraph_LayerTopoSupplement.GetID_s()) is None:
        reg.RegisterLayer(BRepGraph_LayerTopoSupplement())
    assert reg.FindLayer(BRepGraph_LayerTopoSupplement.GetID_s()) is not None
    g.Shapes().Add(_make_edge_with_internal_vertex())
    assert not g.IsEmpty()

    src_layer = g.LayerRegistry().FindLayer(BRepGraph_LayerTopoSupplement.GetID_s())
    assert src_layer is not None
    assert g.Topo().Edges().Nb() > 0

    edge_id = BRepGraph_EdgeId.Start_s()
    src_attached = src_layer.AttachedTo(BRepGraph_NodeId(edge_id))
    assert src_attached.Size() == 1
    uid = src_attached.First()

    c = _copy(g)
    dst_layer = c.LayerRegistry().FindLayer(BRepGraph_LayerTopoSupplement.GetID_s())
    assert dst_layer is not None

    dst_attached = dst_layer.AttachedTo(BRepGraph_NodeId(edge_id))
    assert dst_attached.Size() == 1
    assert dst_attached.First() == uid

    entry = dst_layer.FindByUid(uid)
    assert entry is not None
    assert entry.BaseOwner == BRepGraph_NodeId(edge_id)
    assert entry.Kind == BRepGraph_LayerTopoSupplement.AttachmentKind.EdgeInternalVertex
    assert entry.Shape.ShapeType() == TopAbs_VERTEX
    assert entry.Shape.Orientation() == TopAbs_INTERNAL

    recon = c.Shapes().Reconstruct(BRepGraph_NodeId(edge_id))
    assert not recon.IsNull()
    found = 0
    it = TopoDS_Iterator(recon, False)
    while it.More():
        if it.Value().ShapeType() == TopAbs_VERTEX and it.Value().Orientation() == TopAbs_INTERNAL:
            found += 1
        it.Next()
    assert found == 1


def test_BRepGraph_CopyTest_CopyGraph_CopiesHistoryThroughLayerRemap():
    g = _box_graph()
    assert g.Topo().Faces().Nb() >= 2
    orig_face = BRepGraph_NodeId(BRepGraph_FaceId.Start_s())
    repl_face = BRepGraph_NodeId(BRepGraph_FaceId(1))
    orig_uid = g.UIDs().Of(orig_face)
    repl_uid = g.UIDs().Of(repl_face)
    assert orig_uid.IsValid()
    assert repl_uid.IsValid()

    repl = NCollection_Array1[BRepGraph_NodeId](0, 0)
    repl[0] = repl_face
    _history(g).Record(TCollection_AsciiString("CopyHistory"), orig_face, repl)

    c = _copy(g)
    c_history = c.LayerRegistry().FindLayer(BRepGraph_LayerHistory.GetID_s())
    assert c_history is not None

    c_orig = c.UIDs().NodeIdFrom(orig_uid)
    c_repl = c.UIDs().NodeIdFrom(repl_uid)
    assert c_orig.IsValid()
    assert c_repl.IsValid()

    modified = c_history.FindModified(c_orig)
    assert modified is not None
    assert modified.Size() == 1
    assert modified.Value(0) == c_repl

    c_orig_item_uid = c.UIDs().Of(BRepGraph_ItemId(c_orig))
    item_modified = c_history.FindModified(c_orig_item_uid)
    assert item_modified is not None
    assert item_modified.Size() == 1
    assert item_modified.Value(0) == c.UIDs().Of(BRepGraph_ItemId(c_repl))


def test_BRepGraph_CopyTest_CopyGraph_PreservesRefUIDs():
    g = _box_graph()
    face_id = BRepGraph_FaceId.Start_s()
    assert face_id.IsValid(g.Topo().Faces().Nb())
    rel = g.Topo().Faces().Relations(face_id)
    assert not rel.WireRefIds.IsEmpty()
    wire_ref_id = rel.WireRefIds.First()
    wire_ref_uid = g.UIDs().Of(BRepGraph_RefId(wire_ref_id))
    assert wire_ref_uid.IsValid()

    c = _copy(g)
    assert wire_ref_id.IsValid(c.Refs().Wires().Nb())
    assert c.UIDs().Of(BRepGraph_RefId(wire_ref_id)) == wire_ref_uid

    resolved = c.UIDs().RefIdFrom(wire_ref_uid)
    assert resolved.IsValid()
    assert resolved == BRepGraph_RefId(wire_ref_id)

    stamp = c.UIDs().StampOf(BRepGraph_RefId(wire_ref_id))
    assert stamp.IsValid()
    assert stamp.ItemUID() == BRepGraph_ItemUID.Reference_s(wire_ref_uid.Kind, wire_ref_uid.Counter)


def test_BRepGraph_CopyTest_CopyGraph_PreservesDeletedHistory():
    g = _box_graph()
    history = _history(g)
    face = BRepGraph_FaceId.Start_s()
    face_node = BRepGraph_NodeId(face)
    face_uid = g.UIDs().Of(BRepGraph_ItemId(face))
    assert face_uid.IsValid()

    g.Editor().Gen().RemoveNode(face_node)
    assert face.IsRemoved(g)
    assert history.IsDeleted(face_node)
    assert history.IsDeleted(face_uid)
    assert history.NbRecords() == 1

    c = _copy(g)
    c_history = c.LayerRegistry().FindLayer(BRepGraph_LayerHistory.GetID_s())
    assert c_history is not None

    assert c_history.IsDeleted(face_node)
    assert c_history.IsDeleted(face_uid)
    assert c_history.HasKnownInput(face_uid)
    assert c_history.DeletedItemUids().Contains(face_uid)
    assert c_history.NbRecords() == history.NbRecords()


def test_BRepGraph_CopyTest_CopyCylinder_FaceCount():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape())
    c = _copy(g)
    assert c.Topo().Faces().Nb() == g.Topo().Faces().Nb()


def test_BRepGraph_CopyTest_CopySingleFace():
    g = _box_graph()
    assert g.Topo().Faces().Nb() > 0
    face_node = BRepGraph_NodeId(Kind.Face, BRepGraph_FaceId.Start_s().Index)
    c = BRepGraph()
    BRepGraph_Copy.CopyNode_s(g, c, face_node)
    assert not c.IsEmpty()
    assert c.Topo().Faces().Nb() == 1
    assert c.Topo().Vertices().Nb() > 0
    assert c.Topo().Edges().Nb() > 0
    assert c.Topo().Wires().Nb() > 0
    assert c.Topo().Shells().Nb() == 0
    assert c.Topo().Solids().Nb() == 0

    face = c.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    assert not face.IsNull()
    assert face.ShapeType() == TopAbs_FACE
    assert abs(_area(face)) > 1.0


def test_BRepGraph_CopyTest_CopyFacesOnly_Compound():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    for f in TopExp_Explorer(box, TopAbs_FACE):
        bb.Add(comp, BRepBuilderAPI_Copy(f, True).Shape())

    g = _graph(comp)
    assert g.Topo().Faces().Nb() == 6
    assert g.Topo().Solids().Nb() == 0
    assert g.Topo().Shells().Nb() == 0

    c = _copy(g)
    assert c.Topo().Faces().Nb() == 6
    assert c.Topo().Solids().Nb() == 0
    assert c.Topo().Shells().Nb() == 0


def test_BRepGraph_CopyTest_CopyBox_SameParameter_Preserved():
    c = _copy(_box_graph())
    for i in range(c.Topo().Edges().Nb()):
        assert _edge_same_parameter(c, BRepGraph_EdgeId(i))
        assert _edge_same_range(c, BRepGraph_EdgeId(i))


def test_BRepGraph_CopyTest_FusedBoxes_Regularity_AreaPreserved():
    box1 = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    box2 = BRepPrimAPI_MakeBox(gp_Pnt(10.0, 0.0, 0.0), 10.0, 10.0, 10.0).Shape()
    fuser = BRepAlgoAPI_Fuse(box1, box2)
    assert fuser.IsDone()
    fused = fuser.Shape()
    orig_area = _area(fused)

    g = _graph(fused)
    c = _copy(g)
    assert c.Topo().Faces().Nb() == g.Topo().Faces().Nb()
    assert c.Topo().Edges().Nb() == g.Topo().Edges().Nb()

    copy_area = sum(
        abs(_area(c.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_FaceId(i))))) for i in range(c.Topo().Faces().Nb())
    )
    assert abs(copy_area - orig_area) <= orig_area * 0.01


def test_BRepGraph_CopyTest_CopyBox_UIDsPreserved():
    g = _box_graph()
    c = _copy(g)
    topo = g.Topo()
    for kind, count in (
        (Kind.Vertex, topo.Vertices().Nb()),
        (Kind.Edge, topo.Edges().Nb()),
        (Kind.Wire, topo.Wires().Nb()),
        (Kind.Face, topo.Faces().Nb()),
        (Kind.Shell, topo.Shells().Nb()),
        (Kind.Solid, topo.Solids().Nb()),
    ):
        for i in range(count):
            node = BRepGraph_NodeId(kind, i)
            orig_uid = g.UIDs().Of(node)
            copy_uid = c.UIDs().Of(node)
            assert copy_uid.IsValid() == orig_uid.IsValid()
            if orig_uid.IsValid():
                assert copy_uid == orig_uid

    assert g.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SurfaceRepId.IsValid()
    assert c.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SurfaceRepId.IsValid()
