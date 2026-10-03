# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_TrimmedCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomAbs import GeomAbs_CN
from nanocct.Geom2d import Geom2d_Circle, Geom2d_Line, Geom2d_TrimmedCurve
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


@pytest.fixture
def line():
    return Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0))


@pytest.fixture
def circle():
    return Geom2d_Circle(gp_Circ2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 5.0))


def test_Geom2d_TrimmedCurveTest_ConstructFromLine(line):
    t = Geom2d_TrimmedCurve(line, 0.0, 10.0)
    deq(t.FirstParameter(), 0.0)
    deq(t.LastParameter(), 10.0)


def test_Geom2d_TrimmedCurveTest_ConstructFromCircle(circle):
    t = Geom2d_TrimmedCurve(circle, 0.0, math.pi)
    deq(t.FirstParameter(), 0.0)
    deq(t.LastParameter(), math.pi)


def test_Geom2d_TrimmedCurveTest_StartAndEndPoints(line):
    t = Geom2d_TrimmedCurve(line, 2.0, 8.0)
    near(t.StartPoint().X(), 2.0)
    near(t.EndPoint().X(), 8.0)


def test_Geom2d_TrimmedCurveTest_BasisCurve(circle):
    assert Geom2d_TrimmedCurve(circle, 0.0, math.pi).BasisCurve() is not None


def test_Geom2d_TrimmedCurveTest_EvalD0_MatchesBasisCurve(circle):
    t = Geom2d_TrimmedCurve(circle, 0.0, math.pi)
    u = 0.0
    while u <= math.pi:
        assert t.EvalD0(u).IsEqual(circle.EvalD0(u), TOL)
        u += math.pi / 4.0


def test_Geom2d_TrimmedCurveTest_EvalD1_MatchesBasisCurve(line):
    t = Geom2d_TrimmedCurve(line, 0.0, 10.0)
    rt, rb = t.EvalD1(5.0), line.EvalD1(5.0)
    assert rt.Point.IsEqual(rb.Point, TOL)
    near(rt.D1.X(), rb.D1.X())
    near(rt.D1.Y(), rb.D1.Y())


def test_Geom2d_TrimmedCurveTest_Continuity(line):
    assert Geom2d_TrimmedCurve(line, 0.0, 10.0).Continuity() == GeomAbs_CN


def test_Geom2d_TrimmedCurveTest_IsCN(line):
    assert Geom2d_TrimmedCurve(line, 0.0, 10.0).IsCN(10) is True


def test_Geom2d_TrimmedCurveTest_IsClosed_OpenArc(circle):
    assert Geom2d_TrimmedCurve(circle, 0.0, math.pi).IsClosed() is False


def test_Geom2d_TrimmedCurveTest_IsClosed_FullCircle(circle):
    assert Geom2d_TrimmedCurve(circle, 0.0, 2.0 * math.pi).IsClosed() is True


def test_Geom2d_TrimmedCurveTest_IsPeriodic_PartialArc(circle):
    assert Geom2d_TrimmedCurve(circle, 0.0, math.pi).IsPeriodic() is False


def test_Geom2d_TrimmedCurveTest_IsPeriodic_FullPeriod(circle):
    assert Geom2d_TrimmedCurve(circle, 0.0, 2.0 * math.pi).IsPeriodic() is True


def test_Geom2d_TrimmedCurveTest_IsPeriodic_Line(line):
    assert Geom2d_TrimmedCurve(line, 0.0, 10.0).IsPeriodic() is False


def test_Geom2d_TrimmedCurveTest_SetTrim(line):
    t = Geom2d_TrimmedCurve(line, 0.0, 10.0)
    t.SetTrim(3.0, 7.0)
    deq(t.FirstParameter(), 3.0)
    deq(t.LastParameter(), 7.0)


def test_Geom2d_TrimmedCurveTest_Copy(circle):
    c = Geom2d_TrimmedCurve(circle, 0.0, math.pi).Copy()
    assert isinstance(c, Geom2d_TrimmedCurve)
    deq(c.FirstParameter(), 0.0)
    deq(c.LastParameter(), math.pi)


def test_Geom2d_TrimmedCurveTest_Transform_Translation(line):
    t = Geom2d_TrimmedCurve(line, 0.0, 10.0)
    tr = gp_Trsf2d()
    tr.SetTranslation(gp_Vec2d(5.0, 5.0))
    t.Transform(tr)
    near(t.StartPoint().X(), 5.0)
    near(t.StartPoint().Y(), 5.0)


def test_Geom2d_TrimmedCurveTest_CircleArc_StartEndPoints(circle):
    t = Geom2d_TrimmedCurve(circle, 0.0, math.pi / 2.0)
    s, e = t.StartPoint(), t.EndPoint()
    near(s.X(), 5.0)
    near(s.Y(), 0.0)
    near(e.X(), 0.0)
    near(e.Y(), 5.0)
