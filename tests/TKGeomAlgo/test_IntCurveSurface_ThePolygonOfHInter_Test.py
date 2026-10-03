# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntCurveSurface_ThePolygonOfHInter_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_Line
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pnt
from nanocct.IntCurveSurface import IntCurveSurface_ThePolygonOfHInter


def test_IntCurveSurface_ThePolygonOfHInter_Test_ClosedFlagReflectsStoredState():
    adaptor = GeomAdaptor_Curve(Geom_Line(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))))
    polygon = IntCurveSurface_ThePolygonOfHInter(adaptor, 6)
    assert not polygon.Closed()
    polygon.Closed(True)
    assert polygon.Closed()
