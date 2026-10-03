# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraphInc_Test.cxx (LGPL-2.1 with the OCCT exception)

import pytest

from nanocct import TopAbs, TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Transform,
)
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CacheDerivedState,
    BRepGraph_CoEdgeId,
    BRepGraph_Compact,
    BRepGraph_CompoundId,
    BRepGraph_CompoundsOfChild,
    BRepGraph_CompSolidId,
    BRepGraph_Deduplicate,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_FaceRefId,
    BRepGraph_FacesOfWire,
    BRepGraph_LayerTopoSupplement,
    BRepGraph_NodeId,
    BRepGraph_RefId,
    BRepGraph_ShellId,
    BRepGraph_ShellRefId,
    BRepGraph_ShellsOfFace,
    BRepGraph_SolidId,
    BRepGraph_SolidRefId,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_VertexId,
    BRepGraph_VertexRefId,
    BRepGraph_WireId,
    BRepGraph_WireRefId,
)
from nanocct.BRepGraphInc import (
    BRepGraph_RepId,
    BRepGraphInc_Populate,
    BRepGraphInc_Reconstruct,
    BRepGraphInc_Storage,
    ParityOrientation,
)
from nanocct.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeSphere,
)
from nanocct.Geom import Geom_Plane
from nanocct.Geom2d import Geom2d_Line
from nanocct.GProp import GProp_GProps
from nanocct.gp import gp_Dir2d, gp_Pln, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ProgramError
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import (
    TopoDS_Compound,
    TopoDS_CompSolid,
    TopoDS_Edge,
    TopoDS_Face,
    TopoDS_Iterator,
    TopoDS_Shape,
    TopoDS_Shell,
    TopoDS_Solid,
    TopoDS_Vertex,
    TopoDS_Wire,
)

CONF = Precision.Confusion_s()


# ---------------------------------------------------------------- helpers


def compute_area(shape):
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


def compute_volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def count_sub_shapes(shape, kind):
    return sum(1 for _ in TopExp_Explorer(shape, kind))


def count_iterator(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def populate(shape, parallel=False):
    graph = BRepGraph()
    BRepGraphInc_Populate.Perform_s(graph, shape, parallel)
    return graph


def build(shape):
    graph = BRepGraph()
    graph.Clear()
    graph.Shapes().Add(shape)
    return graph


def ensure_supplement(graph):
    """C++ LayerRegistry().Ensure<BRepGraph_LayerTopoSupplement>() (template): find or register."""
    registry = graph.LayerRegistry()
    layer = registry.FindLayer(BRepGraph_LayerTopoSupplement.GetID_s())
    if layer is None:
        layer = BRepGraph_LayerTopoSupplement()
        registry.RegisterLayer(layer)
    return layer


def is_edge_degenerated(graph, edge_id):
    _ok, degenerated, _closed = BRepGraph_CacheDerivedState.ComputeEdgeProperties_s(graph, edge_id)
    return degenerated


def edge_ids(graph):
    return [BRepGraph_EdgeId(i) for i in range(graph.Topo().Edges().Nb())]


def validate_light(graph):
    return BRepGraph_Validate.Perform_s(graph, BRepGraph_Validate.Options.Lightweight_s()).IsValid()


def add_storage_vertex(storage, point, tolerance):
    vid = storage.AppendVertex()
    vertex = storage.ChangeVertex(vid)
    vertex.Point = point
    vertex.Tolerance = tolerance
    return vid


def add_storage_edge(storage, start_vertex, end_vertex, tolerance=0.0):
    eid = storage.AppendEdge()
    start_ref = storage.AppendVertexRef()
    end_ref = storage.AppendVertexRef()
    storage.ChangeVertexRef(start_ref).ParentEdgeId = eid
    storage.ChangeVertexRef(start_ref).ChildVertexId = start_vertex
    storage.ChangeVertexRef(end_ref).ParentEdgeId = eid
    storage.ChangeVertexRef(end_ref).ChildVertexId = end_vertex
    edge = storage.ChangeEdge(eid)
    edge.StartVertexRefId = start_ref
    edge.EndVertexRefId = end_ref
    edge.Tolerance = tolerance
    return eid


def translation(x, y, z):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return TopLoc_Location(trsf)


def make_inc_edge_with_internal_vertex():
    bb = BRep_Builder()
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0)).Edge()
    vtx = TopoDS_Vertex()
    bb.MakeVertex(vtx, gp_Pnt(5, 0, 0), CONF)
    bb.Add(edge, vtx.Oriented(TopAbs.TopAbs_INTERNAL))
    return edge


def wrap_inc_edge_in_face(edge):
    plane = Geom_Plane(gp_Pln())
    bb = BRep_Builder()
    face = TopoDS_Face()
    bb.MakeFace(face, plane, CONF)
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    bb.Add(wire, edge)
    bb.Add(face, wire)
    return face


def make_inc_face_with_direct_vertex():
    bb = BRep_Builder()
    pts = [gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0), gp_Pnt(10, 10, 0), gp_Pnt(0, 10, 0)]
    verts = []
    for p in pts:
        v = TopoDS_Vertex()
        bb.MakeVertex(v, p, CONF)
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
    face = TopoDS_Face()
    bb.MakeFace(face)
    bb.Add(face, wire)
    loose = TopoDS_Vertex()
    bb.MakeVertex(loose, gp_Pnt(5, 5, 0), CONF)
    bb.Add(face, loose.Oriented(TopAbs.TopAbs_INTERNAL))
    return face


def make_inc_plain_face():
    return BRepBuilderAPI_MakeFace(gp_Pln(), 0.0, 10.0, 0.0, 10.0).Face()


def make_inc_plain_shell():
    bb = BRep_Builder()
    shell = TopoDS_Shell()
    bb.MakeShell(shell)
    bb.Add(shell, make_inc_plain_face())
    return shell


def make_inc_plain_solid():
    bb = BRep_Builder()
    solid = TopoDS_Solid()
    bb.MakeSolid(solid)
    bb.Add(solid, make_inc_plain_shell())
    return solid


def count_direct_children(shape, kind, orientation):
    n = 0
    for child in TopoDS_Iterator(shape, False, False):
        if child.ShapeType() == kind and child.Orientation() == orientation:
            n += 1
    return n


def count_internal_vertices_of_edges(shape):
    n = 0
    for edge in TopExp_Explorer(shape, TopAbs.TopAbs_EDGE):
        for v in TopoDS_Iterator(edge, False):
            if v.ShapeType() == TopAbs.TopAbs_VERTEX and v.Orientation() == TopAbs.TopAbs_INTERNAL:
                n += 1
    return n


def free_edge_graph(n_extra_vertices=0):
    graph = BRepGraph()
    graph.Clear()
    v0 = graph.Editor().Vertices().Add(gp_Pnt(0, 0, 0), 1.0e-7)
    v1 = graph.Editor().Vertices().Add(gp_Pnt(1, 0, 0), 1.0e-7)
    extra = [graph.Editor().Vertices().Add(gp_Pnt(2 + i, 0, 0), 1.0e-7) for i in range(n_extra_vertices)]
    edge = graph.Editor().Edges().Add(v0, v1, None, 0.0, 1.0, 1.0e-7)
    return graph, v0, v1, extra, edge


def edges_of_vertex(graph, vid):
    return list(graph.Topo().Vertices().Edges(vid))


# ---------------------------------------------------------------- entity counts


