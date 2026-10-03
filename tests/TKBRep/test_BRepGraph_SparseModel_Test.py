# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_SparseModel_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgeIterator,
    BRepGraph_Compact,
    BRepGraph_Deduplicate,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_Validate,
    BRepGraph_WireId,
)
from nanocct.Geom import Geom_Line, Geom_Plane
from nanocct.gp import gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.TopAbs import TopAbs_FORWARD


def _arr(cls, items):
    if len(items) == 0:
        return NCollection_Array1[cls]()
    a = NCollection_Array1[cls](1, len(items))
    for i, x in enumerate(items, start=1):
        a[i] = x
    return a


def _vtx(g, x, y, z):
    return g.Editor().Vertices().Add(gp_Pnt(x, y, z), 1.0e-7)


def _free_edge(g, y=0.0, curve=None):
    v0 = _vtx(g, 0, y, 0)
    v1 = _vtx(g, 10, y, 0)
    return v0, v1, g.Editor().Edges().Add(v0, v1, curve, 0.0, 10.0, 1.0e-7)


def _wire(g, edge):
    ce = g.Editor().CoEdges().Add(edge, TopAbs_FORWARD)
    return g.Editor().Wires().Add(_arr(BRepGraph_CoEdgeId, [ce]))


def _plane():
    return Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))


def _face(g, wire):
    return g.Editor().Faces().Add(_plane(), wire, _arr(BRepGraph_WireId, []), 1.0e-7)


def _line():
    return Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))


def _valid(g, audit=False):
    if audit:
        return BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s()).IsValid()
    return BRepGraph_Validate.Perform_s(g).IsValid()


def _remove(g, *ids):
    for i in ids:
        g.Editor().Gen().RemoveNode(BRepGraph_NodeId(i))
    g.Editor().Gen().CleanupRemovedReferences()


def _canonical_solid_product(g, curve=None):
    _v0, _v1, edge = _free_edge(g, curve=curve)
    wire = _wire(g, edge)
    face = _face(g, wire)
    shell = g.Editor().Shells().Add()
    g.Editor().Shells().Append(shell, face)
    solid = g.Editor().Solids().Add()
    g.Editor().Solids().Append(solid, shell)
    product = g.Editor().Products().Add(BRepGraph_NodeId(solid))
    assert product.IsValid()
    g.Editor().Products().AppendDocumentRoot(product)
    return solid, product


# Group 1


def test_BRepGraph_SparseModelTest_Compact_BareVertices_NoOp():
    g = BRepGraph()
    for x in (0, 1, 2):
        assert _vtx(g, x, 0, 0).IsValid()
    assert g.Topo().Vertices().NbActive() == 3
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Vertices().NbActive() == 3
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Compact_FreeEdgeNoCurve_NoOp():
    g = BRepGraph()
    v0, v1, edge = _free_edge(g)
    assert v0.IsValid() and v1.IsValid()
    assert edge.IsValid()
    assert g.Topo().Vertices().NbActive() == 2
    assert g.Topo().Edges().NbActive() == 1
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Vertices().NbActive() == 2
    assert g.Topo().Edges().NbActive() == 1


def test_BRepGraph_SparseModelTest_Compact_FreeWireSingleCoEdge_NoOp():
    g = BRepGraph()
    _v0, _v1, edge = _free_edge(g)
    assert edge.IsValid()
    assert _wire(g, edge).IsValid()
    assert g.Topo().Vertices().NbActive() == 2
    assert g.Topo().Edges().NbActive() == 1
    assert g.Topo().Wires().NbActive() == 1
    assert g.Topo().CoEdges().NbActive() >= 1
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Vertices().NbActive() == 2
    assert g.Topo().Edges().NbActive() == 1
    assert g.Topo().Wires().NbActive() == 1


def test_BRepGraph_SparseModelTest_Compact_EmptyCompound_NoOp():
    g = BRepGraph()
    assert g.Editor().Compounds().Add(_arr(BRepGraph_NodeId, [])).IsValid()
    assert g.Topo().Compounds().NbActive() == 1
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Compounds().NbActive() == 1
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Compact_EmptyShell_NoOp():
    g = BRepGraph()
    assert g.Editor().Shells().Add().IsValid()
    assert g.Topo().Shells().NbActive() == 1
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Shells().NbActive() == 1
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Compact_EmptySolid_NoOp():
    g = BRepGraph()
    assert g.Editor().Solids().Add().IsValid()
    assert g.Topo().Solids().NbActive() == 1
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Solids().NbActive() == 1
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Compact_WirelessSurfacelessFace_NoOp():
    g = BRepGraph()
    assert g.Editor().Faces().Add(None, BRepGraph_WireId(), _arr(BRepGraph_WireId, []), 1.0e-7).IsValid()
    assert g.Topo().Faces().NbActive() == 1
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Faces().NbActive() == 1
    assert _valid(g)


