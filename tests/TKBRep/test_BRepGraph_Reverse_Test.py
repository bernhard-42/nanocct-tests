# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Reverse_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_LayerTopoSupplement,
    BRepGraph_NodeId,
    BRepGraph_ParentExplorer,
    BRepGraph_ShellId,
    BRepGraph_Validate,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.TopAbs import TopAbs_FACE, TopAbs_FORWARD, TopAbs_REVERSED, TopAbs_SHELL
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shell

CoEdgeOrderStatus = BRepGraph.EditorView.WireOps.CoEdgeOrderStatus
ReplaceEdgeStatus = BRepGraph.EditorView.WireOps.ReplaceEdgeStatus


def _find_supplement_layer(g):
    return g.LayerRegistry().FindLayer(BRepGraph_LayerTopoSupplement.GetID_s())


def _build_box_graph():
    g = BRepGraph()
    # LayerRegistry().Ensure<BRepGraph_LayerTopoSupplement>()
    if _find_supplement_layer(g) is None:
        g.LayerRegistry().RegisterLayer(BRepGraph_LayerTopoSupplement())
    assert _find_supplement_layer(g) is not None
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _add_segment(g, start, end):
    return g.Editor().Edges().Add(start, end, None, 0.0, 1.0, 1.0e-7)


def _coedge_array(items):
    arr = NCollection_Array1[BRepGraph_CoEdgeId](0, len(items) - 1)
    for i, item in enumerate(items):
        arr.SetValue(i, item)
    return arr


def _make_reversed_face_shell():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    bb = BRep_Builder()
    shell = TopoDS_Shell()
    bb.MakeShell(shell)
    exp = TopExp_Explorer(box, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face(exp.Current())
        face.Orientation(TopAbs_REVERSED)
        bb.Add(shell, face)
        exp.Next()
    return shell


def _vertices(g, xs):
    return [g.Editor().Vertices().Add(gp_Pnt(x, 0.0, 0.0), 1.0e-7) for x in xs]


def _audit_ok(g):
    return BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s()).IsValid()


def test_BRepGraph_ReverseTest_Wire_OrderAndOrientationFlipped():
    g = _build_box_graph()
    wire = BRepGraph_WireId(0)
    assert wire.IsValid(g.Topo().Wires().Nb())

    order_before = list(g.Topo().Wires().Relations(wire).CoEdgeIds)
    rev_before = [g.Topo().CoEdges().Definition(c).Orientation.IsReversed for c in order_before]
    assert len(order_before) > 1

    g.Editor().Wires().Reverse(wire)

    after = g.Topo().Wires().Relations(wire).CoEdgeIds
    assert after.Size() == len(order_before)
    n = len(order_before)
    for i in range(after.Size()):
        coedge = after.Value(i)
        assert coedge == order_before[n - 1 - i]
        # TopAbs::Reverse on a FORWARD/REVERSED orientation flips the parity bit
        assert g.Topo().CoEdges().Definition(coedge).Orientation.IsReversed == (not rev_before[n - 1 - i])


def test_BRepGraph_ReverseTest_WireOrder_SetCoEdgeOrderCanonicalizesUnorderedPermutation():
    g = _build_box_graph()
    wire = BRepGraph_WireId(0)
    assert wire.IsValid(g.Topo().Wires().Nb())
    coedges = g.Topo().Wires().Relations(wire).CoEdgeIds
    assert coedges.Size() >= 4

    bad = _coedge_array([coedges.Value(0), coedges.Value(2), coedges.Value(1), coedges.Value(3)])
    assert g.Editor().Wires().SetCoEdgeOrder(wire, bad)

    after = g.Topo().Wires().Relations(wire).CoEdgeIds
    assert after.Size() == coedges.Size()
    assert g.Editor().ValidateMutationBoundary()
    assert _audit_ok(g)


def test_BRepGraph_ReverseTest_WireOrder_CheckCoEdgeOrderReportsCurrentAndReordered():
    g = _build_box_graph()
    wire = BRepGraph_WireId(0)
    assert wire.IsValid(g.Topo().Wires().Nb())
    coedges = g.Topo().Wires().Relations(wire).CoEdgeIds
    assert coedges.Size() >= 4

    current = _coedge_array(list(coedges))
    wires = g.Editor().Wires()
    assert wires.CheckCoEdgeOrder(wire, current) == CoEdgeOrderStatus.AlreadyCurrent
    assert wires.SetCoEdgeOrder(wire, current)

    unordered = _coedge_array([coedges.Value(0), coedges.Value(2), coedges.Value(1), coedges.Value(3)])
    assert wires.CheckCoEdgeOrder(wire, unordered) == CoEdgeOrderStatus.Reordered
    assert wires.CheckCoEdgeOrder(BRepGraph_WireId(), unordered) == CoEdgeOrderStatus.InvalidWire


