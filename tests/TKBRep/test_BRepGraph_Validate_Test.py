# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Validate_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_Deduplicate,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_NodeId,
    BRepGraph_OccurrenceId,
    BRepGraph_ProductId,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_VertexId,
    BRepGraph_VertexRefId,
    BRepGraph_WireId,
)
from nanocct.BRepGraphInc import BRepGraph_EdgeCurve3DRepId
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Circle, Geom_CylindricalSurface, Geom_Line, Geom_Plane, Geom_SphericalSurface
from nanocct.gp import gp_Ax2, gp_Ax3, gp_Dir, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FACE, TopAbs_FORWARD, TopAbs_REVERSED
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound

V = BRepGraph_Validate
ERR = BRepGraph_Validate.Severity.Error
WARN = BRepGraph_Validate.Severity.Warning


def _box_graph(dx=10.0, dy=20.0, dz=30.0):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(dx, dy, dz).Shape())
    assert not g.IsEmpty()
    return g


def _audit(g):
    return V.Perform_s(g, V.Options.Audit_s())


def _coedges_of_wire(g, wire_id):
    return g.Topo().Wires().Relations(wire_id).CoEdgeIds


def _edge_with_curve(g, skip=None):
    it = BRepGraph_EdgeIterator(g)
    while it.More():
        eid = it.CurrentId()
        if (skip is None or eid != skip) and it.Current().Curve3DRepId.IsValid():
            return eid
        it.Next()
    return BRepGraph_EdgeId()


def _has_issue(result, needle, sev=None):
    for issue in result.Issues:
        if (sev is None or issue.Sev == sev) and needle in issue.Description.ToCString():
            return True
    return False


def _has_error_containing(result, needle):
    return _has_issue(result, needle, ERR)


def _array(item_type, items):
    # NCollection_LinearVector.ToArray1() is a non-owning view (C++: shared memory), so build an owning Array1.
    arr = NCollection_Array1[item_type](0, len(items) - 1)
    for i, item in enumerate(items):
        arr[i] = item
    return arr


def _coedge_array(g, edges, orients):
    return _array(BRepGraph_CoEdgeId, [g.Editor().CoEdges().Add(e, o) for e, o in zip(edges, orients)])


def _no_inner():
    return NCollection_Array1[BRepGraph_WireId]()


def test_BRepGraph_ValidateTest_CleanGraph_NoIssues():
    g = _box_graph()
    res = V.Perform_s(g)
    assert res.IsValid()
    assert res.NbIssues(ERR) == 0
    assert res.NbIssues(WARN) == 0

    audit = V.Perform_s(g, V.Options.Audit_s())
    assert audit.IsValid()
    assert audit.NbIssues(ERR) == 0

    light = V.Perform_s(g, V.Options.Lightweight_s())
    assert light.IsValid()
    assert light.NbIssues(ERR) == 0


def test_BRepGraph_ValidateTest_AfterGeomDeduplicate_NoIssues():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    face = TopExp_Explorer(box, TopAbs_FACE).Current()
    copy1 = BRepBuilderAPI_Copy(face, True)
    copy2 = BRepBuilderAPI_Copy(face, True)
    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)
    builder.Add(comp, copy1.Shape())
    builder.Add(comp, copy2.Shape())

    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(comp)
    assert not g.IsEmpty()
    BRepGraph_Deduplicate.Perform_s(g)

    res = V.Perform_s(g)
    assert res.IsValid()
    assert res.NbIssues(ERR) == 0


def test_BRepGraph_ValidateTest_DetectsRemovedNodeReference():
    g = _box_graph()
    assert g.Topo().Vertices().Nb() > 0

    ref_to_corrupt = BRepGraph_VertexRefId()
    for i in range(g.Topo().Edges().Nb()):
        start_ref = BRepGraph_Tool.Edge.StartVertexId_s(g, BRepGraph_EdgeId(i))
        if BRepGraph_Tool.Vertex.Usage_s(g, start_ref).IsValid():
            ref_to_corrupt = start_ref
            break
    vtx_to_remove = g.Editor().Vertices().Add(gp_Pnt(100.0, 0.0, 0.0), Precision.Confusion_s())
    assert vtx_to_remove.IsValid()
    assert ref_to_corrupt.IsValid()

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(vtx_to_remove))
    ref_mut = g.Editor().Vertices().MutRef(ref_to_corrupt)
    ref_mut.Internal().ChildVertexId = vtx_to_remove

    assert not V.Perform_s(g).IsValid()
    audit = _audit(g)
    assert not audit.IsValid()
    assert audit.NbIssues(ERR) > 0


