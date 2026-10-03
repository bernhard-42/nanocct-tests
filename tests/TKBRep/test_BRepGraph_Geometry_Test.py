# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Geometry_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CacheDerivedState,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgeIterator,
    BRepGraph_CompoundId,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_NodeId,
    BRepGraph_ParentExplorer,
    BRepGraph_ShellIterator,
    BRepGraph_SolidIterator,
    BRepGraph_Tool,
    BRepGraph_VertexIterator,
    BRepGraph_WireId,
    BRepGraph_WireIterator,
)
from nanocct.BRepGraphInc import BRepGraph_EdgeCurve3DRepId, BRepGraph_FaceSurfaceRepId, BRepGraph_RepId
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.Geom import Geom_Plane
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp_Dir2d, gp_Pln, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Poly import Poly_Polygon2D, Poly_Polygon3D, Poly_PolygonOnTriangulation, Poly_Triangulation
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound

PCONF = Precision.PConfusion_s()


# ---------- helpers ----------


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _box(dx=10.0, dy=20.0, dz=30.0):
    return _graph(BRepPrimAPI_MakeBox(dx, dy, dz).Shape())


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _count(it):
    n = 0
    while it.More():
        it.Current()
        n += 1
        it.Next()
    return n


def _topabs(parity):
    if parity.IsReversed:
        return TopAbs_REVERSED
    return TopAbs_FORWARD


def _edge_same_parameter(g, eid):
    for ceid in g.Topo().Edges().Relations(eid).CoEdgeIds:
        if not BRepGraph_Tool.CoEdge.SameParameter_s(g, ceid):
            return False
    return True


def _edge_same_range(g, eid):
    for ceid in g.Topo().Edges().Relations(eid).CoEdgeIds:
        if not BRepGraph_Tool.CoEdge.SameRange_s(g, ceid):
            return False
    return True


def _component_root_of_face(g, fid):
    node = BRepGraph_NodeId(fid)
    exp = BRepGraph_ParentExplorer(g, node, BRepGraph_NodeId.Kind.Solid)
    if exp.More():
        return exp.Current().DefId
    exp = BRepGraph_ParentExplorer(g, node, BRepGraph_NodeId.Kind.Shell)
    if exp.More():
        return exp.Current().DefId
    return node


def _face_counts_by_component(g):
    counts = {}
    for fid in _ids(BRepGraph_FaceIterator(g)):
        root = _component_root_of_face(g, fid)
        key = (root.Index, root.NodeKind)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _collect_same_domain_faces(g, fid):
    surf = BRepGraph_Tool.Face.Surface_s(g, fid)
    if surf is None:
        return []
    out = []
    for other in _ids(BRepGraph_FaceIterator(g)):
        if other != fid and BRepGraph_Tool.Face.Surface_s(g, other) is surf:
            out.append(other)
    return out


def _two_box_compound(box2):
    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    b.Add(comp, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    b.Add(comp, box2)
    return comp


def _separated_two_boxes():
    return _graph(_two_box_compound(BRepPrimAPI_MakeBox(gp_Pnt(50.0, 50.0, 50.0), 60.0, 60.0, 60.0).Shape()))


# ---------- Geometry navigation ----------


def test_BRepGraph_GeometryTest_Sphere_AllFaces_SameSurface():
    g = _graph(BRepPrimAPI_MakeSphere(15.0).Shape())
    assert g.Topo().Faces().Nb() >= 1
    assert BRepGraph_Tool.Face.HasSurface_s(g, BRepGraph_FaceId.Start_s())
    first = BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId.Start_s())
    assert first is not None
    for fid in _ids(BRepGraph_FaceIterator(g)):
        if fid.Index == 0:
            continue
        assert BRepGraph_Tool.Face.HasSurface_s(g, fid)
        assert BRepGraph_Tool.Face.Surface_s(g, fid) is first


def test_BRepGraph_GeometryTest_Sphere_AllFacesShareSurface():
    g = _graph(BRepPrimAPI_MakeSphere(15.0).Shape())
    assert BRepGraph_Tool.Face.HasSurface_s(g, BRepGraph_FaceId.Start_s())
    first = BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId.Start_s())
    assert first is not None
    same = 0
    for fid in _ids(BRepGraph_FaceIterator(g)):
        if BRepGraph_Tool.Face.HasSurface_s(g, fid) and BRepGraph_Tool.Face.Surface_s(g, fid) is first:
            same += 1
    assert same == g.Topo().Faces().Nb()


