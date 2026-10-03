# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntSurf_Quadric_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Ax3, gp_Cone, gp_Dir, gp_Pnt, gp_Vec
from nanocct.IntSurf import IntSurf_Quadric
from nanocct.Precision import Precision


def test_IntSurf_Quadric_Test_ConeApexGradientRemainsFinite():
    cone = gp_Cone(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0)), 0.5, 0.0)
    quadric = IntSurf_Quadric(cone)
    apex = cone.Apex()
    assert quadric.Gradient(apex).SquareMagnitude() <= Precision.SquareConfusion_s()

    grad = gp_Vec(1.0, 0.0, 0.0)
    dist = quadric.ValAndGrad(apex, grad)
    assert abs(dist - 0.0) <= Precision.Confusion_s()
    assert grad.SquareMagnitude() <= Precision.SquareConfusion_s()