# Group 2


def test_BRepGraph_SparseModelTest_Compact_RemoveVertexFromFreeEdge_RemapsEdgeRefs():
    g = BRepGraph()
    v0, v1, edge = _free_edge(g)
    assert v0.IsValid() and v1.IsValid()
    assert edge.IsValid()
    assert g.Topo().Vertices().NbActive() == 2
    assert g.Topo().Edges().NbActive() == 1
    _remove(g, v0)
    assert g.Topo().Vertices().NbActive() == 1
    assert g.Topo().Edges().NbActive() == 1
    BRepGraph_Compact.Perform_s(g)
    assert g.Topo().Vertices().NbActive() == 1
    assert g.Topo().Edges().NbActive() == 1


def test_BRepGraph_SparseModelTest_Compact_RemoveEdgeFromFreeWire_RetiresCoEdgeAndPrunesRef():
    g = BRepGraph()
    _v0, _v1, edge = _free_edge(g)
    assert edge.IsValid()
    assert _wire(g, edge).IsValid()
    before = g.Topo().CoEdges().NbActive()
    assert before >= 1
    assert g.Topo().Wires().NbActive() == 1
    assert g.Topo().Edges().NbActive() == 1
    _remove(g, edge)
    assert g.Topo().Edges().NbActive() == 0
    assert g.Topo().CoEdges().NbActive() == before - 1
    BRepGraph_Compact.Perform_s(g)
    assert g.Topo().CoEdges().NbActive() == 0
    assert g.Topo().Edges().NbActive() == 0
    assert g.Topo().Wires().NbActive() == 1
    assert g.Topo().Vertices().NbActive() == 2


def test_BRepGraph_SparseModelTest_Compact_RemoveFace_FreeWireCoEdgesSurvive():
    g = BRepGraph()
    _v0, _v1, edge = _free_edge(g)
    wire = _wire(g, edge)
    face = _face(g, wire)
    assert face.IsValid()
    ce_before = g.Topo().CoEdges().NbActive()
    w_before = g.Topo().Wires().NbActive()
    assert ce_before >= 1
    assert w_before == 1
    assert g.Topo().Faces().NbActive() == 1
    _remove(g, face)
    assert g.Topo().Faces().NbActive() == 0
    assert g.Topo().CoEdges().NbActive() == ce_before
    assert g.Topo().Wires().NbActive() == w_before
    BRepGraph_Compact.Perform_s(g)
    assert g.Topo().Faces().NbActive() == 0
    assert g.Topo().CoEdges().NbActive() == ce_before
    assert g.Topo().Wires().NbActive() == w_before
    assert g.Topo().Edges().NbActive() == 1
    assert g.Topo().Vertices().NbActive() == 2


def test_BRepGraph_SparseModelTest_Compact_RemoveTopologyChild_OccurrenceRetired():
    g = BRepGraph()
    solid, _product = _canonical_solid_product(g)
    assert g.Topo().Products().NbActive() == 1
    assert g.Topo().Occurrences().NbActive() == 1
    assert g.Topo().Solids().NbActive() == 1
    _remove(g, solid)
    assert g.Topo().Solids().NbActive() == 0
    assert g.Topo().Occurrences().NbActive() == 0
    assert g.Topo().Products().NbActive() == 1
    BRepGraph_Compact.Perform_s(g)
    assert g.Topo().Solids().NbActive() == 0
    assert g.Topo().Occurrences().NbActive() == 0
    assert g.Topo().Products().NbActive() == 1


def test_BRepGraph_SparseModelTest_Compact_MultipleRemovals_VertexEdgeFace_Validates():
    g = BRepGraph()
    extra = _vtx(g, 100, 0, 0)
    assert extra.IsValid()
    _a, _b, free_edge = _free_edge(g)
    _c, _d, edge = _free_edge(g, y=1.0)
    wire = _wire(g, edge)
    face = _face(g, wire)
    assert face.IsValid()
    assert free_edge.IsValid()
    vtx_before = g.Topo().Vertices().NbActive()
    _remove(g, extra, free_edge, face)
    assert g.Topo().Vertices().NbActive() == vtx_before - 1
    assert g.Topo().Edges().NbActive() == 1
    assert g.Topo().Faces().NbActive() == 0
    BRepGraph_Compact.Perform_s(g)


