# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntCurveSurface_IntersectionPoint_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Pnt
from nanocct.IntCurveSurface import (IntCurveSurface_In, IntCurveSurface_IntersectionPoint, IntCurveSurface_Out,
                                     IntCurveSurface_Tangent)


def test_IntCurveSurface_IntersectionPoint_DefaultConstructor_TransitionInitialized():
    pt = IntCurveSurface_IntersectionPoint()
    assert pt.Transition() == IntCurveSurface_Tangent
    assert pt.U() == 0.0
    assert pt.V() == 0.0
    assert pt.W() == 0.0


def test_IntCurveSurface_IntersectionPoint_ValueConstructor_AllFieldsSet():
    pt = IntCurveSurface_IntersectionPoint(gp_Pnt(1.0, 2.0, 3.0), 0.5, 0.6, 0.7, IntCurveSurface_In)
    assert abs(pt.Pnt().X() - 1.0) <= 1e-15
    assert abs(pt.Pnt().Y() - 2.0) <= 1e-15
    assert abs(pt.Pnt().Z() - 3.0) <= 1e-15
    assert pt.U() == 0.5
    assert pt.V() == 0.6
    assert pt.W() == 0.7
    assert pt.Transition() == IntCurveSurface_In


def test_IntCurveSurface_IntersectionPoint_SetValues_OverwritesTransition():
    pt = IntCurveSurface_IntersectionPoint()
    assert pt.Transition() == IntCurveSurface_Tangent
    pt.SetValues(gp_Pnt(5.0, 6.0, 7.0), 1.0, 2.0, 3.0, IntCurveSurface_Out)
    assert pt.Transition() == IntCurveSurface_Out