def test_BRepGraph_GeometryTest_Box_Curve3d_ValidForAll12Edges():
    g = _box()
    assert g.Topo().Edges().Nb() == 12
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        assert BRepGraph_Tool.Edge.HasCurve_s(g, eid)


def test_BRepGraph_GeometryTest_Box_AllEdgesHaveCurve3d():
    g = _box()
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        assert BRepGraph_Tool.Edge.HasCurve_s(g, eid)


def test_BRepGraph_GeometryTest_Box_FindPCurveCoEdgeId_AllEdgeFacePairs_Valid():
    g = _box()
    n = 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ceid in g.Topo().Edges().CoEdges(eid):
            ce = g.Topo().CoEdges().Definition(ceid)
            assert BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, BRepGraph_FaceId(ce.FaceId)).IsValid()
            n += 1
    assert n > 0


def test_BRepGraph_GeometryTest_CoEdge_FaceIdValid():
    g = _box()
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        vec = g.Topo().Edges().CoEdges(eid)
        for j in range(vec.Size()):
            ce = g.Topo().CoEdges().Definition(vec.Value(j))
            assert ce.FaceId.IsValid()
            assert BRepGraph_NodeId(ce.FaceId).NodeKind == BRepGraph_NodeId.Kind.Face


def test_BRepGraph_GeometryTest_CoEdge_ParamRange_NonZero():
    g = _box()
    n = 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        vec = g.Topo().Edges().CoEdges(eid)
        for j in range(vec.Size()):
            first, last = BRepGraph_Tool.CoEdge.Range_s(g, vec.Value(j))
            assert abs(last - first) > PCONF
            n += 1
    assert n > 0


def test_BRepGraph_GeometryTest_SetPCurveTwoArgPreservesExistingRange():
    g = _box()
    ceid = BRepGraph_CoEdgeId()
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        vec = g.Topo().Edges().CoEdges(eid)
        if not vec.IsEmpty():
            ceid = vec.First()
            break
    assert ceid.IsValid()
    before = BRepGraph_Tool.CoEdge.Range_s(g, ceid)
    replacement = Geom2d_Line(gp_Pnt2d(100.0, 200.0), gp_Dir2d(1.0, 0.0))
    g.Editor().CoEdges().SetPCurve(ceid, replacement)
    after = BRepGraph_Tool.CoEdge.Range_s(g, ceid)
    assert abs(after[0] - before[0]) <= PCONF
    assert abs(after[1] - before[1]) <= PCONF
    assert BRepGraph_Tool.CoEdge.PCurve_s(g, ceid) is replacement


def test_BRepGraph_GeometryTest_FaceDef_Surface_IsNotNull():
    g = _box()
    for fid in _ids(BRepGraph_FaceIterator(g)):
        assert BRepGraph_Tool.Face.HasSurface_s(g, fid)


def test_BRepGraph_GeometryTest_EdgeDef_Curve3d_IsNotNull():
    g = _box()
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        assert BRepGraph_Tool.Edge.HasCurve_s(g, eid)


def test_BRepGraph_GeometryTest_SameDomainFaces_SimpleBox_Empty():
    g = _box()
    for fid in _ids(BRepGraph_FaceIterator(g)):
        assert len(_collect_same_domain_faces(g, fid)) == 0


def test_BRepGraph_GeometryTest_SameDomainFaces_SharedSurfaceAcrossOwnedUses():
    g = BRepGraph()
    g.Clear()
    surface = Geom_Plane(gp_Pln())
    inner = NCollection_Array1[BRepGraph_WireId]()
    fa = g.Editor().Faces().Add(surface, BRepGraph_WireId(), inner, 1.0e-7)
    fb = g.Editor().Faces().Add(surface, BRepGraph_WireId(), inner, 1.0e-7)
    assert fa.IsValid()
    assert fb.IsValid()
    assert g.Topo().Faces().Definition(fa).SurfaceRepId != g.Topo().Faces().Definition(fb).SurfaceRepId
    assert _collect_same_domain_faces(g, fa) == [fb]
    assert _collect_same_domain_faces(g, fb) == [fa]


