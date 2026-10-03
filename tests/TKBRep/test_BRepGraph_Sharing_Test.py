# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Sharing_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CompoundId,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceIterator,
    BRepGraph_NodeId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_VertexIterator,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


@pytest.fixture
def graph():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(box)
    return g


def _box(dx=10.0, dy=20.0, dz=30.0):
    return BRepPrimAPI_MakeBox(dx, dy, dz).Shape()


def _compound(*shapes):
    b = BRep_Builder()
    c = TopoDS_Compound()
    b.MakeCompound(c)
    for s in shapes:
        b.Add(c, s)
    return c


def _moved(shape, x, y, z):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(x, y, z))
    return shape.Moved(TopLoc_Location(t))


def test_BRepGraph_SharingTest_EdgeDef_EachSharedByTwoFaces(graph):
    assert not graph.IsEmpty()
    assert graph.Topo().Edges().Nb() == 12
    for eid in _ids(BRepGraph_EdgeIterator(graph)):
        assert graph.Topo().Edges().NbFaces(eid) == 2


def test_BRepGraph_SharingTest_FaceDef_EachHasValidSurface(graph):
    assert not graph.IsEmpty()
    assert graph.Topo().Faces().Nb() == 6
    for d in BRepGraph_FaceIterator(graph):
        assert d.SurfaceRepId.IsValid()


def test_BRepGraph_SharingTest_SolidDef_HasOneShellRef(graph):
    assert not graph.IsEmpty()
    assert graph.Topo().Solids().Nb() == 1
    assert len(graph.Refs().Shells().IdsOf(BRepGraph_SolidId.Start_s())) == 1


def test_BRepGraph_SharingTest_ShellDef_HasSixFaceRefs(graph):
    assert not graph.IsEmpty()
    assert graph.Topo().Shells().Nb() == 1
    assert len(graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())) == 6


def test_BRepGraph_SharingTest_SolidDef_ContainsOneShellRef(graph):
    assert graph.Topo().Solids().Nb() == 1
    assert len(graph.Refs().Shells().IdsOf(BRepGraph_SolidId.Start_s())) == 1


def test_BRepGraph_SharingTest_ShellDef_ContainsSixFaceRefs(graph):
    assert graph.Topo().Shells().Nb() == 1
    assert len(graph.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s())) == 6


def test_BRepGraph_SharingTest_FaceDef_OuterWireIdx_Valid(graph):
    for fid in _ids(BRepGraph_FaceIterator(graph)):
        assert BRepGraph_Tool.Face.OuterWire_s(graph, fid).IsValid()


def test_BRepGraph_SharingTest_WireDef_CoEdgesCount_FourPerBoxFace(graph):
    for wid in _ids(BRepGraph_WireIterator(graph)):
        n = len(graph.Topo().Wires().Relations(wid).CoEdgeIds)
        assert n > 0
        assert n == 4


def test_BRepGraph_SharingTest_EdgeDef_VertexDefs_BothValid(graph):
    for eid in _ids(BRepGraph_EdgeIterator(graph)):
        assert BRepGraph_Tool.Edge.StartVertexId_s(graph, eid).IsValid()
        assert BRepGraph_Tool.Edge.EndVertexId_s(graph, eid).IsValid()


def test_BRepGraph_SharingTest_SharedEdge_IncidenceRefs_DifferentOrientation(graph):
    count = 0
    for eid in _ids(BRepGraph_EdgeIterator(graph)):
        ces = graph.Topo().Edges().CoEdges(eid)
        if len(ces) < 2:
            continue
        face0 = graph.Topo().CoEdges().Definition(ces[0]).FaceId
        for i in range(1, len(ces)):
            if graph.Topo().CoEdges().Definition(ces[i]).FaceId != face0:
                count += 1
                break
    assert count > 0


