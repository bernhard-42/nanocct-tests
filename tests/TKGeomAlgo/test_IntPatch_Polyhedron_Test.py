# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntPatch_Polyhedron_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_Plane, Geom_SphericalSurface
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt
from nanocct.IntPatch import IntPatch_Polyhedron


def _plane():
    return GeomAdaptor_Surface(Geom_Plane(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))), -1.0, 1.0, -1.0, 1.0)


def _sphere():
    return GeomAdaptor_Surface(Geom_SphericalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0))


def test_IntPatch_Polyhedron_DefaultConstructor_ProducesValidMesh():
    surf = _sphere()
    poly = IntPatch_Polyhedron(surf)
    nb_u, nb_v = poly.Size()
    assert nb_u > 0
    assert nb_v > 0
    assert poly.NbTriangles() > 0
    assert poly.NbPoints() > 0


def test_IntPatch_Polyhedron_ZeroSubdivision_ClampedToMinimum():
    surf = _plane()
    poly = IntPatch_Polyhedron(surf, 0, 0)
    nb_u, nb_v = poly.Size()
    assert nb_u >= 1
    assert nb_v >= 1
    assert poly.NbTriangles() > 0


def test_IntPatch_Polyhedron_SmallSubdivision_ProducesValidMesh():
    surf = _plane()
    poly = IntPatch_Polyhedron(surf, 2, 2)
    nb_u, nb_v = poly.Size()
    assert nb_u == 2
    assert nb_v == 2
    assert poly.NbTriangles() == 2 * 2 * 2


def test_IntPatch_Polyhedron_TriConnex_PedgeZero_NoCrash():
    surf = _sphere()
    poly = IntPatch_Polyhedron(surf, 4, 4)
    p1, _p2, _p3 = poly.Triangle(1)
    result, _tri_con, _other_p = poly.TriConnex(1, p1, 0)
    assert result >= 0


def test_IntPatch_Polyhedron_TriConnex_AllVertices_NoCrash():
    surf = _sphere()
    poly = IntPatch_Polyhedron(surf, 3, 3)
    p1, p2, p3 = poly.Triangle(1)
    poly.TriConnex(1, p1, 0)
    poly.TriConnex(1, p1, p2)
    poly.TriConnex(1, p1, p3)
    poly.TriConnex(1, p2, p3)
