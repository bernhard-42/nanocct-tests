# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_MutGuard_Test.cxx (LGPL-2.1 with the OCCT exception)
# The C++ move-semantics tests are left out. A C++ scope end is written as `del guard` (CPython frees it at once).
import pytest

from nanocct.BRepGraph import BRepGraph, BRepGraph_EdgeId, BRepGraph_VertexId
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.Standard import Standard_ProgramError


def _box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _own_gen(g, v):
    return g.Topo().Vertices().Definition(v).OwnGen


def test_BRepGraph_MutGuardTest_ExceptionInsideScope_StillNotifies():
    g = _box_graph()
    assert not g.IsEmpty()
    before = _own_gen(g, BRepGraph_VertexId.Start_s())

    def scope():
        guard = g.Editor().Vertices().Mut(BRepGraph_VertexId.Start_s())
        g.Editor().Vertices().SetPoint(guard, gp_Pnt(9.0, 9.0, 9.0))
        raise RuntimeError("test: throw mid-scope")

    try:
        scope()
    except RuntimeError:
        pass
    assert _own_gen(g, BRepGraph_VertexId.Start_s()) > before


def test_BRepGraph_MutGuardTest_DuplicateGuard_Rejected():
    g = _box_graph()
    guard1 = g.Editor().Vertices().Mut(BRepGraph_VertexId.Start_s())
    assert bool(guard1)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Vertices().Mut(BRepGraph_VertexId.Start_s())
    del guard1


def test_BRepGraph_MutGuardTest_GuardAllowsGuardedSetter():
    g = _box_graph()
    guard = g.Editor().Edges().Mut(BRepGraph_EdgeId(0))
    g.Editor().Edges().SetTolerance(guard, 0.5)
    assert guard.IsDirty()
    del guard


def test_BRepGraph_MutGuardTest_GuardBlocksStructuralRemoval():
    g = _box_graph()
    guard = g.Editor().Vertices().Mut(BRepGraph_VertexId.Start_s())
    assert bool(guard)
    with pytest.raises(Standard_ProgramError):
        g.Editor().Gen().RemoveNode(BRepGraph_VertexId.Start_s())
    del guard


def test_BRepGraph_MutGuardTest_GuardReleasedOnDestruction_CanReacquire():
    g = _box_graph()
    guard = g.Editor().Vertices().Mut(BRepGraph_VertexId.Start_s())
    assert bool(guard)
    del guard
    guard2 = g.Editor().Vertices().Mut(BRepGraph_VertexId.Start_s())
    assert bool(guard2)
    del guard2


def test_BRepGraph_MutGuardTest_ClearRejectsActiveGuard():
    g = _box_graph()
    guard = g.Editor().Vertices().Mut(BRepGraph_VertexId.Start_s())
    assert bool(guard)
    with pytest.raises(Standard_ProgramError):
        g.Clear()
    del guard
    g.Clear()