def test_BRepGraph_SharingTest_NonClosedEdge_StartEnd_Different(graph):
    for eid in _ids(BRepGraph_EdgeIterator(graph)):
        if BRepGraph_Tool.Edge.Degenerated_s(graph, eid):
            continue
        s = BRepGraph_Tool.Edge.StartVertexId_s(graph, eid)
        e = BRepGraph_Tool.Edge.EndVertexId_s(graph, eid)
        assert s != e


def test_BRepGraph_SharingTest_VertexDef_Points_MatchExpectedBoxCorners(graph):
    assert graph.Topo().Vertices().Nb() == 8
    tol = Precision.Confusion_s()
    for d in BRepGraph_VertexIterator(graph):
        p = d.Point
        assert -tol <= p.X() <= 10.0 + tol
        assert -tol <= p.Y() <= 20.0 + tol
        assert -tol <= p.Z() <= 30.0 + tol


def test_BRepGraph_SharingTest_CompoundTwoIdenticalBoxes():
    box = _box()
    comp = _compound(box, box)
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(comp)
    assert not g.IsEmpty()
    assert g.Topo().Solids().Nb() == 1
    assert g.Topo().Faces().Nb() == 6
    assert g.Topo().Edges().Nb() == 12
    assert g.Topo().Vertices().Nb() == 8
    refs = g.Refs().Children().IdsOf(BRepGraph_CompoundId.Start_s())
    assert len(refs) == 2
    assert refs[0] != refs[1]
    assert (
        g.Refs().Children().Entry(refs[0]).ChildNodeId.Index
        == g.Refs().Children().Entry(refs[1]).ChildNodeId.Index
    )


def test_BRepGraph_SharingTest_SameReferenceRepresentationAcrossDifferentParents_UsesDistinctChildRefs():
    box = _box()
    parent_a = _compound(box)
    parent_b = _compound(box)
    root = _compound(parent_a, parent_b)
    g = BRepGraph()
    g.Shapes().Add(root)
    assert not g.IsEmpty()
    na = g.Shapes().FindNode(parent_a)
    nb = g.Shapes().FindNode(parent_b)
    assert na.NodeKind == BRepGraph_NodeId.Kind.Compound
    assert nb.NodeKind == BRepGraph_NodeId.Kind.Compound
    ra = g.Refs().Children().IdsOf(BRepGraph_CompoundId(na))
    rb = g.Refs().Children().IdsOf(BRepGraph_CompoundId(nb))
    assert len(ra) == 1
    assert len(rb) == 1
    assert ra[0] != rb[0]
    assert g.Refs().Children().Entry(ra[0]).ChildNodeId == g.Refs().Children().Entry(rb[0]).ChildNodeId
    res = BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s())
    assert res.NbIssues(BRepGraph_Validate.Severity.Error) == 0


def test_BRepGraph_SharingTest_CompoundTwoDistinctBoxes():
    comp = _compound(_box(), _box(5.0, 15.0, 25.0))
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(comp)
    assert not g.IsEmpty()
    assert g.Topo().Solids().Nb() == 2
    assert g.Topo().Faces().Nb() == 12
    assert g.Topo().Edges().Nb() == 24
    assert g.Topo().Vertices().Nb() == 16


def _check_moved_compound(dx, dy, dz):
    box = _box()
    comp = _compound(box, _moved(box, dx, dy, dz))
    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(comp)
    assert res.IsOk()
    assert not g.IsEmpty()
    assert g.Topo().Solids().Nb() == 1
    assert g.Topo().Faces().Nb() == 6
    assert g.Topo().Edges().Nb() == 12
    assert g.Topo().Vertices().Nb() == 8
    refs = g.Topo().Compounds().Relations(BRepGraph_CompoundId(res.TopologyRoot)).ChildRefIds
    assert len(refs) == 2
    assert not g.Refs().Gen().LocalLocation(refs[1]).IsIdentity()


def test_BRepGraph_SharingTest_CompoundWithLocation_MoreUsagesThanDefs():
    _check_moved_compound(100.0, 0.0, 0.0)


def test_BRepGraph_SharingTest_TranslatedCopy_SameTShape_SharedDefs():
    _check_moved_compound(50.0, 50.0, 50.0)
