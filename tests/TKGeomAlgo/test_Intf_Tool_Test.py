# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/Intf_Tool_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.Bnd import Bnd_Box, Bnd_Box2d
from nanocct.gp import gp_Ax2, gp_Ax2d, gp_Dir, gp_Dir2d, gp_Hypr, gp_Hypr2d, gp_Parab, gp_Parab2d, gp_Pnt, gp_Pnt2d
from nanocct.Intf import Intf_Tool
from nanocct.Precision import Precision

INF = Precision.Infinite_s()


def _check_segments(tool, check_finite=True):
    n = tool.NbSegments()
    assert 0 <= n <= 6
    for i in range(1, n + 1):
        b = tool.BeginParam(i)
        e = tool.EndParam(i)
        if check_finite:
            assert math.isfinite(b) or b == -INF
            assert math.isfinite(e) or e == INF
        assert b <= e


def test_Intf_Tool_Hypr2dBox_ProducesValidSegments():
    hypr = gp_Hypr2d(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 2.0, 1.0)
    domain = Bnd_Box2d()
    domain.Update(-5.0, -5.0, 5.0, 5.0)
    result = Bnd_Box2d()
    tool = Intf_Tool()
    tool.Hypr2dBox(hypr, domain, result)
    _check_segments(tool)


def test_Intf_Tool_Parab2dBox_ProducesValidSegments():
    parab = gp_Parab2d(gp_Ax2d(gp_Pnt2d(0, 0), gp_Dir2d(1, 0)), 1.0)
    domain = Bnd_Box2d()
    domain.Update(-5.0, -5.0, 5.0, 5.0)
    result = Bnd_Box2d()
    tool = Intf_Tool()
    tool.Parab2dBox(parab, domain, result)
    _check_segments(tool)


def test_Intf_Tool_ParabBox_ProducesValidSegments():
    parab = gp_Parab(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    domain = Bnd_Box()
    domain.Update(-5.0, -5.0, -5.0, 5.0, 5.0, 5.0)
    result = Bnd_Box()
    tool = Intf_Tool()
    tool.ParabBox(parab, domain, result)
    _check_segments(tool, check_finite=False)


def test_Intf_Tool_HyprBox_ProducesValidSegments():
    hypr = gp_Hypr(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 2.0, 1.0)
    domain = Bnd_Box()
    domain.Update(-5.0, -5.0, -5.0, 5.0, 5.0, 5.0)
    result = Bnd_Box()
    tool = Intf_Tool()
    tool.HyprBox(hypr, domain, result)
    assert 0 <= tool.NbSegments() <= 6


def test_Intf_Tool_Hypr2dBox_NoIntersection_ZeroSegments():
    hypr = gp_Hypr2d(gp_Ax2d(gp_Pnt2d(100, 100), gp_Dir2d(1, 0)), 0.1, 0.05)
    domain = Bnd_Box2d()
    domain.Update(-1.0, -1.0, 1.0, 1.0)
    result = Bnd_Box2d()
    tool = Intf_Tool()
    tool.Hypr2dBox(hypr, domain, result)
    assert tool.NbSegments() == 0
