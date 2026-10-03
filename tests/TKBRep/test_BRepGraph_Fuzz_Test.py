# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Fuzz_Test.cxx (LGPL-2.1 with the OCCT exception)
# The C++ test draws from std::mt19937 with std distributions; Python's random.Random gives a different
# (but equally deterministic) mutation sequence per seed.
import random

import pytest

from nanocct.BRepGraph import BRepGraph, BRepGraph_EdgeId, BRepGraph_FaceId, BRepGraph_Validate, BRepGraph_VertexId
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.gp import gp_Pnt

SEEDS = [1, 7, 42, 137, 2026, 0xC0FFEE, 0xDEADBEEF]


def _pick_active(g, rng, id_cls, nb):
    if nb <= 0:
        return None
    for _ in range(8):
        cand = id_cls(rng.randint(0, nb - 1))
        if not cand.IsRemoved(g):
            return cand
    return None


def _apply_one(g, rng):
    kind = rng.randint(0, 2)
    topo = g.Topo()
    ed = g.Editor()
    if kind == 0:
        eid = _pick_active(g, rng, BRepGraph_EdgeId, topo.Edges().Nb())
        if eid is None:
            return False
        tol = topo.Edges().Definition(eid).Tolerance
        mut = ed.Edges().Mut(eid)
        ed.Edges().SetTolerance(mut, tol + 1.0e-4)
        del mut
        return True
    if kind == 1:
        vid = _pick_active(g, rng, BRepGraph_VertexId, topo.Vertices().Nb())
        if vid is None:
            return False
        old = gp_Pnt(topo.Vertices().Definition(vid).Point)
        mut = ed.Vertices().Mut(vid)
        ed.Vertices().SetPoint(
            mut,
            gp_Pnt(old.X() + rng.uniform(-0.1, 0.1), old.Y() + rng.uniform(-0.1, 0.1), old.Z() + rng.uniform(-0.1, 0.1)),
        )
        del mut
        return True
    nb_faces = topo.Faces().Nb()
    if nb_faces <= 0:
        return False
    fid = BRepGraph_FaceId(rng.randint(0, nb_faces - 1))
    if fid.IsRemoved(g):
        return False
    tol = topo.Faces().Definition(fid).Tolerance
    mut = ed.Faces().Mut(fid)
    ed.Faces().SetTolerance(mut, tol + 1.0e-4)
    del mut
    return True


def _run_fuzz(g, seed, nb_iter):
    rng = random.Random(seed)
    nb_validated = 0
    for i in range(nb_iter):
        if _apply_one(g, rng):
            res = BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s())
            nb_validated += 1
            assert res.IsValid(), f"fuzz iteration {i} (seed={seed}) left the graph invalid"
    return nb_validated


def _graph_of(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    assert BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s()).IsValid()
    return g


@pytest.mark.parametrize("seed", SEEDS)
def test_BRepGraph_FuzzSeedTest_BoxSeed_RandomMutations_RemainValid(seed):
    g = _graph_of(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert _run_fuzz(g, seed, 50) >= 1


@pytest.mark.parametrize("seed", SEEDS)
def test_BRepGraph_FuzzSeedTest_CylinderSeed_RandomMutations_RemainValid(seed):
    g = _graph_of(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())
    assert _run_fuzz(g, seed, 40) >= 1
