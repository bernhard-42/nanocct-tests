# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomFill_GuideTrihedronAC_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_BSplineCurve
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.GeomFill import GeomFill_GuideTrihedronAC
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def _bspline_adaptor(p1, p2, p3, p4):
    poles = NCollection_Array1[gp_Pnt](1, 4)
    for i, p in enumerate((p1, p2, p3, p4), 1):
        poles.SetValue(i, p)
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, 4)
    mults.SetValue(2, 4)
    return GeomAdaptor_Curve(Geom_BSplineCurve(poles, knots, mults, 3))


def _trihedron(z=1, s=1):
    guide = _bspline_adaptor(gp_Pnt(0, 0, z), gp_Pnt(s, 0, z), gp_Pnt(s, s, z), gp_Pnt(0, s, z))
    path = _bspline_adaptor(gp_Pnt(0, 0, 0), gp_Pnt(s, 0, 0), gp_Pnt(s, s, 0), gp_Pnt(0, s, 0))
    tri = GeomFill_GuideTrihedronAC(guide)
    tri.SetCurve(path)
    return tri, guide, path


def test_GeomFill_GuideTrihedronAC_D0_ReturnsTrue():
    tri, _g, _p = _trihedron()
    t, n, b = gp_Vec(), gp_Vec(), gp_Vec()
    assert tri.D0(0.5, t, n, b)
    assert t.Magnitude() > CONF
    assert n.Magnitude() > CONF
    assert b.Magnitude() > CONF


def test_GeomFill_GuideTrihedronAC_D1_ReturnsTrue():
    tri, _g, _p = _trihedron()
    t, dt, n, dn, b, db = (gp_Vec() for _ in range(6))
    assert tri.D1(0.5, t, dt, n, dn, b, db)
    assert t.Magnitude() > CONF
    assert n.Magnitude() > CONF
    assert b.Magnitude() > CONF


def test_GeomFill_GuideTrihedronAC_D2_ReturnsTrue():
    tri, _g, _p = _trihedron()
    t, dt, d2t, n, dn, d2n, b, db, d2b = (gp_Vec() for _ in range(9))
    assert tri.D2(0.5, t, dt, d2t, n, dn, d2n, b, db, d2b)
    assert t.Magnitude() > CONF
    assert n.Magnitude() > CONF
    assert b.Magnitude() > CONF


def test_GeomFill_GuideTrihedronAC_D2_ConsistentAtMultipleParams():
    tri, _g, _p = _trihedron(2, 2)
    for param in (0.2, 0.4, 0.6, 0.8):
        vecs = [gp_Vec() for _ in range(9)]
        assert tri.D2(param, *vecs), param
