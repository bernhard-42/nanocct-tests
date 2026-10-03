# Translated from OCCT src/ModelingData/TKGeomBase/GTests/gce_MakeCylinder_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.gce import gce_Done, gce_MakeCylinder, gce_NegativeRadius
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pnt
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def test_gce_MakeCylinderTest_FromAxis_YBranch_DoneAndOrthogonalXAxis():
    ax = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 1))
    m = gce_MakeCylinder(ax, 5.0)
    assert m.IsDone()
    assert m.Status() == gce_Done
    cyl = m.Value()
    assert abs(cyl.Radius() - 5.0) <= CONF
    assert cyl.Axis().Direction().IsParallel(ax.Direction(), ANG)
    assert abs(cyl.Axis().Direction().XYZ().Dot(cyl.Position().XDirection().XYZ())) <= ANG


def test_gce_MakeCylinderTest_FromPoints_ZBranch_DoneAndOrthogonalXAxis():
    p1, p2 = gp_Pnt(0, 0, 0), gp_Pnt(0, 0, 10)
    m = gce_MakeCylinder(p1, p2, gp_Pnt(3, 4, 0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    cyl = m.Value()
    assert abs(cyl.Radius() - 5.0) <= CONF
    assert cyl.Axis().Direction().IsParallel(gp_Dir(p2.XYZ() - p1.XYZ()), ANG)
    assert abs(cyl.Axis().Direction().XYZ().Dot(cyl.Position().XDirection().XYZ())) <= ANG


def test_gce_MakeCylinderTest_FromAxis_NegativeRadius_NegativeRadius():
    m = gce_MakeCylinder(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), -1.0)
    assert not m.IsDone()
    assert m.Status() == gce_NegativeRadius