def test_BRepGraph_GeometryTest_CompoundWithMovedChild_SharedSolidDef():
    box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(100.0, 0.0, 0.0))
    moved = box.Moved(TopLoc_Location(trsf))
    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    b.Add(comp, box)
    b.Add(comp, moved)

    g = BRepGraph()
    g.Clear()
    res = g.Shapes().Add(comp)
    assert res.IsOk()
    assert not g.IsEmpty()
    assert g.Topo().Solids().Nb() == 1
    cid = BRepGraph_CompoundId(res.TopologyRoot)
    child_refs = g.Topo().Compounds().Relations(cid).ChildRefIds
    assert child_refs.Size() == 2
    assert g.Refs().Gen().LocalLocation(child_refs.Value(0)).IsIdentity()
    assert not g.Refs().Gen().LocalLocation(child_refs.Value(1)).IsIdentity()


def test_BRepGraph_GeometryTest_FaceDef_Triangulation_NullForAnalyticNoCrash():
    g = _box()
    for fid in _ids(BRepGraph_FaceIterator(g)):
        assert not g.Mesh().Effective().Faces().Has(fid)


# ---------- Definition traversal ----------


def test_BRepGraph_GeometryTest_SolidDef_CountMatchesNb():
    g = _box(10.0, 10.0, 10.0)
    assert _count(BRepGraph_SolidIterator(g)) == g.Topo().Solids().Nb()


def test_BRepGraph_GeometryTest_ShellDef_CountMatchesNb():
    g = _box(10.0, 10.0, 10.0)
    assert _count(BRepGraph_ShellIterator(g)) == g.Topo().Shells().Nb()


def test_BRepGraph_GeometryTest_FaceDef_CountMatchesNb():
    g = _box(10.0, 10.0, 10.0)
    assert _count(BRepGraph_FaceIterator(g)) == g.Topo().Faces().Nb()


def test_BRepGraph_GeometryTest_WireDef_CountMatchesNb():
    g = _box(10.0, 10.0, 10.0)
    assert _count(BRepGraph_WireIterator(g)) == g.Topo().Wires().Nb()


def test_BRepGraph_GeometryTest_EdgeDef_CountMatchesNb():
    g = _box(10.0, 10.0, 10.0)
    assert _count(BRepGraph_EdgeIterator(g)) == g.Topo().Edges().Nb()


def test_BRepGraph_GeometryTest_VertexDef_CountMatchesNb():
    g = _box(10.0, 10.0, 10.0)
    assert _count(BRepGraph_VertexIterator(g)) == g.Topo().Vertices().Nb()


def test_BRepGraph_GeometryTest_FaceDef_CountViaIterator_MatchesNb():
    g = _box(10.0, 10.0, 10.0)
    assert sum(1 for _ in BRepGraph_FaceIterator(g)) == g.Topo().Faces().Nb()


def test_BRepGraph_GeometryTest_FaceDef_AllSurfacesNonNull():
    g = _box(10.0, 10.0, 10.0)
    n = 0
    for fid in _ids(BRepGraph_FaceIterator(g)):
        assert BRepGraph_Tool.Face.HasSurface_s(g, fid)
        n += 1
    assert n == g.Topo().Faces().Nb()


def test_BRepGraph_GeometryTest_EdgeDef_AllCurves3dNonNull():
    g = _box(10.0, 10.0, 10.0)
    n = 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        if not BRepGraph_Tool.Edge.Degenerated_s(g, eid):
            assert BRepGraph_Tool.Edge.HasCurve_s(g, eid)
        n += 1
    assert n == g.Topo().Edges().Nb()


def test_BRepGraph_GeometryTest_AllCoEdgesHaveCurve2d():
    g = _box(10.0, 10.0, 10.0)
    n = 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ceid in g.Topo().Edges().CoEdges(eid):
            assert BRepGraph_Tool.CoEdge.HasPCurve_s(g, ceid)
            n += 1
    assert n > 0


