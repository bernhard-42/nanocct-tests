# Translated from OCCT src/FoundationClasses/TKMath/GTests/ElCLib_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.ElCLib import ElCLib
from nanocct.gp import (
    gp,
    gp_Ax2,
    gp_Ax22d,
    gp_Circ,
    gp_Circ2d,
    gp_Dir,
    gp_Dir2d,
    gp_Elips,
    gp_Hypr,
    gp_Lin,
    gp_Parab,
    gp_Pnt,
    gp_Pnt2d,
    gp_Vec,
    gp_Vec2d,
)
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def check3(a, b, tol=CONF):
    assert abs(a.X() - b.X()) <= tol
    assert abs(a.Y() - b.Y()) <= tol
    assert abs(a.Z() - b.Z()) <= tol


def test_ElClibTests_InPeriod():
    PI2 = 2.0 * math.pi
    assert abs(ElCLib.InPeriod_s(0.5, 0.0, PI2) - 0.5) <= CONF
    assert abs(ElCLib.InPeriod_s(PI2 + 0.5, 0.0, PI2) - 0.5) <= CONF
    assert abs(ElCLib.InPeriod_s(-0.5, 0.0, PI2) - (PI2 - 0.5)) <= CONF
    assert abs(ElCLib.InPeriod_s(-PI2 - 0.5, 0.0, PI2) - (PI2 - 0.5)) <= CONF
    assert abs(ElCLib.InPeriod_s(1.7, 1.5, 4.5) - 1.7) <= CONF
    assert abs(ElCLib.InPeriod_s(4.7, 1.5, 4.5) - 1.7) <= CONF
    assert abs(ElCLib.InPeriod_s(7.7, 1.5, 4.5) - 1.7) <= CONF
    assert abs(ElCLib.InPeriod_s(1.3, 1.5, 4.5) - 4.3) <= CONF


def test_ElClibTests_AdjustPeriodic():
    PI2 = 2.0 * math.pi

    def adjust(u1, u2):
        # C++: ElCLib::AdjustPeriodic(UFirst, ULast, Precision, U1, U2) reads and replaces U1, U2
        return ElCLib.AdjustPeriodic_s(0.0, PI2, CONF, u1, u2)

    U1, U2 = adjust(0.5, 0.7)
    assert abs(U1 - 0.5) <= CONF and abs(U2 - 0.7) <= CONF
    U1, U2 = adjust(0.5, 0.5 + PI2 + 0.2)
    assert abs(U1 - 0.5) <= CONF and abs(U2 - 0.7) <= CONF
    U1, U2 = adjust(0.5 + PI2, 0.7 + PI2)
    assert abs(U1 - 0.5) <= CONF and abs(U2 - 0.7) <= CONF
    U1, U2 = adjust(-0.5, 0.7)
    assert abs(U1 - (PI2 - 0.5)) <= CONF and abs(U2 - (0.7 + PI2)) <= CONF
    U1, U2 = adjust(1.0, 1.0 + 0.5 * CONF)
    assert abs(U1 - 1.0) <= CONF and abs(U2 - (1.0 + PI2)) <= CONF


def test_ElClibTests_Line3D():
    aLoc = gp_Pnt(1.0, 2.0, 3.0)
    aDir = gp_Dir(gp_Dir.D.Z)
    aLin = gp_Lin(aLoc, aDir)
    aParam = 5.0

    aExpected = gp_Pnt(1.0, 2.0, 8.0)
    check3(ElCLib.Value_s(aParam, aLin), aExpected)

    p, v = gp_Pnt(), gp_Vec()
    ElCLib.D1_s(aParam, aLin, p, v)
    check3(p, aExpected)
    check3(v, gp_Vec(aDir))

    check3(ElCLib.DN_s(aParam, aLin, 1), gp_Vec(aDir))
    check3(ElCLib.DN_s(aParam, aLin, 2), gp_Vec(0.0, 0.0, 0.0))

    assert abs(ElCLib.Parameter_s(aLin, gp_Pnt(1.0, 2.0, 10.0)) - 7.0) <= CONF


