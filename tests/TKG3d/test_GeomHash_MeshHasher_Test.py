# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomHash_MeshHasher_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GeomHash import (
    GeomHash_Polygon2DHasher,
    GeomHash_Polygon3DHasher,
    GeomHash_PolygonOnTriHasher,
    GeomHash_TriangulationHasher,
    PolygonOnTriHashKey,
)
from nanocct.gp import gp_Pnt, gp_Pnt2d
from nanocct.Poly import (
    Poly_Polygon2D,
    Poly_Polygon3D,
    Poly_PolygonOnTriangulation,
    Poly_Triangle,
    Poly_Triangulation,
)


def _polygon2d(defl):
    p = Poly_Polygon2D(2)
    p.ChangeNodes().SetValue(1, gp_Pnt2d(0.0, 0.0))
    p.ChangeNodes().SetValue(2, gp_Pnt2d(1.0, 0.0))
    p.Deflection(defl)
    return p


def _polygon3d(defl):
    p = Poly_Polygon3D(2, False)
    p.ChangeNodes().SetValue(1, gp_Pnt(0.0, 0.0, 0.0))
    p.ChangeNodes().SetValue(2, gp_Pnt(1.0, 0.0, 0.0))
    p.Deflection(defl)
    return p


def _polygon_on_tri(defl):
    p = Poly_PolygonOnTriangulation(2, False)
    p.SetNode(1, 1)
    p.SetNode(2, 2)
    p.Deflection(defl)
    return p


def _triangulation(defl):
    t = Poly_Triangulation(3, 1, False)
    t.SetNode(1, gp_Pnt(0.0, 0.0, 0.0))
    t.SetNode(2, gp_Pnt(1.0, 0.0, 0.0))
    t.SetNode(3, gp_Pnt(0.0, 1.0, 0.0))
    t.SetTriangle(1, Poly_Triangle(1, 2, 3))
    t.Deflection(defl)
    return t


def _key(poly, tri_rep_id):
    k = PolygonOnTriHashKey()
    if poly is not None:
        k.Poly = poly
    k.TriRepId = tri_rep_id
    return k


def test_GeomHash_MeshHasherTest_Polygon2D_CloseDeflectionKeepsEqualHash():
    h = GeomHash_Polygon2DHasher(0.1, 0.01)
    p1, p2 = _polygon2d(0.004), _polygon2d(0.0044)
    assert h(p1, p2)
    assert h(p1) == h(p2)


def test_GeomHash_MeshHasherTest_Polygon3D_CloseDeflectionKeepsEqualHash():
    h = GeomHash_Polygon3DHasher(0.1, 0.01)
    p1, p2 = _polygon3d(0.004), _polygon3d(0.0044)
    assert h(p1, p2)
    assert h(p1) == h(p2)


def test_GeomHash_MeshHasherTest_PolygonOnTriangulation_CloseDeflectionKeepsEqualHash():
    h = GeomHash_PolygonOnTriHasher(0.1, 0.01)
    k1 = _key(_polygon_on_tri(0.004), 7)
    k2 = _key(_polygon_on_tri(0.0044), 7)
    assert h(k1, k2)
    assert h(k1) == h(k2)


def test_GeomHash_MeshHasherTest_Triangulation_CloseDeflectionKeepsEqualHash():
    h = GeomHash_TriangulationHasher(0.1, 0.01)
    t1, t2 = _triangulation(0.004), _triangulation(0.0044)
    assert h(t1, t2)
    assert h(t1) == h(t2)


def test_GeomHash_MeshHasherTest_Polygon2D_DifferentSameCountGeometryChangesHash():
    h = GeomHash_Polygon2DHasher(0.1, 0.01)
    p1, p2 = _polygon2d(0.004), _polygon2d(0.004)
    p2.ChangeNodes().SetValue(2, gp_Pnt2d(2.0, 0.0))
    assert not h(p1, p2)
    assert h(p1) != h(p2)


def test_GeomHash_MeshHasherTest_Polygon3D_DifferentSameCountGeometryChangesHash():
    h = GeomHash_Polygon3DHasher(0.1, 0.01)
    p1, p2 = _polygon3d(0.004), _polygon3d(0.004)
    p2.ChangeNodes().SetValue(2, gp_Pnt(2.0, 0.0, 0.0))
    assert not h(p1, p2)
    assert h(p1) != h(p2)


def test_GeomHash_MeshHasherTest_PolygonOnTriangulation_DifferentSameCountIndicesChangesHash():
    h = GeomHash_PolygonOnTriHasher(0.1, 0.01)
    k1 = _key(_polygon_on_tri(0.004), 7)
    k2 = _key(_polygon_on_tri(0.004), 7)
    k2.Poly.SetNode(2, 3)
    assert not h(k1, k2)
    assert h(k1) != h(k2)


def test_GeomHash_MeshHasherTest_Triangulation_DifferentSameCountGeometryChangesHash():
    h = GeomHash_TriangulationHasher(0.1, 0.01)
    t1, t2 = _triangulation(0.004), _triangulation(0.004)
    t2.SetNode(3, gp_Pnt(0.0, 2.0, 0.0))
    assert not h(t1, t2)
    assert h(t1) != h(t2)


def test_GeomHash_MeshHasherTest_NullHandlesDoNotCrash():
    h2d = GeomHash_Polygon2DHasher()
    h3d = GeomHash_Polygon3DHasher()
    hot = GeomHash_PolygonOnTriHasher()
    htri = GeomHash_TriangulationHasher()

    assert h2d(None) == 0
    assert h2d(None, None)
    assert not h2d(None, _polygon2d(0.004))

    assert h3d(None) == 0
    assert h3d(None, None)
    assert not h3d(None, _polygon3d(0.004))

    assert htri(None) == 0
    assert htri(None, None)
    assert not htri(None, _triangulation(0.004))

    # A default-constructed key carries a null Poly handle (PolygonOnTriHashKey{null, id}).
    n1 = _key(None, 7)
    n2 = _key(None, 7)
    n3 = _key(None, 8)
    assert hot(n1, n2)
    assert not hot(n1, n3)
    assert not hot(n1, _key(_polygon_on_tri(0.004), 7))


def test_GeomHash_MeshHasherTest_HashToleranceAffectsNumericFields():
    p = _polygon2d(0.06)
    fine = GeomHash_Polygon2DHasher(0.1, 0.01)
    coarse = GeomHash_Polygon2DHasher(0.1, 0.1)
    assert fine(p) != coarse(p)