# Group 3


def test_BRepGraph_SparseModelTest_Dedup_BareVertices_NoRewrite():
    g = BRepGraph()
    for x in (0, 1, 2):
        assert _vtx(g, x, 0, 0).IsValid()
    res = BRepGraph_Deduplicate.Perform_s(g)
    assert res.NbCanonicalSurfaces == 0
    assert res.NbCanonicalCurves == 0
    assert res.NbSurfaceRewrites == 0
    assert res.NbCurveRewrites == 0
    assert not res.IsEntityMergeApplied
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Dedup_TwoIdenticalVertices_MergeWhenSafe():
    g = BRepGraph()
    assert _vtx(g, 0, 0, 0).IsValid()
    assert _vtx(g, 0, 0, 0).IsValid()
    assert g.Topo().Vertices().NbActive() == 2
    opts = BRepGraph_Deduplicate.Options()
    opts.MergeEntitiesWhenSafe = True
    res = BRepGraph_Deduplicate.Perform_s(g, opts)
    assert res.NbMergedVertices >= 1
    assert g.Topo().Vertices().NbActive() == 1
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Dedup_TwoIdenticalVertices_NoMergeByDefault():
    g = BRepGraph()
    assert _vtx(g, 0, 0, 0).IsValid()
    assert _vtx(g, 0, 0, 0).IsValid()
    assert g.Topo().Vertices().NbActive() == 2
    res = BRepGraph_Deduplicate.Perform_s(g)
    assert res.NbMergedVertices == 0
    assert not res.IsEntityMergeApplied
    assert g.Topo().Vertices().NbActive() == 2
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Dedup_FreeEdgesWithCurve_CanonicalizesCurves():
    g = BRepGraph()
    line1, line2 = _line(), _line()
    assert line1 is not line2
    assert _free_edge(g, 0.0, line1)[2].IsValid()
    assert _free_edge(g, 1.0, line2)[2].IsValid()
    res = BRepGraph_Deduplicate.Perform_s(g)
    assert res.NbCanonicalCurves == 1
    assert res.NbCurveRewrites == 1
    assert _valid(g)


def test_BRepGraph_SparseModelTest_Dedup_FreeWireSingleCoEdge_NoGeometryRewrite():
    g = BRepGraph()
    _v0, _v1, edge = _free_edge(g)
    assert _wire(g, edge).IsValid()
    res = BRepGraph_Deduplicate.Perform_s(g)
    assert res.NbCanonicalSurfaces == 0
    assert res.NbCanonicalCurves == 1
    assert res.NbCurveRewrites == 0


def test_BRepGraph_SparseModelTest_Dedup_EmptyCompound_NoOp():
    g = BRepGraph()
    assert g.Editor().Compounds().Add(_arr(BRepGraph_NodeId, [])).IsValid()
    res = BRepGraph_Deduplicate.Perform_s(g)
    assert res.NbCanonicalSurfaces == 0
    assert res.NbCanonicalCurves == 0
    assert _valid(g)


# Group 4


def test_BRepGraph_SparseModelTest_Cleanup_RemoveFace_CoEdgeFaceIdCleared_CoEdgeSurvives():
    g = BRepGraph()
    _v0, _v1, edge = _free_edge(g)
    wire = _wire(g, edge)
    face = _face(g, wire)
    assert face.IsValid()
    _remove(g, face)
    it = BRepGraph_CoEdgeIterator(g)
    while it.More():
        ce = it.Current()
        assert not it.CurrentId().IsRemoved(g)
        assert not ce.FaceId.IsValid()
        assert ce.ChildEdgeId.IsValid()
        it.Next()


def test_BRepGraph_SparseModelTest_Cleanup_RemoveEdge_FreeWireCoEdgeRetired():
    g = BRepGraph()
    _v0, _v1, edge = _free_edge(g)
    assert _wire(g, edge).IsValid()
    _remove(g, edge)
    assert g.Topo().CoEdges().NbActive() == 0
    assert g.Topo().CoEdges().Nb() >= 1


def test_BRepGraph_SparseModelTest_Cleanup_RemoveVertex_EdgeVertexRefsCleared():
    g = BRepGraph()
    v0, _v1, edge = _free_edge(g)
    assert edge.IsValid()
    _remove(g, v0)
    assert g.Topo().Vertices().NbActive() == 1
    assert g.Topo().Edges().NbActive() == 1
    for ed in BRepGraph_EdgeIterator(g):
        assert not ed.StartVertexRefId.IsValid()
        assert ed.EndVertexRefId.IsValid()


