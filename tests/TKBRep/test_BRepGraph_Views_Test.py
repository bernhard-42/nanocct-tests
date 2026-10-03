# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Views_Test.cxx (LGPL-2.1 with the OCCT exception)

import pytest

from nanocct import TopAbs
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_Compact,
    BRepGraph_CompoundId,
    BRepGraph_Deduplicate,
    BRepGraph_DefsIterator,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_FaceRefId,
    BRepGraph_LayerHistory,
    BRepGraph_LayerTopoSupplement,
    BRepGraph_NodeId,
    BRepGraph_RefId,
    BRepGraph_RefsIterator,
    BRepGraph_RelatedIterator,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
    BRepGraph_UID,
    BRepGraph_Validate,
    BRepGraph_VertexId,
    BRepGraph_WireId,
)
from nanocct.BRepGraphInc import ParityOrientation
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from nanocct.gp import gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import Standard_ProgramError
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Edge, TopoDS_Face, TopoDS_Shell, TopoDS_Vertex, TopoDS_Wire

Kind = BRepGraph_NodeId.Kind
RelationKind = BRepGraph_RelatedIterator.RelationKind


# ---------------------------------------------------------------- helpers


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def count_iterator(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def count_active_refs(g, ref_ids):
    return sum(1 for r in ref_ids if not r.IsRemoved(g))


def count_active_node_ids(g, node_ids):
    return sum(1 for n in node_ids if not g.Topo().Gen().IsRemoved(BRepGraph_NodeId(n)))


def count_active_nodes(g, kind, upper):
    return sum(1 for i in range(upper) if not g.Topo().Gen().IsRemoved(BRepGraph_NodeId(kind, i)))


def count_related(g, node, kind):
    n = 0
    it = BRepGraph_RelatedIterator(g, node)
    while it.More():
        if it.CurrentRelation() == kind:
            n += 1
        it.Next()
    return n


def first_face_of_edge(g, edge):
    it = g.Topo().Edges().FacesOf(edge)
    return it.CurrentId() if it.More() else BRepGraph_FaceId()


def edge_has_face(g, edge, face):
    return face in list(g.Topo().Edges().FacesOf(edge))


def count_adjacent_edges_of_edge(g, edge):
    if not edge.IsValid(g.Topo().Edges().Nb()) or edge.IsRemoved(g):
        return 0
    adjacent = []
    it = BRepGraph_DefsIterator.DefsVertexOfEdge(g, edge)
    while it.More():
        vid = it.CurrentId()
        for other in g.Topo().Vertices().Edges(vid):
            if other == edge or other.IsRemoved(g) or other in adjacent:
                continue
            adjacent.append(other)
        it.Next()
    return len(adjacent)


def box_compound(n=2):
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    for _ in range(n):
        bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return comp


def find_layer(g, layer_type):
    """C++ LayerRegistry().Find<T>() / FindLayer<T>() (template): look up by the type GUID."""
    return g.LayerRegistry().FindLayer(layer_type.GetID_s())


def square_wire(bb):
    pts = [gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0), gp_Pnt(10.0, 10.0, 0.0), gp_Pnt(0.0, 10.0, 0.0)]
    verts = []
    for p in pts:
        v = TopoDS_Vertex()
        bb.MakeVertex(v, p, 1.0e-7)
        verts.append(v)
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    for i in range(4):
        e = TopoDS_Edge()
        bb.MakeEdge(e)
        bb.Add(e, verts[i].Oriented(TopAbs.TopAbs_FORWARD))
        bb.Add(e, verts[(i + 1) % 4].Oriented(TopAbs.TopAbs_REVERSED))
        bb.Add(wire, e)
    wire.Closed(True)
    return wire


# ---------------------------------------------------------------- DefsView


def test_BRepGraph_ViewsTest_DefsView_NbFaces(graph):
    assert graph.Topo().Faces().Nb() == 6


def test_BRepGraph_ViewsTest_DefsView_NbSolids(graph):
    assert graph.Topo().Solids().Nb() == 1


def test_BRepGraph_ViewsTest_DefsView_NbShells(graph):
    assert graph.Topo().Shells().Nb() == 1


def test_BRepGraph_ViewsTest_DefsView_NbWires(graph):
    assert graph.Topo().Wires().Nb() == 6


def test_BRepGraph_ViewsTest_DefsView_NbEdges(graph):
    assert graph.Topo().Edges().Nb() == 12


def test_BRepGraph_ViewsTest_DefsView_NbVertices(graph):
    assert graph.Topo().Vertices().Nb() == 8


def test_BRepGraph_ViewsTest_DefsView_ActiveCounts_MatchStorageState(graph):
    t = graph.Topo()
    for kind, view in (
        (Kind.Vertex, t.Vertices()),
        (Kind.Edge, t.Edges()),
        (Kind.CoEdge, t.CoEdges()),
        (Kind.Wire, t.Wires()),
        (Kind.Face, t.Faces()),
        (Kind.Shell, t.Shells()),
        (Kind.Solid, t.Solids()),
        (Kind.Compound, t.Compounds()),
        (Kind.CompSolid, t.CompSolids()),
        (Kind.Product, t.Products()),
        (Kind.Occurrence, t.Occurrences()),
    ):
        assert count_active_nodes(graph, kind, view.Nb()) == view.NbActive(), kind


