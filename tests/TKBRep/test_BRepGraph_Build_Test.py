# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Build_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
)
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgesOfWire,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_NodeId,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_VertexId,
    BRepGraph_VertexIterator,
    BRepGraph_WireId,
    BRepGraph_WireIterator,
)
from nanocct.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeTorus,
    BRepPrimAPI_MakeWedge,
)
from nanocct.Geom import (
    Geom_ConicalSurface,
    Geom_CylindricalSurface,
    Geom_Plane,
    Geom_RectangularTrimmedSurface,
    Geom_SphericalSurface,
    Geom_ToroidalSurface,
)
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_IndexedMap
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX, TopAbs_WIRE
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Face, TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher

AddStatus = BRepGraph.ShapesView.AddStatus
Kind = BRepGraph_NodeId.Kind


def _map(shape, kind):
    m = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(shape, kind, m)
    return m


def count_unique(shape, kind):
    return _map(shape, kind).Extent()


def _graph(shape, opts=None):
    g = BRepGraph()
    g.Clear()
    if opts is None:
        g.Shapes().Add(shape)
    else:
        g.Shapes().Add(shape, opts)
    return g


def _flatten():
    # BRepGraph::ShapesView::Options{{}, false, true, false}
    o = BRepGraph.ShapesView.Options()
    o.CreateAutoProduct = False
    o.Flatten = True
    o.Parallel = False
    return o


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _face_ids(g):
    return _ids(BRepGraph_FaceIterator(g))


def _edge_ids(g):
    return _ids(BRepGraph_EdgeIterator(g))


def _surfaces(g):
    return [BRepGraph_Tool.Face.Surface_s(g, f) for f in _face_ids(g)]


def _check_all_counts(g, shape):
    t = g.Topo()
    assert t.Solids().Nb() == count_unique(shape, TopAbs_SOLID)
    assert t.Shells().Nb() == count_unique(shape, TopAbs_SHELL)
    assert t.Faces().Nb() == count_unique(shape, TopAbs_FACE)
    assert t.Wires().Nb() == count_unique(shape, TopAbs_WIRE)
    assert t.Edges().Nb() == count_unique(shape, TopAbs_EDGE)
    assert t.Vertices().Nb() == count_unique(shape, TopAbs_VERTEX)


def _check_fev_counts(g, shape):
    t = g.Topo()
    assert t.Faces().Nb() == count_unique(shape, TopAbs_FACE)
    assert t.Edges().Nb() == count_unique(shape, TopAbs_EDGE)
    assert t.Vertices().Nb() == count_unique(shape, TopAbs_VERTEX)


def _n_degenerated(g):
    return sum(1 for e in _edge_ids(g) if BRepGraph_Tool.Edge.Degenerated_s(g, e))


# Sphere


def test_BRepGraph_BuildTest_Sphere_IsNotEmpty():
    maker = BRepPrimAPI_MakeSphere(10.0)
    shape = maker.Shape()
    assert maker.IsDone()
    _graph(shape)


def test_BRepGraph_BuildTest_Sphere_DefCounts_MatchTopExp():
    shape = BRepPrimAPI_MakeSphere(10.0).Shape()
    _check_all_counts(_graph(shape), shape)


def test_BRepGraph_BuildTest_Sphere_SurfaceType():
    g = _graph(BRepPrimAPI_MakeSphere(5.0).Shape())
    assert g.Topo().Faces().Nb() >= 1
    assert any(isinstance(s, Geom_SphericalSurface) for s in _surfaces(g))


def test_BRepGraph_BuildTest_Sphere_HasDegenerateEdges():
    assert _n_degenerated(_graph(BRepPrimAPI_MakeSphere(8.0).Shape())) >= 1


# Cylinder


def test_BRepGraph_BuildTest_Cylinder_IsNotEmpty():
    maker = BRepPrimAPI_MakeCylinder(5.0, 20.0)
    shape = maker.Shape()
    assert maker.IsDone()
    _graph(shape)


def test_BRepGraph_BuildTest_Cylinder_DefCounts_MatchTopExp():
    shape = BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape()
    _check_fev_counts(_graph(shape), shape)


def test_BRepGraph_BuildTest_Cylinder_SurfaceType():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape())
    assert any(isinstance(s, Geom_CylindricalSurface) for s in _surfaces(g))


