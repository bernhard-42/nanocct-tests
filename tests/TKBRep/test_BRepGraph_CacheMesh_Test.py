# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_CacheMesh_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Mapping notes:
# - BRepGraph_CacheMesh itself is not bound. `Mesh().Cache().Faces().Entry(f) != nullptr` maps to
#   `Mesh().Cache().Faces().Has(f)` (OCCT implements Has exactly so); same for edges (non-null Polygon3D).
# - CacheMesh::FindCoEdgePolygon2D / FindCoEdgePolygonOnTri map to Mesh().Effective().CoEdges()
#   .HasPolygonOnSurface / .HasPolygonOnTriangulation, which check the fresh cache entry first and then the
#   persistent coedge reps; a plain box has no persistent coedge mesh (asserted as a precondition).
# - Mutations through a MutGuard scope map to the by-id Editor setters (same markModified path).
# - Not translated: Needs_* (CacheMesh::Needs not bound), MeshGeneration_MonotonicAcrossClear (raw internals).

import pytest

from nanocct import TopAbs
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CoEdgesOfWire,
    BRepGraph_EdgeId,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceId,
    BRepGraph_FaceIterator,
    BRepGraph_RefsWireOfFace,
    BRepGraph_Tool,
    BRepGraph_VertexId,
    BRepGraph_VertexIterator,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Poly import Poly_Polygon2D, Poly_Polygon3D, Poly_PolygonOnTriangulation, Poly_Triangulation


def _make_box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    return g


def _trivial_tri():
    return Poly_Triangulation(3, 1, False)


def _first_id(it, invalid):
    if it.More():
        return it.CurrentId()
    return invalid


def _first_face(g):
    return _first_id(BRepGraph_FaceIterator(g), BRepGraph_FaceId())


def _first_edge(g):
    return _first_id(BRepGraph_EdgeIterator(g), BRepGraph_EdgeId())


def _first_vertex(g):
    return _first_id(BRepGraph_VertexIterator(g), BRepGraph_VertexId())


def _first_coedge_of_face(g, fid):
    wit = BRepGraph_RefsWireOfFace(g, fid)
    while wit.More():
        wid = g.Refs().Wires().Entry(wit.CurrentId()).ChildWireId
        cit = BRepGraph_CoEdgesOfWire(g, wid)
        while cit.More():
            ce = cit.CurrentId()
            if g.Topo().CoEdges().Definition(ce).FaceId == fid:
                return ce
            cit.Next()
        wit.Next()
    return BRepGraph_CoEdgeId()


def _write_face_mesh(g, fid):
    tri = _trivial_tri()
    g.Editor().Faces().SetPersistentTriangulation(fid, tri)
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, tri)


def _write_coedge_mesh(g, ce, fid):
    g.Mesh().Editor().CoEdges().SetCachedPolygon2D(ce, Poly_Polygon2D(2))
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, _trivial_tri())
    g.Mesh().Editor().CoEdges().AppendCachedPolygonOnTri(ce, Poly_PolygonOnTriangulation(2, False))


def _write_edge_mesh(g, eid):
    g.Mesh().Editor().Edges().SetCachedPolygon3D(eid, Poly_Polygon3D(2, False))


def _face_cached(g, fid):
    return g.Mesh().Cache().Faces().Has(fid)


def _edge_cached(g, eid):
    return g.Mesh().Cache().Edges().Has(eid)


def _coedge_poly2d(g, ce):
    return g.Mesh().Effective().CoEdges().HasPolygonOnSurface(ce)


def _coedge_polyontri(g, ce):
    return g.Mesh().Effective().CoEdges().HasPolygonOnTriangulation(ce)


def _bump_face(g, fid):
    g.Editor().Faces().SetTolerance(fid, BRepGraph_Tool.Face.Tolerance_s(g, fid) + 1.0e-6)


def _bump_edge(g, eid):
    g.Editor().Edges().SetTolerance(eid, BRepGraph_Tool.Edge.Tolerance_s(g, eid) + 1.0e-6)