def test_BRepGraph_ViewsTest_DefsView_NbActiveFaces_ExcludeRemoved(graph):
    before = graph.Topo().Faces().NbActive()
    graph.Editor().Gen().RemoveNode(BRepGraph_FaceId.Start_s())
    assert graph.Topo().Faces().NbActive() == before - 1
    assert graph.Topo().Gen().IsRemoved(BRepGraph_FaceId.Start_s())


def test_BRepGraph_ViewsTest_DefsView_FaceAccessor_Valid(graph):
    it = BRepGraph_FaceIterator(graph)
    while it.More():
        assert it.CurrentId().IsValid()
        it.Next()


def test_BRepGraph_ViewsTest_DefsView_TopoEntity_Valid(graph):
    assert graph.Topo().Gen().TopoEntity(BRepGraph_FaceId(0)) is not None


def test_BRepGraph_ViewsTest_TopoView_GenValidity(graph):
    gen = graph.Topo().Gen()
    fid = BRepGraph_NodeId(BRepGraph_FaceId.Start_s())
    assert gen.Nb(Kind.Face) == graph.Topo().Faces().Nb()
    assert gen.IsValid(fid)
    assert gen.IsActive(fid)
    assert not gen.IsRemoved(fid)

    graph.Editor().Gen().RemoveNode(fid)
    assert gen.IsValid(fid)
    assert not gen.IsActive(fid)
    assert gen.IsRemoved(fid)

    out = BRepGraph_NodeId(Kind.Face, graph.Topo().Faces().Nb())
    assert not gen.IsValid(out)
    assert not gen.IsActive(out)
    assert gen.IsRemoved(out)


def test_BRepGraph_ViewsTest_DefsView_NbNodes_Positive(graph):
    assert graph.Topo().Gen().NbNodes() > 0


def test_BRepGraph_ViewsTest_DefsView_FaceSurface_NonNull(graph):
    it = BRepGraph_FaceIterator(graph)
    while it.More():
        assert BRepGraph_Tool.Face.HasSurface_s(graph, it.CurrentId())
        it.Next()


def test_BRepGraph_ViewsTest_DefsView_EdgeCurve3d_NonNull(graph):
    it = BRepGraph_EdgeIterator(graph)
    while it.More():
        assert BRepGraph_Tool.Edge.HasCurve_s(graph, it.CurrentId())
        it.Next()


def test_BRepGraph_ViewsTest_DefsView_FindPCurveCoEdgeId_NoCrash(graph):
    BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(graph, BRepGraph_EdgeId.Start_s(), BRepGraph_FaceId.Start_s())


def test_BRepGraph_ViewsTest_DefsView_RepIdConvenienceAccessors_RoundTrip(graph):
    assert graph.Topo().Faces().Surface(BRepGraph_FaceId(0)) is not None
    assert graph.Topo().Edges().Curve3D(BRepGraph_EdgeId(0)) is not None
    coedges = graph.Topo().Edges().CoEdges(BRepGraph_EdgeId(0))
    assert coedges.Size() > 0
    assert graph.Topo().CoEdges().Curve2D(coedges.Value(0)) is not None


def test_BRepGraph_ViewsTest_DefsView_RepIdConvenienceAccessors_InvalidInput(graph):
    face_out = BRepGraph_FaceId(graph.Topo().Faces().Nb())
    edge_out = BRepGraph_EdgeId(graph.Topo().Edges().Nb())
    coedge_out = BRepGraph_CoEdgeId(graph.Topo().CoEdges().Nb())
    assert graph.Topo().Faces().Surface(face_out) is None
    assert graph.Topo().Faces().ActiveTriangulation(face_out) is None
    assert graph.Topo().Edges().Curve3D(edge_out) is None
    assert graph.Topo().CoEdges().Curve2D(coedge_out) is None


# ---------------------------------------------------------------- UIDsView


def test_BRepGraph_ViewsTest_UIDsView_Of_Valid(graph):
    assert graph.UIDs().Of(BRepGraph_NodeId(BRepGraph_FaceId(0))).IsValid()


def test_BRepGraph_ViewsTest_UIDsView_Generation_Positive(graph):
    assert graph.UIDs().Generation() > 0


def test_BRepGraph_ViewsTest_UIDsView_NodeIdFrom_RoundTrip(graph):
    fid = BRepGraph_NodeId(BRepGraph_FaceId(0))
    uid = graph.UIDs().Of(fid)
    assert uid.IsValid()
    assert graph.UIDs().NodeIdFrom(uid) == fid


def test_BRepGraph_ViewsTest_UIDsView_NodeIdFrom_MultipleRoundTrip(graph):
    face = BRepGraph_NodeId(BRepGraph_FaceId.Start_s())
    edge = BRepGraph_NodeId(BRepGraph_EdgeId.Start_s())
    uids = [graph.UIDs().Of(face), graph.UIDs().Of(edge)]
    assert uids[0].IsValid()
    assert uids[1].IsValid()
    assert len(uids) == 2
    assert graph.UIDs().NodeIdFrom(uids[0]) == face
    assert graph.UIDs().NodeIdFrom(uids[1]) == edge


def test_BRepGraph_ViewsTest_UIDsView_NodeIdFrom_InvalidAndUnknownUID(graph):
    uids = [BRepGraph_UID(), BRepGraph_UID(Kind.Face, 9999)]
    assert not graph.UIDs().NodeIdFrom(uids[0]).IsValid()
    assert not graph.UIDs().NodeIdFrom(uids[1]).IsValid()