# Cone


def test_BRepGraph_BuildTest_Cone_IsNotEmpty():
    maker = BRepPrimAPI_MakeCone(10.0, 0.0, 15.0)
    shape = maker.Shape()
    assert maker.IsDone()
    _graph(shape)


def test_BRepGraph_BuildTest_Cone_DefCounts_MatchTopExp():
    shape = BRepPrimAPI_MakeCone(10.0, 0.0, 15.0).Shape()
    _check_fev_counts(_graph(shape), shape)


def test_BRepGraph_BuildTest_Cone_SurfaceType():
    g = _graph(BRepPrimAPI_MakeCone(10.0, 5.0, 15.0).Shape())
    assert any(isinstance(s, Geom_ConicalSurface) for s in _surfaces(g))


def test_BRepGraph_BuildTest_Cone_HasDegenerateEdge():
    assert _n_degenerated(_graph(BRepPrimAPI_MakeCone(10.0, 0.0, 15.0).Shape())) >= 1


# Torus


def test_BRepGraph_BuildTest_Torus_IsNotEmpty():
    maker = BRepPrimAPI_MakeTorus(20.0, 5.0)
    shape = maker.Shape()
    assert maker.IsDone()
    _graph(shape)


def test_BRepGraph_BuildTest_Torus_DefCounts_MatchTopExp():
    shape = BRepPrimAPI_MakeTorus(20.0, 5.0).Shape()
    _check_fev_counts(_graph(shape), shape)


def test_BRepGraph_BuildTest_Torus_SurfaceType():
    g = _graph(BRepPrimAPI_MakeTorus(20.0, 5.0).Shape())
    assert any(isinstance(s, Geom_ToroidalSurface) for s in _surfaces(g))


# Wedge


def test_BRepGraph_BuildTest_Wedge_IsNotEmpty():
    maker = BRepPrimAPI_MakeWedge(10.0, 10.0, 10.0, 5.0)
    shape = maker.Shape()
    assert maker.IsDone()
    _graph(shape)


def test_BRepGraph_BuildTest_Wedge_DefCounts_MatchTopExp():
    shape = BRepPrimAPI_MakeWedge(10.0, 10.0, 10.0, 5.0).Shape()
    _check_all_counts(_graph(shape), shape)


def test_BRepGraph_BuildTest_Wedge_AllPlanarSurfaces():
    g = _graph(BRepPrimAPI_MakeWedge(10.0, 10.0, 10.0, 5.0).Shape())
    for s in _surfaces(g):
        assert s is not None
        assert type(s) is Geom_Plane


# Compound builds


def _box_sphere_compound():
    b = BRep_Builder()
    c = TopoDS_Compound()
    b.MakeCompound(c)
    b.Add(c, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    b.Add(c, BRepPrimAPI_MakeSphere(5.0).Shape())
    return c


def test_BRepGraph_BuildTest_Compound_TwoPrimitives_IsNotEmpty():
    _graph(_box_sphere_compound())


def test_BRepGraph_BuildTest_Compound_TwoPrimitives_DefCountsAddUp():
    c = _box_sphere_compound()
    _check_fev_counts(_graph(c), c)


def test_BRepGraph_BuildTest_Compound_ThreeBoxes_DefCounts():
    b = BRep_Builder()
    c = TopoDS_Compound()
    b.MakeCompound(c)
    for i in range(3):
        b.Add(c, BRepPrimAPI_MakeBox(5.0 * (i + 1), 10.0, 10.0).Shape())
    g = _graph(c)
    assert g.Topo().Solids().Nb() == count_unique(c, TopAbs_SOLID)
    assert g.Topo().Faces().Nb() == count_unique(c, TopAbs_FACE)
    assert g.Topo().Edges().Nb() == count_unique(c, TopAbs_EDGE)


def test_BRepGraph_BuildTest_Compound_Nested_DefCounts():
    b = BRep_Builder()
    inner = TopoDS_Compound()
    b.MakeCompound(inner)
    b.Add(inner, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    outer = TopoDS_Compound()
    b.MakeCompound(outer)
    b.Add(outer, inner)
    b.Add(outer, BRepPrimAPI_MakeCylinder(3.0, 10.0).Shape())
    _check_fev_counts(_graph(outer), outer)


# Minimal shapes


def test_BRepGraph_BuildTest_SinglePlanarFace_HasWarnings():
    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(BRepBuilderAPI_MakeFace(gp_Pln()).Shape())
    assert res.IsOk()
    assert res.Status == AddStatus.SuccessWithWarnings


def test_BRepGraph_BuildTest_SinglePlanarFace_Counts():
    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(BRepBuilderAPI_MakeFace(gp_Pln()).Shape())
    assert res.IsOk()
    assert res.Status == AddStatus.SuccessWithWarnings


def test_BRepGraph_BuildTest_SingleEdge_HandlesGracefully():
    maker = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0))
    assert maker.IsDone()
    g = _graph(maker.Shape())
    assert g.Topo().Faces().Nb() == 0
    assert g.Topo().Solids().Nb() == 0


