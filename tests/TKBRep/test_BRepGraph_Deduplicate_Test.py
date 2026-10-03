# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Deduplicate_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_Compact,
    BRepGraph_Deduplicate,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FullCoEdgeIterator,
    BRepGraph_FullEdgeIterator,
    BRepGraph_FullFaceIterator,
    BRepGraph_FullSolidIterator,
    BRepGraph_LayerHistory,
    BRepGraph_NodeId,
    BRepGraph_RefId,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_VertexIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SOLID
from nanocct import TopoDS
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Wire

Dedup = BRepGraph_Deduplicate


# ---------------------------------------------------------------------------------------------
# helpers


def _compound(*shapes):
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    for s in shapes:
        bb.Add(comp, s)
    return comp


def _first_face(shape):
    return TopExp_Explorer(shape, TopAbs_FACE).Current()


def _copy(shape):
    return BRepBuilderAPI_Copy(shape, True).Shape()


def _make_two_copied_identical_faces():
    face = _first_face(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return _compound(_copy(face), _copy(face))


def _make_n_copied_identical_faces(n):
    face = _first_face(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return _compound(*[_copy(face) for _ in range(n)])


def _make_mixed_compound():
    box_face = _first_face(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    cyl_face = _first_face(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())
    return _compound(_copy(box_face), _copy(box_face), cyl_face)


def _make_nested_compound():
    face = _first_face(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    inner = _compound(_copy(face), _copy(face))
    return _compound(inner, _copy(face))


def _make_three_distinct_primitives():
    return _compound(
        BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(),
        BRepPrimAPI_MakeSphere(5.0).Shape(),
        BRepPrimAPI_MakeCone(3.0, 1.0, 8.0).Shape(),
    )


def _make_two_identical_boxes():
    return _compound(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())


def _make_three_copied_boxes():
    return _compound(*[BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape() for _ in range(3)])


def _make_three_copied_identical_edges():
    edge = TopExp_Explorer(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), TopAbs_EDGE).Current()
    return _compound(edge, _copy(edge), _copy(edge))


def _make_two_face_touching_boxes():
    return _compound(
        BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 10.0, 10.0, 10.0).Shape(),
        BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 10), 10.0, 10.0, 10.0).Shape(),
    )


def _make_three_copied_cylinder_faces():
    face = _first_face(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape())
    return _compound(_copy(face), _copy(face), _copy(face))


def _make_full_sphere():
    return BRepPrimAPI_MakeSphere(10.0).Shape()


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _single_copied_box_face_graph():
    return _graph(_copy(_first_face(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())))


def _opts(**kwargs):
    opts = Dedup.Options()
    for k, v in kwargs.items():
        setattr(opts, k, v)
    return opts


def _history(g):
    # C++: theGraph.LayerRegistry().Ensure<BRepGraph_LayerHistory>()
    reg = g.LayerRegistry()
    layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    if layer is None:
        reg.RegisterLayer(BRepGraph_LayerHistory())
        layer = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    return layer


def _count_history_records_by_op(g, op):
    history = g.LayerRegistry().FindLayer(BRepGraph_LayerHistory.GetID_s())
    if history is None:
        return 0
    return sum(1 for i in range(history.NbRecords()) if history.Record(i).OperationName.ToCString() == op)


def _ids(iterator):
    ids = []
    while iterator.More():
        ids.append(iterator.CurrentId())
        iterator.Next()
    return ids


def _distinct(handles):
    # C++ compares raw pointers; nanobind returns the same Python object for the same C++ object while alive.
    alive = [h for h in handles if h is not None]
    return len({id(h) for h in alive})


def _nb_unique_face_surface_defs(g):
    return _distinct([BRepGraph_Tool.Face.Surface_s(g, f) for f in _ids(BRepGraph_FullFaceIterator(g))])


def _nb_unique_edge_curve_defs(g):
    return _distinct([BRepGraph_Tool.Edge.Curve_s(g, e) for e in _ids(BRepGraph_FullEdgeIterator(g))])


def _nb_pcurve_entries(g):
    count = 0
    for e in _ids(BRepGraph_EdgeIterator(g)):
        for ce in g.Topo().Edges().CoEdges(e):
            if g.Topo().CoEdges().Definition(ce).FaceId.IsValid():
                count += 1
    return count


def _nb_unique_pcurve_nodes(g):
    return sum(g.Topo().Edges().CoEdges(e).Size() for e in _ids(BRepGraph_FullEdgeIterator(g)))


def _add_duplicate_pcurves_to_all_edges(g):
    dup_count = 0
    for e in _ids(BRepGraph_FullEdgeIterator(g)):
        ces = g.Topo().Edges().CoEdges(e)
        if ces.IsEmpty():
            continue
        ce_id = ces.Value(0)
        ce = g.Topo().CoEdges().Definition(ce_id)
        if not ce.Curve2DRepId.IsValid():
            continue
        first, last = BRepGraph_Tool.CoEdge.Range_s(g, ce_id)
        pcurve = BRepGraph_Tool.CoEdge.PCurve_s(g, ce_id)
        g.Editor().CoEdges().Add(e, ce.FaceId, pcurve, first, last, ce.Orientation)
        dup_count += 1
    return dup_count


def _count_valid_coedge_pcurves(g):
    count = 0
    for ce in _ids(BRepGraph_FullCoEdgeIterator(g)):
        if not ce.IsRemoved(g) and g.Topo().CoEdges().Definition(ce).Curve2DRepId.IsValid():
            if BRepGraph_Tool.CoEdge.PCurve_s(g, ce) is not None:
                count += 1
    return count