def test_BRepGraphIncTest_Box_EntityCounts_MatchDefCounts():
    g = populate(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    assert g.Topo().Vertices().Nb() == 8
    assert g.Topo().Edges().Nb() == 12
    assert g.Topo().Faces().Nb() == 6
    assert g.Topo().Shells().Nb() == 1
    assert g.Topo().Solids().Nb() == 1


def test_BRepGraphIncTest_ParityOrientationRejectsInternalExternal():
    with pytest.raises(Standard_ProgramError):
        ParityOrientation(TopAbs.TopAbs_INTERNAL)
    with pytest.raises(Standard_ProgramError):
        ParityOrientation(TopAbs.TopAbs_EXTERNAL)
    # C++ assignment from TopAbs_Orientation == construction in Python
    assert ParityOrientation(TopAbs.TopAbs_FORWARD).IsReversed is False
    assert ParityOrientation(TopAbs.TopAbs_REVERSED).IsReversed is True


def test_BRepGraphIncTest_Cylinder_EntityCounts_MatchDefCounts():
    g = populate(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())
    assert not g.IsEmpty()
    assert g.Topo().Vertices().Nb() == 2
    assert g.Topo().Edges().Nb() == 3
    assert g.Topo().Wires().Nb() == 3
    assert g.Topo().Faces().Nb() == 3
    assert g.Topo().Shells().Nb() == 1
    assert g.Topo().Solids().Nb() == 1


def test_BRepGraphIncTest_Sphere_EntityCounts_MatchDefCounts():
    g = populate(BRepPrimAPI_MakeSphere(8.0).Shape())
    assert not g.IsEmpty()
    assert g.Topo().Vertices().Nb() == 2
    assert g.Topo().Edges().Nb() == 3
    assert g.Topo().Wires().Nb() == 1
    assert g.Topo().Faces().Nb() == 1
    assert g.Topo().Shells().Nb() == 1
    assert g.Topo().Solids().Nb() == 1


def test_BRepGraphIncTest_Storage_AppendAccess_UsesTypedIds():
    # IsRemoved(typed id) on the storage is a C++ template and not bound; the rest is.
    s = BRepGraphInc_Storage()
    vid = s.AppendVertex()
    frid = s.AppendFaceRef()
    srid = s.AppendFaceSurfaceRep()
    assert vid.Index == 0
    assert frid.Index == 0
    assert srid.Index == 0

    s.ChangeVertex(vid).Tolerance = 1.25
    s.ChangeFaceRef(frid).Orientation = TopAbs.TopAbs_REVERSED
    assert s.Vertex(vid).Tolerance == 1.25
    assert s.FaceRef(frid).Orientation.IsReversed is True

    s.ChangeFaceRef(frid).Orientation = TopAbs.TopAbs_FORWARD
    assert s.FaceRef(frid).Orientation.IsReversed is False


def test_BRepGraphIncTest_Storage_GenericIdDispatch_UsesTypedHelpers():
    s = BRepGraphInc_Storage()
    vid = s.AppendVertex()
    frid = s.AppendFaceRef()
    s.AppendFaceSurfaceRep()
    s.ChangeFaceRef(frid).Orientation = TopAbs.TopAbs_REVERSED
    assert s.FaceRef(frid).Orientation.IsReversed is True

    assert s.MarkRemoved(BRepGraph_NodeId(vid))
    assert s.MarkRemovedRef(BRepGraph_RefId(frid))
    assert s.NbActiveVertices() == 0
    assert s.NbActiveFaceRefs() == 0


def test_BRepGraphIncTest_Box_RoundTrip_AreaPreserved():
    shape = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_area(recon) - compute_area(shape)) <= CONF


def test_BRepGraphIncTest_Cylinder_RoundTrip_AreaPreserved():
    shape = BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_area(recon) - compute_area(shape)) <= CONF


def test_BRepGraphIncTest_Sphere_RoundTrip_AreaPreserved():
    shape = BRepPrimAPI_MakeSphere(8.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_area(recon) - compute_area(shape)) <= CONF


def test_BRepGraphIncTest_Box_RoundTrip_VolumePreserved():
    shape = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_volume(recon) - compute_volume(shape)) <= CONF


def test_BRepGraphIncTest_Cylinder_RoundTrip_VolumePreserved():
    shape = BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_volume(recon) - compute_volume(shape)) <= CONF


def _assert_same_sub_shape_counts(a, b):
    for kind in (TopAbs.TopAbs_FACE, TopAbs.TopAbs_WIRE, TopAbs.TopAbs_EDGE, TopAbs.TopAbs_VERTEX):
        assert count_sub_shapes(a, kind) == count_sub_shapes(b, kind)


def test_BRepGraphIncTest_Box_RoundTrip_SubShapeCounts():
    shape = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    _assert_same_sub_shape_counts(recon, shape)


def test_BRepGraphIncTest_Cylinder_RoundTrip_SubShapeCounts():
    shape = BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    _assert_same_sub_shape_counts(recon, shape)


# ---------------------------------------------------------------- relations


def test_BRepGraphIncTest_Box_Relations_EdgesToWires():
    g = populate(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    for eid in edge_ids(g):
        assert count_iterator(g.Topo().Edges().WiresOf(eid)) >= 1, eid.Index


def test_BRepGraphIncTest_Box_Relations_EdgesToFaces():
    g = populate(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    for eid in edge_ids(g):
        if is_edge_degenerated(g, eid):
            continue
        assert count_iterator(g.Topo().Edges().FacesOf(eid)) >= 1, eid.Index


def test_BRepGraphIncTest_Box_ParallelPopulate_SameEntityCounts():
    shape = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    serial = populate(shape, False)
    parallel = populate(shape, True)
    assert not serial.IsEmpty()
    assert not parallel.IsEmpty()
    for view in ("Vertices", "Edges", "Wires", "Faces", "Shells", "Solids"):
        assert getattr(parallel.Topo(), view)().Nb() == getattr(serial.Topo(), view)().Nb()


def test_BRepGraphIncTest_NullShape_NoEntities():
    g = populate(TopoDS_Shape())
    assert g.IsEmpty()
    assert g.Topo().Vertices().Nb() == 0
    assert g.Topo().Edges().Nb() == 0


def test_BRepGraphIncTest_Compound_RoundTrip_SubShapeCounts():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    bb.Add(comp, BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape())

    g = populate(comp)
    assert not g.IsEmpty()
    assert g.Topo().Solids().Nb() == 2
    assert g.Topo().Shells().Nb() == 2
    assert g.Topo().Compounds().Nb() == 1
    assert g.Topo().Faces().Nb() == 12

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_CompoundId.Start_s())
    assert not recon.IsNull()
    assert count_sub_shapes(recon, TopAbs.TopAbs_SOLID) == 2
    assert count_sub_shapes(recon, TopAbs.TopAbs_FACE) == 12


def test_BRepGraphIncTest_Box_CoEdgeCount():
    g = populate(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    total = sum(g.Topo().Edges().Relations(eid).CoEdgeIds.Size() for eid in edge_ids(g))
    assert total == 24


def test_BRepGraphIncTest_Cylinder_HasSeamEdges():
    g = populate(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())
    seam_pairs = 0
    for eid in edge_ids(g):
        coedges = list(g.Topo().Edges().Relations(eid).CoEdgeIds)
        for ce in coedges:
            d = g.Topo().CoEdges().Definition(ce)
            if d.Orientation.IsReversed:  # != TopAbs_FORWARD
                continue
            for other in coedges:
                if other == ce:
                    continue
                od = g.Topo().CoEdges().Definition(other)
                if od.FaceId == d.FaceId and od.Orientation.IsReversed != d.Orientation.IsReversed:
                    seam_pairs += 1
                    break
    assert seam_pairs >= 1


def test_BRepGraphIncTest_Cylinder_SeamEdge_Relations_NoDuplicateFace():
    g = populate(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())
    for eid in edge_ids(g):
        seen = []
        it = g.Topo().Edges().FacesOf(eid)
        while it.More():
            fid = it.CurrentId()
            assert fid not in seen
            seen.append(fid)
            it.Next()


def test_BRepGraphIncTest_Sphere_DegenerateEdges_Preserved():
    shape = BRepPrimAPI_MakeSphere(8.0).Shape()
    g = populate(shape)
    degenerate = 0
    for eid in edge_ids(g):
        if is_edge_degenerated(g, eid):
            degenerate += 1
            assert not g.Topo().Edges().Definition(eid).Curve3DRepId.IsValid()
    assert degenerate >= 2

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_area(recon) - compute_area(shape)) <= CONF


def test_BRepGraphIncTest_Compound_TranslatedChildren_VolumePreserved():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(100.0, 0.0, 0.0))
    bb.Add(comp, BRepBuilderAPI_Transform(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), trsf).Shape())

    orig_vol = compute_volume(comp)
    assert abs(orig_vol - 2000.0) <= CONF

    g = populate(comp)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_CompoundId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_volume(recon) - orig_vol) <= CONF
    assert count_sub_shapes(recon, TopAbs.TopAbs_SOLID) == 2
    assert count_sub_shapes(recon, TopAbs.TopAbs_FACE) == 12


