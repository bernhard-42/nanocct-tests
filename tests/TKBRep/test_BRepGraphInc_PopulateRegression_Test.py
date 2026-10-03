# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraphInc_PopulateRegression_Test.cxx (LGPL-2.1 with the OCCT exception)

from nanocct import TopAbs, TopoDS
from nanocct.Bnd import Bnd_Box
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBndLib import BRepBndLib
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_Compact,
    BRepGraph_CompoundId,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_LayerTopoSupplement,
    BRepGraph_NodeId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
)
from nanocct.BRepGraphInc import BRepGraphInc_Populate, BRepGraphInc_Reconstruct
from nanocct.BRepMesh import BRepMesh_IncrementalMesh
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_SphericalSurface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Poly import Poly_Polygon3D
from nanocct.Precision import Precision
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Face, TopoDS_Shape, TopoDS_Vertex

FAILED = BRepGraphInc_Populate.BuildStatus.Failed


# ---------------------------------------------------------------- helpers


def translation_location(x, y, z):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return TopLoc_Location(trsf)


def geometry_bounds(shape):
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box, False, False)
    return box


def mesh_bounds(shape):
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, True)
    return box


def expect_box_near(actual, expected, tol):
    a = actual.Get()
    e = expected.Get()
    for name in ("Xmin", "Ymin", "Zmin", "Xmax", "Ymax", "Zmax"):
        assert abs(getattr(a, name) - getattr(e, name)) <= tol, name


def first_sub_shape(shape, kind):
    exp = TopExp_Explorer(shape, kind)
    return exp.Current() if exp.More() else TopoDS_Shape()


def first_face_of_box(size):
    box = BRepPrimAPI_MakeBox(size, size, size).Shape()
    return TopoDS.Face(first_sub_shape(box, TopAbs.TopAbs_FACE))


def count_source_polygon_on_triangulation(shape, use_face_location):
    """Returns (count, has_located_triangulation)."""
    count = 0
    has_located = False
    for face_shape in TopExp_Explorer(shape, TopAbs.TopAbs_FACE):
        face = TopoDS.Face(face_shape)
        tri_loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, tri_loc)
        if tri is None:
            continue
        has_located = has_located or not tri_loc.IsIdentity()
        for edge_shape in TopExp_Explorer(face, TopAbs.TopAbs_EDGE):
            lookup_loc = tri_loc if use_face_location else TopLoc_Location()
            if BRep_Tool.PolygonOnTriangulation_s(TopoDS.Edge(edge_shape), tri, lookup_loc) is not None:
                count += 1
    return count, has_located


def count_graph_polygon_on_triangulation(graph):
    count = 0
    for i in range(graph.Topo().CoEdges().Nb()):
        if graph.Topo().CoEdges().Definition(BRepGraph_CoEdgeId(i)).PolygonOnTriRepId.IsValid():
            count += 1
    return count


def make_no_wire_natural_sphere_face():
    bb = BRep_Builder()
    face = TopoDS_Face()
    bb.MakeFace(
        face,
        Geom_SphericalSurface(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 10.0),
        Precision.Confusion_s(),
    )
    bb.NaturalRestriction(face, True)
    return face


def count_degenerated_edges(shape):
    return sum(1 for e in TopExp_Explorer(shape, TopAbs.TopAbs_EDGE) if BRep_Tool.Degenerated_s(TopoDS.Edge(e)))


def make_nested_compound(root_loc, inner_loc, solid_loc):
    box = BRepPrimAPI_MakeBox(2.0, 3.0, 4.0).Shape()
    mesher = BRepMesh_IncrementalMesh(box, 0.2)
    assert mesher.IsDone()

    bb = BRep_Builder()
    moved_solid = TopoDS.Solid(TopoDS.Solid(box).Moved(solid_loc))

    inner = TopoDS_Compound()
    bb.MakeCompound(inner)
    bb.Add(inner, moved_solid)
    moved_inner = TopoDS.Compound(inner.Moved(inner_loc))

    root = TopoDS_Compound()
    bb.MakeCompound(root)
    bb.Add(root, moved_inner)
    return TopoDS.Compound(root.Moved(root_loc))


def nested_locations():
    return (
        translation_location(0.0, 0.0, 11.0),
        translation_location(0.0, 7.0, 0.0),
        translation_location(5.0, 0.0, 0.0),
    )


