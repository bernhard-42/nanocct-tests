# Translated from OCCT src/ModelingData/TKGeomBase/GTests/Extrema_ExtSS_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Extrema import Extrema_ExtSS, Extrema_POnSurf
from nanocct.Geom import Geom_Plane, Geom_SphericalSurface
from nanocct.GeomAdaptor import GeomAdaptor_Surface
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt
from nanocct.Precision import Precision
from nanocct.Standard import Standard_OutOfRange
from nanocct.StdFail import StdFail_NotDone


def test_Extrema_ExtSS_Test_Points_ParallelPlanes_Throws():
    p1 = Geom_Plane(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    p2 = Geom_Plane(gp_Pnt(0, 0, 5), gp_Dir(0, 0, 1))
    s1 = GeomAdaptor_Surface(p1, -10.0, 10.0, -10.0, 10.0)
    s2 = GeomAdaptor_Surface(p2, -10.0, 10.0, -10.0, 10.0)
    ext = Extrema_ExtSS(s1, s2, Precision.PConfusion_s(), Precision.PConfusion_s())
    assert ext.IsDone() is True
    assert ext.IsParallel() is True
    assert ext.NbExt() == 1
    assert math.sqrt(ext.SquareDistance(1)) == pytest.approx(5.0, abs=Precision.Confusion_s())
    with pytest.raises(Standard_OutOfRange):
        ext.Points(1, Extrema_POnSurf(), Extrema_POnSurf())


def test_Extrema_ExtSS_Test_Points_SeparatedSpheres_ReturnsExtrema():
    sph1 = Geom_SphericalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 3.0)
    sph2 = Geom_SphericalSurface(gp_Ax3(gp_Pnt(20, 0, 0), gp_Dir(0, 0, 1)), 5.0)
    s1 = GeomAdaptor_Surface(sph1, 0.0, 2.0 * math.pi, -math.pi / 2, math.pi / 2)
    s2 = GeomAdaptor_Surface(sph2, 0.0, 2.0 * math.pi, -math.pi / 2, math.pi / 2)
    ext = Extrema_ExtSS(s1, s2, Precision.PConfusion_s(), Precision.PConfusion_s())
    assert ext.IsDone() is True
    assert ext.IsParallel() is False
    assert ext.NbExt() > 0
    with pytest.raises(Standard_OutOfRange):
        ext.Points(0, Extrema_POnSurf(), Extrema_POnSurf())
    with pytest.raises(Standard_OutOfRange):
        ext.Points(ext.NbExt() + 1, Extrema_POnSurf(), Extrema_POnSurf())
    min_sq = math.inf
    for i in range(1, ext.NbExt() + 1):
        ps1, ps2 = Extrema_POnSurf(), Extrema_POnSurf()
        ext.Points(i, ps1, ps2)
        assert ps1.Value().Distance(ps2.Value()) == pytest.approx(math.sqrt(ext.SquareDistance(i)),
                                                                  abs=Precision.Confusion_s())
        min_sq = min(min_sq, ext.SquareDistance(i))
    assert math.sqrt(min_sq) == pytest.approx(12.0, abs=Precision.Confusion_s())


def test_Extrema_ExtSS_Test_Points_NotDone_Throws():
    ext = Extrema_ExtSS()
    assert ext.IsDone() is False
    with pytest.raises(StdFail_NotDone):
        ext.Points(1, Extrema_POnSurf(), Extrema_POnSurf())