def test_BRepGraphIncTest_Populate_AppliesNormalChildLocationsToDefinitions():
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1.0, 0.0, 0.0)).Edge()
    moved = TopoDS.Edge(edge.Moved(translation(10.0, 0.0, 0.0)))
    bb = BRep_Builder()
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    bb.Add(wire, edge)
    bb.Add(wire, moved)

    g = BRepGraph()
    assert BRepGraphInc_Populate.Perform_s(g, wire, False) != BRepGraphInc_Populate.BuildStatus.Failed
    assert not g.IsEmpty()
    assert g.Topo().Wires().Nb() == 1
    assert g.Topo().Edges().Nb() == 2
    assert g.Topo().Vertices().Nb() == 4

    xs = [g.Topo().Vertices().Definition(BRepGraph_VertexId(i)).Point.X() for i in range(g.Topo().Vertices().Nb())]
    assert abs(min(xs) - 0.0) <= CONF
    assert abs(max(xs) - 11.0) <= CONF

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_WireId.Start_s())
    assert not recon.IsNull()
    assert count_sub_shapes(recon, TopAbs.TopAbs_EDGE) == 2
    assert count_sub_shapes(recon, TopAbs.TopAbs_VERTEX) == 4


def test_BRepGraphIncTest_Populate_AppliesStackedNormalLocationsToDefinitions():
    edge_loc = translation(2.0, 0.0, 0.0)
    wb = BRepBuilderAPI_MakeWire()
    pts = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for i in range(4):
        a = pts[i]
        b = pts[(i + 1) % 4]
        e = BRepBuilderAPI_MakeEdge(gp_Pnt(a[0], a[1], 0.0), gp_Pnt(b[0], b[1], 0.0)).Edge()
        wb.Add(TopoDS.Edge(e.Moved(edge_loc)))
    assert wb.IsDone()

    moved_wire = TopoDS.Wire(wb.Wire().Moved(translation(0.0, 3.0, 0.0)))
    face = BRepBuilderAPI_MakeFace(moved_wire).Face()
    moved_face = TopoDS.Face(face.Moved(translation(0.0, 0.0, 5.0)))

    bb = BRep_Builder()
    shell = TopoDS_Shell()
    bb.MakeShell(shell)
    bb.Add(shell, moved_face)
    moved_shell = TopoDS.Shell(shell.Moved(translation(7.0, 0.0, 0.0)))

    solid = TopoDS_Solid()
    bb.MakeSolid(solid)
    bb.Add(solid, moved_shell)
    moved_solid = TopoDS.Solid(solid.Moved(translation(0.0, 11.0, 0.0)))

    g = BRepGraph()
    assert BRepGraphInc_Populate.Perform_s(g, moved_solid, False) != BRepGraphInc_Populate.BuildStatus.Failed
    assert not g.IsEmpty()
    assert g.Topo().Solids().Nb() == 1
    assert g.Topo().Shells().Nb() == 1
    assert g.Topo().Faces().Nb() == 1
    assert g.Topo().Wires().Nb() == 1
    assert g.Topo().Edges().Nb() == 4

    identity = TopLoc_Location()
    refs = g.Refs()
    for view, id_type in (
        (refs.Shells(), BRepGraph_ShellRefId),
        (refs.Faces(), BRepGraph_FaceRefId),
        (refs.Wires(), BRepGraph_WireRefId),
        (refs.Vertices(), BRepGraph_VertexRefId),
        (refs.Solids(), BRepGraph_SolidRefId),
    ):
        for i in range(view.Nb()):
            assert refs.Gen().LocalLocation(id_type(i)).IsEqual(identity)

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    pnts = [BRep_Tool.Pnt_s(TopoDS.Vertex(v)) for v in TopExp_Explorer(recon, TopAbs.TopAbs_VERTEX)]
    xs = [p.X() for p in pnts]
    ys = [p.Y() for p in pnts]
    zs = [p.Z() for p in pnts]
    assert abs(min(xs) - 9.0) <= CONF
    assert abs(max(xs) - 10.0) <= CONF
    assert abs(min(ys) - 14.0) <= CONF
    assert abs(max(ys) - 15.0) <= CONF
    assert abs(min(zs) - 5.0) <= CONF
    assert abs(max(zs) - 5.0) <= CONF


def test_BRepGraphIncTest_Cylinder_RoundTrip_BRepDump():
    # The C++ test only prints the BRepTools dump diff; the assertion is on the area.
    shape = BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape()
    g = populate(shape)
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert abs(compute_area(recon) - compute_area(shape)) <= CONF


# ---------------------------------------------------------------- supplement layer


def test_BRepGraphIncTest_Populate_RegistersSupplementEdgeVerticesIntoLayer():
    g = BRepGraph()
    supplement = ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, wrap_inc_edge_in_face(make_inc_edge_with_internal_vertex()), False)
    assert not g.IsEmpty()
    assert g.Topo().Edges().Nb() > 0
    eid = BRepGraph_EdgeId.Start_s()

    attached = supplement.AttachedTo(BRepGraph_NodeId(eid))
    assert attached.Size() == 1
    entry = supplement.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == BRepGraph_LayerTopoSupplement.AttachmentKind.EdgeInternalVertex
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_VERTEX
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL


def test_BRepGraphIncTest_Reconstruct_ReplaysSupplementEdgeVerticesFromLayer():
    g = BRepGraph()
    ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, wrap_inc_edge_in_face(make_inc_edge_with_internal_vertex()), False)
    assert not g.IsEmpty()
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_FaceId.Start_s())
    assert not recon.IsNull()
    assert count_internal_vertices_of_edges(recon) > 0


def test_BRepGraphIncTest_Reconstruct_WithoutSupplementLayer_DropsSupplementEdgeVerticesButKeepsCore():
    g = populate(wrap_inc_edge_in_face(make_inc_edge_with_internal_vertex()))
    assert not g.IsEmpty()
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_FaceId.Start_s())
    assert not recon.IsNull()

    edges = boundaries = internal = 0
    for edge in TopExp_Explorer(recon, TopAbs.TopAbs_EDGE):
        edges += 1
        for v in TopoDS_Iterator(edge, False):
            if v.ShapeType() != TopAbs.TopAbs_VERTEX:
                continue
            if v.Orientation() in (TopAbs.TopAbs_FORWARD, TopAbs.TopAbs_REVERSED):
                boundaries += 1
            elif v.Orientation() == TopAbs.TopAbs_INTERNAL:
                internal += 1
    assert edges == 1
    assert boundaries == 2
    assert internal == 0