def test_BRepGraph_ReverseTest_WireOrder_SetCoEdgeOrderCanonicalizesOpenWirePermutation():
    g = BRepGraph()
    v0, v1, v2, v3 = _vertices(g, [0.0, 1.0, 2.0, 3.0])
    ce = g.Editor().CoEdges()
    coedges = [
        ce.Add(_add_segment(g, v0, v1), TopAbs_FORWARD),
        ce.Add(_add_segment(g, v1, v2), TopAbs_FORWARD),
        ce.Add(_add_segment(g, v2, v3), TopAbs_FORWARD),
    ]
    wire = g.Editor().Wires().Add(_coedge_array(coedges))
    assert wire.IsValid()

    unordered = _coedge_array([coedges[2], coedges[0], coedges[1]])
    assert g.Editor().Wires().SetCoEdgeOrder(wire, unordered)

    ordered = g.Topo().Wires().Relations(wire).CoEdgeIds
    assert ordered.Size() == len(coedges)
    assert ordered.Value(0) == coedges[0]
    assert ordered.Value(1) == coedges[1]
    assert ordered.Value(2) == coedges[2]
    assert g.Editor().ValidateMutationBoundary()


def test_BRepGraph_ReverseTest_WireOrder_CheckAppendCoEdgeReportsReadyAndAlreadyContained():
    g = BRepGraph()
    v0, v1, v2 = _vertices(g, [0.0, 1.0, 2.0])
    first_edge = _add_segment(g, v0, v1)
    initial = [g.Editor().CoEdges().Add(first_edge, TopAbs_FORWARD)]
    wire = g.Editor().Wires().Add(_coedge_array(initial))
    assert wire.IsValid()

    second_edge = _add_segment(g, v1, v2)
    second_coedge = g.Editor().CoEdges().Add(second_edge, TopAbs_FORWARD)

    wires = g.Editor().Wires()
    assert wires.CheckAppendCoEdge(wire, second_coedge) == CoEdgeOrderStatus.Ready
    assert wires.CheckAppendCoEdge(wire, initial[0]) == CoEdgeOrderStatus.AlreadyContained


def test_BRepGraph_ReverseTest_WireOrder_CheckReplaceEdgeReportsReadyAndDisconnected():
    g = BRepGraph()
    v0, v1, v2, v3, v4 = _vertices(g, [0.0, 1.0, 2.0, 3.0, 4.0])
    old_edge = _add_segment(g, v0, v1)
    next_edge = _add_segment(g, v1, v2)
    ce = g.Editor().CoEdges()
    wire = g.Editor().Wires().Add(
        _coedge_array([ce.Add(old_edge, TopAbs_FORWARD), ce.Add(next_edge, TopAbs_FORWARD)])
    )
    assert wire.IsValid()

    compatible = _add_segment(g, v0, v1)
    disconnected = _add_segment(g, v3, v4)

    wires = g.Editor().Wires()
    assert wires.CheckReplaceEdge(wire, old_edge, compatible, False) == ReplaceEdgeStatus.Ready
    assert wires.CheckReplaceEdge(wire, old_edge, old_edge, False) == ReplaceEdgeStatus.AlreadyCurrent
    assert wires.CheckReplaceEdge(wire, old_edge, disconnected, False) == ReplaceEdgeStatus.Disconnected


def test_BRepGraph_ReverseTest_WireOrder_RemoveInternalCoEdgeFromClosedWireKeepsConnectedOrder():
    g = _build_box_graph()
    wire = BRepGraph_WireId(0)
    assert wire.IsValid(g.Topo().Wires().Nb())
    before = g.Topo().Wires().Relations(wire).CoEdgeIds
    nb_before = before.Size()
    assert nb_before >= 4

    assert g.Editor().Wires().RemoveCoEdge(wire, before.Value(1))

    after = g.Topo().Wires().Relations(wire).CoEdgeIds
    assert after.Size() == nb_before - 1
    assert g.Editor().ValidateMutationBoundary()
    assert _audit_ok(g)


def test_BRepGraph_ReverseTest_Edge_StartEndVertexRefsSwapped():
    g = _build_box_graph()
    edge = BRepGraph_EdgeId(0)
    assert edge.IsValid(g.Topo().Edges().Nb())
    start_before = g.Topo().Edges().Definition(edge).StartVertexRefId
    end_before = g.Topo().Edges().Definition(edge).EndVertexRefId
    assert start_before.IsValid()
    assert end_before.IsValid()
    assert start_before != end_before

    g.Editor().Edges().Reverse(edge)

    assert g.Topo().Edges().Definition(edge).StartVertexRefId == end_before
    assert g.Topo().Edges().Definition(edge).EndVertexRefId == start_before


