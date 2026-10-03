# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BOPAlgo_PaveFiller_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeWire
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_FORWARD, TopAbs_REVERSED, TopAbs_VERTEX, TopAbs_WIRE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Edge, TopoDS_Face, TopoDS_Shell, TopoDS_Solid, TopoDS_Wire


def _explore(shape, kind):
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        yield exp.Current()
        exp.Next()


def _circular_wire(radius, z):
    circle = gp_Circ(gp_Ax2(gp_Pnt(0, 0, z), gp_Dir(0, 0, 1)), radius)
    edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    return BRepBuilderAPI_MakeWire(edge).Wire()


def _vertex(pnt):
    return BRepBuilderAPI_MakeVertex(pnt).Vertex()


def _has_degenerated_edges_without_pcurves(shape):
    for f in _explore(shape, TopAbs_FACE):
        face = TopoDS.Face(f)
        for e in _explore(face, TopAbs_EDGE):
            edge = TopoDS.Edge(e)
            if BRep_Tool.Degenerated_s(edge):
                pcurve, _first, _last = BRep_Tool.CurveOnSurface_s(edge, face)
                if pcurve is None:
                    return True
    return False


def _volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def _polygon_wire(points):
    mk = BRepBuilderAPI_MakeWire()
    for a, b in zip(points, points[1:] + points[:1]):
        mk.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*a), gp_Pnt(*b)).Edge())
    return mk.Wire()


def test_BOPAlgo_PaveFillerTest_FuseConeLoftWithBox_DegeneratedEdge():
    base_wire = _circular_wire(10.0, 0.0)
    apex = _vertex(gp_Pnt(0, 0, 20.0))
    loft_maker = BRepOffsetAPI_ThruSections(True, True)
    loft_maker.AddWire(base_wire)
    loft_maker.AddVertex(apex)
    loft_maker.Build()
    assert loft_maker.IsDone()
    loft = loft_maker.Shape()
    assert not loft.IsNull()
    box = BRepPrimAPI_MakeBox(gp_Pnt(-5, -5, 5), 10.0, 10.0, 10.0).Shape()
    fuser = BRepAlgoAPI_Fuse(loft, box)
    assert fuser.IsDone()
    assert not fuser.Shape().IsNull()
    loft_volume = _volume(loft)
    box_volume = _volume(box)
    result_volume = _volume(fuser.Shape())
    assert result_volume > 0.0
    assert result_volume < loft_volume + box_volume


def test_BOPAlgo_PaveFillerTest_FuseConeWithBox_DegeneratedEdge():
    cone = BRepPrimAPI_MakeCone(10.0, 0.0, 20.0).Shape()
    assert not cone.IsNull()
    box = BRepPrimAPI_MakeBox(gp_Pnt(-5, -5, 15), 10.0, 10.0, 10.0).Shape()
    fuser = BRepAlgoAPI_Fuse(cone, box)
    assert fuser.IsDone()
    assert not fuser.Shape().IsNull()
    assert _volume(fuser.Shape()) > 0.0


def test_BOPAlgo_PaveFillerTest_FuseTwoLofts_RobustnessCheck():
    bottom1 = _polygon_wire([(10, -10, 0), (100, -10, 0), (100, -100, 0), (10, -100, 0)])
    top1 = _polygon_wire([(0, 0, 10), (100, 0, 10), (100, -100, 10), (0, -100, 10)])
    loft1 = BRepOffsetAPI_ThruSections(True, True)
    loft1.AddWire(bottom1)
    loft1.AddWire(top1)
    loft1.Build()
    assert loft1.IsDone()
    bottom2 = _polygon_wire([(0, 0, 10), (100, 0, 10), (100, -100, 10), (0, -100, 10)])
    top2 = _polygon_wire([(0, 0, 250), (100, 0, 250), (100, -100, 250), (0, -100, 250)])
    loft2 = BRepOffsetAPI_ThruSections(True, True)
    loft2.AddWire(bottom2)
    loft2.AddWire(top2)
    loft2.Build()
    assert loft2.IsDone()
    fuser = BRepAlgoAPI_Fuse(loft1.Shape(), loft2.Shape())
    assert fuser.IsDone()
    assert not fuser.Shape().IsNull()
    assert _volume(fuser.Shape()) > 0.0


def test_BOPAlgo_PaveFillerTest_FuseConeWithRemovedPCurve_NullPCurveHandling():
    cone = BRepPrimAPI_MakeCone(10.0, 0.0, 20.0).Shape()
    assert not cone.IsNull()
    conical_face = TopoDS_Face()
    degenerated_edge = TopoDS_Edge()
    for f in _explore(cone, TopAbs_FACE):
        face = TopoDS.Face(f)
        for e in _explore(face, TopAbs_EDGE):
            edge = TopoDS.Edge(e)
            if BRep_Tool.Degenerated_s(edge):
                conical_face = face
                degenerated_edge = edge
                break
        if not degenerated_edge.IsNull():
            break

    if not degenerated_edge.IsNull():
        surf = BRep_Tool.Surface_s(conical_face)
        first, last = 0.0, 2.0 * math.pi
        vertex = TopoDS.Vertex(TopExp_Explorer(degenerated_edge, TopAbs_VERTEX).Current())
        builder = BRep_Builder()
        new_deg_edge = TopoDS_Edge()
        builder.MakeEdge(new_deg_edge)
        builder.Add(new_deg_edge, vertex.Oriented(TopAbs_FORWARD))
        builder.Add(new_deg_edge, vertex.Oriented(TopAbs_REVERSED))
        builder.Degenerated(new_deg_edge, True)
        builder.Range(new_deg_edge, first, last)
        new_wire = TopoDS_Wire()
        builder.MakeWire(new_wire)
        wire_exp = TopExp_Explorer(conical_face, TopAbs_WIRE)
        if wire_exp.More():
            wire = TopoDS.Wire(wire_exp.Current())
            for e in _explore(wire, TopAbs_EDGE):
                edge = TopoDS.Edge(e)
                if BRep_Tool.Degenerated_s(edge):
                    builder.Add(new_wire, new_deg_edge.Oriented(edge.Orientation()))
                else:
                    builder.Add(new_wire, edge)
        new_face = TopoDS_Face()
        builder.MakeFace(new_face, surf, Precision.Confusion_s())
        builder.Add(new_face, new_wire)
        new_shell = TopoDS_Shell()
        builder.MakeShell(new_shell)
        for f in _explore(cone, TopAbs_FACE):
            face = TopoDS.Face(f)
            if face.IsSame(conical_face):
                builder.Add(new_shell, new_face)
            else:
                builder.Add(new_shell, face)
        new_solid = TopoDS_Solid()
        builder.MakeSolid(new_solid)
        builder.Add(new_solid, new_shell)
        assert _has_degenerated_edges_without_pcurves(new_solid)
        box = BRepPrimAPI_MakeBox(gp_Pnt(-5, -5, 15), 10.0, 10.0, 10.0).Shape()
        fuser = BRepAlgoAPI_Fuse(new_solid, box)
        fuser.IsDone()
    else:
        box_maker = BRepPrimAPI_MakeBox(gp_Pnt(-5, -5, 15), 10.0, 10.0, 10.0)
        fuser = BRepAlgoAPI_Fuse(cone, box_maker.Shape())
        assert fuser.IsDone()
