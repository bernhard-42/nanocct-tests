# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ProjLib_ComputeApproxOnPolarSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_Circle, Geom_CylindricalSurface
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from nanocct.gp import gp_Ax2, gp_Ax3, gp_Dir, gp_Pnt
from nanocct.ProjLib import ProjLib_ComputeApproxOnPolarSurface


def _check(pcurve, surf, curve, t, tol):
    uv = pcurve.Value(t)
    assert surf.Value(uv.X(), uv.Y()).Distance(curve.Value(t)) <= tol


def test_ProjLib_ComputeApproxOnPolarSurfaceTest_BuildInitialCurveAndProjectOnCylinder_Done():
    curve = Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 2), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)), 5.0)
    surf = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)), 5.0)
    ca = GeomAdaptor_Curve(curve)
    sa = GeomAdaptor_Surface(surf)
    pr = ProjLib_ComputeApproxOnPolarSurface()
    pr.SetTolerance(1.0e-6)
    init = pr.BuildInitialCurve2d(ca, sa)
    assert pr.IsDone()
    assert init is not None
    pc = pr.ProjectUsingInitialCurve2d(ca, sa, init)
    assert pr.IsDone()
    assert pc is not None
    first = max(curve.FirstParameter(), pc.FirstParameter())
    last = min(curve.LastParameter(), pc.LastParameter())
    assert first < last
    for t in (first, 0.5 * (first + last), last):
        _check(pc, surf, curve, t, 1.0e-3)
