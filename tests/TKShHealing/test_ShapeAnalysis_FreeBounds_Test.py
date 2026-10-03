# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeAnalysis_FreeBounds_Test.cxx (LGPL-2.1 with the OCCT exception)
from types import SimpleNamespace

from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_HSequence
from nanocct.Precision import Precision
from nanocct.ShapeAnalysis import ShapeAnalysis_FreeBounds
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_EXTERNAL, TopAbs_INTERNAL, TopAbs_WIRE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Shape, TopoDS_Vertex, TopoDS_Wire


def _make_test_data():
    builder = BRep_Builder()
    conf = Precision.Confusion_s()
    v1, v2, v3, vnm = TopoDS_Vertex(), TopoDS_Vertex(), TopoDS_Vertex(), TopoDS_Vertex()
    builder.MakeVertex(v1, gp_Pnt(0.0, 0.0, 0.0), conf)
    builder.MakeVertex(v2, gp_Pnt(1.0, 0.0, 0.0), conf)
    builder.MakeVertex(v3, gp_Pnt(0.0, 1.0, 0.0), conf)
    builder.MakeVertex(vnm, gp_Pnt(2.0, -1.0, 0.0), conf)

    m1 = BRepBuilderAPI_MakeEdge(v1, v2)
    m2 = BRepBuilderAPI_MakeEdge(v2, v3)
    m3 = BRepBuilderAPI_MakeEdge(v3, v1)
    mnm = BRepBuilderAPI_MakeEdge(v1, vnm)
    assert m1.IsDone() and m2.IsDone() and m3.IsDone() and mnm.IsDone()

    d = SimpleNamespace()
    d.Edge1 = m1.Edge()
    d.Edge2 = m2.Edge()
    d.Edge3 = m3.Edge()
    d.InternalEdge = mnm.Edge()
    d.InternalEdge.Orientation(TopAbs_INTERNAL)
    d.ExternalEdge = mnm.Edge()
    d.ExternalEdge.Orientation(TopAbs_EXTERNAL)

    d.Loop, d.InternalWire, d.ExternalWire, d.EmptyWire = TopoDS_Wire(), TopoDS_Wire(), TopoDS_Wire(), TopoDS_Wire()
    builder.MakeWire(d.Loop)
    builder.Add(d.Loop, d.Edge1)
    builder.Add(d.Loop, d.Edge2)
    builder.Add(d.Loop, d.Edge3)
    builder.MakeWire(d.InternalWire)
    builder.Add(d.InternalWire, d.InternalEdge)
    builder.MakeWire(d.ExternalWire)
    builder.Add(d.ExternalWire, d.ExternalEdge)
    builder.MakeWire(d.EmptyWire)
    return d


def _seq(*shapes):
    s = NCollection_HSequence[TopoDS_Shape]()
    for sh in shapes:
        s.Append(sh)
    return s


def _check_result(result, nb_wires, nb_edges, nb_internal, nb_external, has_closed_loop):
    assert result is not None
    assert result.Length() == nb_wires

    n_edges = 0
    n_internal = 0
    n_external = 0
    closed_loop = False
    for wire in result:
        n_wire_edges = 0
        exp = TopExp_Explorer(wire, TopAbs_EDGE)
        while exp.More():
            n_edges += 1
            n_wire_edges += 1
            if exp.Current().Orientation() == TopAbs_INTERNAL:
                n_internal += 1
            elif exp.Current().Orientation() == TopAbs_EXTERNAL:
                n_external += 1
            exp.Next()
        if n_wire_edges == 3 and wire.Closed():
            closed_loop = True
    assert n_edges == nb_edges
    assert n_internal == nb_internal
    assert n_external == nb_external
    assert closed_loop == has_closed_loop


def _square_face(a, b, c, d):
    mw = BRepBuilderAPI_MakeWire()
    mw.Add(BRepBuilderAPI_MakeEdge(a, b).Edge())
    mw.Add(BRepBuilderAPI_MakeEdge(b, c).Edge())
    mw.Add(BRepBuilderAPI_MakeEdge(c, d).Edge())
    mw.Add(BRepBuilderAPI_MakeEdge(d, a).Edge())
    return BRepBuilderAPI_MakeFace(mw.Wire()).Face()


def _wires(shapes):
    return ShapeAnalysis_FreeBounds.ConnectWiresToWires_s(_seq(*shapes), Precision.Confusion_s(), True)


