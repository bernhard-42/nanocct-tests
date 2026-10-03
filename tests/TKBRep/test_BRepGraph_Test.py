# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_ChildExplorer,
    BRepGraph_CompoundsOfChild,
    BRepGraph_CompSolidId,
    BRepGraph_CompSolidsOfSolid,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_FacesOfWire,
    BRepGraph_LayerHistory,
    BRepGraph_NodeId,
    BRepGraph_ParentExplorer,
    BRepGraph_ProductId,
    BRepGraph_ShellId,
    BRepGraph_ShellIterator,
    BRepGraph_ShellsOfFace,
    BRepGraph_SolidId,
    BRepGraph_SolidIterator,
    BRepGraph_SolidsOfShell,
    BRepGraph_Tool,
    BRepGraph_UID,
    BRepGraph_Validate,
    BRepGraph_VertexId,
    BRepGraph_VertexIterator,
    BRepGraph_WireId,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Line
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp_Dir, gp_Dir2d, gp_Lin, gp_Pnt, gp_Pnt2d, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_IndexedMap
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_VERTEX, TopAbs_WIRE
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher

Kind = BRepGraph_NodeId.Kind
Tool = BRepGraph_Tool


# ---------------------------------------------------------------- helpers


def _graph_of(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    return g


@pytest.fixture
def graph():
    return _graph_of(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())


def _ids(iterator_cls, g):
    it = iterator_cls(g)
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _node_ids(explorer):
    return [item.DefId for item in explorer]


def _contains(ids, the_id):
    return any(i == the_id for i in ids)


def _history(g):
    # LayerRegistry().Ensure<BRepGraph_LayerHistory>() is a template: find, else register.
    reg = g.LayerRegistry()
    layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    if layer is None:
        reg.RegisterLayer(BRepGraph_LayerHistory())
        layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    return layer


def _node_array(*nodes):
    arr = NCollection_Array1[BRepGraph_NodeId](0, len(nodes) - 1)
    for i, n in enumerate(nodes):
        arr[i] = n
    return arr


def _empty_node_array():
    return NCollection_Array1[BRepGraph_NodeId]()


def _map(shape, kind):
    m = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(shape, kind, m)
    return m


def _compound(*shapes):
    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)
    for s in shapes:
        builder.Add(comp, s)
    return comp


def _first_face(shape):
    return TopoDS.Face(TopExp_Explorer(shape, TopAbs_FACE).Current())


def _coedges_of_wire(g, wire_id):
    return g.Topo().Wires().Relations(wire_id).CoEdgeIds


def _wire_refs_of_face(g, face_id):
    return g.Refs().Wires().IdsOf(face_id)


def _face_uses_wire(g, face_id, wire_id):
    return any(g.Refs().Wires().Entry(r).ChildWireId == wire_id for r in _wire_refs_of_face(g, face_id))


def _child_refs_of_compound(g, compound_id):
    return g.Refs().Children().IdsOf(compound_id)


def _parents(iterator_cls, g, refs):
    # Keep `refs` alive while iterating: the reverse iterators store a pointer to the ref vector,
    # and a vector returned from Python is a copy (see the report: passing a temporary crashes).
    return list(iterator_cls(g, refs))


def _collect_free_edges(g):
    result = []
    for eid in _ids(BRepGraph_EdgeIterator, g):
        if Tool.Edge.Degenerated_s(g, eid):
            continue
        owning = set()
        for item in BRepGraph_ParentExplorer(g, BRepGraph_NodeId(eid), Kind.Face):
            owning.add(item.DefId.Index)
            if len(owning) > 1:
                break
        if len(owning) == 1:
            result.append(eid)
    return result


def _add_compatible_replacement_edge(g, old_edge, reversed_):
    start_ref = Tool.Edge.StartVertexId_s(g, old_edge)
    end_ref = Tool.Edge.EndVertexId_s(g, old_edge)
    start_v = g.Refs().Vertices().Entry(start_ref).ChildVertexId
    end_v = g.Refs().Vertices().Entry(end_ref).ChildVertexId
    new_start, new_end = (end_v, start_v) if reversed_ else (start_v, end_v)
    p0 = Tool.Vertex.Pnt_s(g, new_start)
    p1 = Tool.Vertex.Pnt_s(g, new_end)
    length = p0.Distance(p1)
    curve = Geom_Line(gp_Lin(p0, gp_Dir(gp_Vec(p0, p1))))
    return g.Editor().Edges().Add(new_start, new_end, curve, 0.0, length, 1.0e-7)


def _component_key(node):
    return (node.Index, node.NodeKind)


def _component_root_of_face(g, face_id):
    for item in BRepGraph_ParentExplorer(g, BRepGraph_NodeId(face_id), Kind.Solid):
        return item.DefId
    for item in BRepGraph_ParentExplorer(g, BRepGraph_NodeId(face_id), Kind.Shell):
        return item.DefId
    return BRepGraph_NodeId(face_id)


def _count_face_components(g):
    return len({_component_key(_component_root_of_face(g, f)) for f in _ids(BRepGraph_FaceIterator, g)})


def _count_same_domain_faces(g, face_id):
    surface = Tool.Face.Surface_s(g, face_id)
    if surface is None:
        return 0
    count = 0
    for other in _ids(BRepGraph_FaceIterator, g):
        if other != face_id and Tool.Face.Surface_s(g, other) is surface:
            count += 1
    return count


# ---------------------------------------------------------------- tests


def test_BRepGraphTest_Build_SimpleBox_IsNotEmpty(graph):
    assert not graph.IsEmpty()


def test_BRepGraphTest_Build_SimpleBox_CorrectCounts(graph):
    topo = graph.Topo()
    assert topo.Solids().Nb() == 1
    assert topo.Shells().Nb() == 1
    assert topo.Faces().Nb() == 6
    assert topo.Wires().Nb() == 6
    assert topo.Edges().Nb() == 12
    assert topo.Vertices().Nb() == 8


def test_BRepGraphTest_Build_SimpleBox_SurfaceCount(graph):
    assert graph.Topo().Faces().Nb() == 6