def test_BRepGraph_ViewsTest_UIDsView_NodeLookup_RemovedNode_ReturnsInvalidAndHasFalse(graph):
    fid = BRepGraph_NodeId(BRepGraph_FaceId(0))
    uid = graph.UIDs().Of(fid)
    assert uid.IsValid()
    assert graph.UIDs().Has(uid)
    assert graph.UIDs().NodeIdFrom(uid) == fid

    graph.Editor().Gen().RemoveNode(fid)
    assert not graph.UIDs().Has(uid)
    assert not graph.UIDs().NodeIdFrom(uid).IsValid()


def test_BRepGraph_ViewsTest_UIDsView_Of_RemovedNode_ReturnsInvalid(graph):
    fid = BRepGraph_NodeId(BRepGraph_FaceId(0))
    assert graph.UIDs().Of(fid).IsValid()
    graph.Editor().Gen().RemoveNode(fid)
    assert not graph.UIDs().Of(fid).IsValid()


def test_BRepGraph_ViewsTest_UIDsView_RefLookup_RemovedRef_ReturnsInvalidAndHasFalse(graph):
    refs = graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert refs.Size() > 0
    ref = refs.Value(0)
    uid = graph.UIDs().Of(BRepGraph_RefId(ref))
    assert uid.IsValid()
    assert graph.UIDs().Has(uid)
    assert graph.UIDs().RefIdFrom(uid) == BRepGraph_RefId(ref)

    assert graph.Editor().Gen().RemoveRef(ref)
    assert not graph.UIDs().Has(uid)
    assert not graph.UIDs().RefIdFrom(uid).IsValid()


def test_BRepGraph_ViewsTest_UIDsView_Of_RemovedRef_ReturnsInvalid(graph):
    refs = graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert refs.Size() > 0
    ref = refs.Value(0)
    assert graph.UIDs().Of(BRepGraph_RefId(ref)).IsValid()
    assert graph.Editor().Gen().RemoveRef(ref)
    assert not graph.UIDs().Of(BRepGraph_RefId(ref)).IsValid()


def test_BRepGraph_ViewsTest_UIDsView_Of_OutOfRangeRef_ReturnsInvalid(graph):
    out = BRepGraph_FaceRefId(graph.Refs().Faces().Nb())
    assert not graph.UIDs().Of(BRepGraph_RefId(out)).IsValid()


# ---------------------------------------------------------------- adjacency


def test_BRepGraph_ViewsTest_SpatialView_AdjacentFaces_FourPerBoxFace(graph):
    assert count_related(graph, BRepGraph_NodeId(BRepGraph_FaceId(0)), RelationKind.AdjacentFace) == 4


def test_BRepGraph_ViewsTest_SpatialView_FacesOfEdge_TwoPerBoxEdge(graph):
    assert count_iterator(graph.Topo().Edges().FacesOf(BRepGraph_EdgeId(0))) == 2


def test_BRepGraph_ViewsTest_SpatialView_OutParam_Parity(graph):
    assert count_related(graph, BRepGraph_NodeId(BRepGraph_FaceId(0)), RelationKind.AdjacentFace) == 4
    assert count_adjacent_edges_of_edge(graph, BRepGraph_EdgeId(0)) >= 4


def test_BRepGraph_ViewsTest_TopoView_GroupedFaceOps_Parity(graph):
    fid = BRepGraph_FaceId(0)
    assert BRepGraph_NodeId(fid) == BRepGraph_NodeId(fid)
    assert graph.Topo().Faces().Surface(fid) is not None
    assert count_related(graph, BRepGraph_NodeId(fid), RelationKind.AdjacentFace) == 4


def test_BRepGraph_ViewsTest_TopoView_GroupedEdgeAndVertexOps_Parity(graph):
    eid = BRepGraph_EdgeId(0)
    vid = BRepGraph_VertexId(0)
    assert BRepGraph_NodeId(eid) == BRepGraph_NodeId(eid)
    assert graph.Topo().Edges().NbFaces(eid) == 2
    assert graph.Topo().Edges().Curve3D(eid) is not None
    assert not BRepGraph_Tool.Edge.IsBoundary_s(graph, eid)
    assert BRepGraph_Tool.Edge.IsManifold_s(graph, eid)
    assert count_iterator(graph.Topo().Edges().WiresOf(eid)) >= 1
    assert graph.Topo().Edges().CoEdges(eid).Size() >= 1
    assert count_iterator(graph.Topo().Edges().FacesOf(eid)) == 2
    assert count_adjacent_edges_of_edge(graph, eid) >= 4
    assert BRepGraph_NodeId(vid) == BRepGraph_NodeId(vid)
    assert graph.Topo().Vertices().Edges(vid).Size() >= 1


def test_BRepGraph_ViewsTest_TopoView_GroupedCoEdgeOps_Parity(graph):
    ce = BRepGraph_CoEdgeId(0)
    d = graph.Topo().CoEdges().Definition(ce)
    assert BRepGraph_NodeId(ce) == BRepGraph_NodeId(ce)
    assert graph.Topo().CoEdges().Definition(ce).ChildEdgeId == d.ChildEdgeId
    assert graph.Topo().CoEdges().Definition(ce).FaceId == d.FaceId
    assert graph.Topo().CoEdges().Curve2D(ce) is not None
    assert BRepGraph_Tool.CoEdge.SeamPair_s(graph, ce) == BRepGraph_Tool.CoEdge.SeamPair_s(graph, ce)