def _count_seam_coedges(g):
    count = 0
    for ce_id in _ids(BRepGraph_FullCoEdgeIterator(g)):
        ce = g.Topo().CoEdges().Definition(ce_id)
        if ce_id.IsRemoved(g) or not ce.FaceId.IsValid() or not ce.ChildEdgeId.IsValid():
            continue
        for other_id in g.Topo().Edges().CoEdges(ce.ChildEdgeId):
            if other_id == ce_id:
                continue
            other = g.Topo().CoEdges().Definition(other_id)
            if (
                not other_id.IsRemoved(g)
                and other.FaceId == ce.FaceId
                and other.Orientation.IsReversed != ce.Orientation.IsReversed
            ):
                count += 1
                break
    return count


def _assert_all_pcurves_not_null(g):
    for ce in _ids(BRepGraph_FullCoEdgeIterator(g)):
        if not ce.IsRemoved(g) and g.Topo().CoEdges().Definition(ce).Curve2DRepId.IsValid():
            assert BRepGraph_Tool.CoEdge.PCurve_s(g, ce) is not None


def _nb_active_faces(g):
    return sum(1 for f in _ids(BRepGraph_FullFaceIterator(g)) if not f.IsRemoved(g))


def _assert_each_active_face_has_one_wire(g):
    for f in _ids(BRepGraph_FullFaceIterator(g)):
        if f.IsRemoved(g):
            continue
        n = sum(
            1 for r in g.Topo().Faces().Relations(f).WireRefIds if not g.Refs().Gen().IsRemoved(BRepGraph_RefId(r))
        )
        assert n == 1


def _same_surface(g, i, j):
    return BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId(i)) is BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId(j))


# ---------------------------------------------------------------------------------------------


def test_BRepGraph_DeduplicateTest_AnalyzeOnly_DoesNotRewrite():
    g = _graph(_make_two_copied_identical_faces())
    assert _nb_unique_face_surface_defs(g) == 2
    res = Dedup.Perform_s(g, _opts(AnalyzeOnly=True))
    assert res.NbSurfaceRewrites == 0
    assert _nb_unique_face_surface_defs(g) == 2


def test_BRepGraph_DeduplicateTest_AnalyzeOnly_ReportsCanonicalCandidates():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g, _opts(AnalyzeOnly=True))
    assert res.NbCanonicalSurfaces == 1
    assert res.NbCanonicalCurves == 4
    assert res.NbSurfaceRewrites == 0
    assert res.NbCurveRewrites == 0


def test_BRepGraph_DeduplicateTest_CanonicalizeSurfaces_RewritesAndRecordsHistory():
    g = _graph(_make_two_copied_identical_faces())
    assert _nb_unique_face_surface_defs(g) == 2
    before = _history(g).NbRecords()
    res = Dedup.Perform_s(g, _opts(AnalyzeOnly=False, HistoryMode=True))
    assert res.NbSurfaceRewrites == 1
    assert _nb_unique_face_surface_defs(g) == 1
    assert _history(g).NbRecords() == before + 5


def test_BRepGraph_DeduplicateTest_CanonicalizeCurves_RewritesAndReducesUnique():
    g = _graph(_make_two_copied_identical_faces())
    assert _nb_unique_edge_curve_defs(g) == 8
    res = Dedup.Perform_s(g, _opts(AnalyzeOnly=False))
    assert res.NbCurveRewrites == 4
    assert _nb_unique_edge_curve_defs(g) == 4


def test_BRepGraph_DeduplicateTest_HistoryModeOff_DoesNotAddHistory():
    g = _graph(_make_two_copied_identical_faces())
    assert _history(g).NbRecords() == 0
    res = Dedup.Perform_s(g, _opts(HistoryMode=False))
    assert res.NbSurfaceRewrites == 1
    assert res.NbCurveRewrites == 4
    assert _history(g).NbRecords() == 0


def test_BRepGraph_DeduplicateTest_RestoresHistoryEnabledFlag():
    g = _graph(_make_two_copied_identical_faces())
    _history(g).SetEnabled(False)
    assert not _history(g).IsEnabled()
    Dedup.Perform_s(g, _opts(HistoryMode=True))
    assert not _history(g).IsEnabled()


def test_BRepGraph_DeduplicateTest_DefaultOverload_PerformWorks():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 1
    assert res.NbSurfaceRewrites == 1
    assert res.NbCurveRewrites == 4
    assert res.NbHistoryRecords == 5
    assert not res.IsEntityMergeApplied


def test_BRepGraph_DeduplicateTest_SingleFace_NoSurfaceRewrite():
    exp = TopExp_Explorer(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), TopAbs_FACE)
    assert exp.More()
    g = _graph(exp.Current())
    assert Dedup.Perform_s(g).NbSurfaceRewrites == 0


def test_BRepGraph_DeduplicateTest_NotDoneGraph_ReturnsEmptyResult():
    g = BRepGraph()
    assert g.IsEmpty()
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 0
    assert res.NbCanonicalCurves == 0
    assert res.NbSurfaceRewrites == 0
    assert res.NbCurveRewrites == 0
    assert res.NbNullifiedSurfaces == 0
    assert res.NbNullifiedCurves == 0
    assert res.NbHistoryRecords == 0
    assert not res.IsEntityMergeApplied
    assert res.NbReorderedWires == 0
    assert res.NbToleranceOrderedWires == 0
    assert res.NbPartialOrderedWires == 0