def test_BRepGraph_ValidateTest_WireConnectivity_DisconnectedEdges():
    g = _box_graph()
    assert g.Topo().Wires().Nb() > 0

    target_wire = BRepGraph_WireId()
    for i in range(g.Topo().Wires().Nb()):
        if _coedges_of_wire(g, BRepGraph_WireId(i)).Size() >= 2:
            target_wire = BRepGraph_WireId(i)
            break
    assert target_wire.IsValid()

    ce_ids = _coedges_of_wire(g, target_wire)
    assert ce_ids.Size() >= 1
    first_coedge = g.Topo().CoEdges().Definition(ce_ids.Value(0))
    first_edge_id = BRepGraph_NodeId(first_coedge.ChildEdgeId)
    assert first_edge_id.IsValid()

    first_edge = g.Editor().Edges().Mut(BRepGraph_EdgeId(first_edge_id))
    end_ref = first_edge.Internal().EndVertexRefId
    start_ref = first_edge.Internal().StartVertexRefId
    orig_end_vtx = g.Refs().Vertices().Entry(end_ref).ChildVertexId
    orig_start_vtx = g.Refs().Vertices().Entry(start_ref).ChildVertexId
    orig_end = BRepGraph_NodeId(orig_end_vtx)
    for i in range(g.Topo().Vertices().Nb()):
        vid = BRepGraph_VertexId(i)
        if BRepGraph_NodeId(vid) != orig_end and BRepGraph_NodeId(vid) != BRepGraph_NodeId(orig_start_vtx):
            mut_end = g.Editor().Vertices().MutRef(end_ref)
            mut_end.Internal().ChildVertexId = vid
            del mut_end
            break

    assert g.Refs().Vertices().Entry(end_ref).ChildVertexId != orig_end_vtx

    res = _audit(g)
    assert not _has_error_containing(res, "Wire edges not connected")
    assert _has_issue(res, "Wire edges not connected", WARN)


def test_BRepGraph_ValidateTest_BoundsCheck_InvalidIndex():
    g = _box_graph()
    assert g.Topo().Edges().Nb() > 0
    edge = g.Editor().Edges().Mut(BRepGraph_EdgeId.Start_s())
    edge.Internal().Curve3DRepId = BRepGraph_EdgeCurve3DRepId()

    res = _audit(g)
    assert not res.IsValid()
    assert res.NbIssues(ERR) > 0


def test_BRepGraph_ValidateTest_AfterSplitEdge_ProducesSubEdges():
    g = _box_graph()
    orig_edge_count = g.Topo().Edges().Nb()

    edge_id = BRepGraph_EdgeId()
    split_param = 0.0
    for i in range(g.Topo().Edges().Nb()):
        cand = BRepGraph_EdgeId(i)
        edef = g.Topo().Edges().Definition(cand)
        if (
            not BRepGraph_Tool.Edge.Degenerated_s(g, cand)
            and edef.Curve3DRepId.IsValid()
            and BRepGraph_Tool.Edge.StartVertexId_s(g, cand).IsValid()
            and BRepGraph_Tool.Edge.EndVertexId_s(g, cand).IsValid()
        ):
            edge_id = cand
            first, last = BRepGraph_Tool.Edge.Range_s(g, cand)
            split_param = 0.5 * (first + last)
            break
    assert edge_id.IsValid()

    mid = gp_Pnt()
    BRepGraph_Tool.Edge.Curve_s(g, edge_id).D0(split_param, mid)
    split_vtx = g.Editor().Vertices().Add(mid, BRepGraph_Tool.Edge.Tolerance_s(g, edge_id))

    sub_a = BRepGraph_EdgeId()
    sub_b = BRepGraph_EdgeId()
    g.Editor().Edges().Split(edge_id, split_vtx, split_param, sub_a, sub_b)

    assert g.Topo().Edges().Nb() == orig_edge_count + 2
    assert sub_a.IsValid()
    assert sub_b.IsValid()
    assert edge_id.IsRemoved(g)

    assert _audit(g).IsValid()