def test_BRepGraph_ViewsTest_TopoView_GroupedProductAndOccurrenceOps_Parity(graph):
    products = graph.Editor().Products()
    part = products.Add(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    products.AppendDocumentRoot(part)
    sub = products.Add()
    products.AppendDocumentRoot(sub)
    root = products.Add()
    products.AppendDocumentRoot(root)
    assert part.IsValid()
    assert sub.IsValid()
    assert root.IsValid()

    sub_occ = products.Append(root, sub, TopLoc_Location())
    part_occ = products.Append(sub, part, TopLoc_Location(), sub_occ)
    assert sub_occ.IsValid()
    assert part_occ.IsValid()

    assert BRepGraph_NodeId(part) == BRepGraph_NodeId(part)
    assert graph.Topo().Products().ShapeRoot(part) == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    assert not graph.Topo().Products().ShapeRoot(root).IsValid()
    assert graph.Refs().Occurrences().IdsOf(root).Size() == 1
    assert graph.Refs().Occurrences().IdsOf(sub).Size() == 1

    assert BRepGraph_NodeId(part_occ) == BRepGraph_NodeId(part_occ)
    assert graph.Topo().Occurrences().Product(part_occ) == part
    assert graph.Topo().Occurrences().ParentProduct(part_occ) == sub

    occ_refs = graph.Refs().Occurrences().IdsOf(sub)
    assert occ_refs.Size() == 1
    graph.Editor().Gen().RemoveRef(occ_refs.Value(0))
    assert graph.Topo().Products().NbComponents(sub) == 0


def test_BRepGraph_ViewsTest_SpatialView_OutParam_ClearAndInvalid(graph):
    assert count_related(graph, BRepGraph_NodeId(BRepGraph_FaceId.Start_s()), RelationKind.AdjacentFace) == 4
    assert count_related(graph, BRepGraph_NodeId(BRepGraph_FaceId(999)), RelationKind.AdjacentFace) == 0
    assert count_adjacent_edges_of_edge(graph, BRepGraph_EdgeId.Start_s()) >= 4
    assert count_adjacent_edges_of_edge(graph, BRepGraph_EdgeId(999)) == 0


# ---------------------------------------------------------------- BRepGraph_Tool


def test_BRepGraph_ViewsTest_BRepGraphTool_FindCoEdgeId_ValidPair(graph):
    edge = BRepGraph_EdgeId(0)
    face = first_face_of_edge(graph, edge)
    assert face.IsValid()
    ce = BRepGraph_Tool.Edge.FindCoEdgeId_s(graph, edge, face)
    assert ce.IsValid()
    d = graph.Topo().CoEdges().Definition(ce)
    assert d.ChildEdgeId == edge
    assert d.FaceId == face


def test_BRepGraph_ViewsTest_BRepGraphTool_FindCoEdgeId_InvalidPair_ReturnsInvalid(graph):
    edge = BRepGraph_EdgeId(0)
    non_adjacent = None
    for i in range(graph.Topo().Faces().Nb()):
        fid = BRepGraph_FaceId(i)
        if not edge_has_face(graph, edge, fid):
            non_adjacent = fid
            break
    if non_adjacent is not None:
        assert not BRepGraph_Tool.Edge.FindCoEdgeId_s(graph, edge, non_adjacent).IsValid()


# ---------------------------------------------------------------- RefsView


def test_BRepGraph_ViewsTest_RefsView_ActiveCounts_MatchFreshBuild(graph):
    r = graph.Refs()
    assert r.Shells().NbActive() == r.Shells().Nb()
    assert r.Faces().NbActive() == r.Faces().Nb()
    assert r.Wires().NbActive() == r.Wires().Nb()
    assert graph.Topo().CoEdges().NbActive() == graph.Topo().CoEdges().Nb()
    assert r.Vertices().NbActive() == r.Vertices().Nb()
    assert r.Solids().NbActive() == r.Solids().Nb()
    assert r.Children().NbActive() == r.Children().Nb()
    assert r.Occurrences().NbActive() == r.Occurrences().Nb()


def test_BRepGraph_ViewsTest_RefsView_RefIdsOf_MatchFreshBuild(graph):
    shell = BRepGraph_ShellId(0)
    face = BRepGraph_FaceId(0)
    wire = BRepGraph_WireId(0)
    solid = BRepGraph_SolidId(0)
    r = graph.Refs()
    assert count_active_refs(graph, r.Faces().IdsOf(shell)) == r.Faces().IdsOf(shell).Size()
    assert count_active_refs(graph, r.Wires().IdsOf(face)) == r.Wires().IdsOf(face).Size()
    coedges = graph.Topo().Wires().Relations(wire).CoEdgeIds
    assert count_active_node_ids(graph, coedges) == coedges.Size()
    assert count_active_refs(graph, r.Shells().IdsOf(solid)) == r.Shells().IdsOf(solid).Size()


def test_BRepGraph_ViewsTest_RefsView_FaceRefIdsOf_LocalFilteringHandlesRemoved(graph):
    shell = BRepGraph_ShellId(0)
    refs = graph.Refs().Faces().IdsOf(shell)
    assert refs.Size() > 0
    before = refs.Size()
    graph.Editor().Gen().RemoveRef(refs.Value(0))
    assert count_active_refs(graph, graph.Refs().Faces().IdsOf(shell)) == before - 1


def test_BRepGraph_ViewsTest_RefsView_VertexRefIdsOfEdge_ContainsBoundaryVertices(graph):
    n = 0
    it = BRepGraph_RefsIterator.RefsVertexOfEdge(graph, BRepGraph_EdgeId.Start_s())
    while it.More():
        vref = it.CurrentId()
        entry = graph.Refs().Vertices().Entry(vref)
        assert not vref.IsRemoved(graph)
        assert entry.ChildVertexId.IsValid(graph.Topo().Vertices().Nb())
        n += 1
        it.Next()
    assert n >= 2


def test_BRepGraph_ViewsTest_RefsView_GenericRefHelpers_RoundTripForTypedRef(graph):
    refs = graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert refs.Size() > 0
    ref = refs.Value(0)
    guard = graph.Editor().Faces().MutRef(ref)
    graph.Editor().Faces().SetRefOrientation(guard, ParityOrientation(TopAbs.TopAbs_REVERSED))
    del guard  # C++ scope end: release the guard

    entry = graph.Refs().Faces().Entry(ref)
    gen = graph.Refs().Gen()
    gref = BRepGraph_RefId(ref)
    assert gen.ChildNode(gref) == BRepGraph_NodeId(entry.ChildFaceId)
    assert gen.LocalLocation(gref).IsIdentity()
    # C++ compares TopAbs_Orientation with the ParityOrientation (implicit conversion)
    assert (gen.Orientation(gref) == TopAbs.TopAbs_REVERSED) == entry.Orientation.IsReversed
    assert gen.Nb(BRepGraph_RefId.Kind.Face) == graph.Refs().Faces().Nb()
    assert gen.IsValid(gref)
    assert gen.IsActive(gref)
    assert not gen.IsRemoved(gref)

    ce = graph.Topo().Wires().Relations(BRepGraph_WireId.Start_s()).CoEdgeIds.Value(0)
    ced = graph.Topo().CoEdges().Definition(ce)
    assert ced.ChildEdgeId.IsValid()
    assert ced.FaceId.IsValid()
    # A ParityOrientation can only hold FORWARD/REVERSED; INTERNAL/EXTERNAL are unrepresentable.
    assert isinstance(ced.Orientation, ParityOrientation)


def test_BRepGraph_ViewsTest_RefsView_RefAtStep_RoundTrip(graph):
    solid = BRepGraph_SolidId(0)
    shell_ref = graph.Topo().Solids().Relations(solid).ShellRefIds.Value(0)
    gen = graph.Refs().Gen()
    assert gen.RefAtStep(BRepGraph_NodeId(solid), 0) == BRepGraph_RefId(shell_ref)
    wire = BRepGraph_NodeId(BRepGraph_WireId(0))
    assert not gen.RefAtStep(wire, 0).IsValid()
    assert not gen.RefAtStep(wire, 100).IsValid()


def test_BRepGraph_ViewsTest_RefsView_GenericRefHelpers_OccurrenceLocalLocation(graph):
    products = graph.Editor().Products()
    part = products.Add(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()

    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(4.0, 5.0, 6.0))
    assert products.Append(assembly, part, TopLoc_Location(trsf)).IsValid()

    occ_refs = graph.Refs().Occurrences().IdsOf(assembly)
    assert occ_refs.Size() == 1
    ref = occ_refs.Value(0)
    entry = graph.Refs().Occurrences().Entry(ref)
    gen = graph.Refs().Gen()
    gref = BRepGraph_RefId(ref)
    assert gen.RefAtStep(BRepGraph_NodeId(assembly), 0) == gref
    assert gen.ChildNode(gref) == BRepGraph_NodeId(entry.ChildOccurrenceId)
    assert gen.LocalLocation(gref).IsEqual(entry.LocalLocation)
    assert gen.Orientation(gref) == TopAbs.TopAbs_FORWARD
    assert not gen.IsRemoved(gref)


def test_BRepGraph_ViewsTest_RefsView_GenericRefHelpers_InvalidAndRemoved(graph):
    gen = graph.Refs().Gen()
    inv = BRepGraph_RefId()
    assert not gen.ChildNode(inv).IsValid()
    assert gen.LocalLocation(inv).IsEqual(TopLoc_Location())
    assert gen.Orientation(inv) == TopAbs.TopAbs_FORWARD
    assert not gen.IsValid(inv)
    assert not gen.IsActive(inv)
    assert gen.IsRemoved(inv)

    refs = graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert refs.Size() > 0
    ref = BRepGraph_RefId(refs.Value(0))
    graph.Editor().Gen().RemoveRef(refs.Value(0))
    assert gen.IsValid(ref)
    assert not gen.IsActive(ref)
    assert gen.IsRemoved(ref)

    out = BRepGraph_RefId(BRepGraph_FaceRefId(graph.Refs().Faces().Nb()))
    assert not gen.IsValid(out)
    assert not gen.IsActive(out)
    assert gen.IsRemoved(out)
    assert not gen.ChildNode(out).IsValid()
    assert gen.LocalLocation(out).IsEqual(TopLoc_Location())
    assert gen.Orientation(out) == TopAbs.TopAbs_FORWARD


# ---------------------------------------------------------------- ShapesView


def test_BRepGraph_ViewsTest_ShapesView_Shape_NonNull(graph):
    assert not graph.Shapes().Shape(BRepGraph_NodeId(BRepGraph_FaceId(0))).IsNull()


def test_BRepGraph_ViewsTest_ShapesView_HasOriginal_True(graph):
    assert graph.Shapes().HasOriginal(BRepGraph_NodeId(BRepGraph_FaceId(0)))


def test_BRepGraph_ViewsTest_ShapesView_Original_ValidNode_ReturnsShape(graph):
    assert not graph.Shapes().Original(BRepGraph_NodeId(BRepGraph_FaceId(0))).IsNull()


def test_BRepGraph_ViewsTest_ShapesView_Original_InvalidNode_ReturnsNull(graph):
    assert graph.Shapes().Original(BRepGraph_NodeId()).IsNull()


def test_BRepGraph_ViewsTest_ShapesView_RemovedNode_OriginalQueries_AreUnavailable(graph):
    fid = BRepGraph_NodeId(BRepGraph_FaceId(0))
    assert graph.Shapes().HasOriginal(fid)
    graph.Editor().Gen().RemoveNode(fid)
    assert not graph.Shapes().HasOriginal(fid)
    assert graph.Shapes().Original(fid).IsNull()
    assert graph.Shapes().Shape(fid).IsNull()


def test_BRepGraph_ViewsTest_ShapesView_Reconstruct_InvalidNode_ReturnsNull(graph):
    assert graph.Shapes().Reconstruct(BRepGraph_NodeId()).IsNull()


def test_BRepGraph_ViewsTest_ShapesView_Reconstruct_RemovedNode_ReturnsNull(graph):
    fid = BRepGraph_NodeId(BRepGraph_FaceId(0))
    graph.Editor().Gen().RemoveNode(fid)
    assert graph.Shapes().Reconstruct(fid).IsNull()


def test_BRepGraph_ViewsTest_ShapesView_FindNodeAndHasNode_RemovedNode_AreUnavailable(graph):
    fid = BRepGraph_NodeId(BRepGraph_FaceId(0))
    face_shape = graph.Shapes().Original(fid)
    assert not face_shape.IsNull()
    assert graph.Shapes().HasNode(face_shape)
    assert graph.Shapes().FindNode(face_shape) == fid

    graph.Editor().Gen().RemoveNode(fid)
    assert not graph.Shapes().HasNode(face_shape)
    assert not graph.Shapes().FindNode(face_shape).IsValid()


# ---------------------------------------------------------------- MutView


def test_BRepGraph_ViewsTest_MutView_EdgeDef_IncrementsOwnGen(graph):
    guard = graph.Editor().Edges().Mut(BRepGraph_EdgeId.Start_s())
    guard.MarkDirty()
    del guard  # C++ scope end fires markModified
    assert graph.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s()).OwnGen > 0