def test_BRepGraphIncTest_Reconstruct_EdgeNode_ReplaysSupplementEdgeVerticesFromLayer():
    g = BRepGraph()
    ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, make_inc_edge_with_internal_vertex(), False)
    assert not g.IsEmpty()
    assert g.Topo().Edges().Nb() > 0
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_EdgeId.Start_s())
    assert not recon.IsNull()
    internal = sum(
        1
        for v in TopoDS_Iterator(recon, False)
        if v.ShapeType() == TopAbs.TopAbs_VERTEX and v.Orientation() == TopAbs.TopAbs_INTERNAL
    )
    assert internal == 1


def test_BRepGraphIncTest_Reconstruct_WireNode_ReplaysSupplementEdgeVerticesFromLayer():
    g = BRepGraph()
    ensure_supplement(g)
    bb = BRep_Builder()
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    bb.Add(wire, make_inc_edge_with_internal_vertex())
    BRepGraphInc_Populate.Perform_s(g, wire, False)
    assert not g.IsEmpty()
    assert g.Topo().Wires().Nb() > 0
    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_WireId.Start_s())
    assert not recon.IsNull()
    assert count_internal_vertices_of_edges(recon) == 1


def test_BRepGraphIncTest_Reconstruct_FaceNode_ReplaysSupplementFaceVerticesFromLayer():
    g = BRepGraph()
    supplement = ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, make_inc_face_with_direct_vertex(), False)
    assert not g.IsEmpty()
    assert g.Topo().Faces().Nb() > 0

    attached = supplement.AttachedTo(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    assert attached.Size() == 1
    entry = supplement.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == BRepGraph_LayerTopoSupplement.AttachmentKind.FaceDirectVertex
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_VERTEX
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_FaceId.Start_s())
    assert not recon.IsNull()
    wires = internal = 0
    for child in TopoDS_Iterator(recon, False, False):
        if child.ShapeType() == TopAbs.TopAbs_WIRE:
            wires += 1
        elif child.ShapeType() == TopAbs.TopAbs_VERTEX and child.Orientation() == TopAbs.TopAbs_INTERNAL:
            internal += 1
    assert wires == 1
    assert internal == 1


def test_BRepGraphIncTest_Populate_ShellRoutesInternalFaceToSupplement():
    bb = BRep_Builder()
    shell = TopoDS_Shell()
    bb.MakeShell(shell)
    bb.Add(shell, make_inc_plain_face().Oriented(TopAbs.TopAbs_FORWARD))
    bb.Add(shell, make_inc_plain_face().Oriented(TopAbs.TopAbs_INTERNAL))

    g = BRepGraph()
    supplement = ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, shell, False)
    assert g.Topo().Shells().Nb() == 1
    assert g.Topo().Shells().Relations(BRepGraph_ShellId.Start_s()).FaceRefIds.Size() == 1

    attached = supplement.AttachedTo(BRepGraph_NodeId(BRepGraph_ShellId.Start_s()))
    assert attached.Size() == 1
    entry = supplement.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == BRepGraph_LayerTopoSupplement.AttachmentKind.ShellAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_FACE
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_ShellId.Start_s())
    assert not recon.IsNull()
    assert count_direct_children(recon, TopAbs.TopAbs_FACE, TopAbs.TopAbs_FORWARD) == 1
    assert count_direct_children(recon, TopAbs.TopAbs_FACE, TopAbs.TopAbs_INTERNAL) == 1


def test_BRepGraphIncTest_Populate_SolidRoutesInternalShellToSupplement():
    bb = BRep_Builder()
    solid = TopoDS_Solid()
    bb.MakeSolid(solid)
    bb.Add(solid, make_inc_plain_shell().Oriented(TopAbs.TopAbs_FORWARD))
    bb.Add(solid, make_inc_plain_shell().Oriented(TopAbs.TopAbs_INTERNAL))

    g = BRepGraph()
    supplement = ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, solid, False)
    assert g.Topo().Solids().Nb() == 1
    assert g.Topo().Solids().Relations(BRepGraph_SolidId.Start_s()).ShellRefIds.Size() == 1

    attached = supplement.AttachedTo(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    assert attached.Size() == 1
    entry = supplement.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == BRepGraph_LayerTopoSupplement.AttachmentKind.SolidAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_SHELL
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    assert count_direct_children(recon, TopAbs.TopAbs_SHELL, TopAbs.TopAbs_FORWARD) == 1
    assert count_direct_children(recon, TopAbs.TopAbs_SHELL, TopAbs.TopAbs_INTERNAL) == 1


def test_BRepGraphIncTest_Populate_CompSolidRoutesInternalSolidToSupplement():
    bb = BRep_Builder()
    cs = TopoDS_CompSolid()
    bb.MakeCompSolid(cs)
    bb.Add(cs, make_inc_plain_solid().Oriented(TopAbs.TopAbs_FORWARD))
    bb.Add(cs, make_inc_plain_solid().Oriented(TopAbs.TopAbs_INTERNAL))

    g = BRepGraph()
    supplement = ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, cs, False)
    assert g.Topo().CompSolids().Nb() == 1
    assert g.Topo().CompSolids().Relations(BRepGraph_CompSolidId.Start_s()).SolidRefIds.Size() == 1

    attached = supplement.AttachedTo(BRepGraph_NodeId(BRepGraph_CompSolidId.Start_s()))
    assert attached.Size() == 1
    entry = supplement.FindByUid(attached.First())
    assert entry is not None
    assert entry.Kind == BRepGraph_LayerTopoSupplement.AttachmentKind.CompSolidAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_SOLID
    assert entry.Shape.Orientation() == TopAbs.TopAbs_INTERNAL

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_CompSolidId.Start_s())
    assert not recon.IsNull()
    assert count_direct_children(recon, TopAbs.TopAbs_SOLID, TopAbs.TopAbs_FORWARD) == 1
    assert count_direct_children(recon, TopAbs.TopAbs_SOLID, TopAbs.TopAbs_INTERNAL) == 1


def test_BRepGraphIncTest_Populate_SolidInvalidOrderChildRoutesToSupplement():
    bb = BRep_Builder()
    solid = TopoDS_Solid()
    bb.MakeSolid(solid)
    bb.Add(solid, make_inc_edge_with_internal_vertex().Oriented(TopAbs.TopAbs_FORWARD))

    g = BRepGraph()
    supplement = ensure_supplement(g)
    BRepGraphInc_Populate.Perform_s(g, solid, False)
    assert g.Topo().Solids().Nb() == 1
    assert g.Topo().Solids().Relations(BRepGraph_SolidId.Start_s()).ShellRefIds.Size() == 0
    solid_node = BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    assert supplement.AttachedTo(solid_node).Size() == 1
    entry = supplement.FindByUid(supplement.AttachedTo(solid_node).First())
    assert entry is not None
    assert entry.Kind == BRepGraph_LayerTopoSupplement.AttachmentKind.SolidAuxShape
    assert entry.Shape.ShapeType() == TopAbs.TopAbs_EDGE

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert count_direct_children(recon, TopAbs.TopAbs_EDGE, TopAbs.TopAbs_FORWARD) == 1


# ---------------------------------------------------------------- validate


def test_BRepGraphIncTest_Relations_Validate_CompoundWithAtomicWire():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    me = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0))
    assert me.IsDone()
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    bb.Add(wire, me.Edge())
    bb.Add(comp, wire)

    g = populate(comp)
    assert not g.IsEmpty()
    assert g.Topo().Compounds().Nb() == 1
    assert g.Topo().Wires().Nb() >= 1
    assert validate_light(g)


