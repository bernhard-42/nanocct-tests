# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Iterator_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeIterator,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_FullFaceIterator,
    BRepGraph_NodeId,
    BRepGraph_RootProductIterator,
    BRepGraph_ShellIterator,
    BRepGraph_SolidIterator,
    BRepGraph_VertexIterator,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _count(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def test_BRepGraph_IteratorTest_FaceIterator_CountMatchesTopology(graph):
    assert _count(BRepGraph_FaceIterator(graph)) == 6


def test_BRepGraph_IteratorTest_EdgeIterator_CountMatchesTopology(graph):
    assert _count(BRepGraph_EdgeIterator(graph)) == 12


def test_BRepGraph_IteratorTest_VertexIterator_CountMatchesTopology(graph):
    assert _count(BRepGraph_VertexIterator(graph)) == 8


def test_BRepGraph_IteratorTest_SolidIterator_BoxHasOneSolid(graph):
    assert _count(BRepGraph_SolidIterator(graph)) == 1


def test_BRepGraph_IteratorTest_ShellIterator_BoxHasOneShell(graph):
    assert _count(BRepGraph_ShellIterator(graph)) == 1


def test_BRepGraph_IteratorTest_WireIterator_BoxHasSixWires(graph):
    assert _count(BRepGraph_WireIterator(graph)) == 6


def test_BRepGraph_IteratorTest_RootProductIterator_MatchesStoredRoots(graph):
    roots = graph.RootProductIds()
    count = 0
    it = BRepGraph_RootProductIterator(graph)
    while it.More():
        assert count < roots.Size()
        assert BRepGraph_NodeId(it.Current()) == BRepGraph_NodeId(roots.Value(count))
        count += 1
        it.Next()
    assert count == roots.Size()


def test_BRepGraph_IteratorTest_CurrentId_ReturnsValidTypedIds(graph):
    it = BRepGraph_FaceIterator(graph)
    assert it.More()
    assert it.CurrentId().IsValid(graph.Topo().Faces().Nb())


def test_BRepGraph_IteratorTest_Current_ReturnsDefinition(graph):
    it = BRepGraph_VertexIterator(graph)
    assert it.More()
    vtx = it.Current()
    assert math.isfinite(vtx.Point.X())
    assert math.isfinite(vtx.Point.Y())
    assert math.isfinite(vtx.Point.Z())


def test_BRepGraph_IteratorTest_RemovedFace_SkippedByDefaultIterator(graph):
    nb_before = graph.Topo().Faces().Nb()
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    assert _count(BRepGraph_FaceIterator(graph)) == nb_before - 1


def test_BRepGraph_IteratorTest_FullTraverse_IncludesRemovedFace(graph):
    nb_before = graph.Topo().Faces().Nb()
    graph.Editor().Gen().RemoveNode(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    assert _count(BRepGraph_FullFaceIterator(graph)) == nb_before


def test_BRepGraph_IteratorTest_RangeFor_WorksCorrectly(graph):
    assert sum(1 for _face in BRepGraph_FaceIterator(graph)) == 6


def test_BRepGraph_IteratorStandalone_EmptyGraph_IteratorIsEmpty():
    g = BRepGraph()
    assert not BRepGraph_FaceIterator(g).More()
    assert not BRepGraph_EdgeIterator(g).More()
    assert not BRepGraph_VertexIterator(g).More()
    assert not BRepGraph_SolidIterator(g).More()


def test_BRepGraph_IteratorTest_CoEdgeIterator_CountMatchesTopology(graph):
    assert _count(BRepGraph_CoEdgeIterator(graph)) == 24