def test_BRepGraphTest_Face_Surface_IsValid(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert Tool.Face.HasSurface_s(graph, fid), fid.Index


def test_BRepGraphTest_Edge_CurveAndVertices_AreValid(graph):
    for eid in _ids(BRepGraph_EdgeIterator, graph):
        if not Tool.Edge.Degenerated_s(graph, eid):
            assert Tool.Edge.HasCurve_s(graph, eid)
        assert Tool.Edge.StartVertexId_s(graph, eid).IsValid()
        assert Tool.Edge.EndVertexId_s(graph, eid).IsValid()


def test_BRepGraphTest_Wire_OuterWire_Exists(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert Tool.Face.OuterWire_s(graph, fid).IsValid()


def test_BRepGraphTest_FaceDef_HasValidSurface(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert Tool.Face.HasSurface_s(graph, fid)


def test_BRepGraphTest_FindPCurveCoEdgeId_ValidPair(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        outer = Tool.Face.OuterWire_s(graph, fid)
        if not outer.IsValid():
            continue
        for ceid in _coedges_of_wire(graph, outer):
            coedge = graph.Topo().CoEdges().Definition(ceid)
            eid = BRepGraph_EdgeId(coedge.ChildEdgeId)
            if Tool.Edge.Degenerated_s(graph, eid):
                continue
            assert Tool.Edge.FindPCurveCoEdgeId_s(graph, eid, fid).IsValid()


def test_BRepGraphTest_UID_Unique(graph):
    uids = set()
    for iterator_cls in (BRepGraph_SolidIterator, BRepGraph_ShellIterator, BRepGraph_FaceIterator,
                         BRepGraph_WireIterator, BRepGraph_EdgeIterator, BRepGraph_VertexIterator):
        for tid in _ids(iterator_cls, graph):
            uid = graph.UIDs().Of(BRepGraph_NodeId(tid))
            key = (uid.Kind, uid.Counter)
            assert key not in uids
            uids.add(key)


def test_BRepGraphTest_UID_NodeIdRoundTrip(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        node = BRepGraph_NodeId(fid)
        uid = graph.UIDs().Of(node)
        assert graph.UIDs().NodeIdFrom(uid) == node


def test_BRepGraphTest_SameDomainFaces_Box_Empty(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert _count_same_domain_faces(graph, fid) == 0


def test_BRepGraphTest_Decompose_TwoSeparateFaces():
    face1 = _first_face(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    face2 = _first_face(BRepPrimAPI_MakeBox(20.0, 20.0, 20.0).Shape())
    g = _graph_of(_compound(face1, face2))
    assert not g.IsEmpty()
    assert g.Topo().Faces().Nb() == 2
    assert _count_face_components(g) == 2


def test_BRepGraphTest_ReBuild_UIDMonotonic():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g = _graph_of(box)
    gen1 = g.UIDs().Generation()
    assert g.Topo().Faces().Nb() > 0
    first_uid = g.UIDs().Of(BRepGraph_NodeId(Kind.Face, 0))
    assert first_uid.IsValid()

    g.Clear()
    g.Shapes().Add(box)
    gen2 = g.UIDs().Generation()
    assert gen2 > gen1
    for fid in _ids(BRepGraph_FaceIterator, g):
        assert g.UIDs().Of(BRepGraph_NodeId(fid)).IsValid()
    assert not g.UIDs().Has(first_uid)


def test_BRepGraphTest_DetectMissingPCurves_ValidBox_Empty(graph):
    missing = []
    for fid in _ids(BRepGraph_FaceIterator, graph):
        for node in _node_ids(BRepGraph_ChildExplorer(graph, BRepGraph_NodeId(fid), Kind.Edge)):
            eid = BRepGraph_EdgeId.FromNodeId_s(node)
            if Tool.Edge.Degenerated_s(graph, eid):
                continue
            if not Tool.Edge.FindPCurveCoEdgeId_s(graph, eid, fid).IsValid():
                missing.append((eid, fid))
    assert len(missing) == 0


def test_BRepGraphTest_DetectDegenerateWires_ValidBox_Empty(graph):
    degenerate = []
    for wid in _ids(BRepGraph_WireIterator, graph):
        nb_edges = len(list(BRepGraph_ChildExplorer(graph, BRepGraph_NodeId(wid), Kind.Edge)))
        if nb_edges < 2:
            degenerate.append(wid)
            continue
        is_outer = False
        for node in _node_ids(BRepGraph_ParentExplorer(graph, BRepGraph_NodeId(wid), Kind.Face)):
            fid = BRepGraph_FaceId.FromNodeId_s(node)
            if Tool.Face.OuterWire_s(graph, fid) == wid:
                is_outer = True
                break
        if is_outer and not Tool.Wire.IsClosed_s(graph, wid):
            degenerate.append(wid)
    assert len(degenerate) == 0


def test_BRepGraphTest_MutableEdge_ModifyTolerance(graph):
    start = BRepGraph_EdgeId.Start_s()
    orig_tol = Tool.Edge.Tolerance_s(graph, start)
    mut = graph.Editor().Edges().Mut(start)
    graph.Editor().Edges().SetTolerance(mut, orig_tol * 2.0)
    assert abs(Tool.Edge.Tolerance_s(graph, start) - orig_tol * 2.0) <= 1.0e-15
    del mut


def test_BRepGraphTest_NbFacesOfEdge_SharedEdge(graph):
    for eid in _ids(BRepGraph_EdgeIterator, graph):
        if not Tool.Edge.Degenerated_s(graph, eid):
            assert graph.Topo().Edges().NbFaces(eid) == 2


def test_BRepGraphTest_FreeEdges_ClosedBox_Empty(graph):
    assert len(_collect_free_edges(graph)) == 0


def test_BRepGraphTest_RecordHistory_BasicEntry(graph):
    hist = _history(graph)
    before = hist.NbRecords()
    hist.Record("TestOp", BRepGraph_NodeId(Kind.Edge, 0), _node_array(BRepGraph_NodeId(Kind.Edge, 1)))
    assert hist.NbRecords() == before + 1
    assert hist.Record(before).OperationName.IsEqual("TestOp")


def test_BRepGraphTest_ReplaceEdge_Substitution(graph):
    wire0 = BRepGraph_WireId.Start_s()
    coedges = _coedges_of_wire(graph, wire0)
    assert coedges.Size() >= 1
    old_edge = graph.Topo().CoEdges().Definition(coedges.Value(0)).ChildEdgeId
    new_edge = _add_compatible_replacement_edge(graph, old_edge, False)
    assert new_edge.IsValid()

    graph.Editor().Wires().ReplaceEdge(wire0, old_edge, new_edge, False)

    after = _coedges_of_wire(graph, wire0)
    assert after.Size() >= 1
    assert graph.Topo().CoEdges().Definition(after.Value(0)).ChildEdgeId.Index == new_edge.Index


def _options(create_auto_product, flatten, parallel):
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = create_auto_product
    opts.Flatten = flatten
    opts.Parallel = parallel
    return opts


def test_BRepGraphTest_ParallelBuild_SameAsSequential():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    seq = BRepGraph()
    seq.Clear()
    seq.Shapes().Add(box, _options(True, False, False))
    assert not seq.IsEmpty()
    par = BRepGraph()
    par.Clear()
    par.Shapes().Add(box, _options(True, False, True))
    assert not par.IsEmpty()
    for name in ("Solids", "Shells", "Faces", "Wires", "Edges", "Vertices"):
        assert getattr(par.Topo(), name)().Nb() == getattr(seq.Topo(), name)().Nb(), name


def test_BRepGraphTest_ParallelBuild_CompoundOfFaces():
    faces = []
    for size in (10.0, 20.0):
        faces.extend(TopExp_Explorer(BRepPrimAPI_MakeBox(size, size, size).Shape(), TopAbs_FACE))
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(_compound(*faces), _options(True, False, True))
    assert not g.IsEmpty()
    assert g.Topo().Faces().Nb() == 12


def test_BRepGraphTest_ReconstructFace_EachBoxFace_SameSubShapeCounts(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        node = BRepGraph_NodeId(fid)
        orig = graph.Shapes().Original(node)
        assert not orig.IsNull()
        recon = graph.Shapes().Reconstruct(node)
        for kind in (TopAbs_VERTEX, TopAbs_EDGE, TopAbs_WIRE):
            assert _map(recon, kind).Extent() == _map(orig, kind).Extent()
        surf1 = BRep_Tool.Surface_s(TopoDS.Face(orig))
        surf2 = BRep_Tool.Surface_s(TopoDS.Face(recon))
        assert surf1 is surf2


def test_BRepGraphTest_ReconstructFace_AfterEdgeReplace_ContainsNewEdge(graph):
    wire0 = BRepGraph_WireId.Start_s()
    coedges = _coedges_of_wire(graph, wire0)
    assert coedges.Size() >= 1
    old_edge = graph.Topo().CoEdges().Definition(coedges.Value(0)).ChildEdgeId
    new_edge = _add_compatible_replacement_edge(graph, old_edge, False)
    assert new_edge.IsValid()

    new_curve = Tool.Edge.Curve_s(graph, new_edge)
    old_curve = Tool.Edge.Curve_s(graph, old_edge)

    graph.Editor().Wires().ReplaceEdge(wire0, old_edge, new_edge, False)

    assert _face_uses_wire(graph, BRepGraph_FaceId.Start_s(), wire0)
    recon = graph.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_FaceId(0)))

    is_new_found = False
    is_old_found = False
    for edge in TopExp_Explorer(recon, TopAbs_EDGE):
        curve, _first, _last = BRep_Tool.Curve_s(TopoDS.Edge(edge))
        if curve is not None and new_curve is not None and curve is new_curve:
            is_new_found = True
        if curve is not None and old_curve is not None and curve is old_curve:
            is_old_found = True
    assert is_new_found
    assert not is_old_found


def test_BRepGraphTest_ReconstructShape_SolidRoot_SameFaceCount(graph):
    recon = graph.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Solid, 0))
    assert len(list(TopExp_Explorer(recon, TopAbs_FACE))) == 6


def test_BRepGraphTest_ReconstructShape_FaceRoot_ReturnsSameShape(graph):
    node = BRepGraph_NodeId(Kind.Face, 0)
    recon = graph.Shapes().Reconstruct(node)
    orig = graph.Shapes().Original(node)
    assert not orig.IsNull()
    assert BRep_Tool.Surface_s(TopoDS.Face(orig)) is BRep_Tool.Surface_s(TopoDS.Face(recon))


def test_BRepGraphTest_Shape_Unmodified_ReturnsSameShape(graph):
    node = BRepGraph_NodeId(Kind.Face, 0)
    shape = graph.Shapes().Shape(node)
    orig = graph.Shapes().Original(node)
    assert not orig.IsNull()
    assert shape.IsSame(orig)


def test_BRepGraphTest_Shape_AfterReplaceEdge_DiffersFromOriginal(graph):
    wire0 = BRepGraph_WireId.Start_s()
    coedges = _coedges_of_wire(graph, wire0)
    assert coedges.Size() >= 1
    old_edge = graph.Topo().CoEdges().Definition(coedges.Value(0)).ChildEdgeId
    new_edge = _add_compatible_replacement_edge(graph, old_edge, False)
    assert new_edge.IsValid()
    graph.Editor().Wires().ReplaceEdge(wire0, old_edge, new_edge, False)

    face_idx = None
    for fid in _ids(BRepGraph_FaceIterator, graph):
        if _face_uses_wire(graph, fid, wire0):
            face_idx = fid.Index
            break
    assert face_idx is not None
    node = BRepGraph_NodeId(Kind.Face, face_idx)
    shape = graph.Shapes().Shape(node)
    orig = graph.Shapes().Original(node)
    assert not orig.IsNull()
    assert not shape.IsSame(orig)


def test_BRepGraphTest_Shape_WireKind_Valid(graph):
    shape = graph.Shapes().Shape(BRepGraph_NodeId(Kind.Wire, 0))
    assert not shape.IsNull()
    assert shape.ShapeType() == TopAbs_WIRE


def test_BRepGraphTest_Shape_EdgeKind_Valid(graph):
    shape = graph.Shapes().Shape(BRepGraph_NodeId(Kind.Edge, 0))
    assert not shape.IsNull()
    assert shape.ShapeType() == TopAbs_EDGE


def test_BRepGraphTest_Shape_VertexKind_Valid(graph):
    shape = graph.Shapes().Shape(BRepGraph_NodeId(Kind.Vertex, 0))
    assert not shape.IsNull()
    assert shape.ShapeType() == TopAbs_VERTEX


def test_BRepGraphTest_OwnGen_MutableEdge_PropagatesSubtreeGenUp(graph):
    start = BRepGraph_EdgeId.Start_s()
    assert graph.Topo().Edges().Definition(start).OwnGen == 0

    graph.Editor().Edges().Mut(start).MarkDirty()  # temporary guard, released at end of statement

    assert graph.Topo().Edges().Definition(start).OwnGen > 0
    if start.IsValid(graph.Topo().Edges().Nb()):
        wire_it = graph.Topo().Edges().WiresOf(start)
        if wire_it.More():
            wid = wire_it.CurrentId()
            assert graph.Topo().Wires().Definition(wid).SubtreeGen > 0
            for fid in _ids(BRepGraph_FaceIterator, graph):
                if _face_uses_wire(graph, fid, wid):
                    assert graph.Topo().Faces().Definition(fid).SubtreeGen > 0
                    break


def test_BRepGraphTest_ReconstructShape_WireKind_NoThrow(graph):
    shape = graph.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Wire, 0))
    assert not shape.IsNull()


def test_BRepGraphTest_HasOriginalShape_AfterBuild_True(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert graph.Shapes().HasOriginal(BRepGraph_NodeId(fid))
    for eid in _ids(BRepGraph_EdgeIterator, graph):
        assert graph.Shapes().HasOriginal(BRepGraph_NodeId(eid))


def test_BRepGraphTest_Shape_CachedOnSecondCall(graph):
    node = BRepGraph_NodeId(Kind.Vertex, 0)
    assert graph.Shapes().Shape(node).IsSame(graph.Shapes().Shape(node))


def test_BRepGraphTest_Shape_InvalidatedAfterMutation(graph):
    node = BRepGraph_NodeId(Kind.Edge, 0)
    before = graph.Shapes().Shape(node)
    assert not before.IsNull()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.123)
    after = graph.Shapes().Shape(node)
    assert not after.IsNull()
    assert not before.IsSame(after)


def test_BRepGraphTest_DefaultBuild_AssignsValidUIDs():
    g = _graph_of(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    assert g.Topo().Faces().Nb() > 0
    node = BRepGraph_NodeId(Kind.Face, 0)
    uid = g.UIDs().Of(node)
    assert uid.IsValid()
    assert g.UIDs().Has(uid)
    assert g.UIDs().NodeIdFrom(uid) == node


def test_BRepGraphTest_UIDsGeneration_IncrementsAcrossBuilds():
    g = _graph_of(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    gen1 = g.UIDs().Generation()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(11.0, 21.0, 31.0).Shape())
    gen2 = g.UIDs().Generation()
    assert gen1 > 0
    assert gen2 == gen1 + 1


def test_BRepGraphTest_StaleUID_HasReturnsFalseAfterRebuild():
    box1 = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
    box2 = BRepPrimAPI_MakeBox(11.0, 21.0, 31.0)
    g = _graph_of(box1.Shape())
    assert g.Topo().Faces().Nb() > 0
    old_uid = g.UIDs().Of(BRepGraph_NodeId(Kind.Face, 0))
    assert old_uid.IsValid()
    assert g.UIDs().Has(old_uid)
    g.Clear()
    g.Shapes().Add(box2.Shape())
    assert not g.UIDs().Has(old_uid)
    assert not g.UIDs().NodeIdFrom(old_uid).IsValid()


def test_BRepGraph_UIDsViewTest_ReverseLookupStaysCurrentAfterProgrammaticAdd():
    g = BRepGraph()
    first = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 0.001)
    first_uid = g.UIDs().Of(BRepGraph_NodeId(first))
    assert first_uid.IsValid()
    assert g.UIDs().NodeIdFrom(first_uid) == first

    second = g.Editor().Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 0.001)
    second_uid = g.UIDs().Of(BRepGraph_NodeId(second))
    assert second_uid.IsValid()

    assert g.UIDs().NodeIdFrom(first_uid) == first
    assert g.UIDs().NodeIdFrom(second_uid) == second
    assert g.UIDs().Has(first_uid)
    assert g.UIDs().Has(second_uid)


def test_BRepGraphTest_RecordHistory_MultipleRecords_SequenceNumbers(graph):
    hist = _history(graph)
    before = hist.NbRecords()
    edge0 = BRepGraph_NodeId(Kind.Edge, 0)
    repl = _node_array(BRepGraph_NodeId(Kind.Edge, 1))
    for name in ("OpA", "OpB", "OpC"):
        hist.Record(name, edge0, repl)
    assert hist.NbRecords() == before + 3
    for idx in range(before + 1, before + 3):
        assert hist.Record(idx).SequenceNumber > hist.Record(idx - 1).SequenceNumber
    assert hist.Record(before).OperationName.IsEqual("OpA")
    assert hist.Record(before + 1).OperationName.IsEqual("OpB")
    assert hist.Record(before + 2).OperationName.IsEqual("OpC")


def test_BRepGraphTest_AddPCurve_NewPCurve_RetrievableViaFindPCurveCoEdgeId(graph):
    eid = BRepGraph_EdgeId(0)
    fid = BRepGraph_FaceId(0)
    curve2d = Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0))
    graph.Editor().CoEdges().Add(eid, fid, curve2d, 0.0, 1.0)

    retrieved = Tool.Edge.FindPCurveCoEdgeId_s(graph, eid, fid)
    assert retrieved.IsValid()
    assert graph.Topo().CoEdges().Definition(retrieved).Curve2DRepId.IsValid()
    assert _contains(graph.Topo().Edges().CoEdges(eid), retrieved)
    assert graph.ValidateRelations()