def _bump_vertex(g, vid):
    g.Editor().Vertices().SetTolerance(vid, BRepGraph_Tool.Vertex.Tolerance_s(g, vid) + 1.0e-6)


@pytest.fixture
def face_setup():
    g = _make_box_graph()
    fid = _first_face(g)
    assert fid.IsValid(g.Topo().Faces().Nb())
    return g, fid


@pytest.fixture
def coedge_setup(face_setup):
    g, fid = face_setup
    ce = _first_coedge_of_face(g, fid)
    assert ce.IsValid(g.Topo().CoEdges().Nb())
    # precondition of the mapping: no persistent coedge mesh on a plain box
    assert not g.Mesh().Persistent().CoEdges().Has(ce)
    assert not g.Mesh().Persistent().CoEdges().HasPolygonOnTriangulation(ce)
    return g, fid, ce


def test_BRepGraph_CacheMeshTest_CacheStaleAfterFaceMutation(face_setup):
    g, fid = face_setup
    tri = _trivial_tri()
    g.Editor().Faces().SetPersistentTriangulation(fid, tri)
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, tri)
    assert _face_cached(g, fid)
    _bump_face(g, fid)
    assert not _face_cached(g, fid)


def test_BRepGraph_CacheMeshTest_CacheStaleAfterSurfaceRepMutation(face_setup):
    g, fid = face_setup
    tri = _trivial_tri()
    g.Editor().Faces().SetPersistentTriangulation(fid, tri)
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, tri)
    assert _face_cached(g, fid)
    g.Editor().Faces().ClearSurface(fid)
    assert not _face_cached(g, fid)


def test_BRepGraph_CacheMeshTest_CacheSurvivesUnrelatedMutation(face_setup):
    g, fid = face_setup
    other = BRepGraph_FaceIterator(g)
    other.Next()
    assert other.More()
    other_fid = other.CurrentId()

    tri = _trivial_tri()
    g.Editor().Faces().SetPersistentTriangulation(fid, tri)
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, tri)
    _bump_face(g, other_fid)
    assert _face_cached(g, fid)


def test_BRepGraph_CacheMeshTest_ClearDropsLargeCacheAndAllowsSmallRegenerate(face_setup):
    g, fid = face_setup
    tri = Poly_Triangulation(3, 1, False)
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, tri)
    assert _face_cached(g, fid)

    g.CacheRegistry().ClearAll()
    assert not _face_cached(g, fid)

    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, tri)
    assert _face_cached(g, fid)
    assert g.Mesh().Cache().Faces().Triangulation(fid) is tri


def test_BRepGraph_CacheMeshTest_FaceCache_StaleAfterEdgeMutation(face_setup):
    g, fid = face_setup
    _write_face_mesh(g, fid)
    assert _face_cached(g, fid)
    eid = _first_edge(g)
    assert eid.IsValid(g.Topo().Edges().Nb())
    _bump_edge(g, eid)
    assert not _face_cached(g, fid)


def test_BRepGraph_CacheMeshTest_FaceCache_StaleAfterCoEdgeMutation(coedge_setup):
    g, fid, ce = coedge_setup
    _write_face_mesh(g, fid)
    assert _face_cached(g, fid)
    g.Editor().CoEdges().SetOrientation(ce, TopAbs.TopAbs_REVERSED)
    assert not _face_cached(g, fid)


def test_BRepGraph_CacheMeshTest_FaceCache_StaleAfterVertexMutation(face_setup):
    g, fid = face_setup
    vid = _first_vertex(g)
    assert vid.IsValid(g.Topo().Vertices().Nb())
    _write_face_mesh(g, fid)
    assert _face_cached(g, fid)
    _bump_vertex(g, vid)
    assert not _face_cached(g, fid)


def test_BRepGraph_CacheMeshTest_EdgeCache_StaleAfterVertexMutation():
    g = _make_box_graph()
    eid = _first_edge(g)
    assert eid.IsValid(g.Topo().Edges().Nb())
    vid = _first_vertex(g)
    assert vid.IsValid(g.Topo().Vertices().Nb())
    _write_edge_mesh(g, eid)
    assert _edge_cached(g, eid)
    _bump_vertex(g, vid)
    assert not _edge_cached(g, eid)


