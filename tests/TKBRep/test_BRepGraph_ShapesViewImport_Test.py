# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_ShapesViewImport_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_ChildExplorer,
    BRepGraph_CoEdgeId,
    BRepGraph_CompoundId,
    BRepGraph_CompSolidId,
    BRepGraph_DefsVertexOfEdge,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_LayerHistory,
    BRepGraph_NodeId,
    BRepGraph_RelatedIterator,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
    BRepGraph_VertexId,
    BRepGraph_VertexIterator,
    BRepGraph_WireId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_Line, Geom_Plane
from nanocct.gp import gp_Dir, gp_Lin, gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_DataMap
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ProgramError
from nanocct.TCollection import TCollection_AsciiString
from nanocct.TopAbs import TopAbs_FACE, TopAbs_FORWARD
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher

Kind = BRepGraph_NodeId.Kind
Relation = BRepGraph_RelatedIterator.RelationKind


def _arr(cls, items):
    if len(items) == 0:
        return NCollection_Array1[cls]()
    a = NCollection_Array1[cls](1, len(items))
    for i, x in enumerate(items, start=1):
        a[i] = x
    return a


def _count(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _rect_edges(g):
    v = [
        g.Editor().Vertices().Add(gp_Pnt(0, 0, 0), 0.001),
        g.Editor().Vertices().Add(gp_Pnt(10, 0, 0), 0.001),
        g.Editor().Vertices().Add(gp_Pnt(10, 10, 0), 0.001),
        g.Editor().Vertices().Add(gp_Pnt(0, 10, 0), 0.001),
    ]
    lines = [
        Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)),
        Geom_Line(gp_Pnt(10, 0, 0), gp_Dir(0, 1, 0)),
        Geom_Line(gp_Pnt(10, 10, 0), gp_Dir(-1, 0, 0)),
        Geom_Line(gp_Pnt(0, 10, 0), gp_Dir(0, -1, 0)),
    ]
    e = [g.Editor().Edges().Add(v[i], v[(i + 1) % 4], lines[i], 0.0, 10.0, 0.001) for i in range(4)]
    return v, e


def _wire_of(g, edges):
    ces = [g.Editor().CoEdges().Add(e, TopAbs_FORWARD) for e in edges]
    return g.Editor().Wires().Add(_arr(BRepGraph_CoEdgeId, ces))


def _rect_face(g):
    v, e = _rect_edges(g)
    w = _wire_of(g, e)
    f = g.Editor().Faces().Add(Geom_Plane(gp_Pln()), w, _arr(BRepGraph_WireId, []), 0.001)
    return v, e, w, f


def _edge_has_face(g, edge, face):
    it = g.Topo().Edges().FacesOf(edge)
    while it.More():
        if it.CurrentId() == face:
            return True
        it.Next()
    return False


def _count_shared_edges(g, fa, fb):
    n = 0
    it = BRepGraph_RelatedIterator(g, BRepGraph_NodeId(fa))
    while it.More():
        if it.CurrentRelation() == Relation.BoundaryEdge and _edge_has_face(
            g, BRepGraph_EdgeId.FromNodeId_s(it.Current()), fb
        ):
            n += 1
        it.Next()
    return n


def _count_adjacent_faces(g, face):
    n = 0
    it = BRepGraph_RelatedIterator(g, BRepGraph_NodeId(face))
    while it.More():
        if it.CurrentRelation() == Relation.AdjacentFace:
            n += 1
        it.Next()
    return n


def _count_adjacent_edges_of_edge(g, edge):
    if not edge.IsValid(g.Topo().Edges().Nb()) or edge.IsRemoved(g):
        return 0
    adjacent = []
    for vid in _ids(BRepGraph_DefsVertexOfEdge(g, edge)):
        for other in g.Topo().Vertices().Edges(vid):
            if other == edge or other.IsRemoved(g) or other in adjacent:
                continue
            adjacent.append(other)
    return len(adjacent)


# Task 2A: Programmatic Node Addition API


def test_BRepGraph_ShapesViewImportTest_AddVertex_ReturnsValidId():
    g = BRepGraph()
    vid = g.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.001)
    assert vid.IsValid()
    assert vid.Index == 0
    d = g.Topo().Vertices().Definition(BRepGraph_VertexId.Start_s())
    tol = Precision.Confusion_s()
    assert abs(d.Point.X() - 1.0) <= tol
    assert abs(d.Point.Y() - 2.0) <= tol
    assert abs(d.Point.Z() - 3.0) <= tol
    assert abs(d.Tolerance - 0.001) <= 1e-10