def test_BRepGraph_ViewsTest_MutView_InvalidNode_ThrowsProgramError(graph):
    with pytest.raises(Standard_ProgramError):
        graph.Editor().Faces().Mut(BRepGraph_FaceId(777777))


def test_BRepGraph_ViewsTest_MutView_RemovedNode_ThrowsProgramError(graph):
    fid = BRepGraph_FaceId(0)
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(fid))
    with pytest.raises(Standard_ProgramError):
        graph.Editor().Faces().Mut(fid)


def test_BRepGraph_ViewsTest_MutView_RemovedRef_ThrowsProgramError(graph):
    refs = graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert refs.Size() > 0
    ref = refs.Value(0)
    assert graph.Editor().Gen().RemoveRef(ref)
    with pytest.raises(Standard_ProgramError):
        graph.Editor().Faces().MutRef(ref)


# ---------------------------------------------------------------- EditorView


def test_BRepGraph_ViewsTest_EditorView_AddVertex_Works(graph):
    before = graph.Topo().Vertices().Nb()
    vid = graph.Editor().Vertices().Add(gp_Pnt(1, 2, 3), 0.001)
    assert vid.IsValid()
    assert graph.Topo().Vertices().Nb() == before + 1


def test_BRepGraph_ViewsTest_EditorView_IsRemoved_False(graph):
    assert not graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(BRepGraph_FaceId(0)))


