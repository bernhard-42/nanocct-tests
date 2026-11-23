# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GeomTools_RealRead_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: the C++ stream state the cases check -- fail() and width() -- because a Python file-like object has
# neither and the binding's stream exists only during the call (R-STREAM-IN). The values and the read position are
# translated: the file-like object moves on by what GetReal read, as the C++ stream does.
import io
import sys

import pytest

from nanocct.GeomTools import GeomTools
from nanocct.Precision import Precision


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def test_GeomToolsTest_LongRealTokenPreservesValueAndFollowingField():
    big = sys.float_info.max
    for value in (Precision.Infinite_s(), -Precision.Infinite_s(), big, -big, 1.25, -1.25, 0.0):
        stream = io.StringIO(f"{value:.40f} 7")          # std::fixed with setprecision(40)
        assert GeomTools.GetReal_s(stream) == _eq(value), value
        assert GeomTools.GetReal_s(stream) == _eq(7.0), value


def test_GeomToolsTest_RealTokenBufferBoundaryAndEndOfStream():
    for length in range(28, 35):
        stream = io.StringIO("0" * (length - 1) + "1")
        assert GeomTools.GetReal_s(stream) == _eq(1.0), length
        assert GeomTools.GetReal_s(stream) == _eq(0.0), length
    stream = io.StringIO("1.00000000000000000000000000000000000000000000000000000000001e-100 9")
    assert GeomTools.GetReal_s(stream) == _eq(1.0e-100)
    assert GeomTools.GetReal_s(stream) == _eq(9.0)


def test_GeomToolsTest_LongLeadingZerosPreserveSignAndStreamWidth():
    stream = io.StringIO("-" + "0" * 480 + "1.25e-20 8")
    assert GeomTools.GetReal_s(stream) == _eq(-1.25e-20)
    assert GeomTools.GetReal_s(stream) == _eq(8.0)


def test_GeomToolsTest_RealTokenLimitRejectsOversizedInput():
    for length in (511, 512, 2048):
        value = GeomTools.GetReal_s(io.StringIO("0" * (length - 1) + "1"))
        assert value == _eq(1.0 if length == 511 else 0.0), length


def test_GeomToolsTest_OversizedCurveCoordinateStopsGeometryRead():
    record = "1 " + "0" * 511 + "1" + " 0 0 1 0 0"
    assert GeomTools.Read_s__Geom_Curve(io.StringIO(record)) is None
