# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_MutationGen_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgeIterator,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_NodeId,
    BRepGraph_ShellIterator,
    BRepGraph_SolidId,
    BRepGraph_SolidIterator,
    BRepGraph_WireId,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Plane
from nanocct.gp import gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.TopAbs import TopAbs_FORWARD
from nanocct.TopLoc import TopLoc_Location


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    return g


def _array1(cls, items):
    a = NCollection_Array1[cls](1, len(items))
    for i, x in enumerate(items, start=1):
        a.SetValue(i, x)
    return a


def _defs(it):
    out = []
    while it.More():
        out.append((it.CurrentId(), it.Current()))
        it.Next()
    return out


def _edge0(g):
    return g.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s())


def test_BRepGraph_MutationGenTest_OwnGen_IncrementedOnMutation(graph):
    assert _edge0(graph).OwnGen == 0
    assert _edge0(graph).SubtreeGen == 0
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    assert _edge0(graph).OwnGen == 1
    assert _edge0(graph).SubtreeGen == 1


def test_BRepGraph_MutationGenEditorTest_EditorCreationRegistersOwnGeneration():
    g = BRepGraph()
    g.Clear()
    ed = g.Editor()
    v0 = ed.Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    v1 = ed.Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    edge = ed.Edges().Add(v0, v1, None, 0.0, 1.0, 1.0e-7)
    coedge = ed.CoEdges().Add(edge, TopAbs_FORWARD)
    wire = ed.Wires().Add(_array1(BRepGraph_CoEdgeId, [coedge]))
    face = ed.Faces().Add(Geom_Plane(gp_Pln()), wire, NCollection_Array1[BRepGraph_WireId](), 1.0e-7)
    shell = ed.Shells().Add()
    solid = ed.Solids().Add()
    compound = ed.Compounds().Add(_array1(BRepGraph_NodeId, [BRepGraph_NodeId(solid)]))
    compsolid = ed.CompSolids().Add(_array1(BRepGraph_SolidId, [solid]))
    t = g.Topo()
    assert t.Vertices().Definition(v0).OwnGen == 1
    assert t.Vertices().Definition(v1).OwnGen == 1
    assert t.Edges().Definition(edge).OwnGen == 3
    assert t.CoEdges().Definition(coedge).OwnGen == 2
    assert t.Wires().Definition(wire).OwnGen == 1
    assert t.Faces().Definition(face).OwnGen == 1
    assert t.Shells().Definition(shell).OwnGen == 1
    assert t.Solids().Definition(solid).OwnGen == 1
    assert t.Compounds().Definition(compound).OwnGen == 1
    assert t.CompSolids().Definition(compsolid).OwnGen == 1
    assert g.ValidateRelations()


def test_BRepGraph_MutationGenEditorTest_ProductAppendRegistersBothProductsAndOccurrence():
    g = BRepGraph()
    g.Clear()
    parent = g.Editor().Products().Add()
    child = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(child)
    parent_stamp = g.UIDs().StampOf(parent)
    child_stamp = g.UIDs().StampOf(child)
    parent_gen = g.Topo().Products().Definition(parent).OwnGen
    child_gen = g.Topo().Products().Definition(child).OwnGen
    occ = g.Editor().Products().Append(parent, child, TopLoc_Location())
    assert occ.IsValid()
    assert g.UIDs().IsStale(parent_stamp)
    assert g.UIDs().IsStale(child_stamp)
    assert g.Topo().Occurrences().Definition(occ).OwnGen == 1
    assert g.Topo().Products().Definition(parent).OwnGen == parent_gen + 1
    assert g.Topo().Products().Definition(child).OwnGen == child_gen + 1
    assert g.ValidateRelations()


def test_BRepGraph_MutationGenTest_OwnGen_MultipleIncrements(graph):
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.1)
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.2)
    assert _edge0(graph).OwnGen == 2


