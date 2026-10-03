# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Transform_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgesOfWire,
    BRepGraph_CompoundId,
    BRepGraph_CompSolidId,
    BRepGraph_Copy,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_ProductId,
    BRepGraph_RefsWireOfFace,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
    BRepGraph_Transform,
    BRepGraph_VertexId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_Array1
from nanocct.Poly import Poly_Polygon2D, Poly_Polygon3D, Poly_PolygonOnTriangulation, Poly_Triangle, Poly_Triangulation
from nanocct.Precision import Precision
from nanocct.TopoDS import TopoDS_Compound, TopoDS_CompSolid

Kind = BRepGraph_NodeId.Kind
GeomPolicy = BRepGraph_Copy.GeomPolicy
MeshPolicy = BRepGraph_Copy.MeshPolicy
TOL = Precision.Confusion_s()


def _graph(shape, clear=True):
    g = BRepGraph()
    if clear:
        g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _box_graph(dx=10.0, dy=20.0, dz=30.0):
    return _graph(BRepPrimAPI_MakeBox(dx, dy, dz).Shape())


def _translation(dx, dy, dz):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(dx, dy, dz))
    return t


def _area(shape):
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


def _first_coedge_of_face(g, face_id):
    wire_it = BRepGraph_RefsWireOfFace(g, face_id)
    while wire_it.More():
        wire_id = g.Refs().Wires().Entry(wire_it.CurrentId()).ChildWireId
        ce_it = BRepGraph_CoEdgesOfWire(g, wire_id)
        while ce_it.More():
            ce_id = ce_it.CurrentId()
            if g.Topo().CoEdges().Definition(ce_id).FaceId == face_id:
                return ce_id
            ce_it.Next()
        wire_it.Next()
    return BRepGraph_CoEdgeId()


def _polygon3d(p1, p2):
    poly = Poly_Polygon3D(2, False)
    poly.ChangeNodes().SetValue(1, p1)
    poly.ChangeNodes().SetValue(2, p2)
    return poly


def _polygon2d(p1, p2):
    poly = Poly_Polygon2D(2)
    poly.ChangeNodes().SetValue(1, p1)
    poly.ChangeNodes().SetValue(2, p2)
    return poly


def _polygon_on_tri():
    poly = Poly_PolygonOnTriangulation(2, False)
    poly.SetNode(1, 1)
    poly.SetNode(2, 2)
    return poly


def _triangulation(p1, p2, p3):
    tri = Poly_Triangulation(3, 1, False)
    tri.SetNode(1, p1)
    tri.SetNode(2, p2)
    tri.SetNode(3, p3)
    tri.SetTriangle(1, Poly_Triangle(1, 2, 3))
    return tri


def _expect_vertices_transformed(source, result, trsf):
    nb = source.Topo().Vertices().Nb()
    assert result.Topo().Vertices().Nb() == nb
    for i in range(nb):
        vid = BRepGraph_VertexId(i)
        expected = BRepGraph_Tool.Vertex.Pnt_s(source, vid)
        expected.Transform(trsf)
        trans = BRepGraph_Tool.Vertex.Pnt_s(result, vid)
        assert abs(trans.X() - expected.X()) <= TOL
        assert abs(trans.Y() - expected.Y()) <= TOL
        assert abs(trans.Z() - expected.Z()) <= TOL


def _copy_subgraph(g, node):
    sub = BRepGraph()
    copied = BRepGraph_Copy.CopyNode_s(g, sub, node, GeomPolicy.Copy, MeshPolicy.Drop)
    assert copied.IsValid()
    assert not sub.IsEmpty()
    return sub


def _transform_node(g, node, trsf, mesh=MeshPolicy.Drop):
    result = BRepGraph()
    assert BRepGraph_Transform.TransformNode_s(g, result, node, trsf, GeomPolicy.Copy, mesh).IsValid()
    assert not result.IsEmpty()
    return result