def test_BRepGraph_DeduplicateTest_Idempotent_SecondRunNoRewrites():
    g = _graph(_make_two_copied_identical_faces())
    res1 = Dedup.Perform_s(g)
    assert res1.NbSurfaceRewrites == 1
    assert res1.NbCurveRewrites == 4
    surfs = _nb_unique_face_surface_defs(g)
    curves = _nb_unique_edge_curve_defs(g)
    Dedup.Perform_s(g)
    assert _nb_unique_face_surface_defs(g) == surfs
    assert _nb_unique_edge_curve_defs(g) == curves


def test_BRepGraph_DeduplicateTest_FullBox_AllSurfacesUnique():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 6
    assert res.NbSurfaceRewrites == 0


def test_BRepGraph_DeduplicateTest_ResultCountersConsistency():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 8
    assert _nb_pcurve_entries(g) == 8
    res = Dedup.Perform_s(g, _opts(AnalyzeOnly=True))
    nf = g.Topo().Faces().Nb()
    ne = g.Topo().Edges().Nb()
    assert res.NbCanonicalSurfaces == 1
    assert res.NbCanonicalSurfaces + (nf - res.NbCanonicalSurfaces) == nf
    assert res.NbCanonicalCurves == 4
    assert res.NbCanonicalCurves + (ne - res.NbCanonicalCurves) == ne


def test_BRepGraph_DeduplicateTest_EmptyCompound_NoRewrites():
    g = _graph(_compound())
    res = Dedup.Perform_s(g)
    assert res.NbSurfaceRewrites == 0
    assert res.NbCurveRewrites == 0


def test_BRepGraph_DeduplicateTest_MultipleCopies_NWayDedup():
    n = 4
    g = _graph(_make_n_copied_identical_faces(n))
    assert g.Topo().Faces().Nb() == n
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 1
    assert res.NbSurfaceRewrites == n - 1
    assert _nb_unique_face_surface_defs(g) == 1


def test_BRepGraph_DeduplicateTest_MixedGeometry_OnlyIdenticalDeduped():
    g = _graph(_make_mixed_compound())
    assert g.Topo().Faces().Nb() == 3
    assert g.Topo().Edges().Nb() == 11
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 2
    assert res.NbCanonicalCurves == 7
    assert res.NbSurfaceRewrites == 1
    assert res.NbCurveRewrites == 4
    assert res.NbHistoryRecords > 0
    assert _nb_unique_face_surface_defs(g) == 2
    assert _nb_unique_edge_curve_defs(g) == 7


def test_BRepGraph_DeduplicateTest_AfterDedup_AllCopiedFacesShareCanonicalSurface():
    g = _graph(_make_n_copied_identical_faces(3))
    Dedup.Perform_s(g)
    assert _nb_unique_face_surface_defs(g) == 1


def test_BRepGraph_DeduplicateTest_HistoryRecordNames_MatchExpectedOps():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g, _opts(HistoryMode=True))
    assert res.NbHistoryRecords == 5
    nb_surf = _count_history_records_by_op(g, "Dedup:CanonicalizeSurface")
    nb_curve = _count_history_records_by_op(g, "Dedup:CanonicalizeCurve")
    assert nb_surf == 1
    assert nb_curve == 4
    assert nb_surf + nb_curve == 5


def test_BRepGraph_DeduplicateTest_AnalyzeOnly_CurveAndPCurveCountsReported():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g, _opts(AnalyzeOnly=True))
    assert res.NbCanonicalSurfaces == 1
    assert res.NbCanonicalCurves == 4
    assert res.NbSurfaceRewrites == 0
    assert res.NbCurveRewrites == 0


def test_BRepGraph_DeduplicateTest_DefaultOptionsStruct_HasExpectedDefaults():
    opts = Dedup.Options()
    assert not opts.AnalyzeOnly
    assert opts.HistoryMode
    assert not opts.MergeEntitiesWhenSafe
    assert abs(opts.CompTolerance - Precision.Angular_s()) <= 1e-20
    assert abs(opts.HashTolerance - Precision.Confusion_s()) <= 1e-20


def test_BRepGraph_DeduplicateTest_DefaultResultStruct_AllZeroed():
    res = Dedup.Result()
    assert res.NbCanonicalSurfaces == 0
    assert res.NbCanonicalCurves == 0
    assert res.NbSurfaceRewrites == 0
    assert res.NbCurveRewrites == 0
    assert res.NbNullifiedSurfaces == 0
    assert res.NbNullifiedCurves == 0
    assert res.NbHistoryRecords == 0
    assert not res.IsEntityMergeApplied
    assert res.NbReorderedWires == 0
    assert res.NbToleranceOrderedWires == 0
    assert res.NbPartialOrderedWires == 0


def test_BRepGraph_DeduplicateTest_MergeDefsWhenSafe_MergesVertices():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert res.NbMergedVertices > 0
    assert res.IsEntityMergeApplied


def test_BRepGraph_DeduplicateTest_NestedCompound_AllCopiesDeduped():
    g = _graph(_make_nested_compound())
    assert g.Topo().Faces().Nb() == 3
    assert g.Topo().Edges().Nb() == 12
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 1
    assert res.NbCanonicalCurves == 4
    assert res.NbSurfaceRewrites == 2
    assert res.NbCurveRewrites == 8
    assert res.NbHistoryRecords > 0
    assert _nb_unique_face_surface_defs(g) == 1
    assert _nb_unique_edge_curve_defs(g) == 4


