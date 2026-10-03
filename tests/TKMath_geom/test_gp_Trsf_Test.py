# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Trsf_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf
from nanocct.Precision import Precision


def test_gp_TrsfTest_OCC23361_TransformationComposition():
    p = gp_Pnt(0, 0, 2)
    t1, t2 = gp_Trsf(), gp_Trsf()
    t1.SetRotation(gp_Ax1(p, gp_Dir(gp_Dir.D.Y)), -0.49328285294022267)
    t2.SetRotation(gp_Ax1(p, gp_Dir(gp_Dir.D.Z)), 0.87538474718473880)
    tcomp = t2 * t1
    p1 = gp_Pnt(10, 3, 4)
    p2 = p1.Transformed(tcomp)
    p3 = p1.Transformed(t1)
    p3.Transform(t2)
    assert p2.IsEqual(p3, Precision.Confusion_s())
