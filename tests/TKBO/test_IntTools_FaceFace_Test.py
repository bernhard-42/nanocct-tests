# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/IntTools_FaceFace_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from nanocct.Geom import Geom_CylindricalSurface, Geom_Plane
from nanocct.gp import gp_Ax2, gp_Ax3, gp_Circ, gp_Dir, gp_Pln, gp_Pnt
from nanocct.IntTools import IntTools_FaceFace
from nanocct.Precision import Precision
from nanocct.TopoDS import TopoDS_Face


def _half_cylinder_face(center, axis, radius, v_min, v_max, u_min=0.0, u_max=math.pi):
    surf = Geom_CylindricalSurface(gp_Ax3(center, axis), radius)
    return BRepBuilderAPI_MakeFace(surf, u_min, u_max, v_min, v_max, 1e-7).Face()


def _cylinder_face(center, axis, radius, v_min, v_max):
    return _half_cylinder_face(center, axis, radius, v_min, v_max, 0.0, 2.0 * math.pi)


def _circular_plane_face(center, normal, radius):
    plane = Geom_Plane(gp_Pln(center, normal))
    circ = gp_Circ(gp_Ax2(center, normal), radius)
    edge = BRepBuilderAPI_MakeEdge(circ).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return BRepBuilderAPI_MakeFace(plane, wire, True).Face()


def _intersect(f1, f2):
    ff = IntTools_FaceFace()
    ff.SetParameters(True, True, True, 1.0e-7)
    ff.Perform(f1, f2)
    assert ff.IsDone()
    return ff


def test_IntTools_FaceFaceTest_PerpendicularCylinderBoundaryTouch_OrderIndependent():
    face1 = _cylinder_face(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), 2.0, -5.0, 5.0)
    face2 = _cylinder_face(gp_Pnt(0.0, 2.0, 0.0), gp_Dir(1.0, 0.0, 0.0), 0.5, 0.0, 4.0)
    assert not face1.IsNull()
    assert not face2.IsNull()
    ff12 = _intersect(face1, face2)
    ff21 = _intersect(face2, face1)
    assert ff12.Lines().Length() == ff21.Lines().Length()
    assert ff12.Points().Length() == ff21.Points().Length()


def test_IntTools_FaceFaceTest_HalfCylinderOutsideCircularPlane_NoIntersection():
    plane = _circular_plane_face(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), 10.0)
    half = _half_cylinder_face(gp_Pnt(20.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), 2.0, -1.0, 1.0)
    assert not plane.IsNull()
    assert not half.IsNull()
    ff = _intersect(plane, half)
    assert ff.Lines().Length() == 0
    assert ff.Points().Length() == 0


def test_IntTools_FaceFaceTest_HalfCylinderInsideCircularPlane_HasIntersection():
    plane = _circular_plane_face(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), 20.0)
    half = _half_cylinder_face(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), 5.0, -1.0, 1.0)
    assert not plane.IsNull()
    assert not half.IsNull()
    ff = _intersect(plane, half)
    assert ff.Lines().Length() >= 1


def test_IntTools_FaceFaceTest_OppositeHalfInsideCircle_HasIntersection():
    plane = _circular_plane_face(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), 15.0)
    half = _half_cylinder_face(gp_Pnt(10.0, 0.0, -5.0), gp_Dir(0.0, 1.0, 0.0), 3.0, -1.0, 1.0,
                               math.pi, 2.0 * math.pi)
    assert not plane.IsNull()
    assert not half.IsNull()
    ff = _intersect(plane, half)
    assert ff.Lines().Length() >= 1


def test_IntTools_FaceFaceTest_PartialCrossing_ProperlyTrimmed():
    plane = _circular_plane_face(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), 15.0)
    half = _half_cylinder_face(gp_Pnt(12.0, 0.0, -8.0), gp_Dir(0.0, 1.0, 0.0), 3.0, -1.0, 1.0, 0.0, math.pi)
    assert not plane.IsNull()
    assert not half.IsNull()
    ff = _intersect(plane, half)
    assert ff.Lines().Length() >= 1


def test_IntTools_FaceFaceTest_BothHalvesCompletelyOutside_NoIntersection():
    center, axis = gp_Pnt(20.0, 0.0, 20.0), gp_Dir(0.0, 1.0, 0.0)
    plane = _circular_plane_face(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), 5.0)
    half1 = _half_cylinder_face(center, axis, 2.0, -1.0, 1.0, 0.0, math.pi)
    assert not plane.IsNull()
    assert not half1.IsNull()
    ff1 = _intersect(plane, half1)
    assert ff1.Lines().Length() == 0
    assert ff1.Points().Length() == 0
    half2 = _half_cylinder_face(center, axis, 2.0, -1.0, 1.0, math.pi, 2.0 * math.pi)
    assert not half2.IsNull()
    ff2 = _intersect(plane, half2)
    assert ff2.Lines().Length() == 0
    assert ff2.Points().Length() == 0


def test_IntTools_FaceFaceTest_OCC24005_PlaneCylinderIntersection():
    plane = Geom_Plane(gp_Ax3(gp_Pnt(-72.948737453424499, 754.30437716359393, 259.52151854671678),
                              gp_Dir(6.2471473085930200e-007, -0.99999999999980493, 0.0),
                              gp_Dir(0.99999999999980493, 6.2471473085930200e-007, 0.0)))
    cylinder = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(-6.4812490053250649, 753.39408794522092, 279.16400974257465),
                                              gp_Dir(1.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0)),
                                       19.712534607908712)
    builder = BRep_Builder()
    face1, face2 = TopoDS_Face(), TopoDS_Face()
    builder.MakeFace(face1, plane, Precision.Confusion_s())
    builder.MakeFace(face2, cylinder, Precision.Confusion_s())
    inters = IntTools_FaceFace()
    inters.SetParameters(False, True, True, Precision.Confusion_s())
    inters.Perform(face1, face2)
    assert inters.IsDone()
    curves = inters.Lines()
    assert curves.Length() + inters.Points().Length() >= 1