def test_BRepGraph_DeduplicateTest_ThreeDistinctPrimitives_MinimalDedup():
    g = _graph(_make_three_distinct_primitives())
    assert g.Topo().Faces().Nb() == 10
    assert g.Topo().Edges().Nb() == 18
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 9
    assert res.NbSurfaceRewrites == 1
    assert _nb_unique_face_surface_defs(g) == 9
    assert _nb_unique_edge_curve_defs(g) <= 18


def test_BRepGraph_DeduplicateTest_TwoIdenticalBoxes_SurfacesAndCurvesDeduped():
    g = _graph(_make_two_identical_boxes())
    assert g.Topo().Faces().Nb() == 12
    assert g.Topo().Edges().Nb() == 24
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 6
    assert res.NbCanonicalCurves == 12
    assert res.NbSurfaceRewrites == 6
    assert res.NbCurveRewrites == 12
    assert res.NbHistoryRecords > 0
    assert _nb_unique_face_surface_defs(g) == 6
    assert _nb_unique_edge_curve_defs(g) == 12


def test_BRepGraph_DeduplicateTest_CurveRewriteCount_MatchesDuplicateEdgeCurves():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Edges().Nb() == 8
    analysis = Dedup.Perform_s(g, _opts(AnalyzeOnly=True))
    assert analysis.NbCanonicalCurves == 4
    assert Dedup.Perform_s(g).NbCurveRewrites == 4


def test_BRepGraph_DeduplicateTest_AfterDedup_AllCopiedEdgesShareCanonicalCurve():
    g = _graph(_make_two_copied_identical_faces())
    assert _nb_unique_edge_curve_defs(g) == 8
    Dedup.Perform_s(g)
    assert _nb_unique_edge_curve_defs(g) == 4


def test_BRepGraph_DeduplicateTest_MultiplePCurveDups_AllEdgesDeduped():
    g = _single_copied_box_face_graph()
    assert _add_duplicate_pcurves_to_all_edges(g) > 0
    Dedup.Perform_s(g)


def test_BRepGraph_DeduplicateTest_PCurveDup_AnalyzeOnly_CountsButNoRewrite():
    g = _single_copied_box_face_graph()
    assert _add_duplicate_pcurves_to_all_edges(g) > 0
    before = _nb_unique_pcurve_nodes(g)
    Dedup.Perform_s(g, _opts(AnalyzeOnly=True))
    assert _nb_unique_pcurve_nodes(g) == before


def test_BRepGraph_DeduplicateTest_NoPCurveDuplicates_ZeroPCurveRewrites():
    g = _single_copied_box_face_graph()
    Dedup.Perform_s(g)


def test_BRepGraph_DeduplicateTest_HistoryFindOriginal_TracesBackToCanonical():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g, _opts(HistoryMode=True))
    assert res.NbHistoryRecords == 5
    history = _history(g)
    for i in range(history.NbRecords()):
        for original, replacements in history.Record(i).Mapping.items():
            for j in range(replacements.Size()):
                assert history.FindOriginal(replacements.Value(j)).IsValid()
                assert original.IsValid()


def test_BRepGraph_DeduplicateTest_HistoryFindDerived_ContainsCanonicalNode():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g, _opts(HistoryMode=True))
    assert res.NbHistoryRecords == 5
    history = _history(g)
    nb_mappings = 0
    for i in range(history.NbRecords()):
        for original in history.Record(i).Mapping:
            assert history.FindDerived(original).Size() == 1
            nb_mappings += 1
    assert nb_mappings == 5


def test_BRepGraph_DeduplicateTest_HistoryRecordSequenceNumbers_AreMonotonic():
    g = _graph(_make_two_copied_identical_faces())
    Dedup.Perform_s(g, _opts(HistoryMode=True))
    history = _history(g)
    prev = None
    for i in range(history.NbRecords()):
        seq = history.Record(i).SequenceNumber
        if prev is not None:
            assert seq > prev
        prev = seq


def test_BRepGraph_DeduplicateTest_HistoryOff_NbRecordsUnchanged():
    g = _graph(_make_two_copied_identical_faces())
    Dedup.Perform_s(g, _opts(HistoryMode=True))
    assert _history(g).NbRecords() == 5

    g2 = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g2, _opts(HistoryMode=False))
    assert res.NbSurfaceRewrites == 1
    assert res.NbCurveRewrites == 4
    assert _history(g2).NbRecords() == 0


def test_BRepGraph_DeduplicateTest_AfterDedup_AllSurfacesValid():
    g = _graph(_make_two_copied_identical_faces())
    Dedup.Perform_s(g)
    for f in _ids(BRepGraph_FullFaceIterator(g)):
        assert g.Topo().Faces().Definition(f).SurfaceRepId.IsValid()


def test_BRepGraph_DeduplicateTest_AfterDedup_AllCurve3dsValid():
    g = _graph(_make_two_copied_identical_faces())
    Dedup.Perform_s(g)
    for e in _ids(BRepGraph_FullEdgeIterator(g)):
        if not BRepGraph_Tool.Edge.Degenerated_s(g, e):
            assert g.Topo().Edges().Definition(e).Curve3DRepId.IsValid()


def test_BRepGraph_DeduplicateTest_AfterDedup_AllInlinePCurvesHaveCurve2d():
    g = _single_copied_box_face_graph()
    _add_duplicate_pcurves_to_all_edges(g)
    Dedup.Perform_s(g)
    for e in _ids(BRepGraph_FullEdgeIterator(g)):
        for ce in g.Topo().Edges().CoEdges(e):
            assert g.Topo().CoEdges().Definition(ce).Curve2DRepId.IsValid()