def test_BRepGraph_TransformTest_TranslateBox_FaceCount():
    g = _box_graph()
    result = BRepGraph()
    assert BRepGraph_Transform.Perform_s(g, result, _translation(100.0, 200.0, 300.0), GeomPolicy.Copy)
    assert not result.IsEmpty()
    assert result.Topo().Faces().Nb() == 6
    assert result.Topo().Faces().Nb() == g.Topo().Faces().Nb()


def test_BRepGraph_TransformTest_TranslateBox_AreaPreserved():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    orig_area = _area(box)
    g = _graph(box)
    result = BRepGraph()
    assert BRepGraph_Transform.Perform_s(g, result, _translation(50.0, 0.0, 0.0), GeomPolicy.Copy)
    assert not result.IsEmpty()
    area = sum(
        abs(_area(result.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_FaceId(i)))))
        for i in range(result.Topo().Faces().Nb())
    )
    assert abs(area - orig_area) <= orig_area * 0.01


def test_BRepGraph_TransformTest_TranslateBox_VertexPointsShifted():
    g = _box_graph()
    assert g.Topo().Vertices().Nb() > 0
    dx, dy, dz = 100.0, 200.0, 300.0
    result = BRepGraph()
    assert BRepGraph_Transform.Perform_s(g, result, _translation(dx, dy, dz), GeomPolicy.Copy)
    assert not result.IsEmpty()
    assert result.Topo().Vertices().Nb() == g.Topo().Vertices().Nb()
    for i in range(g.Topo().Vertices().Nb()):
        orig = BRepGraph_Tool.Vertex.Pnt_s(g, BRepGraph_VertexId(i))
        trans = BRepGraph_Tool.Vertex.Pnt_s(result, BRepGraph_VertexId(i))
        assert abs(trans.X() - (orig.X() + dx)) <= TOL
        assert abs(trans.Y() - (orig.Y() + dy)) <= TOL
        assert abs(trans.Z() - (orig.Z() + dz)) <= TOL


def test_BRepGraph_TransformTest_PerformIntoNonEmptyTargetDoesNotMoveExistingVertices():
    source = _box_graph()
    target = BRepGraph()
    existing = target.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 1.0e-7)
    orig = BRepGraph_Tool.Vertex.Pnt_s(target, existing)

    assert BRepGraph_Transform.Perform_s(
        source, target, _translation(100.0, 200.0, 300.0), GeomPolicy.Copy, MeshPolicy.Drop
    )

    after = BRepGraph_Tool.Vertex.Pnt_s(target, existing)
    assert abs(after.X() - orig.X()) <= TOL
    assert abs(after.Y() - orig.Y()) <= TOL
    assert abs(after.Z() - orig.Z()) <= TOL


def test_BRepGraph_TransformTest_LocationOnly_NoCopyGeom():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g = _graph(box)
    assert g.Topo().Vertices().Nb() > 0
    dx = 50.0

    result = BRepGraph()
    assert BRepGraph_Transform.Perform_s(g, result, _translation(dx, 0.0, 0.0), GeomPolicy.Share)
    assert not result.IsEmpty()
    assert result.Topo().Faces().Nb() == 6
    assert result.Topo().Vertices().Nb() == g.Topo().Vertices().Nb()

    for i in range(g.Topo().Vertices().Nb()):
        orig = BRepGraph_Tool.Vertex.Pnt_s(g, BRepGraph_VertexId(i))
        pt = BRepGraph_Tool.Vertex.Pnt_s(result, BRepGraph_VertexId(i))
        assert abs(pt.X() - orig.X()) <= TOL

    assert result.Topo().Products().Nb() > 0
    rel = result.Topo().Products().Relations(BRepGraph_ProductId.Start_s())
    assert rel.OccurrenceRefIds.Size() >= 1
    occ_ref = result.Refs().Occurrences().Entry(rel.OccurrenceRefIds.Value(0))
    root_loc = occ_ref.LocalLocation
    assert not root_loc.IsIdentity()
    trsf = root_loc.Transformation()
    assert abs(trsf.Value(1, 4) - dx) <= TOL
    assert abs(trsf.Value(2, 4) - 0.0) <= TOL
    assert abs(trsf.Value(3, 4) - 0.0) <= TOL

    assert result.Topo().Solids().Nb() > 0
    solid = result.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_SolidId.Start_s()))
    assert not solid.IsNull()
    solid.Location(root_loc)

    orig_props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(box, orig_props)
    trans_props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(solid, trans_props)
    assert abs(trans_props.CentreOfMass().X() - (orig_props.CentreOfMass().X() + dx)) <= 1.0