def test_ElClibTests_Circle3D():
    anAxis = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.X))
    R = 2.0
    aCircle = gp_Circ(anAxis, R)
    u = math.pi / 4.0

    aExp = gp_Pnt(R * math.cos(u), R * math.sin(u), 0.0)
    check3(ElCLib.Value_s(u, aCircle), aExp)

    p, v1 = gp_Pnt(), gp_Vec()
    ElCLib.D1_s(u, aCircle, p, v1)
    check3(p, aExp)
    e1 = gp_Vec(-R * math.sin(u), R * math.cos(u), 0.0)
    check3(v1, e1)

    p, v1, v2 = gp_Pnt(), gp_Vec(), gp_Vec()
    ElCLib.D2_s(u, aCircle, p, v1, v2)
    check3(p, aExp)
    check3(v1, e1)
    e2 = gp_Vec(-R * math.cos(u), -R * math.sin(u), 0.0)
    check3(v2, e2)

    p, v1, v2, v3 = gp_Pnt(), gp_Vec(), gp_Vec(), gp_Vec()
    ElCLib.D3_s(u, aCircle, p, v1, v2, v3)
    check3(p, aExp)
    check3(v1, e1)
    check3(v2, e2)
    e3 = gp_Vec(R * math.sin(u), -R * math.cos(u), 0.0)
    check3(v3, e3)

    check3(ElCLib.DN_s(u, aCircle, 1), e1)
    check3(ElCLib.DN_s(u, aCircle, 2), e2)
    check3(ElCLib.DN_s(u, aCircle, 3), e3)

    assert abs(ElCLib.Parameter_s(aCircle, aExp) - u) <= CONF


def test_ElClibTests_Ellipse3D():
    anAxis = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.X))
    a, b = 3.0, 2.0
    anEllipse = gp_Elips(anAxis, a, b)
    u = math.pi / 4.0

    aExp = gp_Pnt(a * math.cos(u), b * math.sin(u), 0.0)
    check3(ElCLib.Value_s(u, anEllipse), aExp)

    p, v1 = gp_Pnt(), gp_Vec()
    ElCLib.D1_s(u, anEllipse, p, v1)
    check3(p, aExp)
    check3(v1, gp_Vec(-a * math.sin(u), b * math.cos(u), 0.0))

    assert abs(ElCLib.Parameter_s(anEllipse, aExp) - u) <= CONF


def test_ElClibTests_Hyperbola3D():
    anAxis = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.X))
    a, b = 3.0, 2.0
    aHyp = gp_Hypr(anAxis, a, b)
    u = 0.5

    aExp = gp_Pnt(a * math.cosh(u), b * math.sinh(u), 0.0)
    check3(ElCLib.Value_s(u, aHyp), aExp)

    p, v1 = gp_Pnt(), gp_Vec()
    ElCLib.D1_s(u, aHyp, p, v1)
    check3(p, aExp)
    check3(v1, gp_Vec(a * math.sinh(u), b * math.cosh(u), 0.0))

    assert abs(ElCLib.Parameter_s(aHyp, aExp) - u) <= CONF


def test_ElClibTests_Parabola3D():
    anAxis = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.X))
    f = 2.0
    aParab = gp_Parab(anAxis, f)
    u = 3.0

    aExp = gp_Pnt(u * u / (4.0 * f), u, 0.0)
    check3(ElCLib.Value_s(u, aParab), aExp)

    p, v1 = gp_Pnt(), gp_Vec()
    ElCLib.D1_s(u, aParab, p, v1)
    check3(p, aExp)
    check3(v1, gp_Vec(u / (2.0 * f), 1.0, 0.0))

    assert abs(ElCLib.Parameter_s(aParab, aExp) - u) <= CONF


def test_ElClibTests_To3dConversion():
    aLoc = gp_Pnt(1.0, 2.0, 3.0)
    anAxis = gp_Ax2(aLoc, gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.X))

    check3(ElCLib.To3d_s(anAxis, gp_Pnt2d(2.0, 3.0)), gp_Pnt(3.0, 5.0, 3.0))
    check3(ElCLib.To3d_s(anAxis, gp_Vec2d(1.0, 2.0)), gp_Vec(1.0, 2.0, 0.0))
    s5 = math.sqrt(5.0)
    check3(ElCLib.To3d_s(anAxis, gp_Dir2d(1.0, 2.0)), gp_Dir(1.0 / s5, 2.0 / s5, 0.0))

    anAxis2d = gp_Ax22d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(gp_Dir2d.D.X), True)
    aCirc3d = ElCLib.To3d_s(anAxis, gp_Circ2d(anAxis2d, 2.0))
    assert abs(aCirc3d.Radius() - 2.0) <= CONF
    check3(aCirc3d.Location(), aLoc)


