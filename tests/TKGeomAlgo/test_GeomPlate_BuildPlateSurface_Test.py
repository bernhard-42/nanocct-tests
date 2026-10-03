# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/GeomPlate_BuildPlateSurface_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.GeomPlate import GeomPlate_BuildPlateSurface, GeomPlate_PointConstraint
from nanocct.gp import gp_Pnt


def test_GeomPlate_BuildPlateSurface_OCC525_PerformWithoutConstraints():
    builder = GeomPlate_BuildPlateSurface()
    builder.Perform()
    assert builder.IsDone()
    assert builder.Surface() is None


def test_GeomPlate_BuildPlateSurface_Perform_ClearsStaleResult():
    builder = GeomPlate_BuildPlateSurface(3, 10, 3, 1.0e-5, 1.0e-4, 0.01, 0.1, False)
    for p in (gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), gp_Pnt(0, 1, 0), gp_Pnt(1, 1, 0.1)):
        builder.Add(GeomPlate_PointConstraint(p, 0))
    builder.Perform()
    builder.Init()
    builder.Perform()
    assert builder.IsDone()
    assert builder.Surface() is None