def test_BRepGraph_TransformTest_TransformSingleFace():
    g = _box_graph()
    assert g.Topo().Faces().Nb() > 0
    face_node = BRepGraph_NodeId(Kind.Face, BRepGraph_FaceId.Start_s().Index)
    result = BRepGraph()
    assert BRepGraph_Transform.TransformNode_s(
        g, result, face_node, _translation(10.0, 20.0, 30.0), GeomPolicy.Copy
    ).IsValid()
    assert not result.IsEmpty()
    assert result.Topo().Faces().Nb() == 1


def test_BRepGraph_TransformTest_CopyMesh_TriangulationNodesTransformed():
    g = _box_graph()
    assert g.Topo().Faces().Nb() >= 1
    face_id = BRepGraph_FaceId.Start_s()
    src_tri = _triangulation(gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 5.0, 6.0), gp_Pnt(7.0, 8.0, 9.0))
    src_tri.Deflection(0.1)
    g.Editor().Faces().SetPersistentTriangulation(face_id, src_tri)
    g.Mesh().Editor().Faces().SetCachedTriangulation(face_id, src_tri)

    dx, dy, dz = 5.0, 10.0, 15.0
    result = BRepGraph()
    assert BRepGraph_Transform.Perform_s(g, result, _translation(dx, dy, dz), GeomPolicy.Copy, MeshPolicy.Copy)
    assert not result.IsEmpty()

    new_tri = result.Mesh().Persistent().Faces().Triangulation(face_id)
    assert new_tri is not None
    assert new_tri.NbNodes() == 3
    assert abs(new_tri.Node(1).X() - (1.0 + dx)) <= TOL
    assert abs(new_tri.Node(1).Y() - (2.0 + dy)) <= TOL
    assert abs(new_tri.Node(1).Z() - (3.0 + dz)) <= TOL
    assert abs(new_tri.Node(3).X() - (7.0 + dx)) <= TOL
    assert abs(src_tri.Node(1).X() - 1.0) <= TOL
    assert abs(new_tri.Deflection() - 0.1) <= TOL


def test_BRepGraph_TransformTest_CopyMesh_False_TriangulationInvalidated():
    g = _box_graph()
    face_id = BRepGraph_FaceId.Start_s()
    tri = _triangulation(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), gp_Pnt(0, 1, 0))
    g.Editor().Faces().SetPersistentTriangulation(face_id, tri)

    result = BRepGraph()
    assert BRepGraph_Transform.Perform_s(g, result, _translation(1.0, 0.0, 0.0), GeomPolicy.Copy, MeshPolicy.Drop)
    assert not result.IsEmpty()
    assert result.Mesh().Persistent().Faces().Triangulation(face_id) is None
    assert not result.Mesh().Effective().Faces().Has(face_id)


