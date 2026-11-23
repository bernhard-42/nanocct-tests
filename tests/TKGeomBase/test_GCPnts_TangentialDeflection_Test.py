# Translated from OCCT src/ModelingData/TKGeomBase/GTests/GCPnts_TangentialDeflection_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GCPnts import GCPnts_TangentialDeflection
from nanocct.Geom import Geom_BSplineCurve
from nanocct.Geom2d import Geom2d_BSplineCurve
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp_Pnt, gp_Pnt2d, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision


def _array(kind, values):
    a = NCollection_Array1[kind](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


def test_GCPnts_TangentialDeflectionTest_ShallowPolylineRespectsLinearDeflection():
    knots = _array(float, [0.0, 0.5, 1.0])
    mults = _array(int, [2, 1, 2])
    deflection = 0.01
    conf = Precision.Confusion_s()
    for height in (0.0, 0.005, 0.01, 0.02):
        for is2d in (False, True):
            samples = GCPnts_TangentialDeflection()
            if is2d is True:
                poles = _array(gp_Pnt2d, [gp_Pnt2d(0.0, 0.0), gp_Pnt2d(500.0, height), gp_Pnt2d(1000.0, 0.0)])
                curve2d = Geom2dAdaptor_Curve(Geom2d_BSplineCurve(poles, knots, mults, 1))
                samples.Initialize(curve2d, 0.1, deflection)
            else:
                poles = _array(gp_Pnt, [gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(500.0, height, 0.0), gp_Pnt(1000.0, 0.0, 0.0)])
                curve = GeomAdaptor_Curve(Geom_BSplineCurve(poles, knots, mults, 1))
                samples.Initialize(curve, 0.1, deflection)
            where = (height, is2d)
            n = samples.NbPoints()
            assert n >= 2, where
            assert samples.Value(1).Distance(gp_Pnt(0.0, 0.0, 0.0)) <= conf, where
            assert samples.Value(n).Distance(gp_Pnt(1000.0, 0.0, 0.0)) <= conf, where
            peak = gp_Pnt(500.0, height, 0.0)
            distance = math.inf
            for i in range(2, n + 1):
                start = samples.Value(i - 1)
                segment = gp_Vec(start, samples.Value(i))
                sq = segment.SquareMagnitude()
                t = 0.0 if sq == 0.0 else min(max(gp_Vec(start, peak).Dot(segment) / sq, 0.0), 1.0)
                distance = min(distance, peak.Distance(start.Translated(segment * t)))
            assert distance <= deflection + conf, where
