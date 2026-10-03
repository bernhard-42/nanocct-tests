# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_Ellipse_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_Ellipse
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Elips2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


@pytest.fixture
def ell():
    return Geom2d_Ellipse(gp_Elips2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 10.0, 5.0))


def test_Geom2d_EllipseTest_Radii(ell):
    near(ell.MajorRadius(), 10.0)
    near(ell.MinorRadius(), 5.0)


def test_Geom2d_EllipseTest_ParameterBounds(ell):
    assert ell.FirstParameter() == pytest.approx(0.0, abs=1e-300)
    assert ell.LastParameter() == pytest.approx(2.0 * math.pi, rel=1e-14)


def test_Geom2d_EllipseTest_IsClosedAndPeriodic(ell):
    assert ell.IsClosed() is True
    assert ell.IsPeriodic() is True


def test_Geom2d_EllipseTest_Eccentricity(ell):
    near(ell.Eccentricity(), math.sqrt(1.0 - 25.0 / 100.0))


def test_Geom2d_EllipseTest_Focal(ell):
    near(ell.Focal(), 2.0 * math.sqrt(100.0 - 25.0))


def test_Geom2d_EllipseTest_Foci(ell):
    f1, f2 = ell.Focus1(), ell.Focus2()
    c = math.sqrt(75.0)
    near(f1.X(), c)
    near(f1.Y(), 0.0)
    near(f2.X(), -c)
    near(f2.Y(), 0.0)


def test_Geom2d_EllipseTest_Parameter(ell):
    near(ell.Parameter(), 2.5)


def test_Geom2d_EllipseTest_EvalD0_MajorVertex(ell):
    p = ell.EvalD0(0.0)
    near(p.X(), 10.0)
    near(p.Y(), 0.0)


def test_Geom2d_EllipseTest_EvalD0_MinorVertex(ell):
    p = ell.EvalD0(math.pi / 2.0)
    near(p.X(), 0.0)
    near(p.Y(), 5.0)


def test_Geom2d_EllipseTest_EvalD1_AtZero(ell):
    d1 = ell.EvalD1(0.0).D1
    near(d1.X(), 0.0)
    near(d1.Y(), 5.0)


def test_Geom2d_EllipseTest_EvalD2_AtZero(ell):
    d2 = ell.EvalD2(0.0).D2
    near(d2.X(), -10.0)
    near(d2.Y(), 0.0)


def test_Geom2d_EllipseTest_SetMajorRadius(ell):
    ell.SetMajorRadius(20.0)
    near(ell.MajorRadius(), 20.0)


def test_Geom2d_EllipseTest_SetMinorRadius(ell):
    ell.SetMinorRadius(3.0)
    near(ell.MinorRadius(), 3.0)


def test_Geom2d_EllipseTest_PointOnEllipse_FociDistanceSum(ell):
    f1, f2 = ell.Focus1(), ell.Focus2()
    u = 0.0
    while u < 2.0 * math.pi:
        p = ell.EvalD0(u)
        near(p.Distance(f1) + p.Distance(f2), 20.0)
        u += math.pi / 6.0


def test_Geom2d_EllipseTest_Copy(ell):
    c = ell.Copy()
    assert isinstance(c, Geom2d_Ellipse)
    near(c.MajorRadius(), 10.0)
    near(c.MinorRadius(), 5.0)


def test_Geom2d_EllipseTest_Transform_Translation(ell):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(5.0, 10.0))
    ell.Transform(t)
    near(ell.Location().X(), 5.0)
    near(ell.Location().Y(), 10.0)
    near(ell.MajorRadius(), 10.0)


def test_Geom2d_EllipseTest_ReversedParameter(ell):
    u = math.pi / 4.0
    near(ell.ReversedParameter(u), 2.0 * math.pi - u)