def test_BRepGraph_TransformTest_MoveRef_ChildRef_ComposesLocation():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), clear=False)
    children = NCollection_Array1[BRepGraph_NodeId](0, 0)
    children[0] = BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    compound = g.Editor().Compounds().Add(children)
    assert compound.IsValid()
    assert g.Refs().Children().IdsOf(compound).Size() == 1
    child_ref = g.Refs().Children().IdsOf(compound).First()

    assert g.Refs().Children().Entry(child_ref).LocalLocation.IsIdentity()

    dx = 42.0
    trsf = _translation(dx, 0.0, 0.0)
    assert BRepGraph_Transform.MoveRef_s(g, child_ref, trsf)
    assert abs(g.Refs().Children().Entry(child_ref).LocalLocation.Transformation().Value(1, 4) - dx) <= TOL

    BRepGraph_Transform.MoveRef_s(g, child_ref, trsf)
    assert abs(g.Refs().Children().Entry(child_ref).LocalLocation.Transformation().Value(1, 4) - 2.0 * dx) <= TOL


def test_BRepGraph_TransformTest_MoveRef_OccurrenceRef_ComposesLocationAndRejectsScale():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), clear=False)
    product_id = BRepGraph_ProductId.Start_s()
    assert not g.Topo().Products().Relations(product_id).OccurrenceRefIds.IsEmpty()
    occ_ref = g.Topo().Products().Relations(product_id).OccurrenceRefIds.First()

    assert BRepGraph_Transform.MoveRef_s(g, occ_ref, _translation(1.0, 2.0, 3.0))
    assert abs(g.Refs().Occurrences().Entry(occ_ref).LocalLocation.Transformation().Value(1, 4) - 1.0) <= TOL

    scale = gp_Trsf()
    scale.SetScale(gp_Pnt(), 2.0)
    assert not BRepGraph_Transform.MoveRef_s(g, occ_ref, scale)
    assert abs(g.Refs().Occurrences().Entry(occ_ref).LocalLocation.Transformation().Value(1, 4) - 1.0) <= TOL


def test_BRepGraph_TransformTest_TransformNode_FaceKind_VertexPointsShifted():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), clear=False)
    trsf = _translation(5.0, 10.0, 15.0)
    face_node = BRepGraph_NodeId(Kind.Face, BRepGraph_FaceId.Start_s().Index)
    sub = _copy_subgraph(g, face_node)
    result = _transform_node(g, face_node, trsf)
    assert result.Topo().Faces().Nb() == 1
    _expect_vertices_transformed(sub, result, trsf)


def test_BRepGraph_TransformTest_TransformNode_ShellKind():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), clear=False)
    assert g.Topo().Shells().Nb() >= 1
    shell_node = BRepGraph_NodeId(Kind.Shell, BRepGraph_ShellId.Start_s().Index)
    sub = _copy_subgraph(g, shell_node)
    trsf = _translation(100.0, 0.0, 0.0)
    result = _transform_node(g, shell_node, trsf)
    assert result.Topo().Shells().Nb() == 1
    assert result.Topo().Faces().Nb() == g.Topo().Faces().Nb()
    _expect_vertices_transformed(sub, result, trsf)


def test_BRepGraph_TransformTest_TransformNode_SolidKind():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), clear=False)
    assert g.Topo().Solids().Nb() >= 1
    solid_node = BRepGraph_NodeId(Kind.Solid, BRepGraph_SolidId.Start_s().Index)
    sub = _copy_subgraph(g, solid_node)
    trsf = _translation(0.0, 50.0, 0.0)
    result = _transform_node(g, solid_node, trsf)
    assert result.Topo().Solids().Nb() == 1
    assert result.Topo().Shells().Nb() == g.Topo().Shells().Nb()
    assert result.Topo().Faces().Nb() == g.Topo().Faces().Nb()
    _expect_vertices_transformed(sub, result, trsf)


def test_BRepGraph_TransformTest_TransformNode_VertexKind():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape(), clear=False)
    assert g.Topo().Vertices().Nb() >= 1
    vid = BRepGraph_VertexId.Start_s()
    vertex_node = BRepGraph_NodeId(Kind.Vertex, vid.Index)
    orig = BRepGraph_Tool.Vertex.Pnt_s(g, vid)

    result = _transform_node(g, vertex_node, _translation(1.0, 2.0, 3.0))
    assert result.Topo().Vertices().Nb() == 1
    trans = BRepGraph_Tool.Vertex.Pnt_s(result, BRepGraph_VertexId.Start_s())
    assert abs(trans.X() - (orig.X() + 1.0)) <= TOL
    assert abs(trans.Y() - (orig.Y() + 2.0)) <= TOL
    assert abs(trans.Z() - (orig.Z() + 3.0)) <= TOL