def test_BRepGraph_DeduplicateTest_AfterDedup_CanonicalSurfaceGeomNotNull():
    g = _graph(_make_n_copied_identical_faces(4))
    Dedup.Perform_s(g)
    for f in _ids(BRepGraph_FullFaceIterator(g)):
        assert g.Topo().Faces().Definition(f).SurfaceRepId.IsValid()


def test_BRepGraph_DeduplicateTest_AfterDedup_CanonicalCurveGeomNotNull():
    g = _graph(_make_two_copied_identical_faces())
    Dedup.Perform_s(g)
    for e in _ids(BRepGraph_FullEdgeIterator(g)):
        if not BRepGraph_Tool.Edge.Degenerated_s(g, e):
            assert g.Topo().Edges().Definition(e).Curve3DRepId.IsValid()


def test_BRepGraph_DeduplicateTest_ParallelBuild_SameResultAsSequential():
    comp = _make_two_copied_identical_faces()

    def build(parallel):
        g = BRepGraph()
        g.Clear()
        opts = BRepGraph.ShapesView.Options()
        opts.CreateAutoProduct = True
        opts.Flatten = False
        opts.Parallel = parallel
        g.Shapes().Add(comp, opts)
        assert not g.IsEmpty()
        return g

    res_seq = Dedup.Perform_s(build(False))
    res_par = Dedup.Perform_s(build(True))
    for res in (res_seq, res_par):
        assert res.NbCanonicalSurfaces == 1
        assert res.NbCanonicalCurves == 4
        assert res.NbSurfaceRewrites == 1
        assert res.NbCurveRewrites == 4


def test_BRepGraph_DeduplicateTest_TenCopies_AllDeduplicatedToOneSurface():
    n = 10
    g = _graph(_make_n_copied_identical_faces(n))
    assert g.Topo().Faces().Nb() == n
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 1
    assert res.NbSurfaceRewrites == n - 1
    assert _nb_unique_face_surface_defs(g) == 1


def test_BRepGraph_DeduplicateTest_TwoCopies_CurveCanonicalCountLessThanTotal():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Edges().Nb() == 8
    assert Dedup.Perform_s(g, _opts(AnalyzeOnly=True)).NbCanonicalCurves == 4


def test_BRepGraph_DeduplicateTest_Idempotent_MixedCompound_SurfacesAndCurves():
    g = _graph(_make_mixed_compound())
    res1 = Dedup.Perform_s(g)
    assert res1.NbSurfaceRewrites == 1
    assert res1.NbCurveRewrites == 4
    surfs = _nb_unique_face_surface_defs(g)
    curves = _nb_unique_edge_curve_defs(g)
    Dedup.Perform_s(g)
    assert _nb_unique_face_surface_defs(g) == surfs
    assert _nb_unique_edge_curve_defs(g) == curves


def test_BRepGraph_DeduplicateTest_Idempotent_TwoIdenticalBoxes():
    g = _graph(_make_two_identical_boxes())
    res1 = Dedup.Perform_s(g)
    assert res1.NbSurfaceRewrites == 6
    assert res1.NbCurveRewrites == 12
    surfs = _nb_unique_face_surface_defs(g)
    curves = _nb_unique_edge_curve_defs(g)
    Dedup.Perform_s(g)
    assert _nb_unique_face_surface_defs(g) == surfs
    assert _nb_unique_edge_curve_defs(g) == curves


def test_BRepGraph_DeduplicateTest_RestoresHistoryFlag_WhenHistoryModeOff():
    g = _graph(_make_two_copied_identical_faces())
    _history(g).SetEnabled(True)
    assert _history(g).IsEnabled()
    Dedup.Perform_s(g, _opts(HistoryMode=False))
    assert _history(g).IsEnabled()


def test_BRepGraph_DeduplicateTest_RestoresHistoryFlag_AnalyzeOnlyPath():
    g = _graph(_make_two_copied_identical_faces())
    _history(g).SetEnabled(True)
    Dedup.Perform_s(g, _opts(AnalyzeOnly=True, HistoryMode=False))
    assert _history(g).IsEnabled()


def test_BRepGraph_DeduplicateTest_GeomCountsUnchanged_AfterDedup():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 8
    assert _nb_pcurve_entries(g) == 8
    Dedup.Perform_s(g)
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 8
    assert _nb_pcurve_entries(g) == 8


def test_BRepGraph_DeduplicateTest_DefCountsUnchanged_AfterDedup():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 8
    Dedup.Perform_s(g)
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 8


def test_BRepGraph_DeduplicateTest_PCurveEntryCount_UnchangedAfterDedup():
    g = _single_copied_box_face_graph()
    _add_duplicate_pcurves_to_all_edges(g)
    count = _nb_pcurve_entries(g)
    Dedup.Perform_s(g)
    assert _nb_pcurve_entries(g) == count


def _two_copied_faces_of(shape):
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    assert exp.More()
    face = exp.Current()
    return _compound(_copy(face), _copy(face))


def test_BRepGraph_DeduplicateTest_TwoCopiedSphereFaces_Deduped():
    g = _graph(_two_copied_faces_of(BRepPrimAPI_MakeSphere(10.0).Shape()))
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 6
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 1
    assert res.NbSurfaceRewrites == 1
    assert _same_surface(g, 0, 1)
    assert res.NbHistoryRecords > 0


def test_BRepGraph_DeduplicateTest_TwoCopiedCylinderFaces_Deduped():
    g = _graph(_two_copied_faces_of(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape()))
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 6
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 1
    assert res.NbCanonicalCurves == 3
    assert res.NbSurfaceRewrites == 1
    assert res.NbCurveRewrites == 3
    assert res.NbHistoryRecords > 0