def test_BRepGraphIncTest_Relations_Validate_CompoundWithAtomicEdge():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    me = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(5, 0, 0))
    assert me.IsDone()
    bb.Add(comp, me.Edge())

    g = populate(comp)
    assert not g.IsEmpty()
    assert g.Topo().Compounds().Nb() == 1
    assert g.Topo().Edges().Nb() >= 1
    assert validate_light(g)


def test_BRepGraphIncTest_Relations_Validate_CompoundWithAtomicVertex():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    vtx = TopoDS_Vertex()
    bb.MakeVertex(vtx, gp_Pnt(1, 2, 3), CONF)
    bb.Add(comp, vtx)

    g = populate(comp)
    assert not g.IsEmpty()
    assert g.Topo().Compounds().Nb() == 1
    assert g.Topo().Vertices().Nb() >= 1
    assert validate_light(g)


def test_BRepGraphIncTest_Relations_CoEdgeToWire_IsPopulated():
    g = populate(BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape())
    n = g.Topo().CoEdges().Nb()
    assert n > 0
    for i in range(n):
        assert g.Topo().CoEdges().Definition(BRepGraph_CoEdgeId(i)).ParentWireId.IsValid(), i
    assert validate_light(g)


def test_BRepGraphIncTest_Relations_CompSolid_IncomingMaintained_AfterBuild():
    bb = BRep_Builder()
    cs = TopoDS_CompSolid()
    bb.MakeCompSolid(cs)
    bb.Add(cs, BRepPrimAPI_MakeBox(4.0, 4.0, 4.0).Shape())
    bb.Add(cs, BRepPrimAPI_MakeBox(2.0, 2.0, 2.0).Shape())

    g = populate(cs)
    assert not g.IsEmpty()
    assert g.Topo().CompSolids().Nb() == 1
    assert g.Topo().Solids().Nb() >= 2
    for i in range(g.Topo().Solids().Nb()):
        assert g.Topo().Solids().Relations(BRepGraph_SolidId(i)).ParentSolidRefIds.Size() == 1, i
    assert validate_light(g)


def test_BRepGraphIncTest_Relations_CompSolid_IncomingMaintained_AfterBuildDelta():
    bb = BRep_Builder()
    cs = TopoDS_CompSolid()
    bb.MakeCompSolid(cs)
    bb.Add(cs, BRepPrimAPI_MakeBox(3.0, 3.0, 3.0).Shape())

    g = populate(cs)
    assert not g.IsEmpty()
    assert g.Topo().CompSolids().Nb() == 1
    assert g.Topo().Solids().Nb() >= 1
    assert validate_light(g)
    assert g.Topo().Solids().Relations(BRepGraph_SolidId.Start_s()).ParentSolidRefIds.Size() >= 1


def test_BRepGraphIncTest_Relations_Validate_Box_FullConsistency():
    g = populate(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    assert validate_light(g)


def test_BRepGraphIncTest_Relations_Validate_Compound_FullConsistency():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape())
    bb.Add(comp, BRepPrimAPI_MakeBox(3.0, 3.0, 3.0).Shape())
    g = populate(comp)
    assert not g.IsEmpty()
    assert validate_light(g)


# ---------------------------------------------------------------- editor mutations


def test_BRepGraphIncTest_Relations_AfterEditorMutations_StaysConsistent():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    bb.Add(comp, BRepPrimAPI_MakeCylinder(5.0, 12.0).Shape())

    g = build(comp)
    assert not g.IsEmpty()
    assert g.ValidateRelations()

    it = BRepGraph_FaceIterator(g)
    while it.More():
        fid = it.CurrentId()
        wire_refs = g.Refs().Wires().IdsOf(fid)
        if wire_refs.IsEmpty():
            it.Next()
            continue
        assert g.Editor().Faces().RemoveWire(fid, wire_refs.Value(0))
        break
    assert g.ValidateRelations()

    face_refs = g.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert face_refs.Size() >= 1
    assert g.Editor().Shells().RemoveFace(BRepGraph_ShellId.Start_s(), face_refs.Value(0))
    assert g.ValidateRelations()

    shell_refs = g.Refs().Shells().IdsOf(BRepGraph_SolidId.Start_s())
    assert shell_refs.Size() >= 1
    assert g.Editor().Solids().RemoveShell(BRepGraph_SolidId.Start_s(), shell_refs.Value(0))
    assert g.ValidateRelations()

    assert g.Editor().ValidateMutationBoundary()


def test_BRepGraphIncTest_Relations_BulkBuild_TwiceProducesEqualState():
    shape = BRepPrimAPI_MakeBox(7.0, 11.0, 13.0).Shape()
    ga = populate(shape)
    gb = populate(shape)
    assert not ga.IsEmpty()
    assert not gb.IsEmpty()
    assert ga.Topo().Edges().Nb() == gb.Topo().Edges().Nb()

    for eid in edge_ids(ga):
        for of in ("WiresOf", "FacesOf"):
            ia = getattr(ga.Topo().Edges(), of)(eid)
            ib = getattr(gb.Topo().Edges(), of)(eid)
            while ia.More() and ib.More():
                assert ia.CurrentId() == ib.CurrentId()
                ia.Next()
                ib.Next()
            assert ia.More() == ib.More()