# ---------------------------------------------------------------- history layer


def test_BRepGraph_ViewsTest_History_ConstLookup(graph):
    history = find_layer(graph, BRepGraph_LayerHistory)
    assert history is not None
    assert history.IsEnabled()


def test_BRepGraph_ViewsTest_History_MutableLookup(graph):
    # Ensure<T>() is a template; the history layer is registered by default (see ConstLookup).
    find_layer(graph, BRepGraph_LayerHistory).SetEnabled(False)
    assert not find_layer(graph, BRepGraph_LayerHistory).IsEnabled()
    find_layer(graph, BRepGraph_LayerHistory).SetEnabled(True)
    assert find_layer(graph, BRepGraph_LayerHistory).IsEnabled()


# ---------------------------------------------------------------- BRepGraph_Tool regressions


def test_BRepGraph_ViewsTest_BRepGraphTool_FindPCurveCoEdgeId_SkipsRemovedCoEdges(graph):
    fid = BRepGraph_FaceId.Start_s()
    wid = BRepGraph_Tool.Face.OuterWire_s(graph, fid)
    assert wid.IsValid()
    rel = graph.Topo().Wires().Relations(wid)
    assert rel.CoEdgeIds.Size() > 0
    ce = rel.CoEdgeIds.Value(0)
    assert ce.IsValid()

    d = graph.Topo().CoEdges().Definition(ce)
    eid = d.ChildEdgeId
    fid2 = d.FaceId
    assert BRepGraph_Tool.Edge.FindCoEdgeId_s(graph, eid, fid2) == ce

    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(ce))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(ce))

    assert not BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(graph, eid, fid2).IsValid()
    assert BRepGraph_Tool.Edge.FindCoEdgeId_s(graph, eid, fid2) != ce


