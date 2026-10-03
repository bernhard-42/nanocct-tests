# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepCheck_Face_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from nanocct.BRepCheck import BRepCheck_Analyzer, BRepCheck_Face, BRepCheck_NoError
from nanocct.Geom import Geom_Line
from nanocct.Geom2d import Geom2d_Circle, Geom2d_OffsetCurve
from nanocct.gp import gp_Ax2, gp_Ax2d, gp_Circ, gp_Dir, gp_Dir2d, gp_Lin, gp_Pln, gp_Pnt, gp_Pnt2d
from nanocct.Precision import Precision
from nanocct.TopoDS import TopoDS_Face, TopoDS_Wire


def _make_rectangle(x_min, y_min, x_max, y_max):
    p1 = gp_Pnt(x_min, y_min, 0.0)
    p2 = gp_Pnt(x_max, y_min, 0.0)
    p3 = gp_Pnt(x_max, y_max, 0.0)
    p4 = gp_Pnt(x_min, y_max, 0.0)
    builders = [BRepBuilderAPI_MakeEdge(p1, p2), BRepBuilderAPI_MakeEdge(p2, p3),
                BRepBuilderAPI_MakeEdge(p3, p4), BRepBuilderAPI_MakeEdge(p4, p1)]
    wire_builder = BRepBuilderAPI_MakeWire()
    for b in builders:
        if not b.IsDone():
            return TopoDS_Wire()
        wire_builder.Add(b.Edge())
    if wire_builder.IsDone():
        return wire_builder.Wire()
    return TopoDS_Wire()


def _make_planar_face():
    outer = _make_rectangle(0.0, 0.0, 100.0, 100.0)
    if outer.IsNull():
        return TopoDS_Face()
    fb = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), outer, True)
    if fb.IsDone():
        return fb.Face()
    return TopoDS_Face()


def _add_circular_hole(face, center, radius):
    eb = BRepBuilderAPI_MakeEdge(gp_Circ(gp_Ax2(center, gp_Dir(0.0, 0.0, 1.0)), radius))
    if not eb.IsDone():
        return False
    wb = BRepBuilderAPI_MakeWire(eb.Edge())
    if not wb.IsDone():
        return False
    hole = wb.Wire()
    hole.Reverse()
    BRep_Builder().Add(face, hole)
    return True


def _classify_wires(face):
    return BRepCheck_Face(face).ClassifyWires()


def test_BRepCheck_FaceTest_ClassifyWires_DisjointHolesAreValid():
    face = _make_planar_face()
    assert not face.IsNull()
    for row in range(5):
        for col in range(8):
            assert _add_circular_hole(face, gp_Pnt(10.0 + 11.0 * col, 10.0 + 11.0 * row, 0.0), 2.0)
    assert _classify_wires(face) == BRepCheck_NoError
    assert BRepCheck_Analyzer(face).IsValid()


def test_BRepCheck_FaceTest_ClassifyWires_OffsetPCurve():
    face = _make_planar_face()
    assert not face.IsNull()
    center2d = gp_Pnt2d(50.0, 50.0)
    basis = Geom2d_Circle(gp_Ax2d(center2d, gp_Dir2d(1.0, 0.0)), 4.0)
    offset = Geom2d_OffsetCurve(basis, 1.0)
    radius = offset.Value(0.0).Distance(center2d)
    eb = BRepBuilderAPI_MakeEdge(gp_Circ(gp_Ax2(gp_Pnt(50.0, 50.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), radius))
    assert eb.IsDone()
    edge = eb.Edge()
    BRep_Builder().UpdateEdge(edge, offset, face, Precision.Confusion_s())
    wb = BRepBuilderAPI_MakeWire(edge)
    assert wb.IsDone()
    hole = wb.Wire()
    hole.Reverse()
    BRep_Builder().Add(face, hole)
    assert _classify_wires(face) == BRepCheck_NoError


def test_BRepCheck_FaceTest_ClassifyWires_OpenWireFallbackIsOrientationIndependent():
    face = _make_planar_face()
    assert not face.IsNull()
    eb = BRepBuilderAPI_MakeEdge(gp_Pnt(120.0, 10.0, 0.0), gp_Pnt(130.0, 10.0, 0.0))
    assert eb.IsDone()
    wb = BRepBuilderAPI_MakeWire(eb.Edge())
    assert wb.IsDone()
    BRep_Builder().Add(face, wb.Wire())
    forward = _classify_wires(face)
    reversed_face = TopoDS.Face(face.Reversed())
    assert forward == BRepCheck_NoError
    assert _classify_wires(reversed_face) == forward


def test_BRepCheck_FaceTest_ClassifyWires_UnboundedWireFallbackIsOrientationIndependent():
    face = _make_planar_face()
    assert not face.IsNull()
    line = Geom_Line(gp_Lin(gp_Pnt(0.0, 120.0, 0.0), gp_Dir(1.0, 0.0, 0.0)))
    eb = BRepBuilderAPI_MakeEdge(line)
    assert eb.IsDone()
    wb = BRepBuilderAPI_MakeWire(eb.Edge())
    assert wb.IsDone()
    BRep_Builder().Add(face, wb.Wire())
    forward = _classify_wires(face)
    reversed_face = TopoDS.Face(face.Reversed())
    assert forward == BRepCheck_NoError
    assert _classify_wires(reversed_face) == forward