def test_BRepGraph_CacheMeshTest_EdgeCache_FreshAfterUnrelatedFaceMutation():
    g = _make_box_graph()
    eid = _first_edge(g)
    assert eid.IsValid(g.Topo().Edges().Nb())
    _write_edge_mesh(g, eid)
    assert _edge_cached(g, eid)
    _bump_face(g, _first_face(g))
    assert _edge_cached(g, eid)


def test_BRepGraph_CacheMeshTest_CoEdge_Polygon2DFreshAfterFaceMeshChange(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_poly2d(g, ce)
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, Poly_Triangulation(4, 1, False))
    assert _coedge_poly2d(g, ce)


def test_BRepGraph_CacheMeshTest_CoEdge_PolygonOnTriStaleAfterFaceMeshChange(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_polyontri(g, ce)
    g.Mesh().Editor().Faces().SetCachedTriangulation(fid, Poly_Triangulation(4, 1, False))
    assert not _coedge_polyontri(g, ce)


def test_BRepGraph_CacheMeshTest_CoEdge_PolygonOnTriStaleAfterFaceTopologyChange(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_polyontri(g, ce)
    _bump_face(g, fid)
    assert not _coedge_polyontri(g, ce)


def test_BRepGraph_CacheMeshTest_CoEdge_PolygonOnTriStaleAfterCoEdgeMutation(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_polyontri(g, ce)
    g.Editor().CoEdges().SetOrientation(ce, TopAbs.TopAbs_REVERSED)
    assert not _coedge_polyontri(g, ce)


def test_BRepGraph_CacheMeshTest_CoEdge_FreshAfterUnrelatedEdgeMutation(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_poly2d(g, ce)
    assert _coedge_polyontri(g, ce)

    eit = BRepGraph_EdgeIterator(g)
    eit.Next()
    other = eit.CurrentId()
    if other.IsValid(g.Topo().Edges().Nb()):
        _bump_edge(g, other)

    assert _coedge_poly2d(g, ce)


def test_BRepGraph_CacheMeshTest_CoEdge_UsesCoEdgeDefFaceId(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_polyontri(g, ce)
    face_of_ce = g.Topo().CoEdges().Definition(ce).FaceId
    assert face_of_ce.IsValid(g.Topo().Faces().Nb())
    _bump_face(g, face_of_ce)
    assert not _coedge_polyontri(g, ce)


def test_BRepGraph_CacheMeshTest_CoEdge_Polygon2DStaleAfterSlotRecipeChange(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_poly2d(g, ce)
    # OCCT clears the CacheMesh directly (not bound); ClearAll clears it through the registry
    g.CacheRegistry().ClearAll()
    assert not _coedge_poly2d(g, ce)


def test_BRepGraph_CacheMeshTest_CoEdge_FaceNotYetMeshed_SnapshotZero(coedge_setup):
    g, fid, ce = coedge_setup
    g.Mesh().Editor().CoEdges().SetCachedPolygon2D(ce, Poly_Polygon2D(2))
    g.Mesh().Editor().CoEdges().AppendCachedPolygonOnTri(ce, Poly_PolygonOnTriangulation(2, False))
    assert not _coedge_polyontri(g, ce)

    _write_face_mesh(g, fid)
    assert not _coedge_polyontri(g, ce)


def test_BRepGraph_CacheMeshTest_VertexPropagation_ReachesFaces(face_setup):
    g, fid = face_setup
    vid = _first_vertex(g)
    assert vid.IsValid(g.Topo().Vertices().Nb())
    _write_face_mesh(g, fid)
    assert _face_cached(g, fid)
    _bump_vertex(g, vid)
    assert not _face_cached(g, fid)


def test_BRepGraph_CacheMeshTest_FaceClear_PreservesCoEdgePolygon2D(coedge_setup):
    g, fid, ce = coedge_setup
    _write_coedge_mesh(g, ce, fid)
    assert _coedge_poly2d(g, ce)
    g.Mesh().Editor().Faces().Clear(fid)
    assert _coedge_poly2d(g, ce)
