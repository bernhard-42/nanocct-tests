# Translated from OCCT src/ModelingAlgorithms/TKOffset/GTests/BRepOffsetAPI_MakePipeShell_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from nanocct.GC import GC_MakeArcOfCircle
from nanocct.Geom import Geom_Plane
from nanocct.GProp import GProp_GProps
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Circ, gp_Dir, gp_Pln, gp_Pnt, gp_Vec
from nanocct.Law import Law_Linear
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FACE, TopAbs_WIRE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shell, TopoDS_Solid


def _wire_length(wire):
    props = GProp_GProps()
    BRepGProp.LinearProperties_s(wire, props)
    return props.Mass()


def _build_bent_tube(wall, dia1, dia2, major_radius, length):
    """Returns (wall_solid, gas_solid) or None, mirroring the OCC332 helper."""
    bend_angle = length / major_radius
    if bend_angle >= math.pi:
        return None
    radius_l = dia1 / 2.0
    radius_r = dia2 / 2.0

    origin = gp_Ax2(gp_Pnt(5000.0, -300.0, 1000.0), gp_Dir(0.0, -1.0, -1.0))
    circ1_plane = gp_Pln(origin.Location(), origin.Direction())
    face_circle = gp_Circ(origin, radius_l)
    out_face_circle = gp_Circ(origin, radius_l + wall)

    circ_center = origin.Location().Translated(gp_Vec(origin.XDirection()) * major_radius)
    circ_axis = gp_Ax1(circ_center, origin.YDirection())
    circ2_plane = circ1_plane.Rotated(circ_axis, bend_angle)

    spine_axis = gp_Ax2(circ_center, origin.YDirection(), origin.XDirection().Reversed())
    spine_circle = gp_Circ(spine_axis, major_radius)

    wire1 = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(face_circle).Edge()).Wire()
    out_wire = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(out_face_circle).Edge()).Wire()

    spine_curve = GC_MakeArcOfCircle(spine_circle, 0.0, bend_angle, True).Value()

    law1 = Law_Linear()
    law2 = Law_Linear()
    law1.Set(spine_curve.FirstParameter(), 1.0, spine_curve.LastParameter(), radius_r / radius_l)
    law2.Set(spine_curve.FirstParameter(), 1.0, spine_curve.LastParameter(), (radius_r + wall) / (radius_l + wall))

    mk_edge = BRepBuilderAPI_MakeEdge(spine_curve)
    if not mk_edge.IsDone():
        return None
    spine_wire = BRepBuilderAPI_MakeWire(mk_edge.Edge()).Wire()

    pipe1 = BRepOffsetAPI_MakePipeShell(spine_wire)
    pipe1.SetTolerance(1.0e-8, 1.0e-8, 1.0e-6)
    pipe1.SetLaw(wire1, law1, False, False)
    pipe1.Build()
    if not pipe1.IsDone():
        return None

    pipe2 = BRepOffsetAPI_MakePipeShell(spine_wire)
    pipe2.SetTolerance(1.0e-8, 1.0e-8, 1.0e-6)
    pipe2.SetLaw(out_wire, law2, False, False)
    pipe2.Build()
    if not pipe2.IsDone():
        return None

    mk_face = BRepBuilderAPI_MakeFace()
    mk_face.Init(Geom_Plane(circ1_plane), False, Precision.Confusion_s())
    mk_face.Add(TopoDS.Wire(pipe2.FirstShape()))
    mk_face.Add(TopoDS.Wire(pipe1.FirstShape().Reversed()))
    if not mk_face.IsDone():
        return None
    face1 = mk_face.Face()

    mk_face.Init(Geom_Plane(circ2_plane), False, Precision.Confusion_s())
    mk_face.Add(TopoDS.Wire(pipe2.LastShape()))
    mk_face.Add(TopoDS.Wire(pipe1.LastShape().Reversed()))
    if not mk_face.IsDone():
        return None
    face2 = mk_face.Face()

    tube_shell = TopoDS_Shell()
    builder = BRep_Builder()
    builder.MakeShell(tube_shell)

    face_exp = TopExp_Explorer(pipe1.Shape(), TopAbs_FACE)
    if face_exp.More():
        builder.Add(tube_shell, face_exp.Current().Reversed())

    pipe1.MakeSolid()
    gas_solid = pipe1.Shape()

    face_exp.Init(pipe2.Shape(), TopAbs_FACE)
    if face_exp.More():
        builder.Add(tube_shell, face_exp.Current())

    builder.Add(tube_shell, face1.Reversed())
    builder.Add(tube_shell, face2)
    tube_shell.Closed(BRep_Tool.IsClosed_s(tube_shell))

    wall_solid = TopoDS_Solid()
    builder.MakeSolid(wall_solid)
    builder.Add(wall_solid, tube_shell)
    return wall_solid, gas_solid


def test_BRepOffsetAPI_MakePipeShellTest_Bug332_BentTubeWithScalingLaw():
    wall, dia1, dia2 = 10.0, 30.0, 50.0
    built = _build_bent_tube(wall, dia1, dia2, 100.0, 200.0)
    assert built is not None
    wall_solid, gas_solid = built

    assert BRepCheck_Analyzer(wall_solid).IsValid()
    assert BRepCheck_Analyzer(gas_solid).IsValid()

    lengths = []
    for wire in TopExp_Explorer(wall_solid, TopAbs_WIRE):
        length = _wire_length(TopoDS.Wire(wire))
        if length > Precision.Confusion_s():
            lengths.append(length)

    def count_matching(expected):
        return sum(1 for length in lengths if abs(length - expected) / expected <= 0.001)

    assert count_matching(math.pi * dia1) >= 1
    assert count_matching(math.pi * (dia1 + 2.0 * wall)) >= 2
    assert count_matching(math.pi * (dia2 + 2.0 * wall)) >= 1
