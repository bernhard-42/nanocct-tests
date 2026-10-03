# Translated from OCCT src/ModelingAlgorithms/TKOffset/GTests/BRepOffset_MakeOffset_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepAlgoAPI import BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeWire
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepOffset import BRepOffset_Skin
from nanocct.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid, BRepOffsetAPI_ThruSections
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.GeomAbs import GeomAbs_Intersection
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Elips, gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_List
from nanocct.TopoDS import TopoDS_Shape

NORMAL = gp_Dir(0, 0, 1)


def _circular_wire(center, normal, radius):
    edge_maker = BRepBuilderAPI_MakeEdge(gp_Circ(gp_Ax2(center, normal), radius))
    assert edge_maker.IsDone()
    wire_maker = BRepBuilderAPI_MakeWire(edge_maker.Edge())
    assert wire_maker.IsDone()
    return wire_maker.Wire()


def _rectangular_wire(center, normal, width, height):
    axis = gp_Ax2(center, normal)
    xdir = gp_Vec(axis.XDirection())
    ydir = gp_Vec(axis.YDirection())
    hw = width / 2.0
    hh = height / 2.0
    p1 = center.Translated(xdir * (-hw) + ydir * (-hh))
    p2 = center.Translated(xdir * hw + ydir * (-hh))
    p3 = center.Translated(xdir * hw + ydir * hh)
    p4 = center.Translated(xdir * (-hw) + ydir * hh)
    wire_maker = BRepBuilderAPI_MakeWire()
    wire_maker.Add(BRepBuilderAPI_MakeEdge(p1, p2).Edge())
    wire_maker.Add(BRepBuilderAPI_MakeEdge(p2, p3).Edge())
    wire_maker.Add(BRepBuilderAPI_MakeEdge(p3, p4).Edge())
    wire_maker.Add(BRepBuilderAPI_MakeEdge(p4, p1).Edge())
    assert wire_maker.IsDone()
    return wire_maker.Wire()


def _elliptical_wire(center, normal, major, minor):
    edge_maker = BRepBuilderAPI_MakeEdge(gp_Elips(gp_Ax2(center, normal), major, minor))
    assert edge_maker.IsDone()
    wire_maker = BRepBuilderAPI_MakeWire(edge_maker.Edge())
    assert wire_maker.IsDone()
    return wire_maker.Wire()


def _polygonal_wire(center, normal, radius, nb_sides):
    axis = gp_Ax2(center, normal)
    xdir = gp_Vec(axis.XDirection())
    ydir = gp_Vec(axis.YDirection())
    polygon = BRepBuilderAPI_MakePolygon()
    for i in range(nb_sides + 1):
        angle = 2.0 * math.pi * i / nb_sides
        polygon.Add(center.Translated(xdir * radius * math.cos(angle) + ydir * radius * math.sin(angle)))
    polygon.Close()
    assert polygon.IsDone()
    return polygon.Wire()


def _loft(wires, ruled=False):
    loft = BRepOffsetAPI_ThruSections(True, ruled)
    for wire in wires:
        assert not wire.IsNull()
        loft.AddWire(wire)
    loft.Build()
    assert loft.IsDone()
    shape = loft.Shape()
    assert not shape.IsNull()
    return shape


def _thick(shape, offset=2.0, intersection=False):
    faces = NCollection_List[TopoDS_Shape]()
    maker = BRepOffsetAPI_MakeThickSolid()
    maker.MakeThickSolidByJoin(shape, faces, offset, 1.0e-3, BRepOffset_Skin, intersection, False, GeomAbs_Intersection)
    maker.Build()
    return maker