def test_BRepGraph_ValidateTest_CorruptedPCurve_FaceIdOutOfBounds():
    g = _box_graph()
    assert g.Topo().CoEdges().Nb() > 0
    coedge = g.Editor().CoEdges().Mut(BRepGraph_CoEdgeId.Start_s())
    coedge.Internal().FaceId = BRepGraph_FaceId(g.Topo().Faces().Nb() + 999)

    assert not V.Perform_s(g).IsValid()
    assert not V.Perform_s(g, V.Options.Lightweight_s()).IsValid()
    assert not _audit(g).IsValid()


def test_BRepGraph_ValidateTest_RemoveNodeMaintainsActiveCount():
    g = _box_graph()
    nb_before = g.Topo().Faces().NbActive()
    assert nb_before > 0

    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))

    res = _audit(g)
    assert not _has_issue(res, "NbActiveFaces mismatch")
    assert g.Topo().Faces().NbActive() == nb_before - 1


def test_BRepGraph_ValidateTest_Audit_ValidatesCoEdgeUIDsFromBuilderWireCreation():
    g = _box_graph()
    assert g.Topo().Edges().Nb() > 0

    arr = _coedge_array(g, [BRepGraph_EdgeId.Start_s()], [TopAbs_FORWARD])
    wire_id = g.Editor().Wires().Add(arr)
    assert wire_id.IsValid()

    ce_ids = _coedges_of_wire(g, wire_id)
    assert ce_ids.Size() == 1
    assert g.UIDs().Of(BRepGraph_NodeId(ce_ids.Value(0))).IsValid()

    res = _audit(g)
    assert res.IsValid(), [i.Description.ToCString() for i in res.Issues]
    assert res.NbIssues(ERR) == 0


def test_BRepGraph_ValidateTest_AssemblyGraph_ValidProduct_NoIssuesInAudit():
    g = _box_graph()
    assert g.Topo().Products().Nb() >= 1

    part = BRepGraph_ProductId.Start_s()
    assert g.Topo().Products().IsPart(part)

    assembly = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(assembly)
    assert assembly.IsValid()

    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(20.0, 0.0, 0.0))
    occ1 = g.Editor().Products().Append(assembly, part, TopLoc_Location())
    occ2 = g.Editor().Products().Append(assembly, part, TopLoc_Location(trsf))
    assert occ1.IsValid()
    assert occ2.IsValid()

    assert g.Topo().Products().IsAssembly(assembly)
    assert g.Topo().Products().NbComponents(assembly) == 2

    g.Editor().CommitMutation()

    res = _audit(g)
    assert res.IsValid(), [i.Description.ToCString() for i in res.Issues]


def test_BRepGraph_ValidateTest_DocumentRootReferencedByOccurrence_Detected():
    g = _box_graph()
    part = BRepGraph_ProductId.Start_s()
    assert g.Topo().Products().IsPart(part)

    root = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(root)
    assert root.IsValid()
    assert g.Editor().Products().Append(root, part, TopLoc_Location()).IsValid()

    assert g.RootProductIds().Size() == 1
    assert g.RootProductIds().First() == root

    g.Editor().Products().AppendDocumentRoot(part)

    assert not V.Perform_s(g, V.Options.Lightweight_s()).IsValid()
    audit = _audit(g)
    assert not audit.IsValid()

    found = False
    for issue in audit.Issues:
        if (
            issue.Sev == ERR
            and issue.NodeId == BRepGraph_NodeId(part)
            and "Document root Product is referenced" in issue.Description.ToCString()
        ):
            found = True
            break
    assert found


