# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_SeamRedesign_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgesOfEdge,
    BRepGraph_CoEdgesOfWire,
    BRepGraph_EdgeIterator,
    BRepGraph_NodeId,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.gp import gp_Pnt
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_WIRE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Iterator, TopoDS_Vertex


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    assert g.Shapes().Add(shape).IsOk()
    return g


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _find_seam_coedge(g):
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        # Keep the vector alive in a name: CoEdges() returns a copy in Python and the
        # iterator only stores a pointer to it (a temporary here dangles, see report).
        parents = g.Topo().Edges().CoEdges(eid)
        for ceid in _ids(BRepGraph_CoEdgesOfEdge(g, parents)):
            if BRepGraph_Tool.CoEdge.IsSeam_s(g, ceid):
                return ceid
    return BRepGraph_CoEdgeId()


def _wire_edge_counts(shape):
    counts = []
    for face in TopExp_Explorer(shape, TopAbs_FACE):
        wit = TopoDS_Iterator(face, False, False)
        while wit.More():
            if wit.Value().ShapeType() == TopAbs_WIRE:
                n = 0
                eit = TopoDS_Iterator(wit.Value(), False, False)
                while eit.More():
                    n += 1
                    eit.Next()
                counts.append(n)
            wit.Next()
    return counts


def test_BRepGraph_SeamRedesignTest_CylinderLateralWire_BothSeamHalvesInCoEdgeIds():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    seam = _find_seam_coedge(g)
    assert seam.IsValid()
    pair = BRepGraph_Tool.CoEdge.SeamPair_s(g, seam)
    assert pair.IsValid()
    wire = g.Topo().CoEdges().Wire(seam)
    assert wire.IsValid()
    in_wire = _ids(BRepGraph_CoEdgesOfWire(g, wire))
    assert seam in in_wire
    assert pair in in_wire


def test_BRepGraph_SeamRedesignTest_CylinderLateralWire_NbCoEdges_MatchesTopoDSIterator():
    cyl = BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape()
    g = _graph(cyl)
    lateral = None
    for f in TopExp_Explorer(cyl, TopAbs_FACE):
        face = TopoDS.Face(f)
        if sum(1 for _ in TopExp_Explorer(face, TopAbs_EDGE)) == 4:
            lateral = face
            break
    assert lateral is not None

    classical = sum(_wire_edge_counts(lateral))

    graph_count = 0
    for wid in _ids(BRepGraph_WireIterator(g)):
        fid = BRepGraph_Tool.Wire.FaceOf_s(g, wid)
        if not fid.IsValid():
            continue
        orig = g.Shapes().Original(fid)
        if orig.IsNull() or not orig.IsSame(lateral):
            continue
        graph_count += BRepGraph_Tool.Wire.NbCoEdges_s(g, wid)
    assert graph_count == classical


def test_BRepGraph_SeamRedesignTest_SeamPair_DerivedQuery_IsSymmetric():
    g = _graph(BRepPrimAPI_MakeSphere(10.0).Shape())
    seams = 0
    for i in range(g.Topo().CoEdges().Nb()):
        ceid = BRepGraph_CoEdgeId(i)
        pair = BRepGraph_Tool.CoEdge.SeamPair_s(g, ceid)
        if not pair.IsValid():
            continue
        seams += 1
        assert BRepGraph_Tool.CoEdge.SeamPair_s(g, pair) == ceid
    assert seams > 0


def test_BRepGraph_SeamRedesignTest_SeamPair_BoxHasNoSeams():
    g = _graph(BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape())
    for i in range(g.Topo().CoEdges().Nb()):
        assert not BRepGraph_Tool.CoEdge.IsSeam_s(g, BRepGraph_CoEdgeId(i))


def test_BRepGraph_SeamRedesignTest_SeamPair_FreeWireHasNoSeams():
    bb = BRep_Builder()
    v1 = TopoDS_Vertex()
    v2 = TopoDS_Vertex()
    bb.MakeVertex(v1, gp_Pnt(0, 0, 0), 1.0e-7)
    bb.MakeVertex(v2, gp_Pnt(1, 0, 0), 1.0e-7)
    mk_edge = BRepBuilderAPI_MakeEdge(v1, v2)
    assert mk_edge.IsDone()
    mk_wire = BRepBuilderAPI_MakeWire(mk_edge.Edge())
    assert mk_wire.IsDone()
    g = _graph(mk_wire.Wire())
    for i in range(g.Topo().CoEdges().Nb()):
        assert not BRepGraph_Tool.CoEdge.IsSeam_s(g, BRepGraph_CoEdgeId(i))


def test_BRepGraph_SeamRedesignTest_EdgeOps_IsSeamOnFace_DerivedFromConnectivity():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    seam = _find_seam_coedge(g)
    assert seam.IsValid()
    d = g.Topo().CoEdges().Definition(seam)
    assert BRepGraph_Tool.Edge.IsSeamOnFace_s(g, d.ChildEdgeId, d.FaceId)

    bg = _graph(BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape())
    for i in range(bg.Topo().CoEdges().Nb()):
        d = bg.Topo().CoEdges().Definition(BRepGraph_CoEdgeId(i))
        if not d.FaceId.IsValid():
            continue
        assert not BRepGraph_Tool.Edge.IsSeamOnFace_s(bg, d.ChildEdgeId, d.FaceId)


def test_BRepGraph_SeamRedesignTest_NbDistinctEdges_AccountsForSeamHalves():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    with_seams = 0
    for wid in _ids(BRepGraph_WireIterator(g)):
        raw = BRepGraph_Tool.Wire.NbCoEdges_s(g, wid)
        distinct = BRepGraph_Tool.Wire.NbDistinctEdges_s(g, wid)
        assert distinct <= raw
        if raw > distinct:
            with_seams += 1
            assert raw - distinct >= 1
    assert with_seams >= 1


def test_BRepGraph_SeamRedesignTest_Reconstruct_CylinderWire_TopoDSIteratorOrder():
    original = BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape()
    g = _graph(original)
    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_NodeId.Kind.Solid, 0))
    assert not recon.IsNull()
    assert _wire_edge_counts(recon) == _wire_edge_counts(original)


def test_BRepGraph_SeamRedesignTest_Validate_DetectsAsymmetricSeamPair():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    seam = _find_seam_coedge(g)
    assert seam.IsValid()
    mate = BRepGraph_Tool.CoEdge.SeamPair_s(g, seam)
    assert mate.IsValid()

    ori = g.Topo().CoEdges().Definition(seam).Orientation
    g.Editor().CoEdges().SetOrientation(mate, ori)

    d = g.Topo().CoEdges().Definition(seam)
    assert not BRepGraph_Tool.Edge.IsSeamOnFace_s(g, d.ChildEdgeId, d.FaceId)

    res = BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s())
    assert not res.IsValid()
    Error = BRepGraph_Validate.Severity.Error
    assert res.NbIssues(Error) > 0
    found = False
    for issue in res.Issues:
        if issue.Sev == Error and issue.Description.Search("same Orientation") > 0:
            found = True
            break
    assert found
