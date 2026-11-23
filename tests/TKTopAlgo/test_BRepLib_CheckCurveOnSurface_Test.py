# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepLib_CheckCurveOnSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepLib import BRepLib_CheckCurveOnSurface
from nanocct.Geom import Geom_CylindricalSurface, Geom_Line
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp_Ax3, gp_Dir, gp_Dir2d, gp_Pnt, gp_Pnt2d
from nanocct.Precision import Precision
from nanocct.TopoDS import TopoDS_Edge, TopoDS_Face


def test_BRepLib_CheckCurveOnSurfaceTest_BothSeamPCurvesAndReuse():
    large, small = 0.2, 0.1
    conf = Precision.Confusion_s()
    builder = BRep_Builder()
    surface = Geom_CylindricalSurface(gp_Ax3(), 1.0)
    curve = Geom_Line(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    face = TopoDS_Face()
    builder.MakeFace(face, surface, conf)
    open_edge = TopoDS_Edge()
    builder.MakeEdge(open_edge, curve, conf)
    builder.UpdateEdge(open_edge, Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(0.0, 1.0)), face, conf)
    builder.Range(open_edge, 0.0, 1.0)
    for is_large_first in (False, True):
        for is_parallel in (False, True):
            where = (is_large_first, is_parallel)
            seam = TopoDS_Edge()
            builder.MakeEdge(seam, curve, conf)
            builder.UpdateEdge(seam,
                               Geom2d_Line(gp_Pnt2d(large if is_large_first else small, 0.0), gp_Dir2d(0.0, 1.0)),
                               Geom2d_Line(gp_Pnt2d(2.0 * math.pi + (small if is_large_first else large), 0.0),
                                           gp_Dir2d(0.0, 1.0)),
                               face, conf)
            builder.Range(seam, 0.0, 1.0)
            assert BRep_Tool.IsClosed_s(seam, face) is True, where
            check = BRepLib_CheckCurveOnSurface(seam, face)
            check.SetParallel(is_parallel)
            check.Perform()
            assert check.IsDone() is True, where
            assert check.MaxDistance() == pytest.approx(2.0 * math.sin(0.5 * large), abs=conf), where
            assert 0.0 <= check.MaxParameter() <= 1.0, where
            check.Init(open_edge, face)
            check.Perform()
            assert check.IsDone() is True, where
            assert check.MaxDistance() <= conf, where
