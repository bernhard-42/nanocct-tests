# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_IncrementalMesh_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepAdaptor import BRepAdaptor_Surface
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
)
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepMesh import BRepMesh_IncrementalMesh
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeRevol
from nanocct.Geom import Geom_CylindricalSurface
from nanocct.GeomAbs import GeomAbs_Torus
from nanocct.gp import gp, gp_Ax1, gp_Ax2, gp_Ax3, gp_Circ, gp_Dir, gp_Pln, gp_Pnt, gp_Vec
from nanocct.IMeshTools import IMeshTools_Parameters
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location


def _faces(shape):
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        yield TopoDS.Face(exp.Current())
        exp.Next()


def test_BRepMesh_IncrementalMeshTest_OCC26407_PlanarPolygonMeshStatus():
    pnts = [
        gp_Pnt(587.90000000000009094947, 40.6758179230516248026106, 88.5),
        gp_Pnt(807.824182076948432040808, 260.599999999999965893949, 88.5),
        gp_Pnt(644.174182076948454778176, 424.249999999999943156581, 88.5000000000000142108547),
        gp_Pnt(629.978025792618950617907, 424.25, 88.5),
        gp_Pnt(793.628025792618700506864, 260.599999999999852207111, 88.5),
        gp_Pnt(587.900000000000204636308, 54.8719742073813492311274, 88.5),
        gp_Pnt(218.521974207381418864315, 424.250000000000056843419, 88.5),
        gp_Pnt(204.325817923051886282337, 424.249999999999943156581, 88.5),
    ]
    vertices = [BRepBuilderAPI_MakeVertex(p).Vertex() for p in pnts]
    wire_builder = BRepBuilderAPI_MakeWire()
    for i in range(len(vertices)):
        wire_builder.Add(BRepBuilderAPI_MakeEdge(vertices[i], vertices[(i + 1) % len(vertices)]).Edge())
    assert wire_builder.IsDone()

    v0, v1, v2 = pnts[0], pnts[1], pnts[-1]
    normal = gp_Vec(v0, v1).Crossed(gp_Vec(v0, v2))
    face = BRepBuilderAPI_MakeFace(gp_Pln(v0, gp_Dir(normal)), wire_builder.Wire()).Face()

    mesher = BRepMesh_IncrementalMesh(face, 1.0e-7)
    assert mesher.GetStatusFlags() == 0


def test_BRepMesh_IncrementalMeshTest_TrimmedCylinder_RespectsUVRangeAndDeflection():
    radius, first_u, last_u, first_v, last_v, deflection = 5.0, 0.4, 5.7, -2.0, 7.0, 0.05
    cylinder = Geom_CylindricalSurface(gp_Ax3(gp.Origin_s(), gp.DZ_s()), radius)
    face_builder = BRepBuilderAPI_MakeFace(cylinder, first_u, last_u, first_v, last_v, Precision.Confusion_s())
    assert face_builder.IsDone()
    face = face_builder.Face()

    mesher = BRepMesh_IncrementalMesh(face, deflection)
    assert mesher.IsDone()

    loc = TopLoc_Location()
    tri = BRep_Tool.Triangulation_s(face, loc)
    assert tri is not None
    assert tri.HasUVNodes()
    assert tri.NbTriangles() > 0

    pconf = Precision.PConfusion_s()
    trsf = loc.Transformation()
    for i in range(1, tri.NbNodes() + 1):
        uv = tri.UVNode(i)
        assert first_u - pconf <= uv.X() <= last_u + pconf
        assert first_v - pconf <= uv.Y() <= last_v + pconf
        expected = cylinder.Value(uv.X(), uv.Y())
        actual = tri.Node(i).Transformed(trsf)
        assert actual.Distance(expected) <= Precision.Confusion_s()

    for t in range(1, tri.NbTriangles() + 1):
        n1, n2, n3 = tri.Triangle(t).Get()
        uv1, uv2, uv3 = tri.UVNode(n1), tri.UVNode(n2), tri.UVNode(n3)
        expected = cylinder.Value((uv1.X() + uv2.X() + uv3.X()) / 3.0, (uv1.Y() + uv2.Y() + uv3.Y()) / 3.0)
        p1, p2, p3 = (tri.Node(n).Transformed(trsf) for n in (n1, n2, n3))
        actual = gp_Pnt((p1.XYZ() + p2.XYZ() + p3.XYZ()) / 3.0)
        assert actual.Distance(expected) <= deflection