def test_BRepGraph_GeometryTest_CoEdgePCurveAdaptor_FallsBackOnPlaneWhenStoredPCurveRemoved():
    g = _box(10.0, 10.0, 10.0)
    ceid = BRepGraph_CoEdgeId()
    eid = BRepGraph_EdgeId()
    for candidate in _ids(BRepGraph_EdgeIterator(g)):
        vec = g.Topo().Edges().CoEdges(candidate)
        if vec.Size() == 0:
            continue
        ceid = vec.Value(0)
        eid = candidate
        break
    assert ceid.IsValid()
    assert BRepGraph_Tool.CoEdge.PCurve_s(g, ceid) is not None

    g.Editor().CoEdges().SetPCurve(ceid, None)
    assert BRepGraph_Tool.CoEdge.PCurve_s(g, ceid) is None

    adaptor = BRepGraph_Tool.CoEdge.PCurveAdaptor_s(g, ceid)
    assert adaptor.IsInitialized()
    assert not BRepGraph_Tool.CoEdge.HasPCurve_s(g, ceid)
    first, last = BRepGraph_Tool.Edge.Range_s(g, eid)
    assert abs(adaptor.FirstParameter() - first) <= PCONF
    assert abs(adaptor.LastParameter() - last) <= PCONF


# ---------- Connected components via ParentExplorer ----------


def test_BRepGraph_GeometryTest_ConnectedComponents_SingleBox_OneComponent():
    counts = _face_counts_by_component(_box(10.0, 10.0, 10.0))
    assert len(counts) == 1
    assert list(counts.values()) == [6]


def test_BRepGraph_GeometryTest_ConnectedComponents_TwoBoxCompound_TwoComponents():
    assert len(_face_counts_by_component(_separated_two_boxes())) == 2


def test_BRepGraph_GeometryTest_ConnectedComponents_TwoBoxCompound_FacesGroupedPerRoot():
    counts = _face_counts_by_component(_separated_two_boxes())
    assert len(counts) == 2
    for c in counts.values():
        assert c == 6


def test_BRepGraph_GeometryTest_ConnectedComponents_TwoBoxCompound_CoverAllFaces():
    g = _separated_two_boxes()
    assert sum(_face_counts_by_component(g).values()) == g.Topo().Faces().Nb()


# ---------- SameParameter / SameRange ----------


def test_BRepGraph_GeometryTest_Box_EdgeDef_SameParameter_IsSet():
    g = _box()
    assert g.Topo().Edges().Nb() > 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        assert _edge_same_parameter(g, eid)


def test_BRepGraph_GeometryTest_Box_EdgeDef_SameRange_IsSet():
    g = _box()
    assert g.Topo().Edges().Nb() > 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        assert _edge_same_range(g, eid)


def test_BRepGraph_GeometryTest_DerivedStateCache_LazyAndFreshAfterPCurveRangeMutation():
    g = _box()
    guid = BRepGraph_CacheDerivedState.GetID_s()
    assert g.CacheRegistry().FindCache(guid) is None

    eid = BRepGraph_EdgeId()
    ceid = BRepGraph_CoEdgeId()
    nb_edges = g.Topo().Edges().Nb()
    for cand_ce in _ids(BRepGraph_CoEdgeIterator(g)):
        cand_e = g.Topo().CoEdges().Definition(cand_ce).ChildEdgeId
        if (
            cand_e.IsValid(nb_edges)
            and not cand_e.IsRemoved(g)
            and BRepGraph_Tool.Edge.Curve_s(g, cand_e) is not None
            and BRepGraph_Tool.CoEdge.PCurve_s(g, cand_ce) is not None
        ):
            eid = cand_e
            ceid = cand_ce
            break
    assert eid.IsValid(nb_edges)
    assert ceid.IsValid(g.Topo().CoEdges().Nb())

    assert _edge_same_range(g, eid)
    assert g.CacheRegistry().FindCache(guid) is not None

    first, last = BRepGraph_Tool.Edge.Range_s(g, eid)
    g.Editor().CoEdges().SetParamRange(ceid, first + 1.0, last)
    assert not _edge_same_range(g, eid)
    assert not _edge_same_parameter(g, eid)


# ---------- Seam edges ----------


def test_BRepGraph_GeometryTest_Cylinder_SeamEdge_HasTwoCoEdges():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape())
    found = False
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ceid in g.Topo().Edges().CoEdges(eid):
            pair = BRepGraph_Tool.CoEdge.SeamPair_s(g, ceid)
            if pair.IsValid():
                ce = g.Topo().CoEdges().Definition(ceid)
                pe = g.Topo().CoEdges().Definition(pair)
                assert ce.Orientation.IsReversed != pe.Orientation.IsReversed
                assert ce.FaceId == pe.FaceId
                found = True
                break
        if found:
            break
    assert found