def test_BRepGraph_TransformTest_TransformNode_CompoundKind():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape())
    bb.Add(comp, BRepPrimAPI_MakeBox(3.0, 3.0, 3.0).Shape())

    g = _graph(comp, clear=False)
    assert g.Topo().Compounds().Nb() >= 1
    comp_node = BRepGraph_NodeId(Kind.Compound, BRepGraph_CompoundId.Start_s().Index)
    sub = _copy_subgraph(g, comp_node)
    trsf = _translation(20.0, 0.0, 0.0)
    result = _transform_node(g, comp_node, trsf)
    assert result.Topo().Compounds().Nb() == 1
    assert result.Topo().Solids().Nb() == g.Topo().Solids().Nb()
    assert result.Topo().Faces().Nb() == g.Topo().Faces().Nb()
    _expect_vertices_transformed(sub, result, trsf)


def test_BRepGraph_TransformTest_TransformNode_CompSolidKind():
    bb = BRep_Builder()
    cs = TopoDS_CompSolid()
    bb.MakeCompSolid(cs)
    bb.Add(cs, BRepPrimAPI_MakeBox(4.0, 4.0, 4.0).Shape())

    g = _graph(cs, clear=False)
    assert g.Topo().CompSolids().Nb() >= 1
    cs_node = BRepGraph_NodeId(Kind.CompSolid, BRepGraph_CompSolidId.Start_s().Index)
    sub = _copy_subgraph(g, cs_node)
    trsf = _translation(0.0, 0.0, 7.0)
    result = _transform_node(g, cs_node, trsf)
    assert result.Topo().CompSolids().Nb() == 1
    assert result.Topo().Solids().Nb() == g.Topo().Solids().Nb()
    _expect_vertices_transformed(sub, result, trsf)


def test_BRepGraph_TransformTest_TransformNode_NegativeScale_VertexPointsMirrored():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), clear=False)
    solid_node = BRepGraph_NodeId(Kind.Solid, BRepGraph_SolidId.Start_s().Index)
    sub = _copy_subgraph(g, solid_node)
    trsf = gp_Trsf()
    trsf.SetMirror(gp_Pnt(0.0, 0.0, 0.0))
    result = _transform_node(g, solid_node, trsf)
    assert result.Topo().Faces().Nb() == g.Topo().Faces().Nb()
    assert result.Topo().Vertices().Nb() == g.Topo().Vertices().Nb()
    _expect_vertices_transformed(sub, result, trsf)


def test_BRepGraph_TransformTest_TransformNode_CopyGeomAndMesh_DropsRuntimeCache():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), clear=False)
    assert g.Topo().Faces().Nb() >= 1
    face_id = BRepGraph_FaceId.Start_s()
    tri = _triangulation(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(2.0, 0.0, 0.0), gp_Pnt(0.0, 2.0, 0.0))
    tri.Deflection(1.0)
    g.Mesh().Editor().Faces().SetCachedTriangulation(face_id, tri)

    solid_node = BRepGraph_NodeId(Kind.Solid, BRepGraph_SolidId.Start_s().Index)
    result = _transform_node(g, solid_node, _translation(5.0, 0.0, 0.0), MeshPolicy.Copy)
    # C++: Cache().Faces().Entry(face) == nullptr
    assert not result.Mesh().Cache().Faces().Has(face_id)