def test_BRepGraph_ValidateTest_AssemblyGraph_CorruptedOccurrenceChildNodeId_DetectedByAudit():
    g = _box_graph()
    assert g.Topo().Products().Nb() >= 1
    assert g.Topo().Occurrences().Nb() >= 1

    occ = g.Editor().Occurrences().Mut(BRepGraph_OccurrenceId.Start_s())
    occ.Internal().ChildNodeId = BRepGraph_NodeId(BRepGraph_NodeId.Kind.Solid, g.Topo().Solids().Nb() + 999)

    res = _audit(g)
    assert not res.IsValid()
    assert res.NbIssues(ERR) > 0
    assert _has_error_containing(res, "ChildNodeId invalid")


def test_BRepGraph_ValidateTest_AssemblyGraph_CorruptedOccurrenceChildNodeId_ProductIndex_DetectedByAudit():
    g = _box_graph()
    root = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(root)
    assert root.IsValid()

    part = BRepGraph_ProductId.Start_s()
    assert g.Topo().Products().IsPart(part)
    assert part.IsValid()

    occ_id = g.Editor().Products().Append(root, part, TopLoc_Location())
    assert occ_id.IsValid()

    occ = g.Editor().Occurrences().Mut(occ_id)
    occ.Internal().ChildNodeId = BRepGraph_NodeId(BRepGraph_NodeId.Kind.Product, g.Topo().Products().Nb() + 999)

    res = _audit(g)
    assert not res.IsValid()
    assert res.NbIssues(ERR) > 0
    assert _has_error_containing(res, "ChildNodeId invalid")


def test_BRepGraph_ValidateTest_AssemblyGraph_OccurrenceChildRefersToOccurrence_DetectedByAudit():
    g = _box_graph()
    assert g.Topo().Occurrences().Nb() > 0

    occ = g.Editor().Occurrences().Mut(BRepGraph_OccurrenceId.Start_s())
    occ.Internal().ChildNodeId = BRepGraph_NodeId(BRepGraph_OccurrenceId.Start_s())

    res = _audit(g)
    assert not res.IsValid()
    assert _has_error_containing(res, "cannot reference an Occurrence")


def test_BRepGraph_ValidateTest_LightweightVsAudit_RemovedVertexReference_Differential():
    g = _box_graph()
    assert g.Topo().Vertices().Nb() > 0

    vtx_to_remove = BRepGraph_VertexId()
    for i in range(g.Topo().Edges().Nb()):
        start_ref = BRepGraph_Tool.Edge.StartVertexId_s(g, BRepGraph_EdgeId(i))
        usage = BRepGraph_Tool.Vertex.Usage_s(g, start_ref)
        if usage.IsValid():
            vtx_to_remove = usage.DefId
            break
    assert vtx_to_remove.IsValid()

    ref_to_corrupt = BRepGraph_Tool.Edge.StartVertexId_s(g, BRepGraph_EdgeId.Start_s())
    assert ref_to_corrupt.IsValid()
    vtx_to_remove = g.Editor().Vertices().Add(gp_Pnt(100.0, 0.0, 0.0), Precision.Confusion_s())
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(vtx_to_remove))
    ref_mut = g.Editor().Vertices().MutRef(ref_to_corrupt)
    ref_mut.Internal().ChildVertexId = vtx_to_remove

    assert not V.Perform_s(g, V.Options.Lightweight_s()).IsValid()
    audit = _audit(g)
    assert not audit.IsValid()
    assert audit.NbIssues(ERR) > 0
    assert _has_error_containing(audit, "references removed")


def test_BRepGraph_ValidateTest_Audit_WarnsSurfacedFaceWithNoWireRefs():
    g = _box_graph(10.0, 10.0, 10.0)
    did_corrupt = False
    it = BRepGraph_FaceIterator(g)
    while it.More() and not did_corrupt:
        fid = it.CurrentId()
        wire_refs = g.Topo().Faces().Relations(fid).WireRefIds
        if wire_refs.IsEmpty():
            it.Next()
            continue
        assert g.Editor().Faces().RemoveWire(fid, wire_refs.Last())
        did_corrupt = True
        it.Next()
    assert did_corrupt

    res = _audit(g)
    assert res.IsValid()
    assert not res.Issues.IsEmpty()
    assert res.Issues.First().Sev == WARN
    assert "no wire refs" in res.Issues.First().Description.ToCString()


