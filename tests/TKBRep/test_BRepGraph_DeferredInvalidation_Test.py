# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_DeferredInvalidation_Test.cxx (LGPL-2.1 with the OCCT exception)
# A C++ scope end (MutGuard temporaries, BRepGraph_DeferredScope) is a released Python reference (`del`, end of statement).
import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_DeferredScope,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_ProductId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_WireId,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_REVERSED
from nanocct.TopLoc import TopLoc_Location


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    return g


def _defs(it):
    out = []
    while it.More():
        out.append((it.CurrentId(), it.Current()))
        it.Next()
    return out


def _face_uses_wire(g, face, wire):
    return any(g.Refs().Wires().Entry(r).ChildWireId == wire for r in g.Refs().Wires().IdsOf(face))


def _edge0(g):
    return g.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s())


def _shell_sub(g):
    return g.Topo().Shells().Definition(BRepGraph_ShellId.Start_s()).SubtreeGen


def _solid_sub(g):
    return g.Topo().Solids().Definition(BRepGraph_SolidId.Start_s()).SubtreeGen


def _first_wire_of_edge0(g):
    it = g.Topo().Edges().WiresOf(BRepGraph_EdgeId.Start_s())
    assert it.More()
    return it.CurrentId()


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_EdgeMutation_IncrementsOwnGen(graph):
    assert _edge0(graph).OwnGen == 0
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    assert _edge0(graph).OwnGen > 0
    graph.Editor().EndDeferredInvalidation()


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_PropagatesUpOnFlush(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    wire = _first_wire_of_edge0(graph)
    assert graph.Topo().Wires().Definition(wire).SubtreeGen == 0
    graph.Editor().EndDeferredInvalidation()
    assert graph.Topo().Wires().Definition(wire).SubtreeGen > 0
    for fid, fdef in _defs(BRepGraph_FaceIterator(graph)):
        if _face_uses_wire(graph, fid, wire):
            assert fdef.SubtreeGen > 0
            break
    assert _shell_sub(graph) > 0
    assert _solid_sub(graph) > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_DirectFaceMutation_PropagatesUp(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Faces().Mut(BRepGraph_FaceId.Start_s()).MarkDirty()
    assert graph.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).OwnGen > 0
    assert _shell_sub(graph) == 0
    graph.Editor().EndDeferredInvalidation()
    assert _shell_sub(graph) > 0
    assert _solid_sub(graph) > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_DirectShellMutation_PropagatesUp(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Shells().Mut(BRepGraph_ShellId.Start_s()).MarkDirty()
    assert graph.Topo().Shells().Definition(BRepGraph_ShellId.Start_s()).OwnGen > 0
    assert _solid_sub(graph) == 0
    graph.Editor().EndDeferredInvalidation()
    assert _solid_sub(graph) > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_MultipleEdges_BatchPropagation(graph):
    graph.Editor().BeginDeferredInvalidation()
    for eid, _ in _defs(BRepGraph_EdgeIterator(graph)):
        graph.Editor().Edges().SetTolerance(eid, 0.1)
    for _, wdef in _defs(BRepGraph_WireIterator(graph)):
        assert wdef.SubtreeGen == 0
    graph.Editor().EndDeferredInvalidation()
    for _, wdef in _defs(BRepGraph_WireIterator(graph)):
        assert wdef.SubtreeGen > 0
    for _, fdef in _defs(BRepGraph_FaceIterator(graph)):
        assert fdef.SubtreeGen > 0
    assert _shell_sub(graph) > 0
    assert _solid_sub(graph) > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_ReconstructAfterFlush_Succeeds(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    graph.Editor().EndDeferredInvalidation()
    shape = graph.Shapes().Reconstruct(BRepGraph_SolidId.Start_s())
    assert not shape.IsNull()


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_NoMutations_FlushIsSafe(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().EndDeferredInvalidation()
    t = graph.Topo()
    defs = [
        t.Edges().Definition(BRepGraph_EdgeId.Start_s()),
        t.Wires().Definition(BRepGraph_WireId.Start_s()),
        t.Faces().Definition(BRepGraph_FaceId.Start_s()),
        t.Shells().Definition(BRepGraph_ShellId.Start_s()),
        t.Solids().Definition(BRepGraph_SolidId.Start_s()),
    ]
    for d in defs:
        assert d.OwnGen == 0
        assert d.SubtreeGen == 0


def test_BRepGraph_DeferredInvalidationTest_EndWithoutBegin_IsIdempotent(graph):
    graph.Editor().EndDeferredInvalidation()
    assert _edge0(graph).OwnGen == 0
    assert graph.Topo().Solids().Definition(BRepGraph_SolidId.Start_s()).OwnGen == 0


def test_BRepGraph_DeferredInvalidationTest_DeferredScope_NestedGuards_FlushOnlyOnOuterDestruction(graph):
    wire = _first_wire_of_edge0(graph)
    outer = BRepGraph_DeferredScope(graph)
    assert graph.Editor().IsDeferredMode()
    inner = BRepGraph_DeferredScope(graph)
    assert graph.Editor().IsDeferredMode()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    del inner
    assert graph.Editor().IsDeferredMode()
    assert graph.Topo().Wires().Definition(wire).SubtreeGen == 0
    del outer
    assert not graph.Editor().IsDeferredMode()
    assert graph.Topo().Wires().Definition(wire).SubtreeGen > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_DoubleEnd_IsIdempotent(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    graph.Editor().EndDeferredInvalidation()
    graph.Editor().EndDeferredInvalidation()
    assert _edge0(graph).OwnGen > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_SameEdgeMutatedTwice(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.1)
    graph.Editor().Edges().SetTolerance(BRepGraph_EdgeId.Start_s(), 0.5)
    graph.Editor().EndDeferredInvalidation()
    assert abs(_edge0(graph).Tolerance - 0.5) <= Precision.Confusion_s()
    assert _edge0(graph).OwnGen > 0
    assert _shell_sub(graph) > 0
    assert _solid_sub(graph) > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_DirectWireMutation_PropagatesUp(graph):
    graph.Editor().BeginDeferredInvalidation()
    graph.Editor().Wires().Mut(BRepGraph_WireId.Start_s()).MarkDirty()
    assert graph.Topo().Wires().Definition(BRepGraph_WireId.Start_s()).OwnGen > 0
    assert graph.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SubtreeGen == 0
    graph.Editor().EndDeferredInvalidation()
    assert any(
        _face_uses_wire(graph, fid, BRepGraph_WireId.Start_s()) and fdef.SubtreeGen > 0
        for fid, fdef in _defs(BRepGraph_FaceIterator(graph))
    )
    assert _shell_sub(graph) > 0
    assert _solid_sub(graph) > 0


def test_BRepGraph_DeferredInvalidationTest_DeferredMode_OccurrenceMutation_PropagatesSubtreeGenToProduct(graph):
    part = BRepGraph_ProductId.Start_s()
    assembly = graph.Editor().Products().Add()
    graph.Editor().Products().AppendDocumentRoot(assembly)
    occ = graph.Editor().Products().Append(assembly, part, TopLoc_Location())
    assert occ.IsValid()
    base_sub = graph.Topo().Products().Definition(assembly).SubtreeGen
    base_own = graph.Topo().Products().Definition(assembly).OwnGen
    refs = graph.Refs().Occurrences().IdsOf(assembly)
    assert refs.Size() == 1
    occ_ref = refs.Value(0)
    graph.Editor().BeginDeferredInvalidation()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(100.0, 0.0, 0.0))
    graph.Editor().Occurrences().SetRefLocalLocation(occ_ref, TopLoc_Location(trsf))
    parent = graph.Refs().Occurrences().Entry(occ_ref).ParentProductId
    assert graph.Topo().Products().Definition(parent).OwnGen == base_own + 1
    graph.Editor().EndDeferredInvalidation()
    assert graph.Topo().Products().Definition(assembly).SubtreeGen >= base_sub
    assert graph.Topo().Products().Definition(assembly).OwnGen == base_own + 1


def _first_coedge_of_wire0(g):
    ids = g.Topo().Wires().Relations(BRepGraph_WireId.Start_s()).CoEdgeIds
    assert ids.Size() > 0
    ce = ids.Value(0)
    assert ce.IsValid()
    return ce


def test_BRepGraph_DeferredInvalidationTest_CoEdgeMutation_ImmediatePropagatesToWireAndFace(graph):
    wire = BRepGraph_WireId.Start_s()
    face = BRepGraph_FaceId.Start_s()
    ce = _first_coedge_of_wire0(graph)
    wire_before = graph.Topo().Wires().Definition(wire).SubtreeGen
    face_before = graph.Topo().Faces().Definition(face).SubtreeGen
    graph.Editor().CoEdges().SetOrientation(ce, TopAbs_REVERSED)
    assert graph.Topo().Wires().Definition(wire).SubtreeGen > wire_before
    assert graph.Topo().Faces().Definition(face).SubtreeGen > face_before


def test_BRepGraph_DeferredInvalidationTest_CoEdgeMutation_DeferredPropagatesToWireAndFaceOnFlush(graph):
    wire = BRepGraph_WireId.Start_s()
    face = BRepGraph_FaceId.Start_s()
    ce = _first_coedge_of_wire0(graph)
    graph.Editor().BeginDeferredInvalidation()
    wire_before = graph.Topo().Wires().Definition(wire).SubtreeGen
    face_before = graph.Topo().Faces().Definition(face).SubtreeGen
    graph.Editor().CoEdges().SetOrientation(ce, TopAbs_REVERSED)
    assert graph.Topo().Wires().Definition(wire).SubtreeGen == wire_before
    assert graph.Topo().Faces().Definition(face).SubtreeGen == face_before
    graph.Editor().EndDeferredInvalidation()
    assert graph.Topo().Wires().Definition(wire).SubtreeGen > wire_before
    assert graph.Topo().Faces().Definition(face).SubtreeGen > face_before