def test_BRepGraph_SparseModelTest_Cleanup_RemoveWire_FaceWireRefPruned():
    g = BRepGraph()
    _v0, _v1, edge = _free_edge(g)
    wire = _wire(g, edge)
    face = _face(g, wire)
    assert face.IsValid()
    _remove(g, wire)
    assert g.Topo().Wires().NbActive() == 0
    assert g.Topo().Faces().NbActive() == 1
    rel = g.Topo().Faces().Relations(BRepGraph_FaceId.Start_s())
    assert len(rel.WireRefIds) == 0


# Group 5


def test_BRepGraph_SparseModelTest_Product_EmptyProduct_CompactAndAudit():
    g = BRepGraph()
    assert g.Editor().Products().Add().IsValid()
    assert g.Topo().Products().NbActive() == 1
    assert g.Topo().Occurrences().NbActive() == 0
    res = BRepGraph_Compact.Perform_s(g)
    assert res.NbNodesBefore == res.NbNodesAfter
    assert g.Topo().Products().NbActive() == 1
    assert _valid(g, audit=True)


def test_BRepGraph_SparseModelTest_Product_FullCanonical_RemoveSolid_WholeChainCleans():
    g = BRepGraph()
    solid, _product = _canonical_solid_product(g)
    assert g.Topo().Products().NbActive() == 1
    assert g.Topo().Occurrences().NbActive() == 1
    assert g.Topo().Solids().NbActive() == 1
    _remove(g, solid)
    assert g.Topo().Solids().NbActive() == 0
    assert g.Topo().Occurrences().NbActive() == 0
    BRepGraph_Compact.Perform_s(g)
    assert g.Topo().Solids().NbActive() == 0
    assert g.Topo().Occurrences().NbActive() == 0
    assert g.Topo().Products().NbActive() == 1


def test_BRepGraph_SparseModelTest_Product_FullCanonical_CompactAndDedup_NoRegression():
    g = BRepGraph()
    _canonical_solid_product(g, curve=_line())
    BRepGraph_Compact.Perform_s(g)
    assert _valid(g, audit=True)
    res = BRepGraph_Deduplicate.Perform_s(g)
    assert res.NbCanonicalSurfaces == 1
    assert res.NbCanonicalCurves == 1
    assert _valid(g, audit=True)


# Group 6


def test_BRepGraph_SparseModelTest_Pipeline_RemoveCleanupCompact_GraphValid():
    g = BRepGraph()
    v0 = _vtx(g, 0, 0, 0)
    v1 = _vtx(g, 10, 0, 0)
    extra = _vtx(g, 100, 0, 0)
    edge = g.Editor().Edges().Add(v0, v1, None, 0.0, 10.0, 1.0e-7)
    wire = _wire(g, edge)
    face = _face(g, wire)
    assert face.IsValid()
    _remove(g, face, extra)
    BRepGraph_Compact.Perform_s(g)


def test_BRepGraph_SparseModelTest_Pipeline_RemoveCleanupDedupCompact_GraphValid():
    g = BRepGraph()
    line1, line2 = _line(), _line()
    v0a, _v1a, e1 = _free_edge(g, 0.0, line1)
    assert e1.IsValid()
    assert _free_edge(g, 1.0, line2)[2].IsValid()
    _remove(g, v0a)
    opts = BRepGraph_Deduplicate.Options()
    opts.MergeEntitiesWhenSafe = True
    BRepGraph_Deduplicate.Perform_s(g, opts)
    BRepGraph_Compact.Perform_s(g)
    assert _valid(g, audit=True)


def test_BRepGraph_SparseModelTest_Pipeline_CompoundWithEmptyShells_CompactAndAudit():
    g = BRepGraph()
    s1 = g.Editor().Shells().Add()
    s2 = g.Editor().Shells().Add()
    assert s1.IsValid() and s2.IsValid()
    kids = _arr(BRepGraph_NodeId, [BRepGraph_NodeId(s1), BRepGraph_NodeId(s2)])
    assert g.Editor().Compounds().Add(kids).IsValid()
    assert g.Topo().Shells().NbActive() == 2
    assert g.Topo().Compounds().NbActive() == 1
    _remove(g, s1)
    assert g.Topo().Shells().NbActive() == 1
    BRepGraph_Compact.Perform_s(g)
    assert g.Topo().Shells().NbActive() == 1
    assert g.Topo().Compounds().NbActive() == 1
    assert _valid(g, audit=True)