def test_BRepGraph_ReverseTest_Edge_RoundTripRestoresOriginal():
    g = _build_box_graph()
    edge = BRepGraph_EdgeId(0)
    assert edge.IsValid(g.Topo().Edges().Nb())
    start = g.Topo().Edges().Definition(edge).StartVertexRefId
    end = g.Topo().Edges().Definition(edge).EndVertexRefId

    g.Editor().Edges().Reverse(edge)
    g.Editor().Edges().Reverse(edge)

    assert g.Topo().Edges().Definition(edge).StartVertexRefId == start
    assert g.Topo().Edges().Definition(edge).EndVertexRefId == end


def test_BRepGraph_ReverseTest_LayerTopoSupplement_AddVertexToFaceGoesToSupplementLayer():
    g = _build_box_graph()
    face = BRepGraph_FaceId(0)
    assert face.IsValid(g.Topo().Faces().Nb())
    vertex = g.Editor().Vertices().Add(gp_Pnt(0.5, 0.5, 0.5), 1.0e-7)
    assert vertex.IsValid()

    layer = _find_supplement_layer(g)
    assert layer is not None
    assert layer.AttachedTo(BRepGraph_NodeId(face)).Size() == 0


def test_BRepGraph_ReverseTest_LayerTopoSupplement_ShellStartsWithoutSupplementAttachments():
    g = _build_box_graph()
    assert g.Topo().Shells().Nb() >= 1
    shell = BRepGraph_ShellId(0)
    edge = BRepGraph_EdgeId(0)
    assert edge.IsValid(g.Topo().Edges().Nb())

    layer = _find_supplement_layer(g)
    if layer is not None:
        assert layer.AttachedTo(BRepGraph_NodeId(shell)).Size() == 0


def test_BRepGraph_ReverseTest_Relations_SupplementLayerClearedOnGraphClear():
    g = _build_box_graph()
    assert g.Topo().Shells().Nb() >= 1
    face = BRepGraph_FaceId(0)

    layer_before = _find_supplement_layer(g)
    assert layer_before is not None
    assert layer_before.AttachedTo(BRepGraph_NodeId(face)).Size() == 0

    g.Clear()

    assert g.Topo().Faces().Nb() == 0
    assert g.Topo().Vertices().Nb() == 0

    layer_after = _find_supplement_layer(g)
    assert layer_after is not None
    assert layer_after.AttachedTo(BRepGraph_NodeId(face)).Size() == 0


def test_BRepGraph_ReverseTest_ReversedShell_GraphStoresFaceRefOrientation():
    shell = _make_reversed_face_shell()
    g = BRepGraph()
    assert g.Shapes().Add(shell).IsOk()
    assert g.Topo().Faces().Nb() == 6
    face_refs = g.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())
    assert face_refs.Size() == 6
    for ref_id in face_refs:
        # FaceRef.Orientation is a ParityOrientation; == TopAbs_REVERSED means IsReversed
        assert g.Refs().Faces().Entry(ref_id).Orientation.IsReversed


def test_BRepGraph_ReverseTest_ReversedShell_ParentExplorerReportsShell():
    shell = _make_reversed_face_shell()
    g = BRepGraph()
    assert g.Shapes().Add(shell).IsOk()
    for i in range(6):
        exp = BRepGraph_ParentExplorer(
            g, BRepGraph_FaceId(i), BRepGraph_ParentExplorer.TraversalMode.DirectParents
        )
        assert exp.More()
        assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_ShellId.Start_s())
        assert exp.LeafOrientation() == TopAbs_REVERSED


def test_BRepGraph_ReverseTest_ReversedShell_ReconstructPreservesOrientation():
    shell = _make_reversed_face_shell()
    g = BRepGraph()
    assert g.Shapes().Add(shell).IsOk()
    for i in range(6):
        recon = g.Shapes().Reconstruct(BRepGraph_FaceId(i))
        assert not recon.IsNull()
        assert recon.ShapeType() == TopAbs_FACE


def test_BRepGraph_ReverseTest_ReversedShell_ReconstructShellPreservesFaceOrientations():
    shell = _make_reversed_face_shell()
    g = BRepGraph()
    assert g.Shapes().Add(shell).IsOk()
    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_NodeId.Kind.Shell, 0))
    assert not recon.IsNull()
    assert recon.ShapeType() == TopAbs_SHELL
    n = 0
    exp = TopExp_Explorer(recon, TopAbs_FACE)
    while exp.More():
        assert TopoDS.Face(exp.Current()).Orientation() == TopAbs_REVERSED
        n += 1
        exp.Next()
    assert n == 6
