# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomTools_Test.cxx (LGPL-2.1 with the OCCT exception)
import io

import pytest

from nanocct.Geom import Geom_Circle, Geom_TrimmedCurve
from nanocct.Geom2d import Geom2d_Circle, Geom2d_TrimmedCurve
from nanocct.GeomTools import GeomTools
from nanocct.gp import gp_Ax2, gp_Ax2d, gp_Dir, gp_Dir2d, gp_Pnt, gp_Pnt2d


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def test_GeomToolsTest_Curve2dRoundTripPreservesTrimmedPeriodicChart():
    curve = Geom2d_TrimmedCurve(Geom2d_Circle(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 2), 7, 11, True, False)
    result = GeomTools.Read_s__Geom2d_Curve(io.StringIO(GeomTools.Write_s(curve, precision_hint=17)))   # aStream.precision(17)
    assert result is not None
    assert result.FirstParameter() == _eq(7)
    assert result.LastParameter() == _eq(11)
    for t in (7.0, 9.0, 11.0):
        assert result.EvalD0(t).Distance(curve.EvalD0(t)) <= 1e-12, t


def test_GeomToolsTest_CurveRoundTripPreservesTrimmedPeriodicChart():
    basis = Geom_Circle(gp_Ax2(gp_Pnt(3, 0, 0), gp_Dir(0, 0, 1)), 2)
    curve = Geom_TrimmedCurve(basis, 18, 23, False, False)
    result = GeomTools.Read_s__Geom_Curve(io.StringIO(GeomTools.Write_s(curve, precision_hint=17)))   # aStream.precision(17)
    assert result is not None
    assert result.DynamicType().Name() == curve.DynamicType().Name()
    assert result.FirstParameter() == pytest.approx(curve.FirstParameter(), abs=1e-14)
    assert result.LastParameter() == pytest.approx(curve.LastParameter(), abs=1e-14)
    t = (curve.FirstParameter() + curve.LastParameter()) / 2
    assert result.EvalD0(t).Distance(curve.EvalD0(t)) <= 1e-12