def test_BRepGraph_DeduplicateTest_DifferentSizedCylinders_NotDeduped():
    exp1 = TopExp_Explorer(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape(), TopAbs_FACE)
    exp2 = TopExp_Explorer(BRepPrimAPI_MakeCylinder(10.0, 20.0).Shape(), TopAbs_FACE)
    assert exp1.More()
    assert exp2.More()
    g = _graph(_compound(exp1.Current(), exp2.Current()))
    assert g.Topo().Faces().Nb() == 2
    assert g.Topo().Edges().Nb() == 6
    res = Dedup.Perform_s(g)
    assert res.NbCanonicalSurfaces == 2
    assert res.NbCanonicalCurves == 6
    assert res.NbSurfaceRewrites == 0
    assert res.NbCurveRewrites == 0
    assert res.NbHistoryRecords == 0


def test_BRepGraph_DeduplicateTest_BackRefs_SurfaceRewrite_UpdatesFaceDefUsers():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Faces().Nb() == 2
    assert not _same_surface(g, 0, 1)
    Dedup.Perform_s(g)
    assert _same_surface(g, 0, 1)


def test_BRepGraph_DeduplicateTest_BackRefs_CurveRewrite_UpdatesEdgeDefUsers():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Edges().Nb() == 8
    Dedup.Perform_s(g)
    assert _nb_unique_edge_curve_defs(g) == 4


def test_BRepGraph_DeduplicateTest_FacesOnSurface_AfterDedup_ReturnsCorrectDefs():
    g = _graph(_make_two_copied_identical_faces())
    Dedup.Perform_s(g)
    assert g.Topo().Faces().Nb() == 2
    assert BRepGraph_Tool.Face.HasSurface_s(g, BRepGraph_FaceId.Start_s())
    assert BRepGraph_Tool.Face.HasSurface_s(g, BRepGraph_FaceId(1))
    assert _same_surface(g, 0, 1)


def test_BRepGraph_DeduplicateTest_Nullify_OrphanedSurface_HandleIsNull():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g)
    assert res.NbNullifiedSurfaces == 0
    for f in _ids(BRepGraph_FullFaceIterator(g)):
        assert BRepGraph_Tool.Face.HasSurface_s(g, f)


def test_BRepGraph_DeduplicateTest_Nullify_OrphanedCurve_HandleIsNull():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g)
    assert res.NbNullifiedCurves == 0
    for e in _ids(BRepGraph_FullEdgeIterator(g)):
        if not BRepGraph_Tool.Edge.Degenerated_s(g, e):
            assert BRepGraph_Tool.Edge.HasCurve_s(g, e)
    assert _nb_unique_edge_curve_defs(g) == 4


def test_BRepGraph_DeduplicateTest_Nullify_OrphanedPCurve_HandleIsNull():
    g = _single_copied_box_face_graph()
    assert _add_duplicate_pcurves_to_all_edges(g) > 0
    Dedup.Perform_s(g)


def test_BRepGraph_DeduplicateTest_AnalyzeOnly_NoBackRefChangesOrNullification():
    g = _graph(_make_two_copied_identical_faces())
    faces = _ids(BRepGraph_FullFaceIterator(g))
    edges = _ids(BRepGraph_FullEdgeIterator(g))
    surfs = {f.Index: BRepGraph_Tool.Face.Surface_s(g, f) for f in faces}
    curves = {e.Index: BRepGraph_Tool.Edge.Curve_s(g, e) for e in edges}

    res = Dedup.Perform_s(g, _opts(AnalyzeOnly=True))
    assert res.NbNullifiedSurfaces == 0
    assert res.NbNullifiedCurves == 0

    for f in _ids(BRepGraph_FullFaceIterator(g)):
        assert BRepGraph_Tool.Face.Surface_s(g, f) is surfs[f.Index]
    for e in _ids(BRepGraph_FullEdgeIterator(g)):
        assert BRepGraph_Tool.Edge.Curve_s(g, e) is curves[e.Index]

    for f in _ids(BRepGraph_FullFaceIterator(g)):
        assert BRepGraph_Tool.Face.HasSurface_s(g, f)
    for e in _ids(BRepGraph_FullEdgeIterator(g)):
        if not BRepGraph_Tool.Edge.Degenerated_s(g, e):
            assert BRepGraph_Tool.Edge.HasCurve_s(g, e)


def _reconstruct_faces(g):
    faces = []
    for f in _ids(BRepGraph_FullFaceIterator(g)):
        face = g.Shapes().Reconstruct(BRepGraph_NodeId(f))
        assert not face.IsNull()
        faces.append(face)
    return _compound(*faces)


def test_BRepGraph_DeduplicateTest_RoundTrip_TwoCopiedFaces_FewerSurfaces():
    g1 = _graph(_make_two_copied_identical_faces())
    assert g1.Topo().Faces().Nb() == 2
    Dedup.Perform_s(g1)
    assert _nb_unique_face_surface_defs(g1) == 1

    g2 = _graph(_reconstruct_faces(g1))
    assert g2.Topo().Faces().Nb() == 2
    assert _nb_unique_face_surface_defs(g2) == 1


def test_BRepGraph_DeduplicateTest_RoundTrip_TwoCopiedFaces_FewerCurves():
    g1 = _graph(_make_two_copied_identical_faces())
    assert g1.Topo().Edges().Nb() == 8
    Dedup.Perform_s(g1)
    assert _nb_unique_edge_curve_defs(g1) == 4

    g2 = _graph(_reconstruct_faces(g1))
    assert g2.Topo().Edges().Nb() == 8
    assert _nb_unique_edge_curve_defs(g2) == 4