def test_BRepGraph_BuildTest_SingleVertex_HandlesGracefully():
    g = _graph(BRepBuilderAPI_MakeVertex(gp_Pnt(1.0, 2.0, 3.0)).Shape())
    assert g.Topo().Faces().Nb() == 0
    assert g.Topo().Edges().Nb() == 0


# Box cross-validation with TopExp


def _box():
    return BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()


def test_BRepGraph_BuildTest_Box_FaceDefCount_MatchesTopExp():
    box = _box()
    g = _graph(box)
    assert g.Topo().Faces().Nb() == count_unique(box, TopAbs_FACE)
    assert g.Topo().Faces().Nb() == 6


def test_BRepGraph_BuildTest_Box_EdgeDefCount_MatchesTopExp():
    box = _box()
    g = _graph(box)
    assert g.Topo().Edges().Nb() == count_unique(box, TopAbs_EDGE)
    assert g.Topo().Edges().Nb() == 12


def test_BRepGraph_BuildTest_Box_VertexDefCount_MatchesTopExp():
    box = _box()
    g = _graph(box)
    assert g.Topo().Vertices().Nb() == count_unique(box, TopAbs_VERTEX)
    assert g.Topo().Vertices().Nb() == 8


def test_BRepGraph_BuildTest_Box_VertexPoints_MatchBRepTool():
    box = _box()
    g = _graph(box)
    vmap = _map(box, TopAbs_VERTEX)
    assert g.Topo().Vertices().Nb() == vmap.Extent()
    pts = [BRep_Tool.Pnt_s(TopoDS.Vertex(vmap(i))) for i in range(1, vmap.Extent() + 1)]
    for vid in _ids(BRepGraph_VertexIterator(g)):
        p = BRepGraph_Tool.Vertex.Pnt_s(g, vid)
        assert any(p.Distance(q) < Precision.Confusion_s() for q in pts)


def test_BRepGraph_BuildTest_Box_FaceTolerances_MatchBRepTool():
    box = _box()
    g = _graph(box)
    fmap = _map(box, TopAbs_FACE)
    tols = [BRep_Tool.Tolerance_s(TopoDS.Face(fmap(i))) for i in range(1, fmap.Extent() + 1)]
    for fid in _face_ids(g):
        t = BRepGraph_Tool.Face.Tolerance_s(g, fid)
        assert any(abs(t - x) < Precision.Confusion_s() for x in tols)


def test_BRepGraph_BuildTest_Box_EdgeTolerances_MatchBRepTool():
    box = _box()
    g = _graph(box)
    emap = _map(box, TopAbs_EDGE)
    tols = [BRep_Tool.Tolerance_s(TopoDS.Edge(emap(i))) for i in range(1, emap.Extent() + 1)]
    for eid in _edge_ids(g):
        t = BRepGraph_Tool.Edge.Tolerance_s(g, eid)
        assert any(abs(t - x) < Precision.Confusion_s() for x in tols)


def test_BRepGraph_BuildTest_Box_AllSurfacesArePlanes():
    g = _graph(_box())
    assert g.Topo().Faces().Nb() == 6
    for s in _surfaces(g):
        assert s is not None
        assert type(s) is Geom_Plane


def test_BRepGraph_BuildTest_Box_NoDegenerateEdges():
    g = _graph(_box())
    for e in _edge_ids(g):
        assert not BRepGraph_Tool.Edge.Degenerated_s(g, e)