def _check_seam_orientations(g):
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ceid in g.Topo().Edges().CoEdges(eid):
            if not BRepGraph_Tool.CoEdge.IsSeam_s(g, ceid):
                continue
            fid = BRepGraph_FaceId(g.Topo().CoEdges().Definition(ceid).FaceId.Index)
            fwd = BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, fid, TopAbs_FORWARD)
            rev = BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, fid, TopAbs_REVERSED)
            assert fwd.IsValid()
            assert rev.IsValid()
            assert fwd != rev
            return True
    return False


def test_BRepGraph_GeometryTest_Cylinder_SeamEdge_FindPCurveCoEdgeId_WithOrientation():
    assert _check_seam_orientations(_graph(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape()))


def test_BRepGraph_GeometryTest_Box_FindPCurveCoEdgeId_MatchesCoEdge():
    g = _box()
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ceid in g.Topo().Edges().CoEdges(eid):
            ce = g.Topo().CoEdges().Definition(ceid)
            found = BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, ce.FaceId, _topabs(ce.Orientation))
            assert found == ceid


def test_BRepGraph_GeometryTest_Cylinder_SeamEdge_FindPCurveCoEdgeId_DistinguishesOrientation():
    assert _check_seam_orientations(_graph(BRepPrimAPI_MakeCylinder(5.0, 20.0).Shape()))


# ---------- Representation layer ----------


def test_BRepGraph_GeometryTest_Box_RepCounts_MatchTopology():
    g = _box()
    geo = g.Topo().Geometry()
    assert geo.NbFaceSurfaces() > 0
    assert geo.NbEdgeCurves3D() > 0
    assert geo.NbCoEdgeCurves2D() > 0
    for fid in _ids(BRepGraph_FaceIterator(g)):
        assert BRepGraph_Tool.Face.HasSurface_s(g, fid)
        assert BRepGraph_Tool.Face.Surface_s(g, fid) is not None
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        if not BRepGraph_Tool.Edge.Degenerated_s(g, eid) and BRepGraph_Tool.Edge.HasCurve_s(g, eid):
            assert BRepGraph_Tool.Edge.Curve_s(g, eid) is not None
    it = BRepGraph_CoEdgeIterator(g)
    while it.More():
        if it.Current().Curve2DRepId.IsValid():
            assert BRepGraph_Tool.CoEdge.PCurve_s(g, it.CurrentId()) is not None
        it.Next()


def test_BRepGraph_GeometryTest_Sphere_SurfaceDedup_SharedHandle():
    g = _graph(BRepPrimAPI_MakeSphere(15.0).Shape())
    nb = g.Topo().Faces().Nb()
    if nb > 1:
        first = BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId.Start_s())
        for i in range(1, nb):
            assert BRepGraph_Tool.Face.Surface_s(g, BRepGraph_FaceId(i)) is first


def test_BRepGraph_GeometryTest_Cylinder_TriangulationReps_Populated():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape())
    it = BRepGraph_FaceIterator(g)
    while it.More():
        face = it.Current()
        fid = it.CurrentId()
        if face.TriangulationRepId.IsValid():
            if g.Mesh().Effective().Faces().Has(fid):
                assert g.Mesh().Effective().Faces().Triangulation(fid) is not None
        it.Next()


def test_BRepGraph_GeometryTest_RepId_FactoryMethods():
    surf_id = BRepGraph_FaceSurfaceRepId(42)
    assert BRepGraph_RepId(surf_id).RepKind == BRepGraph_RepId.Kind.FaceSurface
    assert surf_id.Index == 42
    assert surf_id.IsValid()

    curve_id = BRepGraph_EdgeCurve3DRepId(7)
    assert BRepGraph_RepId(curve_id).RepKind == BRepGraph_RepId.Kind.EdgeCurve3D
    assert curve_id.Index == 7

    assert not BRepGraph_RepId().IsValid()
    assert surf_id == BRepGraph_FaceSurfaceRepId(42)
    assert BRepGraph_RepId(surf_id) != BRepGraph_RepId(curve_id)


def test_BRepGraph_GeometryTest_RepId_UntypedArithmetic_PreservesKindAndIndex():
    K = BRepGraph_RepId.Kind
    base = BRepGraph_RepId(K.EdgeCurve3D, 5)
    assert base.RepKind == K.EdgeCurve3D
    assert base.Index == 5
    assert base == BRepGraph_RepId(K.EdgeCurve3D, 5)
    different = BRepGraph_RepId(K.EdgeCurve3D, 9)
    assert base != different
    assert base < different
    assert base != BRepGraph_RepId(K.FaceSurface, 5)


