# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_Hyperbola_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_Hyperbola
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Hypr2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


@pytest.fixture
def hyp():
    return Geom2d_Hyperbola(gp_Hypr2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 5.0, 3.0))


def test_Geom2d_HyperbolaTest_Radii(hyp):
    near(hyp.MajorRadius(), 5.0)
    near(hyp.MinorRadius(), 3.0)


def test_Geom2d_HyperbolaTest_IsNotClosedNotPeriodic(hyp):
    assert hyp.IsClosed() is False
    assert hyp.IsPeriodic() is False


def test_Geom2d_HyperbolaTest_Eccentricity(hyp):
    near(hyp.Eccentricity(), math.sqrt(34.0) / 5.0)


def test_Geom2d_HyperbolaTest_Focal(hyp):
    near(hyp.Focal(), 2.0 * math.sqrt(34.0))


def test_Geom2d_HyperbolaTest_Foci(hyp):
    c = math.sqrt(34.0)
    near(hyp.Focus1().X(), c)
    near(hyp.Focus2().X(), -c)


def test_Geom2d_HyperbolaTest_Parameter(hyp):
    near(hyp.Parameter(), 1.8)


def test_Geom2d_HyperbolaTest_EvalD0_AtZero(hyp):
    p = hyp.EvalD0(0.0)
    near(p.X(), 5.0)
    near(p.Y(), 0.0)


def test_Geom2d_HyperbolaTest_EvalD1_AtZero(hyp):
    d1 = hyp.EvalD1(0.0).D1
    near(d1.X(), 0.0)
    near(d1.Y(), 3.0)


def test_Geom2d_HyperbolaTest_PointOnHyperbola_FociDistanceDifference(hyp):
    f1, f2 = hyp.Focus1(), hyp.Focus2()
    u = -2.0
    while u <= 2.0:
        p = hyp.EvalD0(u)
        near(abs(p.Distance(f1) - p.Distance(f2)), 10.0)
        u += 0.5


def test_Geom2d_HyperbolaTest_SetMajorRadius(hyp):
    hyp.SetMajorRadius(8.0)
    near(hyp.MajorRadius(), 8.0)


def test_Geom2d_HyperbolaTest_SetMinorRadius(hyp):
    hyp.SetMinorRadius(4.0)
    near(hyp.MinorRadius(), 4.0)


def test_Geom2d_HyperbolaTest_Copy(hyp):
    c = hyp.Copy()
    assert isinstance(c, Geom2d_Hyperbola)
    near(c.MajorRadius(), 5.0)
    near(c.MinorRadius(), 3.0)


def test_Geom2d_HyperbolaTest_Transform_Translation(hyp):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(10.0, 20.0))
    hyp.Transform(t)
    near(hyp.Location().X(), 10.0)
    near(hyp.Location().Y(), 20.0)


def test_Geom2d_HyperbolaTest_Asymptotes(hyp):
    near(hyp.Asymptote1().Location().X(), 0.0)
    near(hyp.Asymptote2().Location().X(), 0.0)