def test_BRepGraphTest_ReplaceEdge_Reversed_OrientationFlipped(graph):
    wire0 = BRepGraph_WireId.Start_s()
    coedges = _coedges_of_wire(graph, wire0)
    assert coedges.Size() >= 1
    orig = graph.Topo().CoEdges().Definition(coedges.Value(0))
    old_edge = orig.ChildEdgeId
    orig_reversed = orig.Orientation.IsReversed

    new_edge = _add_compatible_replacement_edge(graph, old_edge, True)
    assert new_edge.IsValid()
    graph.Editor().Wires().ReplaceEdge(wire0, old_edge, new_edge, True)

    after = _coedges_of_wire(graph, wire0)
    assert after.Size() >= 1
    new_coedge = graph.Topo().CoEdges().Definition(after.Value(0))
    assert new_coedge.ChildEdgeId.Index == new_edge.Index
    assert new_coedge.Orientation.IsReversed == (not orig_reversed)


def test_BRepGraphTest_ReplaceEdge_UpdatesEdgeToCoEdgeRelations(graph):
    wire0 = BRepGraph_WireId.Start_s()
    coedges = _coedges_of_wire(graph, wire0)
    assert coedges.Size() >= 1
    ceid = coedges.Value(0)
    old_edge = graph.Topo().CoEdges().Definition(ceid).ChildEdgeId
    new_edge = _add_compatible_replacement_edge(graph, old_edge, False)
    assert new_edge.IsValid()

    def has_coedge(eid):
        return _contains(graph.Topo().Edges().CoEdges(eid), ceid)

    assert has_coedge(old_edge)
    graph.Editor().Wires().ReplaceEdge(wire0, old_edge, new_edge, False)
    assert not has_coedge(old_edge)
    assert has_coedge(new_edge)