def test_BRepGraph_GeometryTest_Compound_TwoBoxes_SurfaceDedup():
    g = _graph(_two_box_compound(BRepPrimAPI_MakeBox(20.0, 20.0, 20.0).Shape()))
    assert g.Topo().Faces().Nb() == 12
    assert g.Topo().Geometry().NbFaceSurfaces() > 0
    assert g.Topo().Geometry().NbFaceSurfaces() <= 12
    for fid in _ids(BRepGraph_FaceIterator(g)):
        assert BRepGraph_Tool.Face.HasSurface_s(g, fid)
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        if not BRepGraph_Tool.Edge.Degenerated_s(g, eid) and BRepGraph_Tool.Edge.HasCurve_s(g, eid):
            assert BRepGraph_Tool.Edge.Curve_s(g, eid) is not None


def test_BRepGraph_GeometryTest_Box_Polygon2DRep_MatchesInline():
    g = _box()
    it = BRepGraph_CoEdgeIterator(g)
    while it.More():
        ce = it.Current()
        if ce.Polygon2DRepId.IsValid():
            assert g.Mesh().Persistent().CoEdges().PolygonOnSurface(it.CurrentId()) is not None
        it.Next()


def test_BRepGraph_GeometryTest_ClearUseOwnersMarksRecordsRemovedAndSetReusesSlots():
    g = _box()
    topo = g.Topo()
    ed = g.Editor()
    geo = topo.Geometry()
    poly = g.Mesh().Poly()

    fid = BRepGraph_FaceId.Start_s()
    assert fid.IsValid(topo.Faces().Nb())
    surf_rep = topo.Faces().Definition(fid).SurfaceRepId
    assert surf_rep.IsValid()
    surface = BRepGraph_Tool.Face.Surface_s(g, fid)
    assert surface is not None

    eid = BRepGraph_EdgeId()
    it = BRepGraph_EdgeIterator(g)
    while it.More():
        if it.Current().Curve3DRepId.IsValid():
            eid = it.CurrentId()
            break
        it.Next()
    assert eid.IsValid(topo.Edges().Nb())
    curve_rep = topo.Edges().Definition(eid).Curve3DRepId
    curve3d = BRepGraph_Tool.Edge.Curve_s(g, eid)
    assert curve3d is not None

    ceid = BRepGraph_CoEdgeId()
    it = BRepGraph_CoEdgeIterator(g)
    while it.More():
        if it.Current().Curve2DRepId.IsValid():
            ceid = it.CurrentId()
            break
        it.Next()
    assert ceid.IsValid(topo.CoEdges().Nb())
    pcurve_rep = topo.CoEdges().Definition(ceid).Curve2DRepId
    pcurve = BRepGraph_Tool.CoEdge.PCurve_s(g, ceid)
    assert pcurve is not None

    n_surf = geo.NbActiveFaceSurfaces()
    assert n_surf > 0
    ed.Faces().ClearSurface(fid)
    assert topo.Faces().Definition(fid).SurfaceRepId == surf_rep
    assert not BRepGraph_Tool.Face.HasSurface_s(g, fid)
    assert geo.NbActiveFaceSurfaces() == n_surf - 1
    ed.Faces().SetSurface(fid, surface)
    assert topo.Faces().Definition(fid).SurfaceRepId == surf_rep
    assert geo.NbActiveFaceSurfaces() == n_surf
    ed.Faces().ClearSurface(fid)
    assert geo.NbActiveFaceSurfaces() == n_surf - 1

    n_c3d = geo.NbActiveEdgeCurves3D()
    assert n_c3d > 0
    ed.Edges().ClearCurve(eid)
    assert topo.Edges().Definition(eid).Curve3DRepId == curve_rep
    assert not BRepGraph_Tool.Edge.HasCurve_s(g, eid)
    assert geo.NbActiveEdgeCurves3D() == n_c3d - 1
    ed.Edges().SetCurve(eid, curve3d, 0.0, 1.0)
    assert topo.Edges().Definition(eid).Curve3DRepId == curve_rep
    assert geo.NbActiveEdgeCurves3D() == n_c3d
    ed.Edges().ClearCurve(eid)
    assert geo.NbActiveEdgeCurves3D() == n_c3d - 1

    n_c2d = geo.NbActiveCoEdgeCurves2D()
    assert n_c2d > 0
    ed.CoEdges().ClearPCurve(ceid)
    assert topo.CoEdges().Definition(ceid).Curve2DRepId == pcurve_rep
    assert not BRepGraph_Tool.CoEdge.HasPCurve_s(g, ceid)
    assert geo.NbActiveCoEdgeCurves2D() == n_c2d - 1
    ed.CoEdges().SetPCurve(ceid, pcurve, 0.0, 1.0)
    assert topo.CoEdges().Definition(ceid).Curve2DRepId == pcurve_rep
    assert geo.NbActiveCoEdgeCurves2D() == n_c2d
    ed.CoEdges().ClearPCurve(ceid)
    assert geo.NbActiveCoEdgeCurves2D() == n_c2d - 1

    tri = Poly_Triangulation(3, 1, False)
    poly3d = Poly_Polygon3D(2, False)
    poly2d = Poly_Polygon2D(2)
    poly_on_tri = Poly_PolygonOnTriangulation(2, False)
    ed.Faces().SetPersistentTriangulation(fid, tri)
    ed.Edges().SetPersistentPolygon3D(eid, poly3d)
    ed.CoEdges().SetPersistentPolygon2D(ceid, poly2d)
    ed.CoEdges().SetPersistentPolygonOnTri(ceid, poly_on_tri)
    tri_rep = topo.Faces().Definition(fid).TriangulationRepId
    p3d_rep = topo.Edges().Definition(eid).Polygon3DRepId
    p2d_rep = topo.CoEdges().Definition(ceid).Polygon2DRepId
    pot_rep = topo.CoEdges().Definition(ceid).PolygonOnTriRepId

    n_tri = poly.NbActiveTriangulations()
    assert n_tri > 0
    ed.Faces().ClearPersistentTriangulation(fid)
    assert topo.Faces().Definition(fid).TriangulationRepId == tri_rep
    assert not g.Mesh().Persistent().Faces().Has(fid)
    assert poly.NbActiveTriangulations() == n_tri - 1
    ed.Faces().SetPersistentTriangulation(fid, tri)
    assert topo.Faces().Definition(fid).TriangulationRepId == tri_rep
    assert poly.NbActiveTriangulations() == n_tri
    ed.Faces().ClearPersistentTriangulation(fid)

    n_p3d = poly.NbActivePolygons3D()
    assert n_p3d > 0
    ed.Edges().ClearPersistentPolygon3D(eid)
    assert topo.Edges().Definition(eid).Polygon3DRepId == p3d_rep
    assert not g.Mesh().Persistent().Edges().Has(eid)
    assert poly.NbActivePolygons3D() == n_p3d - 1
    ed.Edges().SetPersistentPolygon3D(eid, poly3d)
    assert topo.Edges().Definition(eid).Polygon3DRepId == p3d_rep
    assert poly.NbActivePolygons3D() == n_p3d
    ed.Edges().ClearPersistentPolygon3D(eid)

    n_p2d = poly.NbActivePolygons2D()
    assert n_p2d > 0
    ed.CoEdges().SetPersistentPolygon2D(ceid, None)
    assert topo.CoEdges().Definition(ceid).Polygon2DRepId == p2d_rep
    assert not g.Mesh().Persistent().CoEdges().Has(ceid)
    assert poly.NbActivePolygons2D() == n_p2d - 1
    ed.CoEdges().SetPersistentPolygon2D(ceid, poly2d)
    assert topo.CoEdges().Definition(ceid).Polygon2DRepId == p2d_rep
    assert poly.NbActivePolygons2D() == n_p2d
    ed.CoEdges().SetPersistentPolygon2D(ceid, None)

    n_pot = poly.NbActivePolygonsOnTri()
    assert n_pot > 0
    ed.CoEdges().SetPersistentPolygonOnTri(ceid, None)
    assert topo.CoEdges().Definition(ceid).PolygonOnTriRepId == pot_rep
    assert not g.Mesh().Persistent().CoEdges().HasPolygonOnTriangulation(ceid)
    assert poly.NbActivePolygonsOnTri() == n_pot - 1
    ed.CoEdges().SetPersistentPolygonOnTri(ceid, poly_on_tri)
    assert topo.CoEdges().Definition(ceid).PolygonOnTriRepId == pot_rep
    assert poly.NbActivePolygonsOnTri() == n_pot
