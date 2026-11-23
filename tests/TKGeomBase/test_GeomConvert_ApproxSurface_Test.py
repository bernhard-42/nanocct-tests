# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomConvert_ApproxSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_SphericalSurface
from nanocct.GeomAbs import GeomAbs_C0
from nanocct.GeomConvert import GeomConvert_ApproxSurface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt


def test_GeomConvert_ApproxSurfaceTest_SphereApproximationRespectsTolerance():
    tol = 1.0e-3
    sphere = Geom_SphericalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 10.0)
    approx = GeomConvert_ApproxSurface(sphere, tol, GeomAbs_C0, GeomAbs_C0, 8, 8, 100, 0)
    assert approx.IsDone() is True
    result = approx.Surface()
    assert result is not None
    assert result.EvalD0(math.pi, 0.0).Distance(sphere.EvalD0(math.pi, 0.0)) <= tol