def test_BRepGraph_ValidateTest_Audit_DetectsSharedOwnedUse():
    g = _box_graph()
    e1 = _edge_with_curve(g)
    assert e1.IsValid()
    e2 = _edge_with_curve(g, e1)
    assert e2.IsValid()
    rep1 = g.Topo().Edges().Definition(e1).Curve3DRepId
    assert rep1.IsValid()
    edge = g.Editor().Edges().Mut(e2)
    edge.Internal().Curve3DRepId = rep1
    del edge

    res = _audit(g)
    assert not res.IsValid()
    assert _has_error_containing(res, "Active EdgeCurve3DRep has multiple owners")


def test_BRepGraph_ValidateTest_Audit_DetectsActiveOwnedUseWithoutOwner():
    g = _box_graph()
    eid = _edge_with_curve(g)
    assert eid.IsValid()
    assert g.Topo().Edges().Definition(eid).Curve3DRepId.IsValid()
    edge = g.Editor().Edges().Mut(eid)
    edge.Internal().Curve3DRepId = BRepGraph_EdgeCurve3DRepId()
    del edge

    res = _audit(g)
    assert not res.IsValid()
    assert _has_error_containing(res, "Active EdgeCurve3DRep has no owner")


def test_BRepGraph_ValidateTest_Synthetic_Box_AuditClean():
    g = BRepGraph()
    g.Clear()
    vo = g.Editor().Vertices()
    pts = [(0, 0, 0), (10, 0, 0), (10, 20, 0), (0, 20, 0), (0, 0, 30), (10, 0, 30), (10, 20, 30), (0, 20, 30)]
    v = [vo.Add(gp_Pnt(*p), 1e-7) for p in pts]

    eo = g.Editor().Edges()

    def line(p, d, length, a, b):
        return eo.Add(v[a], v[b], Geom_Line(gp_Pnt(*p), gp_Dir(*d)), 0.0, length, 1e-7)

    e = [
        line((0, 0, 0), (1, 0, 0), 10.0, 0, 1),
        line((10, 0, 0), (0, 1, 0), 20.0, 1, 2),
        line((10, 20, 0), (-1, 0, 0), 10.0, 2, 3),
        line((0, 20, 0), (0, -1, 0), 20.0, 3, 0),
        line((0, 0, 30), (1, 0, 0), 10.0, 4, 5),
        line((10, 0, 30), (0, 1, 0), 20.0, 5, 6),
        line((10, 20, 30), (-1, 0, 0), 10.0, 6, 7),
        line((0, 20, 30), (0, -1, 0), 20.0, 7, 4),
        line((0, 0, 0), (0, 0, 1), 30.0, 0, 4),
        line((10, 0, 0), (0, 0, 1), 30.0, 1, 5),
        line((10, 20, 0), (0, 0, 1), 30.0, 2, 6),
        line((0, 20, 0), (0, 0, 1), 30.0, 3, 7),
    ]
    F, R = TopAbs_FORWARD, TopAbs_REVERSED

    def make_wire(idx, ors):
        return g.Editor().Wires().Add(_coedge_array(g, [e[i] for i in idx], ors))

    w = [
        make_wire([0, 1, 2, 3], [F, F, F, F]),
        make_wire([4, 5, 6, 7], [F, F, F, F]),
        make_wire([0, 9, 4, 8], [F, F, R, R]),
        make_wire([1, 10, 5, 9], [F, F, R, R]),
        make_wire([2, 11, 6, 10], [F, F, R, R]),
        make_wire([3, 8, 7, 11], [F, F, R, R]),
    ]
    planes = [
        ((0, 0, 0), (0, 0, -1)),
        ((0, 0, 30), (0, 0, 1)),
        ((0, 0, 0), (0, -1, 0)),
        ((10, 0, 0), (1, 0, 0)),
        ((10, 20, 0), (0, 1, 0)),
        ((0, 20, 0), (-1, 0, 0)),
    ]
    fo = g.Editor().Faces()
    faces = [
        fo.Add(Geom_Plane(gp_Pln(gp_Ax3(gp_Pnt(*p), gp_Dir(*d)))), w[i], _no_inner(), 1e-7)
        for i, (p, d) in enumerate(planes)
    ]
    shell = g.Editor().Shells().Add()
    for f in faces:
        g.Editor().Shells().Append(shell, f)
    solid = g.Editor().Solids().Add()
    g.Editor().Solids().Append(solid, shell)

    res = _audit(g)
    assert res.IsValid()
    assert res.NbIssues(ERR) == 0


