# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomAdaptor_TransformedCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Geom import Geom_Circle, Geom_Line
from nanocct.GeomAbs import GeomAbs_Circle, GeomAbs_Line
from nanocct.GeomAdaptor import GeomAdaptor_TransformedCurve
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Identity, gp_Pnt, gp_Translation, gp_Trsf, gp_Vec

THE_TOLERANCE = 1e-10
PI = math.pi


def near(a, b, tol):
    return abs(a - b) <= tol


def uniform_params(first, last, n):
    step = (last - first) / (n - 1)
    return [first + i * step for i in range(n)]


def translation(dx, dy, dz):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(dx, dy, dz))
    return t


def rotation_z(angle):
    t = gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), angle)
    return t


def x_line():
    return Geom_Line(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0))


def circle2():
    return Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 2.0)


def test_GeomAdaptor_TransformedCurveTest_DefaultConstructor():
    c = GeomAdaptor_TransformedCurve()
    assert c.Is3DCurve() is True
    assert c.IsCurveOnSurface() is False
    assert c.Trsf().Form() == gp_Identity


def test_GeomAdaptor_TransformedCurveTest_ConstructWithCurveAndTrsf():
    c = GeomAdaptor_TransformedCurve(x_line(), translation(0, 0, 5))
    assert c.Is3DCurve() is True
    assert c.GetType() == GeomAbs_Line
    assert c.Trsf().Form() == gp_Translation


def test_GeomAdaptor_TransformedCurveTest_ConstructWithBounds():
    c = GeomAdaptor_TransformedCurve(x_line(), 0.0, 10.0, translation(0, 0, 5))
    assert near(c.FirstParameter(), 0.0, THE_TOLERANCE)
    assert near(c.LastParameter(), 10.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_Line_IdentityTransform():
    line = Geom_Line(gp_Pnt(1, 2, 3), gp_Dir(1, 0, 0))
    c = GeomAdaptor_TransformedCurve(line, gp_Trsf())
    assert near(c.Value(5.0).Distance(line.Value(5.0)), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_Circle_IdentityTransform():
    circ = circle2()
    c = GeomAdaptor_TransformedCurve(circ, gp_Trsf())
    assert c.GetType() == GeomAbs_Circle
    for t in [0.0, PI / 2, PI, 3 * PI / 2, 2 * PI]:
        assert near(c.Value(t).Distance(circ.Value(t)), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_Line_Translation():
    p = GeomAdaptor_TransformedCurve(x_line(), translation(0, 0, 5)).Value(3.0)
    assert near(p.X(), 3.0, THE_TOLERANCE)
    assert near(p.Y(), 0.0, THE_TOLERANCE)
    assert near(p.Z(), 5.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_Line_Rotation():
    p = GeomAdaptor_TransformedCurve(x_line(), rotation_z(PI / 2)).Value(3.0)
    assert near(p.X(), 0.0, THE_TOLERANCE)
    assert near(p.Y(), 3.0, THE_TOLERANCE)
    assert near(p.Z(), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_Circle_Translation():
    circ = circle2()
    c = GeomAdaptor_TransformedCurve(circ, translation(10, 20, 30))
    for t in uniform_params(0.0, 2 * PI, 17):
        loc = circ.Value(t)
        exp = gp_Pnt(loc.X() + 10, loc.Y() + 20, loc.Z() + 30)
        assert near(c.Value(t).Distance(exp), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_D1_Translation():
    circ = circle2()
    c = GeomAdaptor_TransformedCurve(circ, translation(10, 20, 30))
    for t in uniform_params(0.0, 2 * PI, 9):
        p, d1 = gp_Pnt(), gp_Vec()
        c.D1(t, p, d1)
        loc = circ.Value(t)
        exp = gp_Pnt(loc.X() + 10, loc.Y() + 20, loc.Z() + 30)
        assert near(p.Distance(exp), 0.0, THE_TOLERANCE)
        lp, ld1 = gp_Pnt(), gp_Vec()
        circ.D1(t, lp, ld1)
        assert near((d1 - ld1).Magnitude(), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_D1_Rotation():
    c = GeomAdaptor_TransformedCurve(x_line(), rotation_z(PI / 2))
    p, d1 = gp_Pnt(), gp_Vec()
    c.D1(3.0, p, d1)
    assert near(d1.X(), 0.0, THE_TOLERANCE)
    assert near(d1.Y(), 1.0, THE_TOLERANCE)
    assert near(d1.Z(), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_D2_Translation():
    circ = circle2()
    c = GeomAdaptor_TransformedCurve(circ, translation(10, 20, 30))
    for t in uniform_params(0.0, 2 * PI, 9):
        p, d1, d2 = gp_Pnt(), gp_Vec(), gp_Vec()
        c.D2(t, p, d1, d2)
        lp, ld1, ld2 = gp_Pnt(), gp_Vec(), gp_Vec()
        circ.D2(t, lp, ld1, ld2)
        assert near((d1 - ld1).Magnitude(), 0.0, THE_TOLERANCE)
        assert near((d2 - ld2).Magnitude(), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_D3_Rotation():
    circ = circle2()
    tr = rotation_z(PI / 4)
    c = GeomAdaptor_TransformedCurve(circ, tr)
    for t in uniform_params(0.0, 2 * PI, 9):
        p, d1, d2, d3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
        c.D3(t, p, d1, d2, d3)
        lp, ld1, ld2, ld3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
        circ.D3(t, lp, ld1, ld2, ld3)
        for o in (lp, ld1, ld2, ld3):
            o.Transform(tr)
        assert near(p.Distance(lp), 0.0, THE_TOLERANCE)
        assert near((d1 - ld1).Magnitude(), 0.0, THE_TOLERANCE)
        assert near((d2 - ld2).Magnitude(), 0.0, THE_TOLERANCE)
        assert near((d3 - ld3).Magnitude(), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_DN_Rotation():
    circ = circle2()
    tr = rotation_z(PI / 3)
    c = GeomAdaptor_TransformedCurve(circ, tr)
    for order in (1, 2, 3):
        res = c.DN(1.0, order)
        exp = circ.DN(1.0, order)
        exp.Transform(tr)
        assert near((res - exp).Magnitude(), 0.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_LineExtraction_Transform():
    lin = GeomAdaptor_TransformedCurve(x_line(), translation(0, 0, 5)).Line()
    assert near(lin.Location().X(), 0.0, THE_TOLERANCE)
    assert near(lin.Location().Y(), 0.0, THE_TOLERANCE)
    assert near(lin.Location().Z(), 5.0, THE_TOLERANCE)
    assert near(lin.Direction().X(), 1.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_CircleExtraction_Transform():
    ci = GeomAdaptor_TransformedCurve(circle2(), translation(10, 0, 0)).Circle()
    assert near(ci.Location().X(), 10.0, THE_TOLERANCE)
    assert near(ci.Location().Y(), 0.0, THE_TOLERANCE)
    assert near(ci.Location().Z(), 0.0, THE_TOLERANCE)
    assert near(ci.Radius(), 2.0, THE_TOLERANCE)


def test_GeomAdaptor_TransformedCurveTest_ShallowCopy():
    c = GeomAdaptor_TransformedCurve(x_line(), 0.0, 10.0, translation(0, 0, 5))
    cp = c.ShallowCopy()
    assert cp is not None
    assert near(c.Value(3.0).Distance(cp.Value(3.0)), 0.0, THE_TOLERANCE)
