# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_BaseMeshAlgo_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeVertex
from nanocct.BRepMesh import BRepMesh_IncrementalMesh
from nanocct.GeomAPI import GeomAPI_ProjectPointOnSurf
from nanocct.gp import gp, gp_Pln, gp_Pnt
from nanocct.IMeshTools import IMeshTools_Parameters
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_INTERNAL
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Vertex


def _add_internal_vertex(face, point):
    surf = BRep_Tool.Surface_s(face)
    projection = GeomAPI_ProjectPointOnSurf(point, surf)
    if projection.IsDone() is False or projection.NbPoints() == 0:
        return TopoDS_Vertex()
    u, v = projection.Parameters(1)
    vertex = BRepBuilderAPI_MakeVertex(projection.Point(1)).Vertex()
    vertex.Orientation(TopAbs_INTERNAL)
    builder = BRep_Builder()
    builder.UpdateVertex(vertex, u, v, face, Precision.Confusion_s())
    builder.Add(face, vertex)
    return vertex


def _has_only_valid_nodes(tri, loc):
    trsf = loc.Transformation()
    for i in range(1, tri.NbNodes() + 1):
        p = tri.Node(i).Transformed(trsf)
        if abs(p.X()) > 1.0e10 or abs(p.Y()) > 1.0e10 or abs(p.Z()) > 1.0e10:
            return False
    return True


def _has_only_valid_triangles(tri):
    for i in range(1, tri.NbTriangles() + 1):
        n1, n2, n3 = tri.Triangle(i).Get()
        if n1 == n2 or n2 == n3 or n1 == n3:
            return False
    return True


def _find_closest_node(tri, loc, point):
    trsf = loc.Transformation()
    closest, min_sq = 0, math.inf
    for i in range(1, tri.NbNodes() + 1):
        d2 = point.SquareDistance(tri.Node(i).Transformed(trsf))
        if d2 < min_sq:
            closest, min_sq = i, d2
    return closest, math.sqrt(min_sq)


def _params(internal):
    params = IMeshTools_Parameters()
    params.Deflection = 1.0
    params.Angle = 0.5
    params.InternalVerticesMode = internal
    return params


def _plane_face(umax, vmax):
    return BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp.DZ_s()), 0.0, umax, 0.0, vmax).Face()


def test_BRepMesh_BaseMeshAlgoTest_InternalVerticesAreBound():
    face = _plane_face(100.0, 50.0)
    pts = [gp_Pnt(40.0, 20.0, 0.0), gp_Pnt(60.0, 30.0, 0.0), gp_Pnt(77.0, 33.0, 0.0)]
    for p in pts:
        assert not _add_internal_vertex(face, p).IsNull()

    mesher = BRepMesh_IncrementalMesh(face, _params(True))
    assert mesher.IsDone()

    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    assert tri is not None
    assert _has_only_valid_nodes(tri, loc)
    assert _has_only_valid_triangles(tri)
    for p in pts:
        idx, dist = _find_closest_node(tri, loc, p)
        assert idx > 0
        assert dist < 1.0e-6


def test_BRepMesh_BaseMeshAlgoTest_MultipleInternalVertices():
    size, grid = 100.0, 5
    face = _plane_face(size, size)
    pts = []
    for i in range(1, grid):
        for j in range(1, grid):
            p = gp_Pnt(size * i / grid, size * j / grid, 0.0)
            pts.append(p)
            assert not _add_internal_vertex(face, p).IsNull()

    mesher = BRepMesh_IncrementalMesh(face, _params(True))
    assert mesher.IsDone()

    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    assert tri is not None
    assert _has_only_valid_nodes(tri, loc)
    assert _has_only_valid_triangles(tri)
    found = 0
    for p in pts:
        idx, dist = _find_closest_node(tri, loc, p)
        if idx > 0 and dist < 1.0e-6:
            found += 1
    assert found == len(pts)


def test_BRepMesh_BaseMeshAlgoTest_InternalVerticesModeDisabled():
    face = _plane_face(100.0, 50.0)
    pt = gp_Pnt(50.0, 25.0, 0.0)
    assert not _add_internal_vertex(face, pt).IsNull()

    mesher = BRepMesh_IncrementalMesh(face, _params(False))
    assert mesher.IsDone()

    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    assert tri is not None
    assert _has_only_valid_nodes(tri, loc)
    assert _has_only_valid_triangles(tri)
    idx, _dist = _find_closest_node(tri, loc, pt)
    assert idx > 0