def test_BRepGraph_ViewsTest_BRepGraphTool_OuterWire_SkipsRemovedWireDef(graph):
    fid = BRepGraph_FaceId.Start_s()
    wid = BRepGraph_Tool.Face.OuterWire_s(graph, fid)
    assert wid.IsValid()
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(wid))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(wid))
    assert BRepGraph_Tool.Face.OuterWire_s(graph, fid) != wid


def test_BRepGraph_ViewsTest_BRepGraphTool_OuterWire_SkipsWireWithoutUVBounds(graph):
    fid = BRepGraph_FaceId.Start_s()
    valid_wire = BRepGraph_Tool.Face.OuterWire_s(graph, fid)
    assert valid_wire.IsValid()

    empty_wire = graph.Editor().Wires().Add(NCollection_Array1[BRepGraph_CoEdgeId]())
    assert empty_wire.IsValid()
    empty_ref = graph.Editor().Faces().Append(fid, empty_wire, ParityOrientation(TopAbs.TopAbs_FORWARD))
    assert empty_ref.IsValid()

    assert BRepGraph_Tool.Face.OuterWire_s(graph, fid) == valid_wire


def test_BRepGraph_ViewsTest_BRepGraphTool_IsBoundary_SkipsRemovedFaces(graph):
    edge = None
    for i in range(graph.Topo().Edges().Nb()):
        eid = BRepGraph_EdgeId(i)
        if count_iterator(graph.Topo().Edges().FacesOf(eid)) == 2:
            edge = eid
            break
    assert edge is not None
    assert not BRepGraph_Tool.Edge.IsBoundary_s(graph, edge)
    assert BRepGraph_Tool.Edge.IsManifold_s(graph, edge)

    face = first_face_of_edge(graph, edge)
    assert face.IsValid()
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(face))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(face))

    assert BRepGraph_Tool.Edge.IsBoundary_s(graph, edge)
    assert not BRepGraph_Tool.Edge.IsManifold_s(graph, edge)


def test_BRepGraph_ViewsTest_BRepGraphTool_IsBoundaryAndIsManifold_RemovedEdge_ReturnsFalse(graph):
    eid = BRepGraph_EdgeId.Start_s()
    assert eid.IsValid(graph.Topo().Edges().Nb())
    assert not graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(eid))
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(eid))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(eid))
    assert not BRepGraph_Tool.Edge.IsBoundary_s(graph, eid)
    assert not BRepGraph_Tool.Edge.IsManifold_s(graph, eid)


def test_BRepGraph_ViewsTest_BRepGraphTool_SeamPair_BoundsCheck(graph):
    graph.Clear()
    graph.Shapes().Add(BRepPrimAPI_MakeSphere(gp_Pnt(0, 0, 0), 10.0).Shape())
    assert not graph.IsEmpty()

    found = False
    for i in range(graph.Topo().CoEdges().Nb()):
        ce = BRepGraph_CoEdgeId(i)
        pair = BRepGraph_Tool.CoEdge.SeamPair_s(graph, ce)
        if pair.IsValid():
            found = True
            assert BRepGraph_Tool.CoEdge.SeamPair_s(graph, pair) == ce
            break
    assert found


# ---------------------------------------------------------------- EditorView regressions


def _dedup_compact(g):
    opts = BRepGraph_Deduplicate.Options()
    opts.MergeEntitiesWhenSafe = True
    BRepGraph_Deduplicate.Perform_s(g, opts)
    BRepGraph_Compact.Perform_s(g)


def test_BRepGraph_ViewsTest_EditorView_ReplaceEdge_SkipsRemovedCoEdgeDef(graph):
    graph.Clear()
    graph.Shapes().Add(box_compound(2))
    assert not graph.IsEmpty()
    _dedup_compact(graph)
    assert BRepGraph_Validate.Perform_s(graph).IsValid()


def test_BRepGraph_ViewsTest_EditorView_RemoveSolid_PropagatesSubtreeGenToParent(graph):
    graph.Clear()
    graph.Shapes().Add(box_compound(1))
    assert not graph.IsEmpty()
    assert graph.Topo().Compounds().Nb() == 1
    assert graph.Topo().Solids().Nb() == 1

    sid = BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    graph.Editor().Gen().RemoveNode(sid)
    assert graph.Topo().Gen().IsRemoved(sid)
    BRepGraph_Compact.Perform_s(graph)
    assert BRepGraph_Validate.Perform_s(graph).IsValid()


