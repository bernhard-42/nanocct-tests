# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Reconstruct_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_NodeId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
    BRepGraph_VertexId,
    BRepGraph_VertexIterator,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.GProp import GProp_GProps
from nanocct.gp import gp_Pnt
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound

Kind = BRepGraph_NodeId.Kind


def _area(shape):
    p = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, p)
    return p.Mass()


def _volume(shape):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p)
    return p.Mass()


def _count(shape, kind):
    return sum(1 for _ in TopExp_Explorer(shape, kind))


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _box():
    return BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _check_prop(shape, prop):
    orig = prop(shape)
    g = _graph(shape)
    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Solid, 0))
    assert abs(prop(recon) - orig) <= orig * 0.01


def test_BRepGraph_ReconstructTest_Box_Area_Preserved():
    _check_prop(_box(), _area)


def test_BRepGraph_ReconstructTest_Box_Volume_Preserved():
    _check_prop(_box(), _volume)


def test_BRepGraph_ReconstructTest_Sphere_Area_Preserved():
    _check_prop(BRepPrimAPI_MakeSphere(15.0).Shape(), _area)


def test_BRepGraph_ReconstructTest_Sphere_Volume_Preserved():
    _check_prop(BRepPrimAPI_MakeSphere(15.0).Shape(), _volume)


def test_BRepGraph_ReconstructTest_Cylinder_Area_Preserved():
    _check_prop(BRepPrimAPI_MakeCylinder(10.0, 20.0).Shape(), _area)


def test_BRepGraph_ReconstructTest_Cylinder_Volume_Preserved():
    _check_prop(BRepPrimAPI_MakeCylinder(10.0, 20.0).Shape(), _volume)


def test_BRepGraph_ReconstructTest_Shell_FaceCount_MatchesOriginal():
    box = _box()
    g = _graph(box)
    shell = g.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Shell, 0))
    assert _count(shell, TopAbs_FACE) == _count(box, TopAbs_FACE)


def test_BRepGraph_ReconstructTest_Wire_EdgeCount_FourPerBoxFace():
    g = _graph(_box())
    for wid in _ids(BRepGraph_WireIterator(g)):
        wire = g.Shapes().Reconstruct(BRepGraph_NodeId(wid))
        assert _count(wire, TopAbs_EDGE) == 4


def test_BRepGraph_ReconstructTest_Edge_HasCurve_NonNull():
    g = _graph(_box())
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        if BRepGraph_Tool.Edge.Degenerated_s(g, eid):
            continue
        edge = g.Shapes().Reconstruct(BRepGraph_NodeId(eid))
        curve, _first, _last = BRep_Tool.Curve_s(TopoDS.Edge(edge))
        assert curve is not None


def test_BRepGraph_ReconstructTest_Edge_ParameterRange_Preserved():
    g = _graph(_box())
    tol = Precision.Confusion_s()
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        if BRepGraph_Tool.Edge.Degenerated_s(g, eid):
            continue
        edge = g.Shapes().Reconstruct(BRepGraph_NodeId(eid))
        _curve, first, last = BRep_Tool.Curve_s(TopoDS.Edge(edge))
        dfirst, dlast = BRepGraph_Tool.Edge.Range_s(g, eid)
        assert abs(first - dfirst) <= tol
        assert abs(last - dlast) <= tol


def test_BRepGraph_ReconstructTest_Vertex_Point_MatchesDefPoint():
    g = _graph(_box())
    tol = Precision.Confusion_s()
    for vid in _ids(BRepGraph_VertexIterator(g)):
        dp = BRepGraph_Tool.Vertex.Pnt_s(g, vid)
        rp = BRep_Tool.Pnt_s(TopoDS.Vertex(g.Shapes().Reconstruct(BRepGraph_NodeId(vid))))
        assert abs(rp.X() - dp.X()) <= tol
        assert abs(rp.Y() - dp.Y()) <= tol
        assert abs(rp.Z() - dp.Z()) <= tol


def test_BRepGraph_ReconstructTest_Face_PCurvesPresent_OnAllEdges():
    g = _graph(_box())
    for fid in _ids(BRepGraph_FaceIterator(g)):
        rf = g.Shapes().Reconstruct(BRepGraph_NodeId(fid))
        assert not rf.IsNull()
        face = TopoDS.Face(rf)
        for e in TopExp_Explorer(face, TopAbs_EDGE):
            edge = TopoDS.Edge(e)
            if BRep_Tool.Degenerated_s(edge):
                continue
            pc, _f, _l = BRep_Tool.CurveOnSurface_s(edge, face)
            assert pc is not None


def test_BRepGraph_ReconstructTest_Face_OrientationPreserved():
    g = _graph(_box())
    assert g.Topo().Shells().Nb() == 1
    for rid in g.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s()):
        ref = g.Refs().Faces().Entry(rid)
        rf = g.Shapes().Reconstruct(BRepGraph_NodeId(ref.ChildFaceId))
        assert not rf.IsNull()
        assert rf.ShapeType() == TopAbs_FACE


def test_BRepGraph_ReconstructTest_Shape_UnmodifiedGraph_SameAsOriginal():
    g = _graph(_box())
    sid = BRepGraph_NodeId(BRepGraph_SolidId(0))
    assert g.Shapes().HasOriginal(sid)
    shape = g.Shapes().Shape(sid)
    orig = g.Shapes().Original(sid)
    assert not orig.IsNull()
    assert shape.IsSame(orig)