def test_BRepGraph_ShapesViewImportTest_AddEdge_WithCurve():
    g = BRepGraph()
    v1 = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 0.001)
    v2 = g.Editor().Vertices().Add(gp_Pnt(10.0, 0.0, 0.0), 0.001)
    line = Geom_Line(gp_Lin(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)))
    eid = g.Editor().Edges().Add(v1, v2, line, 0.0, 10.0, 0.001)
    assert eid.IsValid()
    e0 = BRepGraph_EdgeId.Start_s()
    d = g.Topo().Edges().Definition(e0)
    assert g.Refs().Vertices().Entry(BRepGraph_Tool.Edge.StartVertexId_s(g, e0)).ChildVertexId == v1
    assert g.Refs().Vertices().Entry(BRepGraph_Tool.Edge.EndVertexId_s(g, e0)).ChildVertexId == v2
    assert d.Curve3DRepId.IsValid()
    first, last = BRepGraph_Tool.Edge.Range_s(g, e0)
    assert abs(first - 0.0) <= 1e-10
    assert abs(last - 10.0) <= 1e-10


def test_BRepGraph_ShapesViewImportTest_AddWire_ClosedRectangle():
    g = BRepGraph()
    _v, e = _rect_edges(g)
    wid = _wire_of(g, e)
    assert wid.IsValid()
    assert len(g.Topo().Wires().Relations(BRepGraph_WireId.Start_s()).CoEdgeIds) == 4
    assert BRepGraph_Tool.Wire.IsClosed_s(g, BRepGraph_WireId.Start_s())


def test_BRepGraph_ShapesViewImportTest_AddFace_WithSurface():
    g = BRepGraph()
    _v, _e, _w, fid = _rect_face(g)
    assert fid.IsValid()
    assert g.Topo().Faces().Nb() == 1
    assert g.Topo().Faces().Definition(BRepGraph_FaceId.Start_s()).SurfaceRepId.IsValid()


def test_BRepGraph_ShapesViewImportTest_AddWireToFace_AppendsInnerWireRefAndRelations():
    g = BRepGraph()
    _v, e = _rect_edges(g)
    outer = _wire_of(g, e)
    inner = _wire_of(g, e)
    fid = g.Editor().Faces().Add(Geom_Plane(gp_Pln()), outer, _arr(BRepGraph_WireId, []), 0.001)
    wref = g.Editor().Faces().Append(fid, inner, TopAbs_FORWARD)
    assert wref.IsValid()
    rel = g.Topo().Faces().Relations(fid)
    assert len(rel.WireRefIds) == 2
    assert rel.WireRefIds.Value(1) == wref
    assert g.Refs().Wires().Entry(wref).ChildWireId == inner
    assert len(g.Topo().Wires().Relations(inner).ParentWireRefIds) == 1


def test_BRepGraph_ShapesViewImportTest_AddEdge_InvalidVertex_ReturnsInvalidAndDoesNotAppend():
    g = BRepGraph()
    vid = g.Editor().Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 0.001)
    eid = g.Editor().Edges().Add(vid, BRepGraph_VertexId(42), None, 0.0, 1.0, 0.001)
    assert not eid.IsValid()
    assert g.Topo().Edges().Nb() == 0


def test_BRepGraph_ShapesViewImportTest_AddWire_InvalidEdge_ReturnsInvalidAndDoesNotAppend():
    g = BRepGraph()
    ce = g.Editor().CoEdges().Add(BRepGraph_EdgeId(17), TopAbs_FORWARD)
    wid = g.Editor().Wires().Add(_arr(BRepGraph_CoEdgeId, [ce]))
    assert not wid.IsValid()
    assert g.Topo().Wires().Nb() == 0
    assert g.Topo().CoEdges().Nb() == 0


def test_BRepGraph_ShapesViewImportTest_AddFace_InvalidOuterWire_ReturnsInvalidAndDoesNotAppend():
    g = BRepGraph()
    fid = g.Editor().Faces().Add(Geom_Plane(gp_Pln()), BRepGraph_WireId(9), _arr(BRepGraph_WireId, []), 0.001)
    assert not fid.IsValid()
    assert g.Topo().Faces().Nb() == 0


