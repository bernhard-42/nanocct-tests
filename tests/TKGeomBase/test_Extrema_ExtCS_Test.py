# Translated from OCCT src/ModelingData/TKGeomBase/GTests/Extrema_ExtCS_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Extrema import Extrema_ExtCS, Extrema_POnCurv, Extrema_POnSurf
from nanocct.Geom import Geom_Line, Geom_Plane, Geom_SphericalSurface
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt
from nanocct.Precision import Precision
from nanocct.Standard import Standard_OutOfRange
from nanocct.StdFail import StdFail_NotDone


def test_Extrema_ExtCS_Test_Points_ParallelLineAndPlane_Throws():
    line = Geom_Line(gp_Pnt(0, 0, 5), gp_Dir(1, 0, 0))
    plane = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    c = GeomAdaptor_Curve(line, -10.0, 10.0)
    s = GeomAdaptor_Surface(plane, -10.0, 10.0, -10.0, 10.0)
    ext = Extrema_ExtCS(c, s, Precision.PConfusion_s(), Precision.PConfusion_s())
    assert ext.IsDone() is True
    assert ext.IsParallel() is True
    assert ext.NbExt() == 1
    assert math.sqrt(ext.SquareDistance(1)) == pytest.approx(5.0, abs=Precision.Confusion_s())
    with pytest.raises(Standard_OutOfRange):
        ext.Points(1, Extrema_POnCurv(), Extrema_POnSurf())


def test_Extrema_ExtCS_Test_Points_LineAndSphere_ReturnsExtrema():
    line = Geom_Line(gp_Pnt(0, 0, 40), gp_Dir(1, 0, 0))
    sphere = Geom_SphericalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 3.0)
    c = GeomAdaptor_Curve(line, -10.0, 10.0)
    s = GeomAdaptor_Surface(sphere, 0.0, 2.0 * math.pi, -math.pi / 2, math.pi / 2)
    ext = Extrema_ExtCS(c, s, Precision.PConfusion_s(), Precision.PConfusion_s())
    assert ext.IsDone() is True
    assert ext.IsParallel() is False
    assert ext.NbExt() > 0
    with pytest.raises(Standard_OutOfRange):
        ext.Points(0, Extrema_POnCurv(), Extrema_POnSurf())
    with pytest.raises(Standard_OutOfRange):
        ext.Points(ext.NbExt() + 1, Extrema_POnCurv(), Extrema_POnSurf())
    min_sq = math.inf
    for i in range(1, ext.NbExt() + 1):
        pc, ps = Extrema_POnCurv(), Extrema_POnSurf()
        ext.Points(i, pc, ps)
        assert pc.Value().Distance(ps.Value()) == pytest.approx(math.sqrt(ext.SquareDistance(i)),
                                                                abs=Precision.Confusion_s())
        min_sq = min(min_sq, ext.SquareDistance(i))
    assert math.sqrt(min_sq) == pytest.approx(37.0, abs=Precision.Confusion_s())


def test_Extrema_ExtCS_Test_Points_NotDone_Throws():
    ext = Extrema_ExtCS()
    assert ext.IsDone() is False
    with pytest.raises(StdFail_NotDone):
        ext.Points(1, Extrema_POnCurv(), Extrema_POnSurf())