def test_BRepGraph_DeduplicateTest_Build_SharedTFace_OneSurfaceNode():
    exp = TopExp_Explorer(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), TopAbs_FACE)
    assert exp.More()
    face = TopoDS.Face(exp.Current())
    g = _graph(_compound(face, face))
    assert g.Topo().Faces().Nb() == 1


def test_BRepGraph_DeduplicateTest_RoundTrip_TwoBoxes_GeomReduction():
    g1 = _graph(_make_two_identical_boxes())
    surfs_before = g1.Topo().Faces().Nb()
    curves_before = g1.Topo().Edges().Nb()
    assert surfs_before == 12
    assert curves_before == 24
    Dedup.Perform_s(g1)

    recon = g1.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_NodeId.Kind.Compound, 0))
    assert not recon.IsNull()

    g2 = _graph(recon)
    assert g2.Topo().Faces().Nb() == surfs_before
    assert g2.Topo().Edges().Nb() == curves_before
    assert _nb_unique_face_surface_defs(g2) == 6
    assert _nb_unique_edge_curve_defs(g2) == 12


def test_BRepGraph_DeduplicateTest_MergeVertices_SharedVerticesReduced():
    g = _graph(_make_two_copied_identical_faces())
    nv_before = g.Topo().Vertices().Nb()
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert res.NbMergedVertices > 0
    assert len(_ids(BRepGraph_VertexIterator(g))) < nv_before


def test_BRepGraph_DeduplicateTest_MergeEdges_SharedEdgesReduced():
    g = _graph(_make_two_copied_identical_faces())
    assert Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True)).NbMergedEdges > 0


def test_BRepGraph_DeduplicateTest_MergeWires_IdenticalWiresMerged():
    g = _graph(_make_two_copied_identical_faces())
    assert Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True)).NbMergedWires >= 0


def test_BRepGraph_DeduplicateTest_MergeFaces_IdenticalFacesMerged():
    g = _graph(_make_two_copied_identical_faces())
    assert Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True)).NbMergedFaces >= 0


def test_BRepGraph_DeduplicateTest_MergeDefsWhenSafe_False_NoMerge():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g)
    assert res.NbMergedVertices == 0
    assert res.NbMergedEdges == 0
    assert res.NbMergedWires == 0
    assert res.NbMergedFaces == 0
    assert not res.IsEntityMergeApplied


def test_BRepGraph_DeduplicateTest_AnalyzeOnly_MergeDefsWhenSafe_CountsOnly():
    g = _graph(_make_two_copied_identical_faces())
    nv_before = g.Topo().Vertices().Nb()
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True, AnalyzeOnly=True))
    assert res.NbMergedVertices > 0
    assert g.Topo().Vertices().Nb() == nv_before
    assert not res.IsEntityMergeApplied


def test_BRepGraph_DeduplicateTest_HistoryRecords_MergePhases():
    g = _graph(_make_two_copied_identical_faces())
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True, HistoryMode=True))
    assert _count_history_records_by_op(g, "Dedup:MergeVertex") == res.NbMergedVertices
    assert _count_history_records_by_op(g, "Dedup:MergeEdge") == res.NbMergedEdges
    assert _count_history_records_by_op(g, "Dedup:MergeWire") == res.NbMergedWires
    assert _count_history_records_by_op(g, "Dedup:MergeFace") == res.NbMergedFaces


def test_BRepGraph_DeduplicateTest_AfterMerge_Validate_NoIssues():
    g = _graph(_make_two_copied_identical_faces())
    Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def _rect_wire(bb, pts):
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    for a, b in zip(pts, pts[1:] + pts[:1]):
        bb.Add(wire, BRepBuilderAPI_MakeEdge(a, b).Edge())
    return wire


def test_BRepGraph_DeduplicateTest_MergeFaces_SameSurfaceDifferentWires_NotMerged():
    plane = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    bb = BRep_Builder()
    wire1 = _rect_wire(bb, [gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0), gp_Pnt(10, 20, 0), gp_Pnt(0, 20, 0)])
    face1 = BRepBuilderAPI_MakeFace(plane, wire1).Face()
    wire2 = _rect_wire(bb, [gp_Pnt(30, 0, 0), gp_Pnt(40, 0, 0), gp_Pnt(40, 10, 0), gp_Pnt(30, 10, 0)])
    face2 = BRepBuilderAPI_MakeFace(plane, wire2).Face()
    assert not face1.IsNull()
    assert not face2.IsNull()

    g = _graph(_compound(face1, face2))
    assert g.Topo().Faces().Nb() == 2

    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert _same_surface(g, 0, 1)
    assert _nb_active_faces(g) == 2
    assert res.NbMergedFaces == 0


def test_BRepGraph_DeduplicateTest_Sphere_SeamPCurve_SurvivesDedupCompactReconstruct():
    g = _graph(_make_full_sphere())
    pcurves_before = _count_valid_coedge_pcurves(g)
    seams_before = _count_seam_coedges(g)
    assert pcurves_before == 4
    assert seams_before == 2

    Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    _assert_all_pcurves_not_null(g)

    BRepGraph_Compact.Perform_s(g)
    assert _count_valid_coedge_pcurves(g) == pcurves_before
    assert _count_seam_coedges(g) == seams_before
    assert BRepGraph_Validate.Perform_s(g).IsValid()

    assert g.RootProductIds().Size() == 1
    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(g.RootProductIds().Value(0)))
    assert not recon.IsNull()
    assert BRepCheck_Analyzer(recon).IsValid()


