# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Ax3_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gp import gp, gp_Ax1, gp_Ax3
from nanocct.Precision import Precision

ANG = Precision.Angular_s()


def test_gp_Ax3_Test_OCC29406_SetDirectionPreservesOrientation():
    DX, DZ = gp.DX_s(), gp.DZ_s()
    # Main (Z) direction
    a1, a2, a3, a4 = gp_Ax3(), gp_Ax3(), gp_Ax3(), gp_Ax3()
    a3.ZReverse()
    a4.ZReverse()
    for ax, d in ((a1, DX), (a2, -DX), (a3, DX), (a4, -DX)):
        before = ax.Direct()
        ax.SetDirection(d)
        assert ax.Direct() == before
        assert d.IsEqual(ax.Direction(), ANG)

    a5, a6 = gp_Ax3(), gp_Ax3()
    a01 = gp_Ax1(gp.Origin_s(), DX)
    a02 = gp_Ax1(gp.Origin_s(), -DX)
    for ax, a0 in ((a5, a01), (a6, a02)):
        before = ax.Direct()
        ax.SetAxis(a0)
        assert ax.Direct() == before
        assert a0.Direction().IsEqual(ax.Direction(), ANG)

    # X direction
    a1, a2, a3, a4 = gp_Ax3(), gp_Ax3(), gp_Ax3(), gp_Ax3()
    a3.XReverse()
    a4.XReverse()
    before = a1.Direct()
    a1.SetXDirection(DZ)
    assert a1.Direct() == before
    good_y1 = a1.Direction().Crossed(DZ)
    if a1.Direct():
        assert good_y1.IsEqual(a1.YDirection(), ANG)
    else:
        assert good_y1.IsOpposite(a1.YDirection(), ANG)
    for ax, d in ((a2, -DZ), (a3, DZ), (a4, -DZ)):
        before = ax.Direct()
        ax.SetXDirection(d)
        assert ax.Direct() == before

    # Y direction
    a1, a2, a3, a4 = gp_Ax3(), gp_Ax3(), gp_Ax3(), gp_Ax3()
    a3.YReverse()
    a4.YReverse()
    before = a1.Direct()
    a1.SetYDirection(DZ)
    assert a1.Direct() == before
    good_x1 = a1.Direction().Crossed(DZ)
    if a1.Direct():
        assert good_x1.IsOpposite(a1.XDirection(), ANG)
    else:
        assert good_x1.IsEqual(a1.XDirection(), ANG)
    for ax, d in ((a2, -DZ), (a3, DZ), (a4, -DZ)):
        before = ax.Direct()
        ax.SetYDirection(d)
        assert ax.Direct() == before