def test_BRepGraphIncTest_Relations_EdgeOpsAdd_BindsStartEndVertices():
    g, v0, v1, _extra, edge = free_edge_graph()
    assert v0.IsValid()
    assert v1.IsValid()
    assert edge.IsValid()
    assert edge in edges_of_vertex(g, v0)
    assert edge in edges_of_vertex(g, v1)
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_RemoveEdge_UnbindsStartEndVertices():
    g, v0, v1, _extra, edge = free_edge_graph()
    assert edge.IsValid()
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(edge))
    assert edge not in edges_of_vertex(g, v0)
    assert edge not in edges_of_vertex(g, v1)
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetRefChildVertexId_RebindsVertexToEdges():
    g, v0, _v1, extra, edge = free_edge_graph(1)
    v2 = extra[0]
    assert edge.IsValid()
    start_ref = g.Topo().Edges().Definition(edge).StartVertexRefId
    g.Editor().Vertices().SetRefChildVertexId(start_ref, v2)
    assert edge not in edges_of_vertex(g, v0)
    assert edge in edges_of_vertex(g, v2)
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_BoxThroughCompact_StaysConsistent():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    fid = BRepGraph_FaceId.Start_s()
    assert g.Editor().Faces().RemoveWire(fid, g.Refs().Wires().IdsOf(fid).Value(0))
    assert g.ValidateRelations()
    BRepGraph_Compact.Perform_s(g)
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetRefChildWireId_RebindsWireToFaces():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    face0 = BRepGraph_FaceId.Start_s()
    face1 = BRepGraph_FaceId(1)
    assert face1.IsValid(g.Topo().Faces().Nb())

    wire_ref0 = g.Refs().Wires().IdsOf(face0).Value(0)
    old_wire = g.Refs().Wires().Entry(wire_ref0).ChildWireId
    new_wire = g.Refs().Wires().Entry(g.Refs().Wires().IdsOf(face1).Value(0)).ChildWireId
    assert old_wire != new_wire

    g.Editor().Wires().SetRefChildWireId(wire_ref0, new_wire)

    old_refs = g.Topo().Wires().Relations(old_wire).ParentWireRefIds
    new_refs = g.Topo().Wires().Relations(new_wire).ParentWireRefIds
    old_faces = list(BRepGraph_FacesOfWire(g, old_refs))
    new_faces = list(BRepGraph_FacesOfWire(g, new_refs))
    assert face0 not in old_faces
    assert face0 in new_faces
    for ce in g.Topo().Wires().Relations(old_wire).CoEdgeIds:
        d = g.Topo().CoEdges().Definition(ce)
        assert d.FaceId != face0
        for fid in g.Topo().Edges().FacesOf(d.ChildEdgeId):
            assert fid != face0
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetRefFaceId_RebindsFaceToShells():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    ref0 = g.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s()).Value(0)
    old_face = g.Refs().Faces().Entry(ref0).ChildFaceId
    new_face = BRepGraph_FaceId(1)
    assert old_face != new_face
    g.Editor().Faces().SetRefFaceId(ref0, new_face)
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetRefChildShellId_RebindsShellToSolids():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert g.Topo().Shells().Nb() >= 1
    ref0 = g.Refs().Shells().IdsOf(BRepGraph_SolidId.Start_s()).Value(0)
    shell = g.Refs().Shells().Entry(ref0).ChildShellId
    g.Editor().Shells().SetRefChildShellId(ref0, shell)
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetChildEdgeIdOnCoEdge_RebindsEdgeToCoEdges():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert g.Topo().CoEdges().Nb() >= 2
    coedge = BRepGraph_CoEdgeId.Start_s()
    old_edge = g.Topo().CoEdges().Definition(coedge).ChildEdgeId
    new_edge = next(e for e in edge_ids(g) if e != old_edge)

    g.Editor().CoEdges().SetChildEdgeId(coedge, new_edge)

    assert coedge not in list(g.Topo().Edges().CoEdges(old_edge))
    assert coedge in list(g.Topo().Edges().CoEdges(new_edge))
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetFaceIdOnCoEdge_LastBondCheck():
    g = build(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    seam_edge = seam_face = seam_coedge = None
    for eid in edge_ids(g):
        ces = list(g.Topo().Edges().CoEdges(eid))
        if len(ces) < 2:
            continue
        seen = {}
        for ce in ces:
            d = g.Topo().CoEdges().Definition(ce)
            if not d.FaceId.IsValid():
                continue
            if d.FaceId.Index in seen:
                seam_edge, seam_face, seam_coedge = eid, d.FaceId, ce
                break
            seen[d.FaceId.Index] = ce
        if seam_edge is not None:
            break
    assert seam_edge is not None, "cylinder must have a seam edge"

    g.Editor().CoEdges().SetFaceId(seam_coedge, BRepGraph_FaceId())
    assert seam_face in list(g.Topo().Edges().FacesOf(seam_edge))
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetFaceIdOnCoEdge_OnlyBondUnbinds():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    coedge = BRepGraph_CoEdgeId.Start_s()
    d = g.Topo().CoEdges().Definition(coedge)
    edge = d.ChildEdgeId
    old_face = d.FaceId
    g.Editor().CoEdges().SetFaceId(coedge, BRepGraph_FaceId())
    for fid in g.Topo().Edges().FacesOf(edge):
        assert fid != old_face
    assert g.ValidateRelations()


def _single_coedge_wire(g):
    v0 = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    v1 = g.Editor().Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    edge = g.Editor().Edges().Add(v0, v1, None, 0.0, 1.0, 1.0e-7)
    assert edge.IsValid()
    coedge = g.Editor().CoEdges().Add(edge, ParityOrientation(TopAbs.TopAbs_FORWARD))
    assert coedge.IsValid()
    arr = NCollection_Array1[BRepGraph_CoEdgeId](0, 0)
    arr.SetValue(0, coedge)
    wire = g.Editor().Wires().Add(arr)
    assert wire.IsValid()
    return edge, coedge, wire


def test_BRepGraphIncTest_Relations_RemoveWireFromSharedWireClearsDetachedFaceContext():
    g = BRepGraph()
    g.Clear()
    edge, coedge, wire = _single_coedge_wire(g)
    inner = NCollection_Array1[BRepGraph_WireId]()
    plane = Geom_Plane(gp_Pln())
    face0 = g.Editor().Faces().Add(plane, wire, inner, 1.0e-7)
    face1 = g.Editor().Faces().Add(plane, wire, inner, 1.0e-7)
    assert face0.IsValid()
    assert face1.IsValid()

    g.Editor().CoEdges().SetFaceId(coedge, face0)
    g.Editor().CoEdges().SetPCurve(coedge, Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 0.0, 1.0)
    assert g.Topo().CoEdges().Definition(coedge).Curve2DRepId.IsValid()
    nb_active = g.Topo().Geometry().NbActiveCoEdgeCurves2D()
    assert g.ValidateRelations()

    wire_ref = g.Topo().Faces().Relations(face0).WireRefIds.First()
    assert wire_ref.IsValid()
    assert g.Editor().Faces().RemoveWire(face0, wire_ref)

    assert not g.Topo().CoEdges().Definition(coedge).FaceId.IsValid()
    assert not g.Topo().CoEdges().Definition(coedge).Curve2DRepId.IsValid()
    assert g.Topo().Geometry().NbActiveCoEdgeCurves2D() == nb_active - 1
    for fid in g.Topo().Edges().FacesOf(edge):
        assert fid != face0
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_ValidateRejectsLivePCurveWithoutFaceContext():
    g = BRepGraph()
    g.Clear()
    _edge, coedge, wire = _single_coedge_wire(g)
    inner = NCollection_Array1[BRepGraph_WireId]()
    face = g.Editor().Faces().Add(Geom_Plane(gp_Pln()), wire, inner, 1.0e-7)
    assert face.IsValid()

    g.Editor().CoEdges().SetFaceId(coedge, face)
    g.Editor().CoEdges().SetPCurve(coedge, Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 0.0, 1.0)
    assert g.Topo().CoEdges().Definition(coedge).Curve2DRepId.IsValid()
    assert g.ValidateRelations()

    guard = g.Editor().CoEdges().Mut(coedge)
    guard.Internal().FaceId = BRepGraph_FaceId()
    del guard  # C++ scope end
    assert not g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetEndVertexRefId_RebindsVertexToEdges():
    g, v0, v1, extra, edge = free_edge_graph(1)
    v2 = extra[0]
    other = g.Editor().Edges().Add(v0, v2, None, 0.0, 1.0, 1.0e-7)
    assert edge.IsValid()
    assert other.IsValid()

    v2_ref = g.Topo().Edges().Definition(other).EndVertexRefId
    old_end_ref = g.Topo().Edges().Definition(edge).EndVertexRefId
    g.Editor().Edges().SetEndVertexRefId(edge, v2_ref)

    assert edge in edges_of_vertex(g, v1)
    assert edge not in edges_of_vertex(g, v2)
    assert g.Topo().Edges().Definition(edge).EndVertexRefId == old_end_ref
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetterIdempotency_NoOp():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    coedge = BRepGraph_CoEdgeId.Start_s()
    d = g.Topo().CoEdges().Definition(coedge)
    g.Editor().CoEdges().SetChildEdgeId(coedge, d.ChildEdgeId)
    g.Editor().CoEdges().SetFaceId(coedge, d.FaceId)
    assert g.ValidateRelations()

    vref = g.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s()).StartVertexRefId
    if vref.IsValid():
        v = g.Refs().Vertices().Entry(vref).ChildVertexId
        g.Editor().Vertices().SetRefChildVertexId(vref, v)
        assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_RebindVertexSkipsRemovedParentEdge():
    s = BRepGraphInc_Storage()
    old_v = s.AppendVertex()
    end_v = s.AppendVertex()
    new_v = s.AppendVertex()
    edge = s.AppendEdge()
    start_ref = s.AppendVertexRef()
    end_ref = s.AppendVertexRef()
    s.ChangeVertexRef(start_ref).ParentEdgeId = edge
    s.ChangeVertexRef(start_ref).ChildVertexId = old_v
    s.ChangeVertexRef(end_ref).ParentEdgeId = edge
    s.ChangeVertexRef(end_ref).ChildVertexId = end_v
    s.ChangeEdge(edge).StartVertexRefId = start_ref
    s.ChangeEdge(edge).EndVertexRefId = end_ref
    s.RebuildDerivedRelations()

    assert s.VertexRelations(old_v).EdgeIds.Size() == 1
    assert s.VertexRelations(new_v).EdgeIds.Size() == 0

    # C++ SetRemoved(anEdge, true) is a template (not bound); MarkRemoved(NodeId) sets the same flag.
    assert s.MarkRemoved(BRepGraph_NodeId(edge))
    s.RebindVertexEdge(old_v, new_v, edge, BRepGraph_VertexRefId())
    s.RebindVertexRef(start_ref, old_v, new_v)

    assert s.VertexRef(start_ref).ChildVertexId == old_v
    assert s.VertexRelations(old_v).EdgeIds.Size() == 1
    assert s.VertexRelations(new_v).EdgeIds.Size() == 0


