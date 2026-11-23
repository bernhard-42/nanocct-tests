# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BOPAlgo_MakerVolume_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.BOPAlgo import BOPAlgo_MakerVolume
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.gp import gp_Ax3, gp_Cone, gp_Dir, gp_Pln, gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_List
from nanocct.TopAbs import TopAbs_SOLID
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape


def _plane(point, normal):
    return BRepBuilderAPI_MakeFace(gp_Pln(point, normal), -1e6, 1e6, -1e6, 1e6).Face()


def _cone(point, normal, degrees):
    return BRepBuilderAPI_MakeFace(gp_Cone(gp_Ax3(point, normal), degrees * math.pi / 180.0, 0.0),
                                   0.0, 2.0 * math.pi, 0.0, 1e6).Face()


def test_BOPAlgo_MakerVolumeTest_ConePlaneProjectionPreservesVolumes():
    side = gp_Dir(0.70710678118654746, 4.4408920985006262e-016, 0.70710678118654768)
    down = gp_Dir(0, -1, 1.1102230246251565e-016)
    up = gp_Dir(0, 1, -1.1102230246251565e-016)
    faces = NCollection_List[TopoDS_Shape]()
    faces.Append(_plane(gp_Pnt(27.577164466275352, -1038.2137499999999, 27.577164466275359), side))
    faces.Append(_cone(gp_Pnt(0, 518.47000000000003, 0), down, 14.999999999912038))
    faces.Append(_plane(gp_Pnt(-27.577164466275352, -1038.2137499999999, -27.577164466275359), side))
    faces.Append(_plane(gp_Pnt(0, -786.50743635718959, 3.8387493219403887e-014), down))
    faces.Append(_plane(gp_Pnt(0, -796.42849000000001, 9.2386370775798815e-015), up))
    faces.Append(_cone(gp_Pnt(0, -440.74363604000001, 0), down, 45.110284878807235))
    maker = BOPAlgo_MakerVolume()
    maker.SetArguments(faces)
    maker.Perform()
    assert maker.HasErrors() is False
    result = maker.Shape()
    assert result.IsNull() is False
    nb_solids = 0
    exp = TopExp_Explorer(result, TopAbs_SOLID)
    while exp.More():
        nb_solids += 1
        exp.Next()
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(result, props, 1e-4)
    assert nb_solids == 17
    assert props.Mass() == pytest.approx(5576802.09207427, abs=1.0)
    assert BRepCheck_Analyzer(result).IsValid() is True