def test_BRepGraph_ValidateTest_Synthetic_Cylinder_AuditClean():
    g = BRepGraph()
    g.Clear()
    vo = g.Editor().Vertices()
    v_bot = vo.Add(gp_Pnt(5, 0, 0), 1e-7)
    v_top = vo.Add(gp_Pnt(5, 0, 15), 1e-7)

    eo = g.Editor().Edges()
    bot_circle = Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5.0)
    e_bot = eo.Add(v_bot, v_bot, bot_circle, 0.0, 2 * math.pi, 1e-7)
    top_circle = Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 15), gp_Dir(0, 0, 1)), 5.0)
    e_top = eo.Add(v_top, v_top, top_circle, 0.0, 2 * math.pi, 1e-7)
    seam = Geom_Line(gp_Pnt(5, 0, 0), gp_Dir(0, 0, 1))
    e_seam = eo.Add(v_bot, v_top, seam, 0.0, 15.0, 1e-7)

    w_bot = g.Editor().Wires().Add(_coedge_array(g, [e_bot, e_seam], [TopAbs_FORWARD, TopAbs_REVERSED]))
    w_top = g.Editor().Wires().Add(_coedge_array(g, [e_top, e_seam], [TopAbs_FORWARD, TopAbs_FORWARD]))
    w_lat = g.Editor().Wires().Add(_coedge_array(g, [e_seam, e_seam], [TopAbs_FORWARD, TopAbs_REVERSED]))

    fo = g.Editor().Faces()
    bot_plane = Geom_Plane(gp_Pln(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, -1))))
    top_plane = Geom_Plane(gp_Pln(gp_Ax3(gp_Pnt(0, 0, 15), gp_Dir(0, 0, 1))))
    lat = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5.0)
    f_bot = fo.Add(bot_plane, w_bot, _no_inner(), 1e-7)
    f_top = fo.Add(top_plane, w_top, _no_inner(), 1e-7)
    f_lat = fo.Add(lat, w_lat, _no_inner(), 1e-7)

    shell = g.Editor().Shells().Add()
    g.Editor().Shells().Append(shell, f_bot)
    g.Editor().Shells().Append(shell, f_top)
    g.Editor().Shells().Append(shell, f_lat)
    solid = g.Editor().Solids().Add()
    g.Editor().Solids().Append(solid, shell)

    assert _audit(g).IsValid()


def test_BRepGraph_ValidateTest_Synthetic_Sphere_AuditClean():
    g = BRepGraph()
    g.Clear()
    v_seam = g.Editor().Vertices().Add(gp_Pnt(8, 0, 0), 1e-7)
    circle = Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), 8.0)
    e_seam = g.Editor().Edges().Add(v_seam, v_seam, circle, 0.0, 2 * math.pi, 1e-7)
    wire = g.Editor().Wires().Add(_coedge_array(g, [e_seam, e_seam], [TopAbs_FORWARD, TopAbs_REVERSED]))
    face = g.Editor().Faces().Add(Geom_SphericalSurface(gp_Ax3(), 8.0), wire, _no_inner(), 1e-7)
    shell = g.Editor().Shells().Add()
    g.Editor().Shells().Append(shell, face)
    solid = g.Editor().Solids().Add()
    g.Editor().Solids().Append(solid, shell)

    assert _audit(g).IsValid()