def test_BRepGraphTest_RemoveCoEdge_PrunesOrphanAndKeepsRelationsConsistent(graph):
    wire0 = BRepGraph_WireId.Start_s()
    before = list(_coedges_of_wire(graph, wire0))
    assert len(before) >= 1
    ceid = before[0]
    eid = graph.Topo().CoEdges().Definition(ceid).ChildEdgeId

    assert graph.Editor().Wires().RemoveCoEdge(wire0, ceid)

    after = list(_coedges_of_wire(graph, wire0))
    assert len(after) == len(before) - 1
    assert ceid.IsRemoved(graph)
    assert graph.Editor().ValidateMutationBoundary()
    for wid in graph.Topo().Edges().WiresOf(eid):
        assert wid != wire0
    for other in graph.Topo().Edges().CoEdges(eid):
        assert other != ceid


def test_BRepGraphTest_CleanupRemovedRefs_ManuallyRemovedEdge_UnbindsEdgeWireRelations(graph):
    wire0 = BRepGraph_WireId.Start_s()
    coedges = _coedges_of_wire(graph, wire0)
    assert coedges.Size() >= 1
    ceid = coedges.Value(0)
    eid = graph.Topo().CoEdges().Definition(ceid).ChildEdgeId
    assert _contains(graph.Topo().Edges().WiresOf(eid), wire0)

    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(eid))
    graph.Editor().Gen().CleanupRemovedReferences()

    assert ceid.IsRemoved(graph)
    assert not _contains(graph.Topo().Edges().WiresOf(eid), wire0)
    assert graph.Editor().ValidateMutationBoundary()