def test_BRepGraph_ShapesViewImportTest_AddShellAndSolid():
    g = BRepGraph()
    assert g.Editor().Shells().Add().IsValid()
    assert g.Editor().Solids().Add().IsValid()


# Incremental Build (flattened Add)


def test_BRepGraph_ShapesViewImportTest_AppendTwoBoxFaces():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    exp = TopExp_Explorer(box, TopAbs_FACE)
    assert exp.More()
    copy1 = BRepBuilderAPI_Copy(exp.Current(), True)
    exp.Next()
    assert exp.More()
    copy2 = BRepBuilderAPI_Copy(exp.Current(), True)
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(copy1.Shape())
    assert g.Topo().Faces().Nb() == 1
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = False
    opts.Flatten = True
    opts.Parallel = False
    g.Shapes().Add(copy2.Shape(), opts)
    assert g.Topo().Faces().Nb() == 2


# Task 2C: Soft Node Removal


def test_BRepGraph_ShapesViewImportTest_RemoveVertex_IsRemoved():
    g = BRepGraph()
    vid = g.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.001)
    assert not g.Topo().Gen().IsRemoved(BRepGraph_NodeId(vid))
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(vid))
    assert g.Topo().Gen().IsRemoved(BRepGraph_NodeId(vid))


def test_BRepGraph_ShapesViewImportTest_RemoveFaceFromBox():
    g = _box_graph()
    assert g.Topo().Faces().Nb() == 6
    fid = BRepGraph_NodeId(BRepGraph_FaceId(0))
    assert not g.Topo().Gen().IsRemoved(fid)
    g.Editor().Gen().RemoveNode(fid)
    assert g.Topo().Gen().IsRemoved(fid)
    for i in range(1, g.Topo().Faces().Nb()):
        assert not g.Topo().Gen().IsRemoved(BRepGraph_NodeId(BRepGraph_FaceId(i)))


def test_BRepGraph_ShapesViewImportTest_RemoveInvalidNode_NoError():
    g = BRepGraph()
    invalid = BRepGraph_NodeId()
    assert not g.Topo().Gen().IsValid(invalid)
    assert not g.Topo().Gen().IsActive(invalid)
    assert g.Topo().Gen().IsRemoved(invalid)
    g.Editor().Gen().RemoveNode(invalid)


def test_BRepGraph_ShapesViewImportTest_RemoveAlreadyRemovedNode_NoError():
    g = BRepGraph()
    vid = g.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 0.001)
    assert vid.IsValid()
    nid = BRepGraph_NodeId(vid)
    g.Editor().Gen().RemoveNode(nid)
    assert g.Topo().Gen().IsRemoved(nid)
    g.Editor().Gen().RemoveNode(nid)
    assert g.Topo().Gen().IsRemoved(nid)


# Item 1: Complete Construction API (Shell/Solid linking)


def test_BRepGraph_ShapesViewImportTest_AddFace_CreatesUsage():
    g = BRepGraph()
    _v, _e, _w, fid = _rect_face(g)
    sid = g.Editor().Shells().Add()
    fref = g.Editor().Shells().Append(sid, fid)
    assert fref.IsValid()
    assert len(g.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())) == 1


def test_BRepGraph_ShapesViewImportTest_AddFace_InvalidNodes_NoMutation():
    g = BRepGraph()
    sid = g.Editor().Shells().Add()
    fref = g.Editor().Shells().Append(sid, BRepGraph_FaceId(4))
    assert not fref.IsValid()
    assert len(g.Refs().Faces().IdsOf(sid)) == 0


def test_BRepGraph_ShapesViewImportTest_AddShell_CreatesUsage():
    g = BRepGraph()
    sh = g.Editor().Shells().Add()
    so = g.Editor().Solids().Add()
    sref = g.Editor().Solids().Append(so, sh)
    assert sref.IsValid()
    assert len(g.Refs().Shells().IdsOf(BRepGraph_SolidId.Start_s())) == 1


def test_BRepGraph_ShapesViewImportTest_MutInvalidTopologyDefs_ThrowProgramError():
    g = BRepGraph()
    ed = g.Editor()
    cases = [
        (ed.Vertices(), BRepGraph_VertexId(7)),
        (ed.Edges(), BRepGraph_EdgeId(7)),
        (ed.Wires(), BRepGraph_WireId(7)),
        (ed.Faces(), BRepGraph_FaceId(7)),
        (ed.Shells(), BRepGraph_ShellId(7)),
        (ed.Solids(), BRepGraph_SolidId(7)),
        (ed.CoEdges(), BRepGraph_CoEdgeId(7)),
    ]
    for ops, bad in cases:
        with pytest.raises(Standard_ProgramError):
            ops.Mut(bad)