def test_BRepMesh_IncrementalMeshTest_BooleanTrimmedTorus_CrossingSeamProducesDenseMesh():
    box_builder = BRepPrimAPI_MakeBox(gp_Pnt(-187.0, -20.0, -67.5), gp_Pnt(187.0, 0.0, 67.5))
    box = box_builder.Shape()
    assert box_builder.IsDone()

    circle = gp_Circ(gp_Ax2(gp_Pnt(200.0, -20.0, 0.0), gp_Dir(0.0, -1.0, 0.0)), 17.5)
    edge_builder = BRepBuilderAPI_MakeEdge(circle)
    edge = edge_builder.Edge()
    assert edge_builder.IsDone()
    wire_builder = BRepBuilderAPI_MakeWire(edge)
    wire = wire_builder.Wire()
    assert wire_builder.IsDone()
    face_builder = BRepBuilderAPI_MakeFace(wire, True)
    profile = face_builder.Face()
    assert face_builder.IsDone()

    axis = gp_Ax1(gp_Pnt(0.0, -20.0, 0.0), gp_Dir(0.0, 0.0, -1.0))
    ring_builder = BRepPrimAPI_MakeRevol(profile, axis, 2.0 * math.pi)
    ring = ring_builder.Shape()
    assert ring_builder.IsDone()

    fuse = BRepAlgoAPI_Fuse(box, ring)
    fuse.Build()
    assert fuse.IsDone()
    fused = fuse.Shape()
    assert not fused.IsNull()
    assert BRepCheck_Analyzer(fused).IsValid()

    params = IMeshTools_Parameters()
    params.Deflection = 0.1
    params.Angle = 0.4
    mesher = BRepMesh_IncrementalMesh(fused, params)
    assert mesher.IsDone()

    torus_faces = torus_nodes = torus_triangles = 0
    for face in _faces(fused):
        if BRepAdaptor_Surface(face).GetType() != GeomAbs_Torus:
            continue
        torus_faces += 1
        tri = BRep_Tool.Triangulation_s(face, TopLoc_Location())
        assert tri is not None
        torus_nodes += tri.NbNodes()
        torus_triangles += tri.NbTriangles()

    assert torus_faces > 0
    assert torus_nodes > 1000
    assert torus_triangles > 1000


def test_BRepMesh_IncrementalMeshTest_ClosedCylinder_SeamPolygonsReferenceValidMeshNodes():
    cyl_builder = BRepPrimAPI_MakeCylinder(5.0, 10.0)
    cyl = cyl_builder.Shape()
    assert cyl_builder.IsDone()
    mesher = BRepMesh_IncrementalMesh(cyl, 0.1)
    assert mesher.IsDone()

    seam_edges = 0
    for face in _faces(cyl):
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        assert tri is not None
        exp = TopExp_Explorer(face, TopAbs_EDGE)
        while exp.More():
            edge = TopoDS.Edge(exp.Current())
            exp.Next()
            if BRep_Tool.IsClosed_s(edge, face) is False:
                continue
            fwd = BRep_Tool.PolygonOnTriangulation_s(edge, tri, loc)
            rev = BRep_Tool.PolygonOnTriangulation_s(TopoDS.Edge(edge.Reversed()), tri, loc)
            assert fwd is not None
            assert rev is not None
            for poly in (fwd, rev):
                for k in range(1, poly.NbNodes() + 1):
                    assert 1 <= poly.Node(k) <= tri.NbNodes()
            seam_edges += 1
    assert seam_edges > 0