def _triangle_solid(g, x0):
    vo = g.Editor().Vertices()
    eo = g.Editor().Edges()
    v0 = vo.Add(gp_Pnt(x0, 0, 0), 1e-7)
    v1 = vo.Add(gp_Pnt(x0 + 10, 0, 0), 1e-7)
    v2 = vo.Add(gp_Pnt(x0 + 5, 10, 0), 1e-7)
    e0 = eo.Add(v0, v1, Geom_Line(gp_Pnt(x0, 0, 0), gp_Dir(1, 0, 0)), 0.0, 10.0, 1e-7)
    e1 = eo.Add(
        v1, v2, Geom_Line(gp_Pnt(x0 + 10, 0, 0), gp_Dir(gp_Vec(-5.0, 10.0, 0.0).Normalized())), 0.0, math.sqrt(125.0), 1e-7
    )
    e2 = eo.Add(
        v2, v0, Geom_Line(gp_Pnt(x0 + 5, 10, 0), gp_Dir(gp_Vec(-5.0, -10.0, 0.0).Normalized())), 0.0, math.sqrt(125.0), 1e-7
    )
    return [e0, e1, e2]


def test_BRepGraph_ValidateTest_Synthetic_Compound_AuditClean():
    g = BRepGraph()
    g.Clear()
    plane = Geom_Plane(gp_Pln(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))))
    solids = []
    for x0 in (0.0, 20.0):
        edges = _triangle_solid(g, x0)
        wire = g.Editor().Wires().Add(_coedge_array(g, edges, [TopAbs_FORWARD] * 3))
        face = g.Editor().Faces().Add(plane, wire, _no_inner(), 1e-7)
        shell = g.Editor().Shells().Add()
        g.Editor().Shells().Append(shell, face)
        solid = g.Editor().Solids().Add()
        g.Editor().Solids().Append(solid, shell)
        solids.append(solid)

    g.Editor().Compounds().Add(_array(BRepGraph_NodeId, [BRepGraph_NodeId(s) for s in solids]))

    assert _audit(g).IsValid()


def test_BRepGraph_ValidateTest_Synthetic_Assembly_AuditClean():
    g = BRepGraph()
    g.Clear()
    vo = g.Editor().Vertices()
    v = [vo.Add(gp_Pnt(*p), 1e-7) for p in [(0, 0, 0), (10, 0, 0), (10, 10, 0), (0, 10, 0)]]
    eo = g.Editor().Edges()
    e = [
        eo.Add(v[0], v[1], Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 0.0, 10.0, 1e-7),
        eo.Add(v[1], v[2], Geom_Line(gp_Pnt(10, 0, 0), gp_Dir(0, 1, 0)), 0.0, 10.0, 1e-7),
        eo.Add(v[2], v[3], Geom_Line(gp_Pnt(10, 10, 0), gp_Dir(-1, 0, 0)), 0.0, 10.0, 1e-7),
        eo.Add(v[3], v[0], Geom_Line(gp_Pnt(0, 10, 0), gp_Dir(0, -1, 0)), 0.0, 10.0, 1e-7),
    ]
    wire = g.Editor().Wires().Add(_coedge_array(g, e, [TopAbs_FORWARD] * 4))
    face = g.Editor().Faces().Add(Geom_Plane(gp_Pln()), wire, _no_inner(), 1e-7)
    shell = g.Editor().Shells().Add()
    g.Editor().Shells().Append(shell, face)
    solid = g.Editor().Solids().Add()
    g.Editor().Solids().Append(solid, shell)

    part = BRepGraph_ProductId.Start_s()
    assembly = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(assembly)

    t1 = gp_Trsf()
    t1.SetTranslation(gp_Vec(0.0, 0.0, 0.0))
    g.Editor().Products().Append(assembly, part, TopLoc_Location(t1))
    t2 = gp_Trsf()
    t2.SetTranslation(gp_Vec(20.0, 0.0, 0.0))
    g.Editor().Products().Append(assembly, part, TopLoc_Location(t2))

    g.Editor().CommitMutation()

    assert _audit(g).IsValid()