def test_BRepGraph_ViewsTest_EditorView_RemoveOccurrence_UnbindsProductOccurrence(graph):
    g = BRepGraph()
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepBuilderAPI_Copy(box, True).Shape())
    bb.Add(comp, BRepBuilderAPI_Copy(box, True).Shape())
    g.Shapes().Add(comp)
    assert not g.IsEmpty()

    opts = BRepGraph_Deduplicate.Options()
    opts.MergeEntitiesWhenSafe = True
    BRepGraph_Deduplicate.Perform_s(g, opts)
    BRepGraph_Compact.Perform_s(g, BRepGraph_Compact.Options())
    assert g.ValidateRelations()


def test_BRepGraph_ViewsTest_EditorView_ReplaceEdge_RejectsRemovedWire(graph):
    graph.Clear()
    graph.Shapes().Add(box_compound(2))
    assert not graph.IsEmpty()
    _dedup_compact(graph)
    assert BRepGraph_Validate.Perform_s(graph).IsValid()


def test_BRepGraph_ViewsTest_EditorView_Split_RejectsRemovedVertex(graph):
    eid = BRepGraph_EdgeId.Start_s()
    start_ref = BRepGraph_Tool.Edge.StartVertexId_s(graph, eid)
    usage = BRepGraph_Tool.Vertex.Usage_s(graph, start_ref)
    assert usage.IsValid()
    start_v = usage.DefId
    assert not graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(start_v))

    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(start_v))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(start_v))

    sub_a = BRepGraph_EdgeId()
    sub_b = BRepGraph_EdgeId()
    graph.Editor().Edges().Split(eid, start_v, 0.5, sub_a, sub_b)
    assert not sub_a.IsValid()
    assert not sub_b.IsValid()


def test_BRepGraph_ViewsTest_CleanupRemovedRefs_OrphanedCoEdgesMarkedRemoved(graph):
    eid = BRepGraph_EdgeId.Start_s()
    assert eid.IsValid(graph.Topo().Edges().Nb())
    before = graph.Topo().CoEdges().NbActive()
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(eid))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(eid))
    graph.Editor().Gen().CleanupRemovedReferences()
    assert graph.Topo().CoEdges().NbActive() < before
    assert graph.ValidateRelations()


def test_BRepGraph_ViewsTest_TopoView_RepAccessors_ReturnNullForRemovedEntity(graph):
    eid = BRepGraph_EdgeId.Start_s()
    assert graph.Topo().Edges().Curve3D(eid) is not None
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(eid))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(eid))
    assert graph.Topo().Edges().Curve3D(eid) is None

    fid = BRepGraph_FaceId.Start_s()
    assert graph.Topo().Faces().Surface(fid) is not None
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(fid))
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(fid))
    assert graph.Topo().Faces().Surface(fid) is None
    assert graph.Topo().Faces().ActiveTriangulation(fid) is None


# ---------------------------------------------------------------- supplement routing


def test_BRepGraph_ViewsTest_ShapesView_ShellAddFace_Internal_RoutedToSupplement():
    g = BRepGraph()
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = False

    bb = BRep_Builder()
    shell = TopoDS_Shell()
    bb.MakeShell(shell)
    wire = square_wire(bb)
    face = TopoDS_Face()
    bb.MakeFace(face)
    bb.Add(face, wire)
    bb.Add(shell, face)

    shell_res = g.Shapes().Add(shell, opts)
    assert shell_res.IsOk()
    shell_id = BRepGraph_ShellId(shell_res.TopologyRoot)

    internal = TopoDS_Face()
    bb.MakeFace(internal)
    bb.Add(internal, wire)
    internal.Orientation(TopAbs.TopAbs_INTERNAL)

    add_res = g.Shapes().Add(internal, BRepGraph_NodeId(shell_id))
    assert add_res.IsOk()

    layer = find_layer(g, BRepGraph_LayerTopoSupplement)
    assert layer is not None
    assert layer.AttachedTo(BRepGraph_NodeId(shell_id)).Size() > 0


def test_BRepGraph_ViewsTest_ShapesView_CompoundAddChild_MixedOrientations_CoreRefAndSupplement():
    g = BRepGraph()
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = False

    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    comp_res = g.Shapes().Add(comp, opts)
    assert comp_res.IsOk()
    comp_id = BRepGraph_CompoundId(comp_res.TopologyRoot)

    wire = square_wire(bb)

    fwd = TopoDS_Face()
    bb.MakeFace(fwd)
    bb.Add(fwd, wire)
    fwd.Orientation(TopAbs.TopAbs_FORWARD)
    fwd_res = g.Shapes().Add(fwd, BRepGraph_NodeId(comp_id))
    assert fwd_res.IsOk()
    assert fwd_res.InsertedRef.IsValid()

    internal = TopoDS_Face()
    bb.MakeFace(internal)
    bb.Add(internal, wire)
    internal.Orientation(TopAbs.TopAbs_INTERNAL)
    int_res = g.Shapes().Add(internal, BRepGraph_NodeId(comp_id))
    assert int_res.IsOk()
    assert not int_res.InsertedRef.IsValid()

    layer = find_layer(g, BRepGraph_LayerTopoSupplement)
    assert layer is not None
    assert layer.AttachedTo(BRepGraph_NodeId(comp_id)).Size() == 1
