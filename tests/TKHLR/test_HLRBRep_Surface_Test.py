# Translated from OCCT src/ModelingAlgorithms/TKHLR/GTests/HLRBRep_Surface_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from nanocct.Geom import Geom_BSplineSurface
from nanocct.GeomAbs import GeomAbs_BSplineSurface
from nanocct.gp import gp_Pnt, gp_Trsf
from nanocct.HLRAlgo import HLRAlgo_Projector
from nanocct.HLRBRep import HLRBRep_BSurfaceTool, HLRBRep_Surface, HLRBRep_SurfaceTool
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.Precision import Precision


def test_HLRBRep_SurfaceTest_SplineSamplingAndEdgeOnProjection():
    poles = NCollection_Array2[gp_Pnt](1, 4, 1, 2)
    ys = (0.0, 0.25, -0.25, 0.0)
    for i in range(1, 5):
        for j in range(1, 3):
            poles.SetValue(i, j, gp_Pnt((i - 1) / 3.0, ys[i - 1], j - 1.0))
    knots = NCollection_Array1[float](1, 2)
    knots[1], knots[2] = 0.0, 1.0
    u_mults, v_mults = NCollection_Array1[int](1, 2), NCollection_Array1[int](1, 2)
    u_mults.Init(4)
    v_mults.Init(2)
    spline = Geom_BSplineSurface(poles, knots, knots, u_mults, v_mults, 3, 1)
    builder = BRepBuilderAPI_MakeFace(spline, Precision.Confusion_s())
    assert builder.IsDone() is True
    projector = HLRAlgo_Projector(gp_Trsf(), False, 1.0)
    surface = HLRBRep_Surface()
    surface.Surface(builder.Face())
    surface.Projector(projector)
    assert surface.GetType() == GeomAbs_BSplineSurface
    assert HLRBRep_SurfaceTool.NbSamplesU_s(surface) == spline.NbUKnots() * spline.UDegree()
    assert HLRBRep_SurfaceTool.NbSamplesV_s(surface) == spline.NbVKnots() * spline.VDegree()
    assert surface.IsSide(Precision.Confusion_s(), Precision.Angular_s()) is True

    spline.IncreaseDegree(6, 11)
    knots[1], knots[2] = -2.0, 6.0
    spline.SetUKnots(knots)
    knots[1], knots[2] = 100.0, 104.0
    spline.SetVKnots(knots)
    high_degree = BRepBuilderAPI_MakeFace(spline, Precision.Confusion_s())
    assert high_degree.IsDone() is True
    surface.Surface(high_degree.Face())
    adaptor = surface.Surface()
    u_samples = spline.NbUKnots() * spline.UDegree()
    v_samples = spline.NbVKnots() * spline.VDegree()
    for tool, arg in ((HLRBRep_SurfaceTool, surface), (HLRBRep_BSurfaceTool, adaptor)):
        assert tool.NbSamplesU_s(arg, -2.0, 6.0) == u_samples, tool
        assert tool.NbSamplesV_s(arg, 100.0, 104.0) == v_samples, tool
        assert tool.NbSamplesU_s(arg, -2.0, 2.0) == u_samples // 2, tool
        assert tool.NbSamplesV_s(arg, 102.0, 104.0) == v_samples // 2, tool
        assert tool.NbSamplesU_s(arg, -2.0, -1.5) == 5, tool
        assert tool.NbSamplesV_s(arg, 100.0, 100.25) == 5, tool
        assert tool.NbSamplesU_s(arg, -4.0, 8.0) == u_samples, tool
        assert tool.NbSamplesV_s(arg, 98.0, 106.0) == v_samples, tool
