# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_BatchOps_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_ChildRefId,
    BRepGraph_CoEdgeId,
    BRepGraph_FaceId,
    BRepGraph_FaceRefId,
    BRepGraph_NodeId,
    BRepGraph_OccurrenceId,
    BRepGraph_OccurrenceRefId,
    BRepGraph_ProductId,
    BRepGraph_ShellId,
    BRepGraph_ShellRefId,
    BRepGraph_SolidId,
    BRepGraph_SolidRefId,
    BRepGraph_WireId,
)
from nanocct.BRepGraphInc import ParityOrientation
from nanocct.Geom import Geom_Plane
from nanocct.gp import gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED
from nanocct.TopLoc import TopLoc_Location


def _arr(T, items):
    """0-based NCollection_Array1 like the C++ NCollection_Array1<T>(n)."""
    if len(items) == 0:
        return NCollection_Array1[T]()
    a = NCollection_Array1[T](0, len(items) - 1)
    for i, v in enumerate(items):
        a.SetValue(i, v)
    return a


def _all_valid(refs, n):
    assert refs.Size() == n
    for i in range(n):
        assert refs.Value(i).IsValid()


def create_simple_face(g):
    ed = g.Editor()
    v0 = ed.Vertices().Add(gp_Pnt(0, 0, 0), 1.0e-7)
    v1 = ed.Vertices().Add(gp_Pnt(10, 0, 0), 1.0e-7)
    edge = ed.Edges().Add(v0, v1, None, 0.0, 10.0, 1.0e-7)
    coedges = [ed.CoEdges().Add(edge, TopAbs_FORWARD)]
    wire = ed.Wires().Add(_arr(BRepGraph_CoEdgeId, coedges))
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    return ed.Faces().Add(plane, wire, _arr(BRepGraph_WireId, []), 1.0e-7)


def _faces(g, n):
    faces = [create_simple_face(g) for _ in range(n)]
    for f in faces:
        assert f.IsValid()
    return faces


def _shells_with_faces(g, faces):
    shells = []
    for f in faces:
        s = g.Editor().Shells().Add()
        assert s.IsValid()
        g.Editor().Shells().Append(s, f)
        shells.append(s)
    return shells


def _solids_with_shells(g, shells):
    solids = []
    for s in shells:
        so = g.Editor().Solids().Add()
        assert so.IsValid()
        g.Editor().Solids().Append(so, s)
        solids.append(so)
    return solids


def test_BRepGraph_BatchOpsTest_ShellOps_AppendBatch_AllForward():
    g = BRepGraph()
    faces = _faces(g, 3)
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()
    refs = g.Editor().Shells().Append(shell, _arr(BRepGraph_FaceId, faces))
    _all_valid(refs, 3)


def test_BRepGraph_BatchOpsTest_ShellOps_AppendBatch_WithOrientations():
    g = BRepGraph()
    faces = _faces(g, 2)
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()
    oris = _arr(ParityOrientation, [ParityOrientation(TopAbs_FORWARD), ParityOrientation(TopAbs_REVERSED)])
    refs = g.Editor().Shells().Append(shell, _arr(BRepGraph_FaceId, faces), oris)
    _all_valid(refs, 2)


def test_BRepGraph_BatchOpsTest_ShellOps_AppendBatch_InvalidFace_ReturnsEmpty():
    g = BRepGraph()
    (f0,) = _faces(g, 1)
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()
    refs = g.Editor().Shells().Append(shell, _arr(BRepGraph_FaceId, [f0, BRepGraph_FaceId(999)]))
    assert refs.Size() == 0


def test_BRepGraph_BatchOpsTest_ShellOps_AppendBatch_InvalidShell_ReturnsEmpty():
    g = BRepGraph()
    (f0,) = _faces(g, 1)
    refs = g.Editor().Shells().Append(BRepGraph_ShellId(999), _arr(BRepGraph_FaceId, [f0]))
    assert refs.Size() == 0


def test_BRepGraph_BatchOpsTest_ShellOps_RemoveFaces_AllRemoved():
    g = BRepGraph()
    f0, f1 = _faces(g, 2)
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()
    r0 = g.Editor().Shells().Append(shell, f0)
    r1 = g.Editor().Shells().Append(shell, f1)
    assert r0.IsValid()
    assert r1.IsValid()
    assert g.Editor().Shells().RemoveFaces(shell, _arr(BRepGraph_FaceRefId, [r0, r1]))


def test_BRepGraph_BatchOpsTest_ShellOps_RemoveFaces_InvalidRef_ReturnsFalse():
    g = BRepGraph()
    (f0,) = _faces(g, 1)
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()
    r0 = g.Editor().Shells().Append(shell, f0)
    assert r0.IsValid()
    assert not g.Editor().Shells().RemoveFaces(shell, _arr(BRepGraph_FaceRefId, [r0, BRepGraph_FaceRefId(999)]))


def test_BRepGraph_BatchOpsTest_SolidOps_AppendBatch_AllForward():
    g = BRepGraph()
    shells = _shells_with_faces(g, _faces(g, 2))
    solid = g.Editor().Solids().Add()
    assert solid.IsValid()
    refs = g.Editor().Solids().Append(solid, _arr(BRepGraph_ShellId, shells))
    _all_valid(refs, 2)