def ensure_supplement(graph):
    """C++ LayerRegistry().Ensure<BRepGraph_LayerTopoSupplement>() (template): find or register."""
    registry = graph.LayerRegistry()
    layer = registry.FindLayer(BRepGraph_LayerTopoSupplement.GetID_s())
    if layer is None:
        layer = BRepGraph_LayerTopoSupplement()
        registry.RegisterLayer(layer)
    return layer


# ---------------------------------------------------------------- tests


def test_BRepGraphInc_PopulateRegressionTest_LocatedFacePolygonOnTriangulation_IsCaptured():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    mesher = BRepMesh_IncrementalMesh(box, 0.5)
    assert mesher.IsDone()
    moved_box = box.Moved(translation_location(5.0, 6.0, 7.0))

    source_count, has_located = count_source_polygon_on_triangulation(moved_box, True)
    identity_count, _ = count_source_polygon_on_triangulation(moved_box, False)

    assert has_located
    assert source_count > 0
    assert identity_count == 0

    g = BRepGraph()
    assert BRepGraphInc_Populate.Perform_s(g, moved_box, False) != FAILED
    assert count_graph_polygon_on_triangulation(g) > 0


def test_BRepGraphInc_PopulateRegressionTest_NoWireNaturalSphere_DegenerateBoundaryEdgesRoundTrip():
    face = make_no_wire_natural_sphere_face()
    g = BRepGraph()
    assert BRepGraphInc_Populate.Perform_s(g, face, False) != FAILED

    degenerate = 0
    for i in range(g.Topo().Edges().Nb()):
        eid = BRepGraph_EdgeId(i)
        if BRepGraph_Tool.Edge.Degenerated_s(g, eid):
            degenerate += 1
            assert not g.Topo().Edges().Definition(eid).Curve3DRepId.IsValid()
    assert degenerate >= 2

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_FaceId.Start_s())
    assert not recon.IsNull()
    assert count_degenerated_edges(recon) >= 2


def test_BRepGraphInc_PopulateRegressionTest_CompoundReferencesKeepDirectSourceLocationsAtEveryLevel():
    root_loc, inner_loc, solid_loc = nested_locations()
    moved_root = make_nested_compound(root_loc, inner_loc, solid_loc)

    g = BRepGraph()
    res = g.Shapes().Add(moved_root)
    assert res.IsOk()
    assert res.TopologyRoot.NodeKind == BRepGraph_NodeId.Kind.Compound
    assert res.Product.IsValid()

    product_rel = g.Topo().Products().Relations(res.Product)
    assert product_rel.OccurrenceRefIds.Size() == 1
    occ_ref = g.Refs().Occurrences().Entry(product_rel.OccurrenceRefIds.Value(0))
    assert occ_ref.LocalLocation.IsEqual(root_loc)

    root_compound = BRepGraph_CompoundId(res.TopologyRoot)
    root_refs = g.Topo().Compounds().Relations(root_compound).ChildRefIds
    assert root_refs.Size() == 1
    root_child_ref = root_refs.Value(0)
    assert g.Refs().Gen().LocalLocation(root_child_ref).IsEqual(inner_loc)

    inner_node = g.Refs().Children().Entry(root_child_ref).ChildNodeId
    assert inner_node.NodeKind == BRepGraph_NodeId.Kind.Compound
    inner_refs = g.Topo().Compounds().Relations(BRepGraph_CompoundId(inner_node)).ChildRefIds
    assert inner_refs.Size() == 1
    assert g.Refs().Gen().LocalLocation(inner_refs.Value(0)).IsEqual(solid_loc)


