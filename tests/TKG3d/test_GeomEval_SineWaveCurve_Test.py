# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomEval_SineWaveCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomEval import GeomEval_SineWaveCurve
from nanocct.gp import gp_Ax2, gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import (
    Standard_ConstructionError,
    Standard_NoSuchObject,
    Standard_NotImplemented,
)

THE_FD_TOL = 1e-5
CONF = Precision.Confusion_s()


def test_GeomEval_SineWaveCurveTest_Construction_ValidParams():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 2.0, 3.0, 0.0)
    assert abs(c.Amplitude() - 2.0) <= CONF
    assert abs(c.Omega() - 3.0) <= CONF
    assert abs(c.Phase() - 0.0) <= CONF


def test_GeomEval_SineWaveCurveTest_Construction_InvalidParams_Throws():
    ax = gp_Ax2()
    for a, om in ((0.0, 1.0), (-1.0, 1.0), (1.0, 0.0), (1.0, -1.0)):
        with pytest.raises(Standard_ConstructionError):
            GeomEval_SineWaveCurve(ax, a, om)


def test_GeomEval_SineWaveCurveTest_EvalD0_AtKnownPoints():
    a, om = 2.0, 3.0
    c = GeomEval_SineWaveCurve(gp_Ax2(), a, om, 0.0)
    p0 = c.EvalD0(0.0)
    assert abs(p0.X()) <= CONF
    assert abs(p0.Y()) <= CONF
    assert abs(p0.Z()) <= CONF
    t1 = math.pi / (2.0 * om)
    p1 = c.EvalD0(t1)
    assert abs(p1.X() - t1) <= CONF
    assert abs(p1.Y() - a) <= CONF
    assert abs(p1.Z()) <= CONF


def test_GeomEval_SineWaveCurveTest_IsPeriodic():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 2.0, 3.0, 0.0)
    assert c.IsPeriodic() is False
    with pytest.raises(Standard_NoSuchObject):
        c.Period()
    assert c.IsClosed() is False


def test_GeomEval_SineWaveCurveTest_Reverse_NotImplemented():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 2.0, 3.0, 0.0)
    with pytest.raises(Standard_NotImplemented):
        c.Reverse()
    with pytest.raises(Standard_NotImplemented):
        c.ReversedParameter(0.5)


def test_GeomEval_SineWaveCurveTest_EvalD1_ConsistentWithD0():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 2.0, 3.0, 0.5)
    t = 1.0
    d1 = c.EvalD1(t)
    p1 = c.EvalD0(t + CONF)
    p2 = c.EvalD0(t - CONF)
    fd = gp_Vec((p1.XYZ() - p2.XYZ()) / (2.0 * CONF))
    assert abs(d1.D1.X() - fd.X()) <= THE_FD_TOL
    assert abs(d1.D1.Y() - fd.Y()) <= THE_FD_TOL
    assert abs(d1.D1.Z() - fd.Z()) <= THE_FD_TOL


def test_GeomEval_SineWaveCurveTest_EvalD2_Analytical():
    a, om, phi = 2.0, 3.0, 0.5
    c = GeomEval_SineWaveCurve(gp_Ax2(), a, om, phi)
    t = 1.0
    d2 = c.EvalD2(t)
    exp_y = -a * om * om * math.sin(om * t + phi)
    assert abs(d2.D2.X()) <= CONF
    assert abs(d2.D2.Y() - exp_y) <= CONF
    assert abs(d2.D2.Z()) <= CONF


def test_GeomEval_SineWaveCurveTest_ComparisonWithLine_ZeroAmplitude_Like():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 1e-10, 1.0, 0.0)
    d3 = c.EvalD3(1.0)
    assert abs(d3.D2.Magnitude()) <= 1e-5
    assert abs(d3.D3.Magnitude()) <= 1e-5


def test_GeomEval_SineWaveCurveTest_Transform_NotImplemented():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 2.0, 3.0, 0.5)
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(1.0, 2.0, 3.0))
    with pytest.raises(Standard_NotImplemented):
        c.Transform(trsf)
    with pytest.raises(Standard_NotImplemented):
        c.Transformed(trsf)


def test_GeomEval_SineWaveCurveTest_Copy_Independent():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 2.0, 3.0, 0.5)
    cp = c.Copy()
    assert cp is not None
    assert isinstance(cp, GeomEval_SineWaveCurve)
    assert abs(cp.Amplitude() - 2.0) <= CONF
    assert abs(cp.Omega() - 3.0) <= CONF
    assert abs(cp.Phase() - 0.5) <= CONF


def test_GeomEval_SineWaveCurveTest_DumpJson_NoCrash():
    c = GeomEval_SineWaveCurve(gp_Ax2(), 2.0, 3.0, 0.0)
    s = c.DumpJson()
    assert isinstance(s, str)
