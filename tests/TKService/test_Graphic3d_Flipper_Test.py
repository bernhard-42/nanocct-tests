# Translated from OCCT src/Visualization/TKService/GTests/Graphic3d_Flipper_Test.cxx (LGPL-2.1 with the OCCT exception)
# Only SetRefPlane_RoundTrip is translated: Graphic3d_Flipper::Compute/Apply (NCollection_Mat4<double>) are not bound.
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.Graphic3d import Graphic3d_Flipper
from nanocct.Precision import Precision


def test_Graphic3d_FlipperTest_SetRefPlane_RoundTrip():
    flipper = Graphic3d_Flipper(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)))
    flipper.SetRefPlane(gp_Ax2(gp_Pnt(10, 20, 30), gp_Dir(1, 0, 0), gp_Dir(0, 1, 0)))
    loc = flipper.RefPlane().Location()
    tol = Precision.Confusion_s()
    assert abs(loc.X() - 10.0) <= tol
    assert abs(loc.Y() - 20.0) <= tol
    assert abs(loc.Z() - 30.0) <= tol
