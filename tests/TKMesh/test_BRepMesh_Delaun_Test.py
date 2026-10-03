# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_Delaun_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from nanocct.BRepMesh import BRepMesh_IncrementalMesh
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.Geom import Geom_Plane
from nanocct.gp import gp, gp_Pln, gp_Pnt, gp_Vec2d, gp_XY
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location


def test_BRepMesh_DelaunTest_Vec2dAngleSignConvention():
    right = gp_Vec2d(1.0, 0.0)
    up = gp_Vec2d(0.0, 1.0)
    ang_ccw = up.Angle(right)
    assert ang_ccw < 0.0
    assert abs(ang_ccw - (-math.pi / 2)) <= Precision.Angular_s()
    ang_cw = right.Angle(up)
    assert ang_cw > 0.0
    assert abs(ang_cw - math.pi / 2) <= Precision.Angular_s()


def _winding(vertices):
    center = gp_XY(0.0, 0.0)
    prev = gp_Vec2d(vertices[0] - center)
    total = 0.0
    for v in vertices[1:]:
        cur = gp_Vec2d(v - center)
        total += cur.Angle(prev)
        prev = cur
    return total


def test_BRepMesh_DelaunTest_WindingAngleCCWPolygon():
    total = _winding([gp_XY(1.0, 0.0), gp_XY(0.0, 1.0), gp_XY(-1.0, 0.0), gp_XY(0.0, -1.0), gp_XY(1.0, 0.0)])
    assert abs(abs(total) - 2.0 * math.pi) <= Precision.Angular_s()
    two_pi = 2.0 * math.pi
    assert (abs(two_pi - total) <= Precision.Angular_s()) is False
    assert (abs(abs(total) - two_pi) <= Precision.Angular_s()) is True


def test_BRepMesh_DelaunTest_WindingAngleCWPolygon():
    total = _winding([gp_XY(1.0, 0.0), gp_XY(0.0, -1.0), gp_XY(-1.0, 0.0), gp_XY(0.0, 1.0), gp_XY(1.0, 0.0)])
    assert abs(total - 2.0 * math.pi) <= Precision.Angular_s()
    two_pi = 2.0 * math.pi
    assert (abs(two_pi - total) <= Precision.Angular_s()) is True
    assert (abs(abs(total) - two_pi) <= Precision.Angular_s()) is True


def _square_wire(half):
    pts = [gp_Pnt(-half, -half, 0.0), gp_Pnt(half, -half, 0.0), gp_Pnt(half, half, 0.0), gp_Pnt(-half, half, 0.0)]
    maker = BRepBuilderAPI_MakeWire()
    for i in range(4):
        maker.Add(BRepBuilderAPI_MakeEdge(pts[i], pts[(i + 1) % 4]).Edge())
    assert maker.IsDone()
    return maker.Wire()


def test_BRepMesh_DelaunTest_MeshPlanarFaceWithHole():
    outer = _square_wire(5.0)
    inner = _square_wire(1.0)
    plane = Geom_Plane(gp_Pln(gp.Origin_s(), gp.DZ_s()))
    face_maker = BRepBuilderAPI_MakeFace(plane, outer)
    face_maker.Add(inner)
    assert face_maker.IsDone()
    face = face_maker.Face()

    mesher = BRepMesh_IncrementalMesh(face, 0.1)
    assert mesher.IsDone()

    tri = BRep_Tool.Triangulation_s(face, TopLoc_Location())
    assert tri is not None
    assert tri.NbTriangles() > 0
    assert tri.NbNodes() > 0


def test_BRepMesh_DelaunTest_MeshBoxAllFaces():
    box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    mesher = BRepMesh_IncrementalMesh(box, 0.5)
    assert mesher.IsDone()

    face_count = 0
    exp = TopExp_Explorer(box, TopAbs_FACE)
    while exp.More():
        tri = BRep_Tool.Triangulation_s(TopoDS.Face(exp.Current()), TopLoc_Location())
        assert tri is not None
        assert tri.NbTriangles() > 0
        face_count += 1
        exp.Next()
    assert face_count == 6


def test_BRepMesh_DelaunTest_MeshCylinderCurvedFaces():
    cyl = BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape()
    mesher = BRepMesh_IncrementalMesh(cyl, 0.5)
    assert mesher.IsDone()

    total = 0
    exp = TopExp_Explorer(cyl, TopAbs_FACE)
    while exp.More():
        tri = BRep_Tool.Triangulation_s(TopoDS.Face(exp.Current()), TopLoc_Location())
        assert tri is not None
        total += tri.NbTriangles()
        exp.Next()
    assert total > 0