def test_BRepGraph_ShapesViewImportTest_AddCompound_WithChildren():
    g = BRepGraph()
    s1 = g.Editor().Solids().Add()
    s2 = g.Editor().Solids().Add()
    cid = g.Editor().Compounds().Add(_arr(BRepGraph_NodeId, [BRepGraph_NodeId(s1), BRepGraph_NodeId(s2)]))
    assert cid.IsValid()
    assert g.Topo().Compounds().Nb() == 1
    assert len(g.Refs().Children().IdsOf(BRepGraph_CompoundId.Start_s())) == 2


def test_BRepGraph_ShapesViewImportTest_AddCompSolid_WithSolids():
    g = BRepGraph()
    s1 = g.Editor().Solids().Add()
    s2 = g.Editor().Solids().Add()
    csid = g.Editor().CompSolids().Add(_arr(BRepGraph_SolidId, [s1, s2]))
    assert csid.IsValid()
    assert g.Topo().CompSolids().Nb() == 1
    g.Topo().CompSolids().Definition(BRepGraph_CompSolidId.Start_s())
    assert len(g.Refs().Solids().IdsOf(BRepGraph_CompSolidId.Start_s())) == 2


def test_BRepGraph_ShapesViewImportTest_FullSolid_ProgrammaticConstruction():
    g = BRepGraph()
    _v, _e, _w, fid = _rect_face(g)
    sh = g.Editor().Shells().Add()
    g.Editor().Shells().Append(sh, fid)
    so = g.Editor().Solids().Add()
    g.Editor().Solids().Append(so, sh)
    assert g.Topo().Solids().Nb() == 1
    assert g.Topo().Shells().Nb() == 1
    assert g.Topo().Faces().Nb() == 1
    assert len(g.Refs().Shells().IdsOf(BRepGraph_SolidId.Start_s())) == 1


# Item 2: Field-Level Mutation via Editor() for All Def Types


def test_BRepGraph_ShapesViewImportTest_MutableFaceDefinition_ChangesTolerance():
    g = _box_graph()
    assert g.Topo().Faces().Nb() > 0
    f0 = BRepGraph_FaceId.Start_s()
    guard = g.Editor().Faces().Mut(f0)
    g.Editor().Faces().SetTolerance(guard, 0.5)
    del guard  # C++ scope exit
    assert abs(BRepGraph_Tool.Face.Tolerance_s(g, f0) - 0.5) <= 1e-10
    assert g.Topo().Faces().Definition(f0).OwnGen > 0


def test_BRepGraph_ShapesViewImportTest_MutableShellDefinition():
    g = _box_graph()
    assert g.Topo().Shells().Nb() > 0
    guard = g.Editor().Shells().Mut(BRepGraph_ShellId.Start_s())
    guard.MarkDirty()
    del guard
    assert g.Topo().Shells().Definition(BRepGraph_ShellId.Start_s()).OwnGen > 0


def test_BRepGraph_ShapesViewImportTest_MutableSolidDefinition():
    g = _box_graph()
    assert g.Topo().Solids().Nb() > 0
    guard = g.Editor().Solids().Mut(BRepGraph_SolidId.Start_s())
    guard.MarkDirty()
    del guard
    assert g.Topo().Solids().Definition(BRepGraph_SolidId.Start_s()).OwnGen > 0


def test_BRepGraph_ShapesViewImportTest_MutableCompoundDefinition():
    g = BRepGraph()
    g.Editor().Compounds().Add(_arr(BRepGraph_NodeId, []))
    assert g.Topo().Compounds().Nb() == 1
    guard = g.Editor().Compounds().Mut(BRepGraph_CompoundId.Start_s())
    guard.MarkDirty()
    del guard
    assert g.Topo().Compounds().Definition(BRepGraph_CompoundId.Start_s()).OwnGen > 0


