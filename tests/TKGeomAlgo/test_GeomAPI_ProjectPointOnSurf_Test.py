# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomAPI_ProjectPointOnSurf_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_CylindricalSurface, Geom_RectangularTrimmedSurface
from nanocct.GeomAPI import GeomAPI_ProjectPointOnSurf
from nanocct.gp import gp, gp_Pnt


def test_GeomAPI_ProjectPointOnSurfTest_Bug867_InitWithTightBoundsNoException():
    cyl = Geom_CylindricalSurface(gp.XOY_s(), 10.0)
    trim = Geom_RectangularTrimmedSurface(cyl, 0.0, 4.0, 0.0, 2.0)
    proj = GeomAPI_ProjectPointOnSurf()
    proj.Init(trim, 0.0, 3.0, 0.0, 2.0)
    proj.Perform(gp_Pnt(30.0, 30.0, 30.0))