def test_BRepGraph_MutationGenTest_OwnGen_DeferredMode(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    assert _edge0(graph).OwnGen == 1
    graph.Editor().EndDeferredInvalidation()
    assert _edge0(graph).OwnGen == 1


def test_BRepGraph_MutationGenTest_SubtreeGen_PropagatedParent_Incremented(graph):
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    assert _edge0(graph).OwnGen == 1
    assert _edge0(graph).SubtreeGen == 1
    for it_cls in (BRepGraph_WireIterator, BRepGraph_FaceIterator, BRepGraph_ShellIterator, BRepGraph_SolidIterator):
        defs = [d for _, d in _defs(it_cls(graph))]
        assert any(d.SubtreeGen > 0 for d in defs)
        assert all(d.OwnGen == 0 for d in defs)


def test_BRepGraph_MutationGenTest_SubtreeGen_DeferredPropagatedParent_Incremented(graph):
    edge_gen = _edge0(graph).OwnGen
    wire_before = [d.SubtreeGen for _, d in _defs(BRepGraph_WireIterator(graph))]
    face_before = [d.SubtreeGen for _, d in _defs(BRepGraph_FaceIterator(graph))]
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    graph.Editor().EndDeferredInvalidation()
    assert _edge0(graph).OwnGen == edge_gen + 1
    assert any(d.SubtreeGen > wire_before[i.Index] for i, d in _defs(BRepGraph_WireIterator(graph)))
    assert any(d.SubtreeGen > face_before[i.Index] for i, d in _defs(BRepGraph_FaceIterator(graph)))


def _root_product_and_occurrence(g):
    assert g.RootProductIds().Size() == 1
    product = g.RootProductIds().Value(0)
    occurrence = g.Topo().Products().Component(product, 0)
    assert occurrence.IsValid()
    return product, occurrence


def test_BRepGraph_MutationGenTest_SubtreeGen_SolidMutation_PropagatesThroughRootOccurrence(graph):
    product, occurrence = _root_product_and_occurrence(graph)
    occ_before = graph.Topo().Occurrences().Definition(occurrence).SubtreeGen
    prod_before = graph.Topo().Products().Definition(product).SubtreeGen
    shell = graph.Editor().Shells().Add()
    assert shell.IsValid()
    ref = graph.Editor().Solids().Append(BRepGraph_SolidId.Start_s(), shell)
    assert ref.IsValid()
    assert graph.Topo().Occurrences().Definition(occurrence).SubtreeGen > occ_before
    assert graph.Topo().Products().Definition(product).SubtreeGen > prod_before


def test_BRepGraph_MutationGenTest_SubtreeGen_DeferredSolidMutation_PropagatesThroughRootOccurrence(graph):
    product, occurrence = _root_product_and_occurrence(graph)
    occ_before = graph.Topo().Occurrences().Definition(occurrence).SubtreeGen
    prod_before = graph.Topo().Products().Definition(product).SubtreeGen
    graph.Editor().BeginDeferredInvalidation()
    shell = graph.Editor().Shells().Add()
    assert shell.IsValid()
    ref = graph.Editor().Solids().Append(BRepGraph_SolidId.Start_s(), shell)
    assert ref.IsValid()
    assert graph.Topo().Occurrences().Definition(occurrence).SubtreeGen == occ_before
    assert graph.Topo().Products().Definition(product).SubtreeGen == prod_before
    graph.Editor().EndDeferredInvalidation()
    assert graph.Topo().Occurrences().Definition(occurrence).SubtreeGen > occ_before
    assert graph.Topo().Products().Definition(product).SubtreeGen > prod_before


def test_BRepGraph_MutationGenTest_RepMutation_SurfacePropagatesSubtreeGenToFace(graph):
    fid = BRepGraph_FaceId(0)
    assert graph.Topo().Faces().Definition(fid).OwnGen == 0
    assert graph.Topo().Faces().Definition(fid).SubtreeGen == 0
    graph.Editor().Faces().ClearSurface(fid)
    assert graph.Topo().Faces().Definition(fid).OwnGen > 0
    assert graph.Topo().Faces().Definition(fid).SubtreeGen > 0


def test_BRepGraph_MutationGenTest_RepMutation_Curve3DPropagatesSubtreeGenToEdge(graph):
    eid = BRepGraph_EdgeId(0)
    assert graph.Topo().Edges().Definition(eid).OwnGen == 0
    assert graph.Topo().Edges().Definition(eid).SubtreeGen == 0
    graph.Editor().Edges().ClearCurve(eid)
    assert graph.Topo().Edges().Definition(eid).OwnGen > 0
    assert graph.Topo().Edges().Definition(eid).SubtreeGen > 0


def test_BRepGraph_MutationGenTest_RepMutation_Curve2DPropagatesSubtreeGenToCoEdge(graph):
    it = BRepGraph_CoEdgeIterator(graph)
    assert it.More()
    cid = it.CurrentId()
    assert it.Current().OwnGen == 0
    assert it.Current().SubtreeGen == 0
    graph.Editor().CoEdges().ClearPCurve(cid)
    assert graph.Topo().CoEdges().Definition(cid).OwnGen > 0
    assert graph.Topo().CoEdges().Definition(cid).SubtreeGen > 0


def test_BRepGraph_MutationGenTest_RepMutation_TriangulationPropagatesSubtreeGenToFace(graph):
    it = BRepGraph_FaceIterator(graph)
    assert it.More()
    fid = it.CurrentId()
    assert it.Current().OwnGen == 0
    assert it.Current().SubtreeGen == 0
    graph.Editor().Faces().ClearPersistentTriangulation(fid)
    assert graph.Topo().Faces().Definition(fid).OwnGen > 0
    assert graph.Topo().Faces().Definition(fid).SubtreeGen > 0


def test_BRepGraph_MutationGenTest_RepMutation_Polygon3DPropagatesSubtreeGenToEdge(graph):
    it = BRepGraph_EdgeIterator(graph)
    assert it.More()
    eid = it.CurrentId()
    assert it.Current().OwnGen == 0
    assert it.Current().SubtreeGen == 0
    graph.Editor().Edges().ClearPersistentPolygon3D(eid)
    assert graph.Topo().Edges().Definition(eid).OwnGen > 0
    assert graph.Topo().Edges().Definition(eid).SubtreeGen > 0
