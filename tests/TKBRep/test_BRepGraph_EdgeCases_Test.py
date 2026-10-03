# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_EdgeCases_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import BRepGraph, BRepGraph_NodeId
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Shape


def _box():
    return BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()


def _box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(_box())
    assert not g.IsEmpty()
    return g


def _counts(g):
    t = g.Topo()
    return (
        t.Solids().Nb(),
        t.Shells().Nb(),
        t.Faces().Nb(),
        t.Wires().Nb(),
        t.Edges().Nb(),
        t.Vertices().Nb(),
        t.Gen().NbNodes(),
    )


def _options(parallel):
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = True
    opts.Flatten = False
    opts.Parallel = parallel
    return opts


def test_BRepGraph_EdgeCasesTest_Build_NullShape_IsEmpty():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(TopoDS_Shape())
    assert g.IsEmpty()


def test_BRepGraph_EdgeCasesTest_Build_EmptyCompound_IsEmptyZeroCounts():
    g = BRepGraph()
    comp = TopoDS_Compound()
    BRep_Builder().MakeCompound(comp)
    g.Clear()
    g.Shapes().Add(comp)
    t = g.Topo()
    assert t.Solids().Nb() == 0
    assert t.Shells().Nb() == 0
    assert t.Faces().Nb() == 0
    assert t.Wires().Nb() == 0
    assert t.Edges().Nb() == 0
    assert t.Vertices().Nb() == 0


def test_BRepGraph_EdgeCasesTest_Shape_InvalidNodeId_ReturnsNull():
    g = _box_graph()
    assert g.Shapes().Shape(BRepGraph_NodeId()).IsNull()


def test_BRepGraph_EdgeCasesTest_ReconstructShape_InvalidNodeId_ReturnsNull():
    g = _box_graph()
    assert g.Shapes().Reconstruct(BRepGraph_NodeId()).IsNull()


def test_BRepGraph_EdgeCasesTest_TopoEntity_InvalidNodeId_ReturnsNull():
    g = _box_graph()
    assert g.Topo().Gen().TopoEntity(BRepGraph_NodeId()) is None


def test_BRepGraph_EdgeCasesTest_NbNodes_BeforeBuild_ReturnsZero():
    assert BRepGraph().Topo().Gen().NbNodes() == 0


def test_BRepGraph_EdgeCasesTest_Build_TwiceOnSameGraph_GenerationIncrements():
    g = BRepGraph()
    box = _box()
    g.Clear()
    g.Shapes().Add(box)
    assert not g.IsEmpty()
    first = g.UIDs().Generation()
    g.Clear()
    g.Shapes().Add(box)
    assert not g.IsEmpty()
    assert g.UIDs().Generation() > first


def test_BRepGraph_EdgeCasesTest_Build_TwiceOnSameGraph_OldUIDsInvalidated():
    g = BRepGraph()
    box = _box()
    g.Clear()
    g.Shapes().Add(box)
    assert not g.IsEmpty()
    first = g.UIDs().Generation()
    assert g.Topo().Gen().NbNodes() > 0
    g.Clear()
    g.Shapes().Add(box)
    assert not g.IsEmpty()
    assert g.UIDs().Generation() != first
    uid = g.UIDs().Of(BRepGraph_NodeId(BRepGraph_NodeId.Kind.Solid, 0))
    assert uid.IsValid()


def test_BRepGraph_EdgeCasesTest_Build_TwiceOnSameGraph_CountsResetCorrectly():
    g = BRepGraph()
    box = _box()
    g.Clear()
    g.Shapes().Add(box)
    assert not g.IsEmpty()
    first = _counts(g)[:6]
    g.Clear()
    g.Shapes().Add(box)
    assert not g.IsEmpty()
    assert _counts(g)[:6] == first


def test_BRepGraph_EdgeCasesTest_UID_AlwaysEnabled_AfterBuild():
    g = _box_graph()
    assert g.UIDs().Of(BRepGraph_NodeId(BRepGraph_NodeId.Kind.Solid, 0)).IsValid()


def test_BRepGraph_EdgeCasesTest_ParallelBuild_Sphere_SameAsSequential():
    sphere = BRepPrimAPI_MakeSphere(50.0).Shape()
    seq = BRepGraph()
    seq.Clear()
    seq.Shapes().Add(sphere, _options(False))
    assert not seq.IsEmpty()
    par = BRepGraph()
    par.Clear()
    par.Shapes().Add(sphere, _options(True))
    assert not par.IsEmpty()
    assert _counts(par) == _counts(seq)


def test_BRepGraph_EdgeCasesTest_ParallelBuild_Compound_SameAsSequential():
    b = BRep_Builder()
    comp = TopoDS_Compound()
    b.MakeCompound(comp)
    b.Add(comp, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    b.Add(comp, BRepPrimAPI_MakeBox(20.0, 30.0, 40.0).Shape())
    b.Add(comp, BRepPrimAPI_MakeBox(5.0, 15.0, 25.0).Shape())
    seq = BRepGraph()
    seq.Clear()
    seq.Shapes().Add(comp, _options(False))
    assert not seq.IsEmpty()
    par = BRepGraph()
    par.Clear()
    par.Shapes().Add(comp, _options(True))
    assert not par.IsEmpty()
    assert _counts(par) == _counts(seq)
