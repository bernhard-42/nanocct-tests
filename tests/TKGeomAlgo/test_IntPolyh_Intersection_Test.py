# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntPolyh_Intersection_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_CylindricalSurface, Geom_Plane, Geom_SphericalSurface
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt
from nanocct.IntPolyh import IntPolyh_Intersection
from nanocct.Precision import Precision


def _line_points(inter):
    for il in range(1, inter.NbSectionLines() + 1):
        for ip in range(1, inter.NbPointsInLine(il) + 1):
            _x, _y, _z, u1, v1, u2, v2, _inc = inter.GetLinePoint(il, ip)
            assert math.isfinite(u1) and math.isfinite(v1), (il, ip)
            assert math.isfinite(u2) and math.isfinite(v2), (il, ip)
            yield u1, v1, u2, v2


def test_IntPolyh_Intersection_SpherePlane_ValidUVCoordinates():
    axis = gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    surf_s = GeomAdaptor_Surface(Geom_SphericalSurface(axis, 1.0))
    surf_p = GeomAdaptor_Surface(Geom_Plane(axis))
    inter = IntPolyh_Intersection(surf_s, surf_p)
    assert inter.IsDone()
    assert inter.NbSectionLines() > 0
    for _ in _line_points(inter):
        pass


def test_IntPolyh_Intersection_SphereCylinder_ValidUVCoordinates():
    axis = gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    surf_s = GeomAdaptor_Surface(Geom_SphericalSurface(axis, 2.0))
    surf_c = GeomAdaptor_Surface(Geom_CylindricalSurface(gp_Ax3(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 1.0))
    inter = IntPolyh_Intersection(surf_s, surf_c)
    assert inter.IsDone()
    assert inter.NbSectionLines() > 0
    pconf = Precision.PConfusion_s()
    for u1, v1, u2, v2 in _line_points(inter):
        assert not (abs(u1 - u2) < pconf and abs(v1 - v2) < pconf)


def test_IntPolyh_Intersection_TwoPlanes_ProducesSectionLine():
    s1 = GeomAdaptor_Surface(Geom_Plane(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))), -5.0, 5.0, -5.0, 5.0)
    s2 = GeomAdaptor_Surface(Geom_Plane(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 1))), -5.0, 5.0, -5.0, 5.0)
    inter = IntPolyh_Intersection(s1, s2)
    assert inter.IsDone()
    assert inter.NbSectionLines() > 0
