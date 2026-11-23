# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_Delaun_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from nanocct.BRepMesh import BRepMesh_DataStructureOfDelaun, BRepMesh_Delaun, BRepMesh_Edge, BRepMesh_Fixed, BRepMesh_Free, BRepMesh_Frontier, BRepMesh_IncrementalMesh, BRepMesh_Triangle, BRepMesh_Vertex
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.Geom import Geom_Plane
from nanocct.gp import gp, gp_Pln, gp_Pnt, gp_Vec2d, gp_XY
from nanocct.NCollection import NCollection_IncAllocator, NCollection_Shared__NCollection_DynamicArray__int
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



def test_BRepMesh_DelaunTest_InteriorPointNearLongFrontierIsInserted():
    for scale in (0.1, 1.0, 10.0):
        structure = BRepMesh_DataStructureOfDelaun(NCollection_IncAllocator())
        structure.Data().SetTolerance(Precision.PConfusion_s())
        nodes = [structure.AddNode(BRepMesh_Vertex(u, v, BRepMesh_Frontier))
                 for u, v in ((0.0, 0.0), (scale, 0.0), (0.5 * scale, 0.25 * scale))]
        edges, orientations = [], []
        for i in range(3):
            edge = structure.AddLink(BRepMesh_Edge(nodes[i], nodes[(i + 1) % 3], BRepMesh_Frontier))
            edges.append(abs(edge))
            orientations.append(edge > 0)
        triangle = structure.AddElement(BRepMesh_Triangle(edges, orientations, BRepMesh_Free))
        mesher = BRepMesh_Delaun(structure, 2, 2, True)
        # The centroid height is one third of the triangle height aScale / 4.
        point = BRepMesh_Vertex(0.5 * scale, scale / 12.0, BRepMesh_Free)
        tol_u, tol_v = structure.Data().GetTolerance()
        contains, edge_on = mesher.Contains(triangle, point, tol_u * tol_u + tol_v * tol_v)
        assert contains is True, scale
        assert edge_on == 0, scale
        vertices = NCollection_Shared__NCollection_DynamicArray__int()
        point_id = structure.AddNode(point)
        vertices.Append(point_id)
        mesher.AddVertices(vertices)
        elements = structure.ElementsOfDomain()
        assert elements.Size() == 3, scale
        incident = 0
        it = type(elements).Iterator(elements)
        while it.More():
            incident += structure.ElementNodes(structure.GetElement(it.Key())).count(point_id)
            it.Next()
        assert incident == 3, scale


def test_BRepMesh_DelaunTest_SharedEdgeAndBoundaryInsertionKeepConstraints():
    for case in (0, 1, 2, 3):
        structure = BRepMesh_DataStructureOfDelaun(NCollection_IncAllocator())
        nodes = [structure.AddNode(BRepMesh_Vertex(u, v, BRepMesh_Frontier))
                 for u, v in ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))]
        outer = [structure.AddLink(BRepMesh_Edge(nodes[i], nodes[(i + 1) % 4], BRepMesh_Frontier)) for i in range(4)]
        diagonal = structure.AddLink(BRepMesh_Edge(nodes[0], nodes[2], BRepMesh_Fixed if case == 3 else BRepMesh_Free))
        structure.AddElement(BRepMesh_Triangle([outer[0], outer[1], diagonal], [True, True, False], BRepMesh_Free))
        structure.AddElement(BRepMesh_Triangle([diagonal, outer[2], outer[3]], [True, True, True], BRepMesh_Free))
        mesher = BRepMesh_Delaun(structure, 2, 2, True)
        parameter = gp_XY(0.5, 0.0 if case == 1 else (-0.5 if case == 2 else 0.5))
        point = structure.AddNode(BRepMesh_Vertex(parameter, 0, BRepMesh_Free))
        vertices = NCollection_Shared__NCollection_DynamicArray__int()
        vertices.Append(point)
        mesher.AddVertices(vertices)
        elements = structure.ElementsOfDomain()
        assert elements.Size() == (4 if case == 0 else 2), case
        incident = 0
        it = type(elements).Iterator(elements)
        while it.More():
            incident += structure.ElementNodes(structure.GetElement(it.Key())).count(point)
            it.Next()
        assert incident == (4 if case == 0 else 0), case
        for edge in outer:
            assert structure.GetLink(edge).Movability() == BRepMesh_Frontier, case
        if case == 3:
            assert structure.GetLink(diagonal).Movability() == BRepMesh_Fixed