def test_BRepGraph_BatchOpsTest_SolidOps_RemoveShells_AllRemoved():
    g = BRepGraph()
    (shell,) = _shells_with_faces(g, _faces(g, 1))
    solid = g.Editor().Solids().Add()
    assert solid.IsValid()
    r0 = g.Editor().Solids().Append(solid, shell)
    assert r0.IsValid()
    assert g.Editor().Solids().RemoveShells(solid, _arr(BRepGraph_ShellRefId, [r0]))


def test_BRepGraph_BatchOpsTest_CompoundOps_AppendBatch_AllForward():
    g = BRepGraph()
    f0, f1 = _faces(g, 2)
    comp = g.Editor().Compounds().Add(_arr(BRepGraph_NodeId, []))
    assert comp.IsValid()
    refs = g.Editor().Compounds().Append(comp, _arr(BRepGraph_NodeId, [BRepGraph_NodeId(f0), BRepGraph_NodeId(f1)]))
    _all_valid(refs, 2)


def test_BRepGraph_BatchOpsTest_CompoundOps_RemoveChildren_AllRemoved():
    g = BRepGraph()
    (f0,) = _faces(g, 1)
    comp = g.Editor().Compounds().Add(_arr(BRepGraph_NodeId, []))
    assert comp.IsValid()
    r0 = g.Editor().Compounds().Append(comp, BRepGraph_NodeId(f0))
    assert r0.IsValid()
    assert g.Editor().Compounds().RemoveChildren(comp, _arr(BRepGraph_ChildRefId, [r0]))


def test_BRepGraph_BatchOpsTest_CompoundOps_ReplaceChild():
    g = BRepGraph()
    f0, f1 = _faces(g, 2)
    comp = g.Editor().Compounds().Add(_arr(BRepGraph_NodeId, []))
    assert comp.IsValid()
    r0 = g.Editor().Compounds().Append(comp, BRepGraph_NodeId(f0))
    assert r0.IsValid()
    g.Editor().Compounds().ReplaceChild(r0, BRepGraph_NodeId(f1))


def test_BRepGraph_BatchOpsTest_CompSolidOps_AppendBatch_AllForward():
    g = BRepGraph()
    solids = _solids_with_shells(g, _shells_with_faces(g, _faces(g, 2)))
    cs = g.Editor().CompSolids().Add(_arr(BRepGraph_SolidId, []))
    assert cs.IsValid()
    refs = g.Editor().CompSolids().Append(cs, _arr(BRepGraph_SolidId, solids))
    _all_valid(refs, 2)


def test_BRepGraph_BatchOpsTest_CompSolidOps_RemoveSolids_AllRemoved():
    g = BRepGraph()
    (solid,) = _solids_with_shells(g, _shells_with_faces(g, _faces(g, 1)))
    cs = g.Editor().CompSolids().Add(_arr(BRepGraph_SolidId, []))
    assert cs.IsValid()
    r0 = g.Editor().CompSolids().Append(cs, solid)
    assert r0.IsValid()
    assert g.Editor().CompSolids().RemoveSolids(cs, _arr(BRepGraph_SolidRefId, [r0]))


def test_BRepGraph_BatchOpsTest_CompSolidOps_ReplaceSolid():
    g = BRepGraph()
    s0, s1 = _solids_with_shells(g, _shells_with_faces(g, _faces(g, 2)))
    cs = g.Editor().CompSolids().Add(_arr(BRepGraph_SolidId, []))
    assert cs.IsValid()
    r0 = g.Editor().CompSolids().Append(cs, s0)
    assert r0.IsValid()
    g.Editor().CompSolids().ReplaceSolid(r0, s1)


def test_BRepGraph_BatchOpsTest_ProductOps_AppendBatch():
    g = BRepGraph()
    s0, s1 = _solids_with_shells(g, _shells_with_faces(g, _faces(g, 2)))
    c0 = g.Editor().Products().Add(BRepGraph_NodeId(s0))
    c1 = g.Editor().Products().Add(BRepGraph_NodeId(s1))
    assert c0.IsValid()
    assert c1.IsValid()
    parent = g.Editor().Products().Add()
    assert parent.IsValid()
    refs = g.Editor().Products().Append(
        parent,
        _arr(BRepGraph_ProductId, [c0, c1]),
        _arr(TopLoc_Location, [TopLoc_Location(), TopLoc_Location()]),
    )
    _all_valid(refs, 2)


def test_BRepGraph_BatchOpsTest_ProductOps_RemoveOccurrences_AllRemoved():
    g = BRepGraph()
    (s0,) = _solids_with_shells(g, _shells_with_faces(g, _faces(g, 1)))
    child = g.Editor().Products().Add(BRepGraph_NodeId(s0))
    assert child.IsValid()
    parent = g.Editor().Products().Add()
    assert parent.IsValid()
    out_ref = BRepGraph_OccurrenceRefId()
    occ = g.Editor().Products().Append(parent, child, TopLoc_Location(), BRepGraph_OccurrenceId(), out_ref)
    assert occ.IsValid()
    assert out_ref.IsValid()
    assert g.Editor().Products().RemoveOccurrences(parent, _arr(BRepGraph_OccurrenceRefId, [out_ref]))


def test_BRepGraph_BatchOpsTest_Validation_AfterBatchOperations():
    g = BRepGraph()
    faces = _faces(g, 3)
    shell = g.Editor().Shells().Add()
    assert shell.IsValid()
    refs = g.Editor().Shells().Append(shell, _arr(BRepGraph_FaceId, faces))
    _all_valid(refs, 3)
    to_remove = _arr(BRepGraph_FaceRefId, [refs.Value(0), refs.Value(1)])
    assert g.Editor().Shells().RemoveFaces(shell, to_remove)
