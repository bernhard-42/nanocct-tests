# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntPatch_PolyhedronBVH_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_CylindricalSurface, Geom_Plane, Geom_SphericalSurface
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Ax3, gp_Cylinder, gp_Dir, gp_Pln, gp_Pnt, gp_Sphere
from nanocct.IntPatch import (IntPatch_BVHTraversal, IntPatch_InterferencePolyhedron, IntPatch_Polyhedron,
                              IntPatch_PolyhedronBVH, IntPatch_PolyhedronTool)


@pytest.fixture
def surfaces():
    sphere = GeomAdaptor_Surface(Geom_SphericalSurface(gp_Sphere(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)))
    cyl = GeomAdaptor_Surface(Geom_CylindricalSurface(gp_Cylinder(gp_Ax3(gp_Pnt(0.5, 0, 0), gp_Dir(0, 0, 1)), 0.8)),
                              0, 2 * math.pi, -1, 1)
    return sphere, cyl


def test_IntPatch_PolyhedronBVHTest_Construction(surfaces):
    sphere, _cyl = surfaces
    poly = IntPatch_Polyhedron(sphere, 10, 10)
    bvh = IntPatch_PolyhedronBVH(poly)
    assert bvh.IsInitialized()
    assert bvh.Size() > 0
    assert bvh.Size() <= IntPatch_PolyhedronTool.NbTriangles_s(poly)


def test_IntPatch_PolyhedronBVHTest_Box(surfaces):
    sphere, _cyl = surfaces
    poly = IntPatch_Polyhedron(sphere, 5, 5)
    bvh = IntPatch_PolyhedronBVH(poly)
    for i in range(bvh.Size()):
        assert bvh.Box(i).IsValid(), i


def test_IntPatch_PolyhedronBVHTest_Center(surfaces):
    sphere, _cyl = surfaces
    poly = IntPatch_Polyhedron(sphere, 5, 5)
    bvh = IntPatch_PolyhedronBVH(poly)
    bounding = IntPatch_PolyhedronTool.Bounding_s(poly)
    xmin, ymin, zmin, xmax, ymax, zmax = bounding.Get__float__float__float__float__float__float()
    for i in range(bvh.Size()):
        cx, cy, cz = bvh.Center(i, 0), bvh.Center(i, 1), bvh.Center(i, 2)
        assert xmin - 1e-10 <= cx <= xmax + 1e-10
        assert ymin - 1e-10 <= cy <= ymax + 1e-10
        assert zmin - 1e-10 <= cz <= zmax + 1e-10


def test_IntPatch_PolyhedronBVHTest_OriginalIndex(surfaces):
    sphere, _cyl = surfaces
    poly = IntPatch_Polyhedron(sphere, 5, 5)
    bvh = IntPatch_PolyhedronBVH(poly)
    nb_tri = bvh.Size()
    nb_poly_tri = IntPatch_PolyhedronTool.NbTriangles_s(poly)
    for i in range(nb_tri):
        assert 1 <= bvh.OriginalIndex(i) <= nb_poly_tri
    bvh.BVH()
    used = [False] * (nb_poly_tri + 1)
    for i in range(nb_tri):
        idx = bvh.OriginalIndex(i)
        assert not used[idx]
        used[idx] = True


def test_IntPatch_PolyhedronBVHTest_Traversal(surfaces):
    sphere, cyl = surfaces
    poly1 = IntPatch_Polyhedron(sphere, 10, 10)
    poly2 = IntPatch_Polyhedron(cyl, 10, 10)
    set1 = IntPatch_PolyhedronBVH(poly1)
    set2 = IntPatch_PolyhedronBVH(poly2)
    trav = IntPatch_BVHTraversal()
    nb_pairs = trav.Perform(set1, set2, False)
    assert nb_pairs > 0
    pairs = trav.Pairs()
    assert nb_pairs == pairs.Size()
    n1 = IntPatch_PolyhedronTool.NbTriangles_s(poly1)
    n2 = IntPatch_PolyhedronTool.NbTriangles_s(poly2)
    for pair in pairs:
        assert 1 <= pair.First <= n1
        assert 1 <= pair.Second <= n2


def test_IntPatch_PolyhedronBVHTest_SelfInterference(surfaces):
    sphere, _cyl = surfaces
    poly = IntPatch_Polyhedron(sphere, 5, 5)
    bvh_set = IntPatch_PolyhedronBVH(poly)
    trav = IntPatch_BVHTraversal()
    trav.Perform(bvh_set, bvh_set, True)
    for pair in trav.Pairs():
        assert pair.First < pair.Second


def test_IntPatch_PolyhedronBVHTest_InterferencePolyhedron(surfaces):
    sphere, cyl = surfaces
    poly1 = IntPatch_Polyhedron(sphere, 10, 10)
    poly2 = IntPatch_Polyhedron(cyl, 10, 10)
    interf = IntPatch_InterferencePolyhedron(poly1, poly2)
    assert interf.NbSectionPoints() > 0 or interf.NbSectionLines() > 0 or interf.NbTangentZones() > 0


def test_IntPatch_PolyhedronBVHTest_NoOverlap(surfaces):
    sphere, _cyl = surfaces
    plane = GeomAdaptor_Surface(Geom_Plane(gp_Pln(gp_Pnt(10, 10, 10), gp_Dir(1, 0, 0))), -1, 1, -1, 1)
    poly1 = IntPatch_Polyhedron(sphere, 5, 5)
    poly2 = IntPatch_Polyhedron(plane, 5, 5)
    set1 = IntPatch_PolyhedronBVH(poly1)
    set2 = IntPatch_PolyhedronBVH(poly2)
    trav = IntPatch_BVHTraversal()
    assert trav.Perform(set1, set2, False) == 0