def test_BRepGraph_ReconstructTest_HasOriginal_BuildFace_ReturnsTrue():
    g = _graph(_box())
    assert g.Shapes().HasOriginal(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))


def test_BRepGraph_ReconstructTest_Original_Face_IsSameAsBuildInputFace():
    box = _box()
    exp = TopExp_Explorer(box, TopAbs_FACE)
    assert exp.More()
    first = exp.Current()
    g = _graph(box)
    orig = g.Shapes().Original(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    assert not orig.IsNull()
    assert orig.IsSame(first)


def test_BRepGraph_ReconstructTest_HasOriginal_ManualVertex_ReturnsFalse():
    g = _graph(_box())
    vid = g.Editor().Vertices().Add(gp_Pnt(42.0, 0.0, 0.0), 0.001)
    assert vid.IsValid()
    assert not g.Shapes().HasOriginal(BRepGraph_NodeId(vid))


def test_BRepGraph_ReconstructTest_FindNode_OriginalFace_RoundTrip():
    g = _graph(_box())
    fid = BRepGraph_NodeId(BRepGraph_FaceId.Start_s())
    orig = g.Shapes().Original(fid)
    assert not orig.IsNull()
    assert g.Shapes().FindNode(orig) == fid


def test_BRepGraph_ReconstructTest_Reconstruct_Face_ValidShape():
    g = _graph(_box())
    assert g.Topo().Faces().Nb() > 0
    r = g.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_FaceId.Start_s()))
    assert not r.IsNull()
    assert r.ShapeType() == TopAbs_FACE


def test_BRepGraph_ReconstructTest_Reconstruct_Edge_ValidShape():
    g = _graph(_box())
    assert g.Topo().Edges().Nb() > 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        if BRepGraph_Tool.Edge.Degenerated_s(g, eid):
            continue
        r = g.Shapes().Reconstruct(BRepGraph_NodeId(eid))
        assert not r.IsNull()
        assert r.ShapeType() == TopAbs_EDGE
        return
    pytest.fail("No non-degenerate edge found")


def test_BRepGraph_ReconstructTest_Reconstruct_Vertex_CorrectPoint():
    g = _graph(_box())
    assert g.Topo().Vertices().Nb() > 0
    expected = BRepGraph_Tool.Vertex.Pnt_s(g, BRepGraph_VertexId.Start_s())
    r = g.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Vertex, 0))
    assert not r.IsNull()
    assert r.ShapeType() == TopAbs_VERTEX
    assert BRep_Tool.Pnt_s(TopoDS.Vertex(r)).Distance(expected) <= Precision.Confusion_s()


def test_BRepGraph_ReconstructTest_AfterVertexMutation_ModifiedFlagAndPointChanged():
    g = _graph(_box())
    wid = BRepGraph_Tool.Face.OuterWire_s(g, BRepGraph_FaceId.Start_s())
    assert wid.IsValid()
    coedges = g.Topo().Wires().Relations(wid).CoEdgeIds
    assert len(coedges) > 0
    ce = g.Topo().CoEdges().Definition(coedges.First())
    vref = BRepGraph_Tool.Edge.StartVertexId_s(g, BRepGraph_EdgeId(ce.ChildEdgeId))
    assert vref.IsValid()
    vidx = g.Refs().Vertices().Entry(vref).ChildVertexId.Index
    vid = BRepGraph_VertexId(vidx)
    old = BRepGraph_Tool.Vertex.Pnt_s(g, vid)
    guard = g.Editor().Vertices().Mut(vid)
    g.Editor().Vertices().SetPoint(guard, gp_Pnt(old.X(), old.Y(), old.Z() + 5.0))
    del guard  # C++ scope exit
    assert g.Topo().Vertices().Definition(vid).OwnGen > 0
    new = BRepGraph_Tool.Vertex.Pnt_s(g, vid)
    assert old.Distance(new) > Precision.Confusion_s()


def test_BRepGraph_ReconstructTest_AfterToleranceMutation_NewTShape():
    g = _graph(_box())
    eid = BRepGraph_EdgeId(0)
    before = g.Shapes().Shape(BRepGraph_NodeId(eid))
    tol = g.Topo().Edges().Definition(BRepGraph_EdgeId.Start_s()).Tolerance
    guard = g.Editor().Edges().Mut(BRepGraph_EdgeId.Start_s())
    g.Editor().Edges().SetTolerance(guard, tol + 1.0)
    del guard  # C++ scope exit
    after = g.Shapes().Shape(BRepGraph_NodeId(eid))
    assert not after.IsNull()
    assert not after.IsSame(before)


def test_BRepGraph_ReconstructTest_CompoundRoot_TwoSolids_Preserved():
    box1 = _box()
    box2 = BRepPrimAPI_MakeBox(5.0, 10.0, 15.0).Shape()
    b = BRep_Builder()
    comp = TopoDS_Compound()
    b.MakeCompound(comp)
    b.Add(comp, box1)
    b.Add(comp, box2)
    g = _graph(comp)
    assert g.Topo().Solids().Nb() == 2
    v1, v2 = _volume(box1), _volume(box2)
    r1 = _volume(g.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Solid, 0)))
    r2 = _volume(g.Shapes().Reconstruct(BRepGraph_NodeId(Kind.Solid, 1)))
    direct = abs(r1 - v1) < v1 * 0.01 and abs(r2 - v2) < v2 * 0.01
    swapped = abs(r1 - v2) < v2 * 0.01 and abs(r2 - v1) < v1 * 0.01
    assert direct or swapped