def test_ElClibTests_Parabola3D_NearZeroFocal_DegeneratesToLine():
    anAxis = gp_Ax2(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0))
    f = 0.5 * gp.Resolution_s()
    u = 4.0

    check3(ElCLib.ParabolaValue_s(u, anAxis, f), gp_Pnt(1.0 + u, 2.0, 3.0))

    p, d1 = gp_Pnt(), gp_Vec()
    ElCLib.ParabolaD1_s(u, anAxis, f, p, d1)
    check3(p, gp_Pnt(1.0 + u, 2.0, 3.0))
    check3(d1, gp_Vec(1.0, 0.0, 0.0))

    d2 = gp_Vec()
    ElCLib.ParabolaD2_s(u, anAxis, f, p, d1, d2)
    check3(d2, gp_Vec(0.0, 0.0, 0.0))

    check3(ElCLib.ParabolaDN_s(u, anAxis, f, 1), gp_Vec(1.0, 0.0, 0.0))
    check3(ElCLib.ParabolaDN_s(u, anAxis, f, 2), gp_Vec(0.0, 0.0, 0.0))


def test_ElClibTests_Parabola2D_NearZeroFocal_DegeneratesToLine():
    anAxis = gp_Ax22d(gp_Pnt2d(1.0, 2.0), gp_Dir2d(1.0, 0.0), True)
    f = 0.5 * gp.Resolution_s()
    u = 3.0

    v = ElCLib.ParabolaValue_s(u, anAxis, f)
    assert abs(v.X() - (1.0 + u)) <= CONF
    assert abs(v.Y() - 2.0) <= CONF

    p, d1 = gp_Pnt2d(), gp_Vec2d()
    ElCLib.ParabolaD1_s(u, anAxis, f, p, d1)
    assert abs(p.X() - (1.0 + u)) <= CONF
    assert abs(p.Y() - 2.0) <= CONF
    assert abs(d1.X() - 1.0) <= CONF
    assert abs(d1.Y() - 0.0) <= CONF

    d2 = gp_Vec2d()
    ElCLib.ParabolaD2_s(u, anAxis, f, p, d1, d2)
    assert abs(d2.X()) <= CONF
    assert abs(d2.Y()) <= CONF

    dn1 = ElCLib.ParabolaDN_s(u, anAxis, f, 1)
    dn2 = ElCLib.ParabolaDN_s(u, anAxis, f, 2)
    assert abs(dn1.X() - 1.0) <= CONF
    assert abs(dn1.Y()) <= CONF
    assert abs(dn2.X()) <= CONF
    assert abs(dn2.Y()) <= CONF


def test_ElClibTests_Parabola3D_AboveResolutionFocal_NotDegenerate():
    anAxis = gp_Ax2(gp_Pnt(1.0, 2.0, 3.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0))
    f = 2.0 * gp.Resolution_s()
    u = 1.0
    v = ElCLib.ParabolaValue_s(u, anAxis, f)
    assert abs(v.X() - (1.0 + u)) > 1.0
    assert ElCLib.ParabolaDN_s(u, anAxis, f, 2).Magnitude() > 1.0


def test_ElClibTests_Parabola2D_AboveResolutionFocal_NotDegenerate():
    anAxis = gp_Ax22d(gp_Pnt2d(1.0, 2.0), gp_Dir2d(1.0, 0.0), True)
    f = 2.0 * gp.Resolution_s()
    u = 1.0
    v = ElCLib.ParabolaValue_s(u, anAxis, f)
    assert abs(v.X() - (1.0 + u)) > 1.0
    assert ElCLib.ParabolaDN_s(u, anAxis, f, 2).Magnitude() > 1.0