def test_BRepGraphIncTest_CanonicalizeWireCoEdgeOrderStatus_ReordersExactConnectedWire():
    s = BRepGraphInc_Storage()
    wire = s.AppendWire()
    va = add_storage_vertex(s, gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    vb = add_storage_vertex(s, gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    vc = add_storage_vertex(s, gp_Pnt(2.0, 0.0, 0.0), 1.0e-7)
    e_bc = add_storage_edge(s, vb, vc)
    e_ab = add_storage_edge(s, va, vb)
    fwd = ParityOrientation(TopAbs.TopAbs_FORWARD)
    ce_bc = s.CreateCoEdgeUse(wire, e_bc, BRepGraph_FaceId(), fwd)
    ce_ab = s.CreateCoEdgeUse(wire, e_ab, BRepGraph_FaceId(), fwd)

    assert not s.ValidateWireCoEdgeOrder(wire)
    assert s.CanonicalizeWireCoEdgeOrderStatus(wire) == BRepGraphInc_Storage.WireCoEdgeOrderStatus.Reordered
    ces = s.WireRelations(wire).CoEdgeIds
    assert ces.Size() == 2
    assert ces.Value(0) == ce_ab
    assert ces.Value(1) == ce_bc
    assert s.ValidateWireCoEdgeOrder(wire)


def test_BRepGraphIncTest_CanonicalizeWireCoEdgeOrderStatus_UsesVertexTolerance():
    s = BRepGraphInc_Storage()
    wire = s.AppendWire()
    va = add_storage_vertex(s, gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    vb = add_storage_vertex(s, gp_Pnt(1.0, 0.0, 0.0), 1.0e-2)
    vc = add_storage_vertex(s, gp_Pnt(1.005, 0.0, 0.0), 1.0e-2)
    vd = add_storage_vertex(s, gp_Pnt(2.0, 0.0, 0.0), 1.0e-7)
    e_ab = add_storage_edge(s, va, vb)
    e_cd = add_storage_edge(s, vc, vd)
    fwd = ParityOrientation(TopAbs.TopAbs_FORWARD)
    ce_ab = s.CreateCoEdgeUse(wire, e_ab, BRepGraph_FaceId(), fwd)
    ce_cd = s.CreateCoEdgeUse(wire, e_cd, BRepGraph_FaceId(), fwd)

    assert not s.ValidateWireCoEdgeOrder(wire)
    assert (
        s.CanonicalizeWireCoEdgeOrderStatus(wire)
        == BRepGraphInc_Storage.WireCoEdgeOrderStatus.ToleranceOrdered
    )
    ces = s.WireRelations(wire).CoEdgeIds
    assert ces.Size() == 2
    assert ces.Value(0) == ce_ab
    assert ces.Value(1) == ce_cd


def test_BRepGraphIncTest_CanonicalizeWireCoEdgeOrderStatus_PartialPreservesDisconnectedRuns():
    s = BRepGraphInc_Storage()
    wire = s.AppendWire()
    va = add_storage_vertex(s, gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    vb = add_storage_vertex(s, gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    vc = add_storage_vertex(s, gp_Pnt(2.0, 0.0, 0.0), 1.0e-7)
    vx = add_storage_vertex(s, gp_Pnt(10.0, 0.0, 0.0), 1.0e-7)
    vy = add_storage_vertex(s, gp_Pnt(11.0, 0.0, 0.0), 1.0e-7)
    e_bc = add_storage_edge(s, vb, vc)
    e_xy = add_storage_edge(s, vx, vy)
    e_ab = add_storage_edge(s, va, vb)
    fwd = ParityOrientation(TopAbs.TopAbs_FORWARD)
    ce_bc = s.CreateCoEdgeUse(wire, e_bc, BRepGraph_FaceId(), fwd)
    ce_xy = s.CreateCoEdgeUse(wire, e_xy, BRepGraph_FaceId(), fwd)
    ce_ab = s.CreateCoEdgeUse(wire, e_ab, BRepGraph_FaceId(), fwd)

    assert s.CanonicalizeWireCoEdgeOrderStatus(wire) == BRepGraphInc_Storage.WireCoEdgeOrderStatus.Partial
    ces = s.WireRelations(wire).CoEdgeIds
    assert ces.Size() == 3
    assert ces.Value(0) == ce_ab
    assert ces.Value(1) == ce_bc
    assert ces.Value(2) == ce_xy


# ---------------------------------------------------------------- cleanup removed references


def test_BRepGraphIncTest_CleanupRemovedRefs_AfterRemoveFace_ValidatePasses():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    fid = BRepGraph_FaceId.Start_s()
    assert fid.IsValid(g.Topo().Faces().Nb())
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(fid))
    g.Editor().Gen().CleanupRemovedReferences()
    assert g.ValidateRelations()


def test_BRepGraphIncTest_CleanupRemovedRefs_AfterRemoveFace_RemovesCoEdgePCurves():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    fid = BRepGraph_FaceId.Start_s()
    face_coedges = []
    pcurves = []
    for i in range(g.Topo().CoEdges().Nb()):
        ce = BRepGraph_CoEdgeId(i)
        d = g.Topo().CoEdges().Definition(ce)
        if d.FaceId == fid and d.Curve2DRepId.IsValid():
            face_coedges.append(ce)
            pcurves.append(d.Curve2DRepId)
    assert len(pcurves) > 0
    nb_active = g.Topo().Geometry().NbActiveCoEdgeCurves2D()

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(fid))
    g.Editor().Gen().CleanupRemovedReferences()

    for ce in face_coedges:
        assert not g.Topo().CoEdges().Definition(ce).Curve2DRepId.IsValid()
    for pc in pcurves:
        assert BRepGraph_RepId(pc).IsRemoved(g)
    assert g.Topo().Geometry().NbActiveCoEdgeCurves2D() == nb_active - len(pcurves)
    assert g.ValidateRelations()


def test_BRepGraphIncTest_CleanupRemovedRefs_AfterRemoveWire_ValidatePasses():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    outer = BRepGraph_Tool.Face.OuterWire_s(g, BRepGraph_FaceId.Start_s())
    assert outer.IsValid()
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(outer))
    g.Editor().Gen().CleanupRemovedReferences()
    result = BRepGraph_Validate.Perform_s(g)
    assert g.ValidateRelations()
    assert result.IsValid()


def test_BRepGraphIncTest_CleanupRemovedRefs_AfterRemoveVertex_ValidatePasses():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    eid = BRepGraph_EdgeId.Start_s()
    start_v = BRepGraph_Tool.Edge.StartVertexId_s(g, eid)
    assert start_v.IsValid()
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(g.Refs().Vertices().Entry(start_v).ChildVertexId))
    g.Editor().Gen().CleanupRemovedReferences()
    assert g.ValidateRelations()
    assert not g.Topo().Edges().Definition(eid).StartVertexRefId.IsValid()


def test_BRepGraphIncTest_CleanupRemovedRefs_AfterRemoveMultiple_ValidatePasses():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_EdgeId.Start_s()))
    g.Editor().Gen().CleanupRemovedReferences()
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraphIncTest_Storage_MarkRemoved_UnbindsTShapeAndOriginal():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    fid = BRepGraph_FaceId.Start_s()
    assert fid.IsValid(g.Topo().Faces().Nb())
    assert g.Shapes().HasOriginal(BRepGraph_NodeId(fid))
    orig = g.Shapes().Original(BRepGraph_NodeId(fid))
    assert not orig.IsNull()
    assert g.Shapes().HasNode(orig)

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(fid))
    assert not g.Shapes().HasNode(orig)
    assert not g.Shapes().HasOriginal(BRepGraph_NodeId(fid))