def test_BRepGraphInc_PopulateRegressionTest_ShapeViewFindNode_AcceptsOriginalPlacedSubshapes():
    root_loc, inner_loc, solid_loc = nested_locations()
    moved_root = make_nested_compound(root_loc, inner_loc, solid_loc)

    orig_solid = first_sub_shape(moved_root, TopAbs.TopAbs_SOLID)
    orig_face = first_sub_shape(moved_root, TopAbs.TopAbs_FACE)
    assert not orig_solid.IsNull()
    assert not orig_face.IsNull()

    g = BRepGraph()
    res = g.Shapes().Add(moved_root)
    assert res.IsOk()
    assert res.TopologyRoot.IsValid()
    assert res.Product.IsValid()

    assert g.Shapes().FindNode(moved_root) == res.TopologyRoot
    assert g.Shapes().FindNode(orig_solid).NodeKind == BRepGraph_NodeId.Kind.Solid
    assert g.Shapes().FindNode(orig_face).NodeKind == BRepGraph_NodeId.Kind.Face

    product_shape = g.Shapes().Shape(BRepGraph_NodeId(res.Product))
    assert not product_shape.IsNull()
    expect_box_near(geometry_bounds(product_shape), geometry_bounds(moved_root), 1.0e-6)
    expect_box_near(mesh_bounds(product_shape), mesh_bounds(moved_root), 1.0e-6)

    root_local = TopoDS_Shape(moved_root)
    root_local.Location(TopLoc_Location())
    topology_shape = g.Shapes().Shape(res.TopologyRoot)
    assert not topology_shape.IsNull()
    expect_box_near(geometry_bounds(topology_shape), geometry_bounds(root_local), 1.0e-6)


def test_BRepGraphInc_PopulateRegressionTest_Compact_PreservesAssemblyShapeLookupAndPlacement():
    root_loc, inner_loc, solid_loc = nested_locations()
    moved_root = make_nested_compound(root_loc, inner_loc, solid_loc)

    orig_solid = first_sub_shape(moved_root, TopAbs.TopAbs_SOLID)
    orig_face = first_sub_shape(moved_root, TopAbs.TopAbs_FACE)
    assert not orig_solid.IsNull()
    assert not orig_face.IsNull()

    g = BRepGraph()
    res = g.Shapes().Add(moved_root)
    assert res.IsOk()
    assert res.TopologyRoot.IsValid()
    assert res.Product.IsValid()

    no_product = BRepGraph.ShapesView.Options()
    no_product.CreateAutoProduct = False
    junk = g.Shapes().Add(BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape(), no_product)
    assert junk.IsOk()
    assert junk.TopologyRoot.IsValid()
    g.Editor().Gen().RemoveSubgraph(junk.TopologyRoot)

    compact = BRepGraph_Compact.Perform_s(g)
    assert compact.NbNodesBefore > compact.NbNodesAfter

    assert g.Shapes().FindNode(moved_root) == res.TopologyRoot
    assert g.Shapes().FindNode(orig_solid).NodeKind == BRepGraph_NodeId.Kind.Solid
    assert g.Shapes().FindNode(orig_face).NodeKind == BRepGraph_NodeId.Kind.Face

    root_compound = BRepGraph_CompoundId(g.Shapes().FindNode(moved_root))
    assert root_compound.IsValid()
    root_refs = g.Topo().Compounds().Relations(root_compound).ChildRefIds
    assert root_refs.Size() == 1
    assert g.Refs().Gen().LocalLocation(root_refs.Value(0)).IsEqual(inner_loc)

    inner_node = g.Refs().Children().Entry(root_refs.Value(0)).ChildNodeId
    assert inner_node.NodeKind == BRepGraph_NodeId.Kind.Compound
    inner_refs = g.Topo().Compounds().Relations(BRepGraph_CompoundId(inner_node)).ChildRefIds
    assert inner_refs.Size() == 1
    assert g.Refs().Gen().LocalLocation(inner_refs.Value(0)).IsEqual(solid_loc)

    root_local = TopoDS_Shape(moved_root)
    root_local.Location(TopLoc_Location())
    recon_root = BRepGraphInc_Reconstruct.Node_s(g, root_compound)
    assert not recon_root.IsNull()
    expect_box_near(geometry_bounds(recon_root), geometry_bounds(root_local), 1.0e-6)

    product_shape = g.Shapes().Shape(BRepGraph_NodeId(res.Product))
    assert not product_shape.IsNull()
    expect_box_near(geometry_bounds(product_shape), geometry_bounds(moved_root), 1.0e-6)