def test_BRepGraphTest_RemoveChild_PreservesSharedChildAndKeepsRelationsConsistent(graph):
    compound = graph.Editor().Compounds().Add(_node_array(BRepGraph_NodeId(BRepGraph_SolidId.Start_s())))
    assert compound.IsValid()
    refs_before = _child_refs_of_compound(graph, compound)
    assert refs_before.Size() == 1
    child_ref = refs_before.Value(0)
    child = graph.Refs().Children().Entry(child_ref).ChildNodeId

    assert graph.Editor().Compounds().RemoveChild(compound, child_ref)

    assert _child_refs_of_compound(graph, compound).Size() == 0
    assert not graph.Topo().Gen().IsRemoved(child)
    assert graph.Editor().ValidateMutationBoundary()
    assert graph.Topo().Gen().CompoundRefIds(BRepGraph_NodeId(compound)).Size() == 0


def test_BRepGraphTest_RemoveChild_UsesDistinctRefsForSharedChild(graph):
    assert graph.Topo().Solids().Nb() > 0
    solid = BRepGraph_SolidId.Start_s()
    solid_node = BRepGraph_NodeId(solid)
    first = graph.Editor().Compounds().Add(_node_array(solid_node))
    assert first.IsValid()
    second = graph.Editor().Compounds().Add(_empty_node_array())
    assert second.IsValid()

    first_refs = _child_refs_of_compound(graph, first)
    assert first_refs.Size() == 1
    first_ref = first_refs.Value(0)
    second_ref = graph.Editor().Compounds().Append(second, solid_node)
    assert second_ref.IsValid()
    assert first_ref != second_ref
    graph.Editor().Gen().CleanupRemovedReferences()

    assert BRepGraph_Validate.Perform_s(graph, BRepGraph_Validate.Options.Audit_s()).IsValid()

    def compounds_of_solid():
        return _parents(BRepGraph_CompoundsOfChild, graph, graph.Topo().Gen().CompoundRefIds(solid_node))

    before = compounds_of_solid()
    assert _contains(before, first)
    assert _contains(before, second)

    assert graph.Editor().Compounds().RemoveChild(first, first_ref)
    assert first_ref.IsRemoved(graph)
    assert not second_ref.IsRemoved(graph)
    after_first = compounds_of_solid()
    assert not _contains(after_first, first)
    assert _contains(after_first, second)
    assert _child_refs_of_compound(graph, first).Size() == 0
    assert _child_refs_of_compound(graph, second).Size() == 1

    assert graph.Editor().Compounds().RemoveChild(second, second_ref)
    assert second_ref.IsRemoved(graph)
    assert not _contains(compounds_of_solid(), second)
    assert graph.Editor().ValidateMutationBoundary()