def test_BRepGraph_BuildTest_Box_EdgeVertexDefsAreValid():
    g = _graph(_box())
    for e in _edge_ids(g):
        start = BRepGraph_Tool.Edge.StartVertexId_s(g, e)
        end = BRepGraph_Tool.Edge.EndVertexId_s(g, e)
        assert start.IsValid()
        assert end.IsValid()
        assert BRepGraph_NodeId(g.Refs().Vertices().Entry(start).ChildVertexId).NodeKind == Kind.Vertex
        assert BRepGraph_NodeId(g.Refs().Vertices().Entry(end).ChildVertexId).NodeKind == Kind.Vertex


def test_BRepGraph_BuildTest_Box_FaceSurfacesAreValid():
    g = _graph(_box())
    for f in _face_ids(g):
        assert BRepGraph_Tool.Face.HasSurface_s(g, f)


def test_BRepGraph_BuildTest_Box_EdgeParamRange_IsNonDegenerate():
    g = _graph(_box())
    for e in _edge_ids(g):
        first, last = BRepGraph_Tool.Edge.Range_s(g, e)
        assert first < last


def test_BRepGraph_BuildTest_AddFlatten_OnEmptyGraph_BuildsFlattenedGraph():
    g = BRepGraph()
    g.Shapes().Add(_box(), _flatten())
    assert g.Topo().Solids().Nb() == 0
    assert g.Topo().Shells().Nb() == 0
    assert g.Topo().Faces().Nb() == 6
    n = g.Topo().Faces().Nb()
    for i in range(n):
        fid = BRepGraph_FaceId(i)
        assert fid.IsValid(n)
        assert not g.Topo().Gen().IsRemoved(fid)
    assert g.Editor().ValidateMutationBoundary()


def test_BRepGraph_BuildTest_Build_MutationBoundary_IsValid():
    g = _graph(_box())
    assert g.Editor().ValidateMutationBoundary()


def _first_face(shape):
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    assert exp.More()
    return TopoDS.Face(exp.Current())


def test_BRepGraph_BuildTest_AddFlatten_SameFaceTwice_DedupsDefinition():
    face = _first_face(_box())
    g = BRepGraph()
    g.Shapes().Add(face, _flatten())
    g.Shapes().Add(face, _flatten())
    assert g.Topo().Faces().Nb() == 1


def test_BRepGraph_BuildTest_AddFlatten_AfterBuild_DoesNotCreateNewSolidDefs():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    solids = g.Topo().Solids().Nb()
    faces = g.Topo().Faces().Nb()
    g.Shapes().Add(BRepPrimAPI_MakeBox(15.0, 25.0, 35.0).Shape(), _flatten())
    assert g.Topo().Solids().Nb() == solids
    assert g.Topo().Faces().Nb() == faces + 6
    assert g.RootProductIds().Size() == 1
    assert g.Editor().ValidateMutationBoundary()


def test_BRepGraph_BuildTest_AddFull_MutationBoundary_IsValid():
    g = _graph(_box())
    g.Shapes().Add(BRepPrimAPI_MakeSphere(5.0).Shape())
    assert g.Editor().ValidateMutationBoundary()


def test_BRepGraph_BuildTest_AddFlatten_AppendedFaceHasNoParentShell():
    g = BRepGraph()
    g.Shapes().Add(_first_face(_box()), _flatten())
    assert g.Topo().Faces().Nb() == 1
    assert g.Topo().Shells().Nb() == 0


def test_BRepGraph_BuildTest_AddFlatten_PreservesExistingUIDs():
    g = _graph(_box())
    assert g.Topo().Edges().Nb() > 0
    orig = g.UIDs().Of(BRepGraph_EdgeId.Start_s())
    assert orig.IsValid()
    g.Shapes().Add(BRepPrimAPI_MakeSphere(5.0).Shape(), _flatten())
    assert g.UIDs().Of(BRepGraph_EdgeId.Start_s()) == orig


def test_BRepGraph_BuildTest_AddFlatten_StandaloneVertex_AppendsIntoNonEmptyGraph():
    g = _graph(_box())
    before = g.Topo().Vertices().Nb()
    vshape = BRepBuilderAPI_MakeVertex(gp_Pnt(100.0, 0.0, 0.0)).Shape()
    g.Shapes().Add(vshape, _flatten())
    assert g.Topo().Vertices().Nb() == before + 1
    assert g.Shapes().FindNode(vshape).IsValid()
    assert not g.Shapes().Shape(BRepGraph_VertexId(before)).IsNull()