def test_BRepGraph_TransformTest_TransformNode_CopyGeomAndMesh_CopiesPersistentMeshAndDropsCache():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), clear=False)
    face_id = BRepGraph_FaceId.Start_s()
    coedge_id = _first_coedge_of_face(g, face_id)
    assert coedge_id.IsValid(g.Topo().CoEdges().Nb())
    edge_id = g.Topo().CoEdges().Definition(coedge_id).ChildEdgeId
    assert edge_id.IsValid(g.Topo().Edges().Nb())

    ed = g.Editor()
    unused_tri = _triangulation(gp_Pnt(100.0, 0.0, 0.0), gp_Pnt(101.0, 0.0, 0.0), gp_Pnt(100.0, 1.0, 0.0))
    ed.Faces().SetPersistentTriangulation(face_id, unused_tri)
    ed.Edges().SetPersistentPolygon3D(edge_id, _polygon3d(gp_Pnt(100.0, 0.0, 0.0), gp_Pnt(101.0, 0.0, 0.0)))
    ed.CoEdges().SetPersistentPolygon2D(coedge_id, _polygon2d(gp_Pnt2d(100.0, 0.0), gp_Pnt2d(101.0, 0.0)))
    ed.CoEdges().SetPersistentPolygonOnTri(coedge_id, _polygon_on_tri())

    tri = _triangulation(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(1.0, 0.0, 0.0), gp_Pnt(0.0, 1.0, 0.0))
    ed.Faces().SetPersistentTriangulation(face_id, tri)
    p3d = _polygon3d(gp_Pnt(1.0, 2.0, 3.0), gp_Pnt(4.0, 5.0, 6.0))
    ed.Edges().SetPersistentPolygon3D(edge_id, p3d)
    p2d = _polygon2d(gp_Pnt2d(7.0, 8.0), gp_Pnt2d(9.0, 10.0))
    ed.CoEdges().SetPersistentPolygon2D(coedge_id, p2d)
    pot = _polygon_on_tri()
    ed.CoEdges().SetPersistentPolygonOnTri(coedge_id, pot)

    me = g.Mesh().Editor()
    me.Faces().SetCachedTriangulation(face_id, tri)
    me.Edges().SetCachedPolygon3D(edge_id, p3d)
    me.CoEdges().SetCachedPolygon2D(coedge_id, p2d)
    me.CoEdges().AppendCachedPolygonOnTri(coedge_id, pot)

    solid_node = BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    result = _transform_node(g, solid_node, _translation(5.0, 0.0, 0.0), MeshPolicy.Copy)

    r_coedge = _first_coedge_of_face(result, face_id)
    assert r_coedge.IsValid(result.Topo().CoEdges().Nb())
    r_edge = result.Topo().CoEdges().Definition(r_coedge).ChildEdgeId
    assert r_edge.IsValid(result.Topo().Edges().Nb())

    assert not result.Mesh().Cache().Edges().Has(r_edge)

    pers = result.Mesh().Persistent()
    r_p3d = pers.Edges().Polygon3D(r_edge)
    assert r_p3d is not None
    assert abs(r_p3d.Nodes().Value(1).X() - (1.0 + 5.0)) <= TOL

    assert not result.Mesh().Cache().CoEdges().Has(r_coedge)

    r_coedge_def = result.Topo().CoEdges().Definition(r_coedge)
    r_p2d = pers.CoEdges().PolygonOnSurface(r_coedge)
    assert r_p2d is not None
    assert abs(r_p2d.Nodes().Value(1).X() - 7.0) <= TOL

    assert r_coedge_def.FaceId.IsValid(result.Topo().Faces().Nb())
    r_tri = pers.Faces().Triangulation(r_coedge_def.FaceId)
    assert r_tri is not None
    assert abs(r_tri.Node(2).X() - (1.0 + 5.0)) <= TOL

    r_pot = pers.Edges().PolygonOnTriangulation(r_edge, r_coedge_def.FaceId)
    assert r_pot is not None
    r_tri2 = pers.Faces().Triangulation(r_coedge_def.FaceId)
    assert r_tri2 is not None
    assert abs(r_tri2.Node(2).X() - (1.0 + 5.0)) <= TOL