def test_BRepGraphTest_RemoveFace_PrunesOrphanAndKeepsRelationsConsistent(graph):
    shell0 = BRepGraph_ShellId.Start_s()
    refs_before = graph.Refs().Faces().IdsOf(shell0)
    assert refs_before.Size() >= 1
    nb_before = refs_before.Size()
    face_ref = refs_before.Value(0)
    fid = graph.Refs().Faces().Entry(face_ref).ChildFaceId

    assert graph.Editor().Shells().RemoveFace(shell0, face_ref)

    assert graph.Refs().Faces().IdsOf(shell0).Size() == nb_before - 1
    assert fid.IsRemoved(graph)
    assert graph.Editor().ValidateMutationBoundary()
    for sid in _parents(BRepGraph_SolidsOfShell, graph, graph.Topo().Shells().Relations(shell0).ParentShellRefIds):
        assert sid != BRepGraph_SolidId()
    for shid in _parents(BRepGraph_ShellsOfFace, graph, graph.Topo().Faces().Relations(fid).ParentFaceRefIds):
        assert shid != shell0


def test_BRepGraphTest_RemoveShell_PrunesOrphanAndKeepsRelationsConsistent(graph):
    solid0 = BRepGraph_SolidId.Start_s()
    refs_before = graph.Refs().Shells().IdsOf(solid0)
    assert refs_before.Size() >= 1
    nb_before = refs_before.Size()
    shell_ref = refs_before.Value(0)
    shid = graph.Refs().Shells().Entry(shell_ref).ChildShellId

    assert graph.Editor().Solids().RemoveShell(solid0, shell_ref)

    assert graph.Refs().Shells().IdsOf(solid0).Size() == nb_before - 1
    assert shid.IsRemoved(graph)
    assert graph.Editor().ValidateMutationBoundary()
    for csid in _parents(BRepGraph_CompSolidsOfSolid, graph, graph.Topo().Solids().Relations(solid0).ParentSolidRefIds):
        assert csid != BRepGraph_CompSolidId()
    for sid in _parents(BRepGraph_SolidsOfShell, graph, graph.Topo().Shells().Relations(shid).ParentShellRefIds):
        assert sid != solid0


def test_BRepGraphTest_RemoveWire_PrunesOrphanAndKeepsRelationsConsistent(graph):
    wire0 = BRepGraph_WireId.Start_s()
    found = None
    for fid in _ids(BRepGraph_FaceIterator, graph):
        for wref in _wire_refs_of_face(graph, fid):
            if graph.Refs().Wires().Entry(wref).ChildWireId == wire0:
                found = (fid, wref)
                break
        if found is not None:
            break
    assert found is not None
    fid, wref = found
    nb_before = _wire_refs_of_face(graph, fid).Size()

    assert graph.Editor().Faces().RemoveWire(fid, wref)

    assert _wire_refs_of_face(graph, fid).Size() == nb_before - 1
    assert not _face_uses_wire(graph, fid, wire0)
    assert wire0.IsRemoved(graph)
    assert graph.Editor().ValidateMutationBoundary()
    for wfid in _parents(BRepGraph_FacesOfWire, graph, graph.Topo().Wires().Relations(wire0).ParentWireRefIds):
        assert wfid != fid


def test_BRepGraphTest_RemoveOccurrence_PrunesOccurrenceSubtreeAndKeepsRelationsConsistent(graph):
    part = BRepGraph_ProductId.Start_s()
    assembly = graph.Editor().Products().Add()
    graph.Editor().Products().AppendDocumentRoot(assembly)
    assert assembly.IsValid()
    occ = graph.Editor().Products().Append(assembly, part, TopLoc_Location())
    assert occ.IsValid()

    occ_refs = graph.Refs().Occurrences().IdsOf(assembly)
    assert occ_refs.Size() == 1
    occ_ref = occ_refs.Value(0)

    assert graph.Editor().Products().RemoveOccurrence(assembly, occ_ref)

    assert graph.Refs().Occurrences().IdsOf(assembly).Size() == 0
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(occ))
    assert graph.Topo().Products().NbComponents(assembly) == 0
    assert graph.Editor().ValidateMutationBoundary()


def test_BRepGraphTest_RemoveShapeRoot_PrunesUniqueTopologyRoot(graph):
    part = BRepGraph_ProductId.Start_s()
    root_before = graph.Topo().Products().ShapeRoot(part)
    assert root_before.IsValid()

    assert graph.Editor().Products().RemoveShapeRoot(part)

    assert not graph.Topo().Products().ShapeRoot(part).IsValid()
    assert graph.Topo().Gen().IsRemoved(root_before)
    assert not graph.Topo().Products().IsPart(part)
    assert not graph.Topo().Products().IsAssembly(part)
    assert graph.Topo().Products().NbComponents(part) == 0
    assert graph.Editor().ValidateMutationBoundary()


def test_BRepGraphTest_RemoveVertex_ClearsBoundarySlotAndPrunesUniqueVertex(graph):
    tol = Precision.Confusion_s()
    v_start = graph.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), tol)
    v_end = graph.Editor().Vertices().Add(gp_Pnt(10.0, 0.0, 0.0), tol)
    assert v_start.IsValid()
    assert v_end.IsValid()
    edge = graph.Editor().Edges().Add(v_start, v_end, None, 0.0, 1.0, tol)
    assert edge.IsValid()

    start_ref = graph.Topo().Edges().Definition(edge).StartVertexRefId
    assert start_ref.IsValid()

    assert graph.Editor().Edges().RemoveVertex(edge, start_ref)

    assert not graph.Topo().Edges().Definition(edge).StartVertexRefId.IsValid()
    assert graph.Topo().Gen().IsRemoved(BRepGraph_NodeId(v_start))
    assert not Tool.Edge.StartVertexId_s(graph, edge).IsValid()
    assert Tool.Edge.EndVertexId_s(graph, edge).IsValid()
    assert graph.Editor().ValidateMutationBoundary()


def test_BRepGraphTest_RemoveNode_EdgeWithReplacement_ReparentsAllCoEdges(graph):
    coedges = _coedges_of_wire(graph, BRepGraph_WireId.Start_s())
    assert coedges.Size() >= 1
    old_edge = graph.Topo().CoEdges().Definition(coedges.Value(0)).ChildEdgeId
    new_edge = BRepGraph_EdgeId((old_edge.Index + 1) % graph.Topo().Edges().Nb())

    graph.Editor().Gen().ReplaceNode(BRepGraph_NodeId(old_edge), BRepGraph_NodeId(new_edge))

    assert graph.Topo().Edges().CoEdges(old_edge).Size() == 0
    new_coedges = graph.Topo().Edges().CoEdges(new_edge)
    assert new_coedges.Size() > 0
    for ceid in new_coedges:
        assert graph.Topo().CoEdges().Definition(ceid).ChildEdgeId == new_edge


