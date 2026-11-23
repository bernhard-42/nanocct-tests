# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ProjLib_CompProjectedCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom import Geom_BSplineSurface, Geom_Line
from nanocct.GeomAbs import GeomAbs_C1, GeomAbs_C2
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from nanocct.gp import gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Precision import Precision
from nanocct.ProjLib import ProjLib_CompProjectedCurve


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def _array(kind, values):
    a = NCollection_Array1[kind](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


def test_ProjLib_CompProjectedCurveTest_SurfaceCrossingsFollowCurveParameters():
    u_knots, v_knots = _array(float, [0.0, 1.0]), _array(float, [0.0, 0.25, 0.5, 1.0])
    u_mults, v_mults = _array(int, [2, 2]), _array(int, [2, 1, 1, 2])
    y_values = (0.0, 0.7, 0.9, 1.0)
    for is_u in (False, True):
        poles = NCollection_Array2[gp_Pnt](1, 4 if is_u else 2, 1, 2 if is_u else 4)
        for i in range(4):
            for lin in range(2):
                p = gp_Pnt(y_values[i] if is_u else float(lin), float(lin) if is_u else y_values[i], 0.0)
                if is_u:
                    poles.SetValue(i + 1, lin + 1, p)
                else:
                    poles.SetValue(lin + 1, i + 1, p)
        surface = GeomAdaptor_Surface(Geom_BSplineSurface(poles,
                                                          v_knots if is_u else u_knots,
                                                          u_knots if is_u else v_knots,
                                                          v_mults if is_u else u_mults,
                                                          u_mults if is_u else v_mults,
                                                          1, 1))
        for is_reversed in (False, True):
            for is_trimmed in (False, True):
                start = 1.0 if is_reversed else 0.0
                direction = -1.0 if is_reversed else 1.0
                first = 0.05 if is_trimmed else 0.0
                last = 0.95 if is_trimmed else 1.0
                line = Geom_Line(gp_Pnt(start if is_u else 0.5, 0.5 if is_u else start, 0.0),
                                 gp_Dir(direction if is_u else 0.0, 0.0 if is_u else direction, 0.0))
                curve = GeomAdaptor_Curve(line, first, last)
                projection = ProjLib_CompProjectedCurve(Precision.Confusion_s(), surface, curve)
                assert projection.NbCurves() == 1
                for continuity in (GeomAbs_C1, GeomAbs_C2):
                    where = (is_u, is_reversed, is_trimmed, continuity)
                    nb = projection.NbIntervals(continuity)
                    assert nb == 3, where
                    intervals = NCollection_Array1[float](1, nb + 1)
                    projection.Intervals(intervals, continuity)
                    assert intervals[1] == _eq(first), where
                    assert intervals[2] == pytest.approx(0.1 if is_reversed else 0.7, abs=Precision.PConfusion_s()), where
                    assert intervals[3] == pytest.approx(0.3 if is_reversed else 0.9, abs=Precision.PConfusion_s()), where
                    assert intervals[4] == _eq(last), where