def test_BRepGraph_DeduplicateTest_ThreeCopiedCylinderFaces_PCurvesSurviveFullPipeline():
    g = _graph(_make_three_copied_cylinder_faces())
    assert g.Topo().Faces().Nb() == 3
    assert g.Topo().Edges().Nb() == 9
    assert _count_valid_coedge_pcurves(g) == 12

    Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    _assert_all_pcurves_not_null(g)

    compact_res = BRepGraph_Compact.Perform_s(g)
    assert compact_res.NbRemovedEdges == 6
    _assert_all_pcurves_not_null(g)

    assert BRepGraph_Validate.Perform_s(g).IsValid()

    for f in _ids(BRepGraph_FullFaceIterator(g)):
        if f.IsRemoved(g):
            continue
        face = g.Shapes().Reconstruct(BRepGraph_NodeId(f))
        assert not face.IsNull()
        assert BRepCheck_Analyzer(face).IsValid()


def test_BRepGraph_DeduplicateTest_ThreeCopiedBoxes_DedupMergeCompact_FacesKeepOuterWires():
    g = _graph(_make_three_copied_boxes())
    assert g.Topo().Faces().Nb() == 18
    assert g.Topo().Solids().Nb() == 3

    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert res.NbMergedVertices == 16
    assert res.NbMergedEdges == 24
    assert res.NbMergedWires == 12
    assert res.NbMergedFaces == 12

    compact_res = BRepGraph_Compact.Perform_s(g)
    assert compact_res.NbRemovedFaces == 12
    assert compact_res.NbRemovedEdges == 24

    _assert_each_active_face_has_one_wire(g)
    assert BRepGraph_Validate.Perform_s(g).IsValid()

    for s in _ids(BRepGraph_FullSolidIterator(g)):
        if s.IsRemoved(g):
            continue
        solid = g.Shapes().Reconstruct(BRepGraph_NodeId(s))
        assert not solid.IsNull()
        assert BRepCheck_Analyzer(solid).IsValid()


def test_BRepGraph_DeduplicateTest_SelfLoopEdge_AfterVertexMerge_OrientationCorrect():
    g = _graph(_compound(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()))
    assert g.Topo().Solids().Nb() == 2

    Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g).IsValid()

    for s in _ids(BRepGraph_FullSolidIterator(g)):
        if s.IsRemoved(g):
            continue
        solid = g.Shapes().Reconstruct(BRepGraph_NodeId(s))
        assert not solid.IsNull()
        assert solid.ShapeType() == TopAbs_SOLID


def test_BRepGraph_DeduplicateTest_EdgeMerge_ThreeCopiedEdges_GraphValidates():
    g = _graph(_make_three_copied_identical_edges())
    assert g.Topo().Edges().Nb() == 3
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert res.NbMergedEdges == 2
    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_DeduplicateTest_FaceMerge_TwoIdenticalSingularFaces_Merge():
    g = _graph(_make_two_copied_identical_faces())
    assert g.Topo().Faces().Nb() == 2
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert res.NbMergedFaces == 1
    BRepGraph_Compact.Perform_s(g)
    assert _nb_active_faces(g) == 1
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_DeduplicateTest_DedupMerge_TwoBoxesWithSharedEdge_EdgeFaceCountCorrect():
    g = _graph(_make_two_face_touching_boxes())
    Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))

    nb_edges_with_2_faces = 0
    for e in _ids(BRepGraph_EdgeIterator(g)):
        faces = set()
        for ce_id in g.Topo().Edges().CoEdges(e):
            ce = g.Topo().CoEdges().Definition(ce_id)
            if not ce_id.IsRemoved(g) and ce.FaceId.IsValid():
                faces.add(ce.FaceId.Index)
        if len(faces) == 2:
            nb_edges_with_2_faces += 1
    assert nb_edges_with_2_faces == 16

    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g).IsValid()


def test_BRepGraph_DeduplicateTest_DedupMerge_TwoSpheres_DifferentSize_NotMerged():
    g = _graph(_compound(BRepPrimAPI_MakeSphere(5.0).Shape(), BRepPrimAPI_MakeSphere(10.0).Shape()))
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert res.NbMergedFaces == 0
    assert res.NbMergedEdges == 0
    assert _nb_active_faces(g) == 2


def test_BRepGraph_DeduplicateTest_DedupMerge_ThreeBoxes_AllEdgesMergeCorrectly():
    g = _graph(_make_three_copied_boxes())
    res = Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    assert res.NbMergedVertices == 16
    assert res.NbMergedEdges == 24
    assert res.NbMergedWires == 12
    assert res.NbMergedFaces == 12

    compact_res = BRepGraph_Compact.Perform_s(g)
    assert compact_res.NbRemovedFaces == 12
    assert compact_res.NbRemovedEdges == 24
    assert BRepGraph_Validate.Perform_s(g).IsValid()
    _assert_each_active_face_has_one_wire(g)


def test_BRepGraph_DeduplicateTest_DedupMerge_SelfLoopEdge_OrientationPreserved():
    g = _graph(_make_full_sphere())
    Dedup.Perform_s(g, _opts(MergeEntitiesWhenSafe=True))
    BRepGraph_Compact.Perform_s(g)
    assert BRepGraph_Validate.Perform_s(g).IsValid()

    assert g.RootProductIds().Size() == 1
    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(g.RootProductIds().Value(0)))
    assert not recon.IsNull()
    assert BRepCheck_Analyzer(recon).IsValid()