def test_BRepGraphTest_MutableVertex_ChangePoint_Verified(graph):
    start = BRepGraph_VertexId.Start_s()
    mut = graph.Editor().Vertices().Mut(start)
    graph.Editor().Vertices().SetPoint(mut, gp_Pnt(99.0, 99.0, 99.0))
    vert = graph.Topo().Vertices().Definition(start)
    tol = Precision.Confusion_s()
    assert abs(vert.Point.X() - 99.0) <= tol
    assert abs(vert.Point.Y() - 99.0) <= tol
    assert abs(vert.Point.Z() - 99.0) <= tol
    del mut


def test_BRepGraphTest_EdgeDef_HasValidCurve3d(graph):
    for eid in _ids(BRepGraph_EdgeIterator, graph):
        if Tool.Edge.Degenerated_s(graph, eid):
            continue
        assert Tool.Edge.HasCurve_s(graph, eid)


def test_BRepGraphTest_FreeEdges_SingleFace_AllEdgesFree():
    g = _graph_of(_first_face(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()))
    assert not g.IsEmpty()
    assert len(_collect_free_edges(g)) == 4


def test_BRepGraphTest_Decompose_ThreeDisconnectedFaces_ThreeComponents():
    faces = [_first_face(BRepPrimAPI_MakeBox(s, s, s).Shape()) for s in (10.0, 20.0, 30.0)]
    g = _graph_of(_compound(*faces))
    assert not g.IsEmpty()
    assert g.Topo().Faces().Nb() == 3
    assert _count_face_components(g) == 3


def test_BRepGraphTest_DetectToleranceConflicts_ManualConflict_Detected(graph):
    def usable(eid):
        return not Tool.Edge.Degenerated_s(graph, eid) and Tool.Edge.HasCurve_s(graph, eid)

    nb_edges = graph.Topo().Edges().Nb()
    is_conflict_set_up = False
    for i in range(nb_edges):
        eid = BRepGraph_EdgeId(i)
        if is_conflict_set_up:
            break
        if not usable(eid):
            continue
        for j in range(i + 1, nb_edges):
            other = BRepGraph_EdgeId(j)
            if not usable(other):
                continue
            if Tool.Edge.Curve_s(graph, eid) is not Tool.Edge.Curve_s(graph, other):
                continue
            graph.Editor().Edges().SetTolerance(eid, 0.001)
            graph.Editor().Edges().SetTolerance(other, 1.0)
            is_conflict_set_up = True
            break

    if is_conflict_set_up:
        conflicts = []
        keys = set()
        for eid in _ids(BRepGraph_EdgeIterator, graph):
            if not usable(eid):
                continue
            curve = Tool.Edge.Curve_s(graph, eid)
            min_tol = max_tol = graph.Topo().Edges().Definition(eid).Tolerance
            curve_edges = [eid]
            for other in _ids(BRepGraph_EdgeIterator, graph):
                if other == eid or not usable(other) or Tool.Edge.Curve_s(graph, other) is not curve:
                    continue
                tol = graph.Topo().Edges().Definition(other).Tolerance
                min_tol = min(min_tol, tol)
                max_tol = max(max_tol, tol)
                curve_edges.append(other)
            if len(curve_edges) > 1 and max_tol - min_tol > 0.5:
                for c in curve_edges:
                    if c.Index not in keys:
                        keys.add(c.Index)
                        conflicts.append(c)
        assert len(conflicts) >= 1


def test_BRepGraphTest_Build_EmptyCompound_IsEmptyZeroCounts():
    g = _graph_of(_compound())
    assert not g.IsEmpty()
    topo = g.Topo()
    for name in ("Solids", "Shells", "Faces", "Wires", "Edges", "Vertices"):
        assert getattr(topo, name)().Nb() == 0, name


def test_BRepGraphTest_TopoNode_GenericLookup_MatchesTypedAccess(graph):
    assert graph.Topo().Gen().TopoEntity(BRepGraph_NodeId(Kind.Face, 0)) is not None
    assert graph.Topo().Gen().TopoEntity(BRepGraph_NodeId()) is None


def test_BRepGraphTest_NbNodes_Box_TotalCount(graph):
    topo = graph.Topo()
    expected = sum(
        getattr(topo, name)().Nb()
        for name in ("Solids", "Shells", "Faces", "Wires", "CoEdges", "Edges", "Vertices",
                     "Compounds", "CompSolids", "Products", "Occurrences")
    )
    assert topo.Gen().NbNodes() == expected


def test_BRepGraphTest_HasUID_ValidFace_ReturnsTrue(graph):
    uid = graph.UIDs().Of(BRepGraph_NodeId(Kind.Face, 0))
    assert graph.UIDs().Has(uid)


def test_BRepGraphTest_HasUID_InvalidUID_ReturnsFalse(graph):
    assert not graph.UIDs().Has(BRepGraph_UID.Invalid_s())


def test_BRepGraphTest_NodeIdFromUID_InvalidUID_ReturnsInvalid(graph):
    assert not graph.UIDs().NodeIdFrom(BRepGraph_UID.Invalid_s()).IsValid()


def test_BRepGraphTest_Allocator_DefaultConstructor_NotNull(graph):
    assert graph.Allocator() is not None


def test_BRepGraphTest_Build_DefaultAllocator_IsNotEmpty():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    assert g.Topo().Faces().Nb() == 6
    assert g.Allocator() is not None