def test_BRepGraph_BuildTest_AddFlatten_StandaloneEdge_AppendsIntoNonEmptyGraph():
    g = _graph(_box())
    before = g.Topo().Edges().Nb()
    eshape = BRepBuilderAPI_MakeEdge(gp_Pnt(100.0, 0.0, 0.0), gp_Pnt(120.0, 0.0, 0.0)).Shape()
    g.Shapes().Add(eshape, _flatten())
    assert g.Topo().Edges().Nb() == before + 1
    assert g.Shapes().FindNode(eshape).IsValid()
    assert not g.Shapes().Shape(BRepGraph_EdgeId(before)).IsNull()


def test_BRepGraph_BuildTest_AddFlatten_StandaloneWire_AppendsIntoNonEmptyGraph():
    g = _graph(_box())
    before = g.Topo().Wires().Nb()
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0)).Shape()
    wshape = BRepBuilderAPI_MakeWire(TopoDS.Edge(edge)).Shape()
    g.Shapes().Add(wshape, _flatten())
    assert g.Topo().Wires().Nb() == before + 1
    assert g.Shapes().FindNode(wshape).IsValid()
    assert not g.Shapes().Shape(BRepGraph_WireId(before)).IsNull()


def test_BRepGraph_BuildTest_AddFlatten_CompoundWithStandaloneShapes():
    g = _graph(_box())
    b = BRep_Builder()
    c = TopoDS_Compound()
    b.MakeCompound(c)
    b.Add(c, BRepBuilderAPI_MakeVertex(gp_Pnt(50.0, 0.0, 0.0)).Shape())
    b.Add(c, BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0)).Shape())
    nv = g.Topo().Vertices().Nb()
    ne = g.Topo().Edges().Nb()
    g.Shapes().Add(c, _flatten())
    assert g.Topo().Vertices().Nb() > nv
    assert g.Topo().Edges().Nb() > ne


def test_BRepGraph_BuildTest_Build_BasicQueriesAndAlgorithmsWork():
    opts = BRepGraph.ShapesView.Options()
    opts.Parallel = False
    g = _graph(_box(), opts)
    assert g.Topo().Faces().Nb() == 6
    assert g.Topo().Edges().Nb() == 12
    assert g.Topo().Vertices().Nb() == 8


def test_BRepGraph_BuildTest_RootProductIds_Box_ReturnsOneProduct():
    g = _graph(_box())
    roots = g.RootProductIds()
    assert roots.Size() == 1
    root = roots.Value(0)
    assert root.IsValid()
    shape_root = g.Topo().Products().ShapeRoot(root)
    assert shape_root.IsValid()
    assert shape_root.NodeKind == Kind.Solid


def test_BRepGraph_BuildTest_BuildOptions_DisableAutoProduct_DoesNotCreateProducts():
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = False
    opts.Parallel = False
    g = _graph(_box(), opts)
    assert g.Topo().Products().Nb() == 0
    assert g.RootProductIds().Size() == 0
    assert g.Topo().Solids().Nb() == 1


def test_BRepGraph_BuildTest_RootProductIds_AddFlatten_ProductCountUnchanged():
    g = _graph(_box())
    assert g.RootProductIds().Size() == 1
    faces = g.Topo().Faces().Nb()
    g.Shapes().Add(_first_face(BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape()), _flatten())
    roots = g.RootProductIds()
    assert roots.Size() == 1
    assert g.Topo().Faces().Nb() == faces + 1
    assert roots.Value(0).IsValid()


# Natural-bound populate normalization


def _no_wire_natural_face(surface):
    b = BRep_Builder()
    f = TopoDS_Face()
    b.MakeFace(f, surface, Precision.Confusion_s())
    b.NaturalRestriction(f, True)
    return f


def _expect_synthesized(surface):
    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(_no_wire_natural_face(surface))
    assert res.IsOk()
    assert g.Topo().Faces().Nb() == 1
    assert BRepGraph_Tool.Face.NbWires_s(g, BRepGraph_FaceId.Start_s()) > 0
    assert g.Topo().Wires().Nb() > 0
    assert g.Topo().Edges().Nb() > 0
    assert g.Topo().Vertices().Nb() > 0


