# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomFill_NSections_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_BSplineCurve, Geom_Curve
from nanocct.GeomFill import GeomFill_NSections
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_Sequence


def test_GeomFill_NSectionsTest_OCC27875_SingleCurveDoesNotThrow():
    poles = NCollection_Array1[gp_Pnt](1, 2)
    poles.SetValue(1, gp_Pnt(0.0, 0.0, 0.0))
    poles.SetValue(2, gp_Pnt(1.0, 0.0, 0.0))
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, 2)
    mults.SetValue(2, 2)
    curve = Geom_BSplineCurve(poles, knots, mults, 1)
    seq = NCollection_Sequence[Geom_Curve]()
    seq.Append(curve)
    GeomFill_NSections(seq)