def test_BRepGraphTest_Wire_IsClosed_BoxOuterWires(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        outer = Tool.Face.OuterWire_s(graph, fid)
        assert outer.IsValid()
        assert Tool.Wire.IsClosed_s(graph, outer)


def test_BRepGraphTest_Face_InnerWireRefs_BoxHasNone(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert _wire_refs_of_face(graph, fid).Size() == 1


def test_BRepGraphTest_Face_Orientation_ValidValue(graph):
    # FaceRef.Orientation is a ParityOrientation (FORWARD or REVERSED only by construction).
    assert graph.Topo().Shells().Nb() == 1
    for ref in graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s()):
        assert graph.Refs().Faces().Entry(ref).Orientation.IsReversed in (True, False)


def test_BRepGraphTest_Shell_ContainsSixFaces(graph):
    assert graph.Topo().Shells().Nb() == 1
    assert graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s()).Size() == 6


def test_BRepGraphTest_Solid_ContainsOneShell(graph):
    assert graph.Topo().Solids().Nb() == 1
    assert graph.Refs().Shells().IdsOf(BRepGraph_SolidId.Start_s()).Size() == 1


def test_BRepGraphTest_Edge_ParamRange_ValidBounds(graph):
    for eid in _ids(BRepGraph_EdgeIterator, graph):
        if Tool.Edge.Degenerated_s(graph, eid):
            continue
        first, last = Tool.Edge.Range_s(graph, eid)
        assert first < last


def test_BRepGraphTest_Vertex_TolerancePositive(graph):
    for vid in _ids(BRepGraph_VertexIterator, graph):
        assert Tool.Vertex.Tolerance_s(graph, vid) > 0.0


def test_BRepGraphTest_Edge_TolerancePositive(graph):
    for eid in _ids(BRepGraph_EdgeIterator, graph):
        assert Tool.Edge.Tolerance_s(graph, eid) > 0.0


def test_BRepGraphTest_Face_ToleranceNonNegative(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert Tool.Face.Tolerance_s(graph, fid) >= 0.0


def test_BRepGraphTest_Wire_IsClosed_DerivedFromCoedgeChain(graph):
    outer = Tool.Face.OuterWire_s(graph, BRepGraph_FaceId.Start_s())
    assert outer.IsValid()
    assert Tool.Wire.IsClosed_s(graph, outer)


def test_BRepGraphTest_Build_SingleFace_CorrectCounts():
    g = _graph_of(_first_face(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()))
    assert not g.IsEmpty()
    topo = g.Topo()
    assert topo.Solids().Nb() == 0
    assert topo.Shells().Nb() == 0
    assert topo.Faces().Nb() == 1
    assert topo.Wires().Nb() == 1
    assert topo.Edges().Nb() == 4
    assert topo.Vertices().Nb() == 4


def _first_shell_of_box():
    exp = TopExp_Explorer(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), TopAbs_SHELL)
    assert exp.More()
    return exp.Current()


def test_BRepGraphTest_Build_Shell_CorrectCounts():
    g = _graph_of(_first_shell_of_box())
    assert not g.IsEmpty()
    topo = g.Topo()
    assert topo.Solids().Nb() == 0
    assert topo.Shells().Nb() == 1
    assert topo.Faces().Nb() == 6
    assert topo.Edges().Nb() == 12
    assert topo.Vertices().Nb() == 8


def test_BRepGraphTest_Build_CompoundOfTwoSolids():
    g = _graph_of(_compound(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), BRepPrimAPI_MakeBox(20.0, 20.0, 20.0).Shape()))
    assert not g.IsEmpty()
    assert g.Topo().Solids().Nb() == 2
    assert g.Topo().Shells().Nb() == 2
    assert g.Topo().Faces().Nb() == 12


def test_BRepGraphTest_ReconstructShape_ShellRoot_SameFaceCount():
    g = _graph_of(_first_shell_of_box())
    assert not g.IsEmpty()
    assert g.Topo().Shells().Nb() == 1
    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Shell, 0))
    assert len(list(TopExp_Explorer(recon, TopAbs_FACE))) == 6


def test_BRepGraphTest_UID_FaceIsTopology(graph):
    assert graph.UIDs().Of(BRepGraph_NodeId(Kind.Face, 0)).IsTopology()


def test_BRepGraphTest_UID_AllTopoNodesHaveValidUIDs(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        assert graph.UIDs().Of(BRepGraph_NodeId(fid)).IsValid()
    for eid in _ids(BRepGraph_EdgeIterator, graph):
        assert graph.UIDs().Of(BRepGraph_NodeId(eid)).IsValid()


def test_BRepGraphTest_Wire_OuterWireIdx_MatchesFaceDef(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        outer = Tool.Face.OuterWire_s(graph, fid)
        assert outer.IsValid()
        assert outer.Index < graph.Topo().Wires().Nb()


def test_BRepGraphTest_Wire_CoEdges_FourEdgesPerBoxFace(graph):
    for fid in _ids(BRepGraph_FaceIterator, graph):
        outer = Tool.Face.OuterWire_s(graph, fid)
        assert outer.IsValid()
        assert _coedges_of_wire(graph, outer).Size() == 4


def test_BRepGraphTest_SetHistoryEnabled_DefaultTrue(graph):
    assert _history(graph).IsEnabled()


def test_BRepGraphTest_SetHistoryEnabled_DisableAndQuery(graph):
    _history(graph).SetEnabled(False)
    assert not _history(graph).IsEnabled()
    _history(graph).SetEnabled(True)
    assert _history(graph).IsEnabled()


def test_BRepGraphTest_RecordHistory_Disabled_NoRecordAdded(graph):
    hist = _history(graph)
    before = hist.NbRecords()
    hist.SetEnabled(False)
    hist.Record("ShouldNotRecord", BRepGraph_NodeId(Kind.Edge, 0), _node_array(BRepGraph_NodeId(Kind.Edge, 1)))
    assert hist.NbRecords() == before


def test_BRepGraphTest_RecordHistory_ReEnabled_RecordsAgain(graph):
    hist = _history(graph)
    hist.SetEnabled(False)
    before = hist.NbRecords()
    edge0 = BRepGraph_NodeId(Kind.Edge, 0)
    repl = _node_array(BRepGraph_NodeId(Kind.Edge, 1))
    hist.Record("Skipped", edge0, repl)
    assert hist.NbRecords() == before
    hist.SetEnabled(True)
    hist.Record("Recorded", edge0, repl)
    assert hist.NbRecords() == before + 1
    assert hist.Record(before).OperationName.IsEqual("Recorded")