def test_BRepGraph_ShapesViewImportTest_MutableCompSolidDefinition():
    g = BRepGraph()
    g.Editor().CompSolids().Add(_arr(BRepGraph_SolidId, []))
    assert g.Topo().CompSolids().Nb() == 1
    guard = g.Editor().CompSolids().Mut(BRepGraph_CompSolidId.Start_s())
    guard.MarkDirty()
    del guard
    assert g.Topo().CompSolids().Definition(BRepGraph_CompSolidId.Start_s()).OwnGen > 0


# Item 3: Definition Traversal Skips Removed Nodes


def test_BRepGraph_ShapesViewImportTest_SkipsRemovedFaces():
    g = _box_graph()
    assert g.Topo().Faces().Nb() == 6
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(Kind.Face, 0))
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(Kind.Face, 3))
    ids = _ids(BRepGraph_FaceIterator(g))
    for fid in ids:
        assert not fid.IsRemoved(g)
    assert len(ids) == 4


def test_BRepGraph_ShapesViewImportTest_SkipsRemovedEdges():
    g = _box_graph()
    n = g.Topo().Edges().Nb()
    assert n > 0
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(Kind.Edge, 0))
    ids = _ids(BRepGraph_EdgeIterator(g))
    for eid in ids:
        assert not eid.IsRemoved(g)
    assert len(ids) == n - 1


def test_BRepGraph_ShapesViewImportTest_SkipsFirstNode():
    g = BRepGraph()
    for x in (0, 1, 2):
        g.Editor().Vertices().Add(gp_Pnt(x, 0, 0), 0.001)
    g.Editor().Gen().RemoveNode(BRepGraph_NodeId(Kind.Vertex, 0))
    ids = _ids(BRepGraph_VertexIterator(g))
    for vid in ids:
        assert not vid.IsRemoved(g)
    assert len(ids) == 2


# Item 4: Cascading Soft Removal


def test_BRepGraph_ShapesViewImportTest_RemoveFace_RemovesWiresAndEdges():
    g = BRepGraph()
    v, e, w, f = _rect_face(g)
    g.Editor().Gen().RemoveSubgraph(BRepGraph_NodeId(f))
    for x in [f, w, *e, *v]:
        assert g.Topo().Gen().IsRemoved(BRepGraph_NodeId(x))


def test_BRepGraph_ShapesViewImportTest_RemoveSolid_CascadesToFaces():
    g = _box_graph()
    sid = BRepGraph_NodeId(BRepGraph_SolidId(0))
    g.Editor().Gen().RemoveSubgraph(sid)
    assert g.Topo().Gen().IsRemoved(sid)
    for i in range(g.Topo().Shells().Nb()):
        assert g.Topo().Gen().IsRemoved(BRepGraph_NodeId(BRepGraph_ShellId(i)))
    for i in range(g.Topo().Faces().Nb()):
        assert g.Topo().Gen().IsRemoved(BRepGraph_NodeId(BRepGraph_FaceId(i)))


def test_BRepGraph_ShapesViewImportTest_RemoveSubgraph_SharedFace_PreservesSharedEdgesAndVertices():
    g = _box_graph()
    nf, ne, nv = g.Topo().Faces().Nb(), g.Topo().Edges().Nb(), g.Topo().Vertices().Nb()
    assert (nf, ne, nv) == (6, 12, 8)
    removed = BRepGraph_NodeId(BRepGraph_FaceId(0))
    g.Editor().Gen().RemoveSubgraph(removed)
    assert g.Topo().Gen().IsRemoved(removed)
    for i in range(1, nf):
        assert not g.Topo().Gen().IsRemoved(BRepGraph_NodeId(BRepGraph_FaceId(i)))
    for i in range(ne):
        assert not g.Topo().Gen().IsRemoved(BRepGraph_NodeId(BRepGraph_EdgeId(i)))
    for i in range(nv):
        assert not g.Topo().Gen().IsRemoved(BRepGraph_NodeId(BRepGraph_VertexId(i)))


# Item 5: Edge Adjacency Queries


def test_BRepGraph_ShapesViewImportTest_FacesOfEdge_BoxSharedEdge():
    g = _box_graph()
    for i in range(g.Topo().Edges().Nb()):
        assert _count(g.Topo().Edges().FacesOf(BRepGraph_EdgeId(i))) == 2


def test_BRepGraph_ShapesViewImportTest_SharedEdges_AdjacentBoxFaces():
    g = _box_graph()
    n = g.Topo().Faces().Nb()
    assert n == 6
    pairs = 0
    for a in range(n):
        for b in range(a + 1, n):
            if _count_shared_edges(g, BRepGraph_FaceId(a), BRepGraph_FaceId(b)) > 0:
                pairs += 1
    assert pairs == 12


