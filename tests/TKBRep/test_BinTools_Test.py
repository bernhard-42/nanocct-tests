# Translated from OCCT src/ModelingData/TKBRep/GTests/BinTools_Test.cxx (LGPL-2.1 with the OCCT exception)
import io
import math

import pytest

from nanocct.BinTools import BinTools_Curve2dSet, BinTools_CurveSet
from nanocct.Geom import Geom_Circle, Geom_Ellipse, Geom_Line, Geom_TrimmedCurve
from nanocct.Geom2d import Geom2d_Circle, Geom2d_Ellipse, Geom2d_Line, Geom2d_OffsetCurve, Geom2d_TrimmedCurve
from nanocct.gp import gp_Ax2, gp_Ax2d, gp_Dir, gp_Dir2d, gp_Pnt, gp_Pnt2d

PERIOD = 2 * math.acos(-1.0)
RANGES = ((-8.0, -3.0), (5.0, 8.0), (7.0, 11.0), (0.0, PERIOD), (7.0, 7.0 + PERIOD), (7.0, 21.0))


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def _check_round_trip(curve):
    is2d = isinstance(curve, (Geom2d_TrimmedCurve, Geom2d_OffsetCurve))
    if is2d:
        data = BinTools_Curve2dSet.WriteCurve2d_s(curve)
    else:
        data = BinTools_CurveSet.WriteCurve_s(curve)
    stream = io.BytesIO(data)
    restored = BinTools_Curve2dSet.ReadCurve2d_s(stream) if is2d else BinTools_CurveSet.ReadCurve_s(stream)
    assert restored is not None
    assert stream.read(1) == b""                         # peek() == eof: the read consumed exactly the record
    assert restored.DynamicType().Name() == curve.DynamicType().Name()
    assert restored.FirstParameter() == _eq(curve.FirstParameter())
    assert restored.LastParameter() == _eq(curve.LastParameter())
    first, last = curve.FirstParameter(), curve.LastParameter()
    for t in (first, (first + last) / 2, last):
        assert restored.EvalD0(t).Distance(curve.EvalD0(t)) < 1e-12, t
        assert (restored.EvalD1(t).D1 - curve.EvalD1(t).D1).Magnitude() < 1e-12, t


def test_BinToolsCurve2dSetTest_PeriodicTrims_PreserveParametersAndGeometry():
    axis = gp_Ax2d(gp_Pnt2d(2, -3), gp_Dir2d(1, 2))
    for curve in (Geom2d_Circle(axis, 4, False), Geom2d_Ellipse(axis, 5, 2, False)):
        for first, last in RANGES:
            trim = Geom2d_TrimmedCurve(curve, first, last, True, False)
            _check_round_trip(trim)
            _check_round_trip(Geom2d_OffsetCurve(trim, 0.5))


def test_BinToolsCurveSetTest_PeriodicTrims_PreserveParametersAndGeometry():
    axis = gp_Ax2(gp_Pnt(2, -3, 1), gp_Dir(1, 1, 1))
    for curve in (Geom_Circle(axis, 4), Geom_Ellipse(axis, 5, 2)):
        for first, last in RANGES:
            _check_round_trip(Geom_TrimmedCurve(curve, first, last, True, False))


def test_BinToolsCurve2dSetTest_BoundedLine_PreservesInterval():
    _check_round_trip(Geom2d_TrimmedCurve(Geom2d_Line(gp_Pnt2d(2, -3), gp_Dir2d(1, 2)), -5, 7))


def test_BinToolsCurveSetTest_BoundedLine_PreservesInterval():
    _check_round_trip(Geom_TrimmedCurve(Geom_Line(gp_Pnt(2, -3, 1), gp_Dir(1, 2, 3)), -5, 7))