def test_BRepGraphInc_PopulateRegressionTest_Append_ReusesSameLocatedDefinitionAcrossCalls():
    box = BRepPrimAPI_MakeBox(2.0, 3.0, 4.0).Shape()
    moved_box = box.Moved(translation_location(5.0, 0.0, 0.0))

    g = BRepGraph()
    assert BRepGraphInc_Populate.Append_s(g, moved_box, False) != FAILED
    nb_solids = g.Topo().Solids().Nb()
    first_node = g.Shapes().FindNode(moved_box)
    assert first_node.IsValid()

    assert BRepGraphInc_Populate.Append_s(g, moved_box, False) != FAILED
    assert g.Topo().Solids().Nb() == nb_solids
    assert g.Shapes().FindNode(moved_box) == first_node

    second = box.Moved(translation_location(9.0, 0.0, 0.0))
    assert BRepGraphInc_Populate.Append_s(g, second, False) != FAILED
    assert g.Topo().Solids().Nb() == nb_solids + 1
    assert g.Shapes().FindNode(second) != first_node


def test_BRepGraphInc_PopulateRegressionTest_PersistentTriangulationBounds_AgreeWithMovedNodes():
    box = BRepPrimAPI_MakeBox(2.0, 3.0, 4.0).Shape()
    mesher = BRepMesh_IncrementalMesh(box, 0.2)
    assert mesher.IsDone()
    for face in TopExp_Explorer(box, TopAbs.TopAbs_FACE):
        tri = BRep_Tool.Triangulation_s(TopoDS.Face(face), TopLoc_Location())
        if tri is not None:
            tri.UpdateCachedMinMax()

    moved_box = box.Moved(translation_location(25.0, -3.0, 8.0))
    g = BRepGraph()
    assert BRepGraphInc_Populate.Perform_s(g, moved_box, False) != FAILED

    has_tri = False
    for i in range(g.Topo().Faces().Nb()):
        tri = g.Mesh().Persistent().Faces().Triangulation(BRepGraph_FaceId(i))
        if tri is None:
            continue
        has_tri = True
        assert not tri.HasCachedMinMax()
    assert has_tri

    recon = BRepGraphInc_Reconstruct.Node_s(g, BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()
    expect_box_near(mesh_bounds(recon), mesh_bounds(moved_box), 1.0e-6)


def test_BRepGraphInc_PopulateRegressionTest_Perform_ReplacesGraphThroughClearSemantics():
    g = BRepGraph()
    assert BRepGraphInc_Populate.Perform_s(g, BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape(), False) != FAILED

    layer = ensure_supplement(g)
    vertex = TopoDS_Vertex()
    BRep_Builder().MakeVertex(vertex, gp_Pnt(42.0, 0.0, 0.0), Precision.Confusion_s())
    solid_node = BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    assert (
        layer.AddAttachment(solid_node, BRepGraph_LayerTopoSupplement.AttachmentKind.SolidAuxShape, vertex) != 0
    )

    eid = BRepGraph_EdgeId.Start_s()
    g.Mesh().Editor().Edges().SetCachedPolygon3D(eid, Poly_Polygon3D(2, False))
    # Entry() returns a raw struct pointer (not bound); Has() is documented as "Entry() would return non-null"
    assert g.Mesh().Cache().Edges().Has(eid)

    assert BRepGraphInc_Populate.Perform_s(g, BRepPrimAPI_MakeBox(2.0, 2.0, 2.0).Shape(), False) != FAILED
    assert layer.AttachedTo(solid_node).IsEmpty()
    assert not g.Mesh().Cache().Edges().Has(eid)


def test_BRepGraphInc_PopulateRegressionTest_FlattenedTraversal_SkipsInternalExternalChildren():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)

    fwd = first_face_of_box(1.0)
    fwd.Orientation(TopAbs.TopAbs_FORWARD)
    internal = first_face_of_box(2.0)
    internal.Orientation(TopAbs.TopAbs_INTERNAL)
    external = first_face_of_box(3.0)
    external.Orientation(TopAbs.TopAbs_EXTERNAL)
    bb.Add(comp, fwd)
    bb.Add(comp, internal)
    bb.Add(comp, external)

    g = BRepGraph()
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = False
    opts.Flatten = True
    res = g.Shapes().Add(comp, opts)
    assert res.IsOk()
    assert g.Topo().Faces().Nb() == 1
    assert res.TopologyRoot.IsValid()
    assert res.TopologyRoot.NodeKind == BRepGraph_NodeId.Kind.Face