def test_BRepGraphIncTest_Storage_MarkRemoved_EraseLast_EmptyStore():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    old_nb = g.Topo().Geometry().NbFaceSurfaces()
    assert old_nb != 0
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    BRepGraph_Compact.Perform_s(g)
    new_nb = g.Topo().Geometry().NbFaceSurfaces()
    assert new_nb < old_nb
    assert g.ValidateRelations()

    g.Editor().Faces().SetSurface(BRepGraph_FaceId.Start_s(), Geom_Plane(gp_Pln()))
    assert g.Topo().Geometry().NbFaceSurfaces() == new_nb


def test_BRepGraphIncTest_Storage_MarkRemoved_UnbindsTShapeToNodeId():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    solid = g.Shapes().Shape(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    assert not solid.IsNull()
    old_node = g.Shapes().FindNode(solid)
    assert old_node.IsValid()
    assert old_node.NodeKind == BRepGraph_NodeId.Kind.Solid

    g.Editor().Gen().RemoveNode(old_node)
    BRepGraph_Compact.Perform_s(g)
    assert not g.Shapes().FindNode(solid).IsValid()
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Storage_RebuildDerivedRelations_RecountsRefStoreNbActive():
    s = BRepGraphInc_Storage()
    v1 = s.AppendVertex()
    v2 = s.AppendVertex()
    edge = s.AppendEdge()
    start_ref = s.AppendVertexRef()
    end_ref = s.AppendVertexRef()
    s.ChangeVertexRef(start_ref).ParentEdgeId = edge
    s.ChangeVertexRef(start_ref).ChildVertexId = v1
    s.ChangeVertexRef(end_ref).ParentEdgeId = edge
    s.ChangeVertexRef(end_ref).ChildVertexId = v2
    s.ChangeEdge(edge).StartVertexRefId = start_ref
    s.ChangeEdge(edge).EndVertexRefId = end_ref
    s.RebuildDerivedRelations()

    old_active = s.NbActiveVertexRefs()
    assert old_active > 0
    assert s.MarkRemovedRef(BRepGraph_RefId(start_ref))
    assert s.NbActiveVertexRefs() == old_active - 1
    s.RebuildDerivedRelations()
    assert s.NbActiveVertexRefs() == old_active - 1


def test_BRepGraphIncTest_Relations_BuildDelta_ExistingEdgeNewCoedge_GetsNewFace():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())

    g = build(comp)
    assert g.Topo().Solids().Nb() == 2

    opts = BRepGraph_Deduplicate.Options()
    opts.MergeEntitiesWhenSafe = True
    BRepGraph_Deduplicate.Perform_s(g, opts)
    BRepGraph_Compact.Perform_s(g)

    for eid in edge_ids(g):
        if eid.IsRemoved(g):
            continue
        assert g.Topo().Edges().NbFaces(eid) != 0
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SeamEdge_NoDuplicateEdgeToWireEntries():
    g = populate(BRepPrimAPI_MakeSphere(8.0).Shape())
    for eid in edge_ids(g):
        seen = []
        it = g.Topo().Edges().WiresOf(eid)
        while it.More():
            wid = it.CurrentId()
            assert wid not in seen
            seen.append(wid)
            it.Next()
    assert validate_light(g)


def test_BRepGraphIncTest_Relations_SetChildRefChildNodeId_CrossKindRebinds():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(2.0, 2.0, 2.0).Shape())

    g = build(comp)
    assert g.Topo().Compounds().Nb() >= 1
    assert g.Topo().Solids().Nb() >= 1
    assert g.Topo().Shells().Nb() >= 1

    comp0 = BRepGraph_CompoundId.Start_s()
    child_refs = g.Topo().Compounds().Relations(comp0).ChildRefIds
    assert child_refs.Size() >= 1
    child_ref = child_refs.Value(0)
    old_child = g.Refs().Children().Entry(child_ref).ChildNodeId
    assert old_child.NodeKind == BRepGraph_NodeId.Kind.Solid

    shell = BRepGraph_ShellId.Start_s()
    g.Editor().Gen().SetChildRefChildNodeId(child_ref, BRepGraph_NodeId(shell))

    old_solid = BRepGraph_SolidId.FromNodeId_s(old_child)
    # Keep the ref vectors alive in variables: passing the temporary straight into the
    # iterator constructor segfaults in nanocct (the iterator does not keep its argument alive).
    old_refs = g.Topo().Gen().CompoundRefIds(BRepGraph_NodeId(old_solid))
    new_refs = g.Topo().Gen().CompoundRefIds(BRepGraph_NodeId(shell))
    old_comps = list(BRepGraph_CompoundsOfChild(g, old_refs))
    new_comps = list(BRepGraph_CompoundsOfChild(g, new_refs))
    assert comp0 not in old_comps
    assert comp0 in new_comps
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_SetChildEdgeIdOnCoEdge_LastBondInWireCheck():
    g = build(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    seam_edge = seam_wire = seam_coedge = None
    for eid in edge_ids(g):
        ces = list(g.Topo().Edges().CoEdges(eid))
        if len(ces) < 2:
            continue
        seen = {}
        for ce in ces:
            w = g.Topo().CoEdges().Wire(ce)
            if w.IsValid():
                if w.Index in seen:
                    seam_edge, seam_wire, seam_coedge = eid, w, ce
                    break
                seen[w.Index] = ce
        if seam_edge is not None:
            break
    assert seam_edge is not None

    target = next(e for e in edge_ids(g) if e != seam_edge)
    g.Editor().CoEdges().SetChildEdgeId(seam_coedge, target)
    assert seam_wire in list(g.Topo().Edges().WiresOf(seam_edge))
    assert g.ValidateRelations()


def test_BRepGraphIncTest_Relations_FaceSupplementVertex_NoPersistedRefUpdate():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    g.Editor().Vertices().Add(gp_Pnt(7, 7, 7), 1.0e-7)
    assert g.ValidateRelations()
    layer = ensure_supplement(g)
    assert layer is not None
    assert layer.AttachedTo(BRepGraph_NodeId(BRepGraph_FaceId.Start_s())).Size() == 0


def test_BRepGraphIncTest_Relations_RemoveRef_UnbindsByKind():
    g = build(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    face_refs = g.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert face_refs.Size() >= 1
    face_ref = face_refs.Value(0)
    fid = g.Refs().Faces().Entry(face_ref).ChildFaceId

    assert g.Editor().Gen().RemoveRef(face_ref)
    parent_refs = g.Topo().Faces().Relations(fid).ParentFaceRefIds
    for sid in BRepGraph_ShellsOfFace(g, parent_refs):
        assert sid != BRepGraph_ShellId.Start_s()
    assert g.ValidateRelations()