def _circle_to_rect(rect_z=100.0, ruled=False):
    circle = _circular_wire(gp_Pnt(0, 0, 0), NORMAL, 50.0)
    rect = _rectangular_wire(gp_Pnt(0, 0, rect_z), NORMAL, 80.0, 60.0)
    return _loft([circle, rect], ruled)


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangleLoft():
    loft = _circle_to_rect()
    assert BRepCheck_Analyzer(loft).IsValid()
    maker = _thick(loft)
    assert maker.IsDone()
    shape = maker.Shape()
    if not shape.IsNull():
        assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangleLoft_IntersectionMode():
    maker = _thick(_circle_to_rect(), intersection=True)
    assert maker.IsDone()
    shape = maker.Shape()
    if not shape.IsNull():
        assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepOffset_MakeOffsetTest_ThickSolid_SimpleBox_Baseline():
    bottom = _rectangular_wire(gp_Pnt(0, 0, 0), NORMAL, 100.0, 100.0)
    top = _rectangular_wire(gp_Pnt(0, 0, 50), NORMAL, 100.0, 100.0)
    maker = _thick(_loft([bottom, top], ruled=True))
    assert maker.IsDone()
    assert not maker.Shape().IsNull()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToEllipseLoft():
    circle = _circular_wire(gp_Pnt(0, 0, 0), NORMAL, 50.0)
    ellipse = _elliptical_wire(gp_Pnt(0, 0, 100), NORMAL, 60.0, 40.0)
    assert _thick(_loft([circle, ellipse])).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToHexagonLoft():
    circle = _circular_wire(gp_Pnt(0, 0, 0), NORMAL, 50.0)
    hexagon = _polygonal_wire(gp_Pnt(0, 0, 100), NORMAL, 50.0, 6)
    assert _thick(_loft([circle, hexagon])).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToSquareLoft():
    circle = _circular_wire(gp_Pnt(0, 0, 0), NORMAL, 50.0)
    square = _rectangular_wire(gp_Pnt(0, 0, 100), NORMAL, 80.0, 80.0)
    assert _thick(_loft([circle, square])).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_EllipseToRectangleLoft():
    ellipse = _elliptical_wire(gp_Pnt(0, 0, 0), NORMAL, 60.0, 30.0)
    rect = _rectangular_wire(gp_Pnt(0, 0, 100), NORMAL, 100.0, 50.0)
    assert _thick(_loft([ellipse, rect])).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_ThreeSectionLoft():
    circle = _circular_wire(gp_Pnt(0, 0, 0), NORMAL, 40.0)
    ellipse = _elliptical_wire(gp_Pnt(0, 0, 50), NORMAL, 50.0, 35.0)
    rect = _rectangular_wire(gp_Pnt(0, 0, 100), NORMAL, 80.0, 60.0)
    assert _thick(_loft([circle, ellipse, rect])).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangleLoft_Ruled():
    assert _thick(_circle_to_rect(ruled=True)).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangleLoft_SmallOffset():
    assert _thick(_circle_to_rect(), offset=0.5).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangleLoft_LargeOffset():
    assert _thick(_circle_to_rect(), offset=10.0).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangleLoft_NegativeOffset():
    assert _thick(_circle_to_rect(), offset=-2.0).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_Cylinder_Baseline():
    cylinder = BRepPrimAPI_MakeCylinder(50.0, 100.0).Shape()
    assert not cylinder.IsNull()
    maker = _thick(cylinder)
    assert maker.IsDone()
    assert BRepCheck_Analyzer(maker.Shape()).IsValid()


def test_BRepOffset_MakeOffsetTest_ThickSolid_Sphere_Baseline():
    sphere = BRepPrimAPI_MakeSphere(50.0).Shape()
    assert not sphere.IsNull()
    maker = _thick(sphere)
    assert maker.IsDone()
    assert BRepCheck_Analyzer(maker.Shape()).IsValid()


def test_BRepOffset_MakeOffsetTest_ThickSolid_FusedBoxCylinder():
    box = BRepPrimAPI_MakeBox(100.0, 100.0, 50.0).Shape()
    assert not box.IsNull()
    cyl = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(50, 50, 50), gp_Dir(0, 0, 1)), 30.0, 50.0).Shape()
    assert not cyl.IsNull()
    fuser = BRepAlgoAPI_Fuse(box, cyl)
    assert fuser.IsDone()
    assert _thick(fuser.Shape()).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangle_ThinLoft():
    # Only "must not crash"; IsDone() is not required by OCCT.
    _thick(_circle_to_rect(rect_z=10.0), offset=1.0).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToRectangle_TallLoft():
    assert _thick(_circle_to_rect(rect_z=500.0)).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToTriangleLoft():
    circle = _circular_wire(gp_Pnt(0, 0, 0), NORMAL, 50.0)
    triangle = _polygonal_wire(gp_Pnt(0, 0, 100), NORMAL, 60.0, 3)
    assert _thick(_loft([circle, triangle])).IsDone()


def test_BRepOffset_MakeOffsetTest_ThickSolid_CircleToOctagonLoft():
    circle = _circular_wire(gp_Pnt(0, 0, 0), NORMAL, 50.0)
    octagon = _polygonal_wire(gp_Pnt(0, 0, 100), NORMAL, 55.0, 8)
    assert _thick(_loft([circle, octagon])).IsDone()