def test_BRepGraph_BuildTest_NaturalBound_FiniteNoWireNaturalFaces_SynthesizeTopology():
    ax = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    _expect_synthesized(Geom_SphericalSurface(ax, 10.0))
    _expect_synthesized(Geom_ToroidalSurface(ax, 10.0, 3.0))
    _expect_synthesized(
        Geom_RectangularTrimmedSurface(Geom_CylindricalSurface(ax, 5.0), 0.0, 2.0 * math.pi, 0.0, 10.0, True, True)
    )
    _expect_synthesized(
        Geom_RectangularTrimmedSurface(Geom_ConicalSurface(ax, 0.2, 5.0), 0.0, 2.0 * math.pi, 0.0, 10.0, True, True)
    )
    _expect_synthesized(
        Geom_RectangularTrimmedSurface(Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 0.0, 3.0, 0.0, 4.0, True, True)
    )


def _all_faces_have_wires(shape):
    g = _graph(shape)
    assert g.Topo().Faces().Nb() >= 1
    for f in _face_ids(g):
        assert BRepGraph_Tool.Face.NbWires_s(g, f) > 0
    return g


def test_BRepGraph_BuildTest_NaturalBound_Sphere_HasWiresAndEdges():
    maker = BRepPrimAPI_MakeSphere(10.0)
    shape = maker.Shape()
    assert maker.IsDone()
    g = _all_faces_have_wires(shape)
    assert g.Topo().Wires().Nb() > 0
    assert g.Topo().Edges().Nb() > 0
    assert g.Topo().Vertices().Nb() > 0


def test_BRepGraph_BuildTest_NaturalBound_Cylinder_HasWiresAndEdges():
    _all_faces_have_wires(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())


def test_BRepGraph_BuildTest_NaturalBound_Cone_HasWiresAndEdges():
    _all_faces_have_wires(BRepPrimAPI_MakeCone(5.0, 2.0, 10.0).Shape())


def test_BRepGraph_BuildTest_NaturalBound_Torus_HasWiresAndEdges():
    _all_faces_have_wires(BRepPrimAPI_MakeTorus(10.0, 3.0).Shape())


def test_BRepGraph_BuildTest_NaturalBound_InfinitePlane_ProducesWarnings():
    face = _no_wire_natural_face(Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)))
    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(face)
    assert res.IsOk()
    assert res.Status == AddStatus.SuccessWithWarnings
    assert not g.IsEmpty()
    assert g.Topo().Faces().NbActive() == 1
    fid = BRepGraph_FaceId.Start_s()
    assert BRepGraph_Tool.Face.NbWires_s(g, fid) == 0
    audit = BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s())
    assert audit.IsValid()
    assert audit.NbIssues(BRepGraph_Validate.Severity.Error) == 0
    assert audit.NbIssues(BRepGraph_Validate.Severity.Warning) == 1
    assert not g.Shapes().Reconstruct(fid).IsNull()


def test_BRepGraph_BuildTest_NaturalBound_PreservesExplicitWires():
    maker = BRepPrimAPI_MakeSphere(10.0)
    shape = maker.Shape()
    assert maker.IsDone()
    g = _graph(shape)
    assert g.Topo().Wires().Nb() > 0
    assert g.Topo().Edges().Nb() > 0
    assert g.Topo().Vertices().Nb() > 0


def test_BRepGraph_BuildTest_NaturalBound_PlaneSynthesis_SkipsPCurves():
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    trimmed = Geom_RectangularTrimmedSurface(plane, -10.0, 10.0, -10.0, 10.0, False, False)
    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(_no_wire_natural_face(trimmed))
    assert res.IsOk()
    assert g.Topo().Wires().Nb() > 0
    assert g.Topo().Edges().Nb() > 0
    for wid in _ids(BRepGraph_WireIterator(g)):
        for ce in _ids(BRepGraph_CoEdgesOfWire(g, wid)):
            assert not BRepGraph_Tool.CoEdge.HasPCurve_s(g, ce)
            adaptor = BRepGraph_Tool.CoEdge.PCurveAdaptor_s(g, ce)
            assert adaptor.IsInitialized()
