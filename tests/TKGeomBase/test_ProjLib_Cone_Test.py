# Translated from OCCT src/ModelingData/TKGeomBase/GTests/ProjLib_Cone_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.GeomAbs import GeomAbs_Line
from nanocct.gp import gp_Ax2, gp_Circ, gp_Cone, gp_Dir, gp_Pnt
from nanocct.Precision import Precision
from nanocct.ProjLib import ProjLib_Cone


def _cone():
    return gp_Cone(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi / 6.0, 5.0)


def test_ProjLib_ConeTest_ProjectCircle_ParallelAxes_DoneLine():
    circ = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 10), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)), 2.0)
    pr = ProjLib_Cone(_cone(), circ)
    assert pr.IsDone()
    assert pr.GetType() == GeomAbs_Line
    assert abs(pr.Line().Direction().Y()) <= Precision.Angular_s()


def test_ProjLib_ConeTest_ProjectCircle_NonParallelAxes_NotDone():
    circ = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 10), gp_Dir(1, 0, 0), gp_Dir(0, 1, 0)), 2.0)
    assert not ProjLib_Cone(_cone(), circ).IsDone()


def test_ProjLib_ConeTest_ProjectCircle_OppositeNormal_DoneLineWithNegativeDirection():
    circ = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 6), gp_Dir(0, 0, -1), gp_Dir(1, 0, 0)), 2.0)
    pr = ProjLib_Cone(_cone(), circ)
    assert pr.IsDone()
    assert pr.GetType() == GeomAbs_Line
    assert pr.Line().Direction().X() < 0.0