def _edges(shapes):
    return ShapeAnalysis_FreeBounds.ConnectEdgesToWires_s(_seq(*shapes), Precision.Confusion_s(), True)


def test_ShapeAnalysis_FreeBoundsTest_ConnectWires_InternalOnlyWireAfterManifoldWire():
    d = _make_test_data()
    _check_result(_wires([d.Loop, d.InternalWire]), 2, 4, 1, 0, True)


def test_ShapeAnalysis_FreeBoundsTest_ConnectWires_InternalOnlyWireBeforeManifoldWire():
    d = _make_test_data()
    _check_result(_wires([d.InternalWire, d.Loop]), 2, 4, 1, 0, True)


def test_ShapeAnalysis_FreeBoundsTest_ConnectWires_OnlyNonManifoldWires():
    d = _make_test_data()
    _check_result(_wires([d.InternalWire, d.ExternalWire]), 2, 2, 1, 1, False)


def test_ShapeAnalysis_FreeBoundsTest_ConnectWires_EmptyWireBeforeValidWires():
    d = _make_test_data()
    _check_result(_wires([d.EmptyWire, d.InternalWire, d.Loop]), 2, 4, 1, 0, True)


def test_ShapeAnalysis_FreeBoundsTest_ConnectWires_OnlyEmptyWire():
    d = _make_test_data()
    _check_result(_wires([d.EmptyWire]), 0, 0, 0, 0, False)


def test_ShapeAnalysis_FreeBoundsTest_ConnectWires_MixedManifoldAndInternalEdges():
    d = _make_test_data()
    builder = BRep_Builder()
    mixed = TopoDS_Wire()
    builder.MakeWire(mixed)
    builder.Add(mixed, d.Edge1)
    builder.Add(mixed, d.Edge2)
    builder.Add(mixed, d.Edge3)
    builder.Add(mixed, d.InternalEdge)
    _check_result(_wires([mixed]), 1, 4, 1, 0, False)


def test_ShapeAnalysis_FreeBoundsTest_ConnectEdges_InternalEdgeAfterManifoldEdges():
    d = _make_test_data()
    _check_result(_edges([d.Edge1, d.Edge2, d.Edge3, d.InternalEdge]), 1, 3, 0, 0, True)


def test_ShapeAnalysis_FreeBoundsTest_ConnectEdges_InternalEdgeBeforeManifoldEdges():
    d = _make_test_data()
    _check_result(_edges([d.InternalEdge, d.Edge1, d.Edge2, d.Edge3]), 1, 3, 0, 0, True)


def test_ShapeAnalysis_FreeBoundsTest_ConnectEdges_ExternalEdgeIsSkipped():
    d = _make_test_data()
    _check_result(_edges([d.Edge1, d.Edge2, d.Edge3, d.ExternalEdge]), 1, 3, 0, 0, True)


def test_ShapeAnalysis_FreeBoundsTest_SingleFaceNoCrash():
    face = _square_face(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1.0, 0.0, 0.0), gp_Pnt(1.0, 1.0, 0.0), gp_Pnt(0.0, 1.0, 0.0))
    free_bounds = ShapeAnalysis_FreeBounds(face, 0.01, True, True)
    free_bounds.GetClosedWires()
    free_bounds.GetOpenWires()


def test_ShapeAnalysis_FreeBoundsTest_TwoDisjointFacesNoCrash():
    face_a = _square_face(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1.0, 0.0, 0.0), gp_Pnt(1.0, 1.0, 0.0), gp_Pnt(0.0, 1.0, 0.0))
    face_b = _square_face(gp_Pnt(5.0, 5.0, 0.0), gp_Pnt(6.0, 5.0, 0.0), gp_Pnt(6.0, 6.0, 0.0), gp_Pnt(5.0, 6.0, 0.0))

    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    builder.Add(compound, face_a)
    builder.Add(compound, face_b)

    free_bounds = ShapeAnalysis_FreeBounds(compound, 0.01, True, True)
    closed = free_bounds.GetClosedWires()
    opened = free_bounds.GetOpenWires()

    def count(shape):
        n = 0
        exp = TopExp_Explorer(shape, TopAbs_WIRE)
        while exp.More():
            n += 1
            exp.Next()
        return n

    assert count(closed) == 2
    assert count(opened) == 0