def test_BRepGraph_ShapesViewImportTest_AdjacentFaces_BoxFace():
    g = _box_graph()
    assert g.Topo().Faces().Nb() == 6
    for i in range(g.Topo().Faces().Nb()):
        assert _count_adjacent_faces(g, BRepGraph_FaceId(i)) == 4


def test_BRepGraph_ShapesViewImportTest_FacesOfEdge_NoFaces_Programmatic():
    g = BRepGraph()
    v0 = g.Editor().Vertices().Add(gp_Pnt(0, 0, 0), 0.001)
    v1 = g.Editor().Vertices().Add(gp_Pnt(10, 0, 0), 0.001)
    eid = g.Editor().Edges().Add(v0, v1, Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 0.0, 10.0, 0.001)
    assert _count(g.Topo().Edges().FacesOf(eid)) == 0


def test_BRepGraph_ShapesViewImportTest_EdgesOfFace_Box_HasEdges():
    g = _box_graph()
    exp = BRepGraph_ChildExplorer(g, BRepGraph_NodeId(BRepGraph_FaceId.Start_s()), Kind.Edge)
    assert _count(exp) == 4


def test_BRepGraph_ShapesViewImportTest_VerticesOfEdge_Box_HasTwoVertices():
    g = _box_graph()
    exp = BRepGraph_ChildExplorer(g, BRepGraph_NodeId(BRepGraph_EdgeId.Start_s()), Kind.Vertex)
    assert _count(exp) == 2


def test_BRepGraph_ShapesViewImportTest_EdgesOfVertex_Box_ThreeEdges():
    g = _box_graph()
    assert len(g.Topo().Vertices().Edges(BRepGraph_VertexId.Start_s())) == 3


def test_BRepGraph_ShapesViewImportTest_AdjacentEdges_Box_SharedVertex():
    g = _box_graph()
    assert _count_adjacent_edges_of_edge(g, BRepGraph_EdgeId.Start_s()) >= 4


def test_BRepGraph_ShapesViewImportTest_NbFacesOfEdge_Box_TwoFaces():
    g = _box_graph()
    assert g.Topo().Edges().NbFaces(BRepGraph_EdgeId.Start_s()) == 2


def test_BRepGraph_ShapesViewImportTest_IsManifoldEdge_Box_True():
    g = _box_graph()
    assert BRepGraph_Tool.Edge.IsManifold_s(g, BRepGraph_EdgeId.Start_s())
    assert not BRepGraph_Tool.Edge.IsBoundary_s(g, BRepGraph_EdgeId.Start_s())


def test_BRepGraph_ShapesViewImportTest_InvalidInput_ReturnsEmpty():
    g = _box_graph()
    assert len(g.Topo().Vertices().Edges(BRepGraph_VertexId(999))) == 0
    assert _count_adjacent_edges_of_edge(g, BRepGraph_EdgeId(999)) == 0


def test_BRepGraph_ShapesViewImportTest_AddWithHistory_PreservesRequestedAddedNodes():
    g = BRepGraph()
    reg = g.LayerRegistry()
    hist = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    if hist is None:
        reg.RegisterLayer(BRepGraph_LayerHistory())
        hist = reg.FindLayer(BRepGraph_LayerHistory.GetID_s())
    hist.SetEnabled(False)
    opts = BRepGraph.ShapesView.Options()
    opts.TrackAddedNodes = True
    inputs = NCollection_DataMap[TopoDS_Shape, BRepGraph_NodeId, TopTools_ShapeMapHasher]()
    box = BRepPrimAPI_MakeBox(10, 20, 30).Shape()
    res = g.Shapes().AddWithHistory(box, inputs, None, TCollection_AsciiString("Test:DisabledHistory"), opts)
    assert res.IsOk()
    assert res.AddedNodes.Extent() > 0
    from_roots = NCollection_DataMap[TopoDS_Shape, BRepGraph_NodeId, TopTools_ShapeMapHasher]()
    g.Shapes().CollectHistoryInputs(_arr(BRepGraph_NodeId, [res.TopologyRoot]), from_roots)
    assert from_roots.Extent() > 0
    assert reg.FindLayer(BRepGraph_LayerHistory.GetID_s()).NbRecords() == 0
