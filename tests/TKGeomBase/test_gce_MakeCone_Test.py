# Translated from OCCT src/ModelingData/TKGeomBase/GTests/gce_MakeCone_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.gce import gce_Done, gce_MakeCone, gce_NegativeRadius
from nanocct.gp import gp_Ax2, gp_Cone, gp_Dir, gp_Lin, gp_Pnt
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()
ANG = Precision.Angular_s()


def _base():
    return gp_Cone(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.pi / 6.0, 10.0)


def _check_axis(cone, p1, p2):
    assert cone.Axis().Direction().IsParallel(gp_Dir(p2.XYZ() - p1.XYZ()), ANG)
    dot = cone.Axis().Direction().XYZ().Dot(cone.Position().XDirection().XYZ())
    assert abs(dot) <= ANG


def test_gce_MakeConeTest_FromConeAndDist_Valid_Done():
    base = _base()
    m = gce_MakeCone(base, 2.0)
    assert m.IsDone()
    assert m.Status() == gce_Done
    cone = m.Value()
    assert abs(cone.RefRadius() - (base.RefRadius() + 2.0 / math.cos(base.SemiAngle()))) <= CONF
    assert abs(cone.SemiAngle() - base.SemiAngle()) <= CONF
    assert cone.Location().IsEqual(base.Location(), CONF)
    assert cone.Axis().Direction().IsParallel(base.Axis().Direction(), ANG)


def test_gce_MakeConeTest_FromConeAndDist_TooNegative_NegativeRadius():
    base = _base()
    m = gce_MakeCone(base, -(base.RefRadius() * math.cos(base.SemiAngle()) + 1.0))
    assert not m.IsDone()
    assert m.Status() == gce_NegativeRadius


def test_gce_MakeConeTest_FromConeAndPoint_Valid_Done():
    base = _base()
    r = 12.0 + 4.0 * math.tan(base.SemiAngle())
    m = gce_MakeCone(base, gp_Pnt(r, 0.0, 4.0))
    assert m.IsDone()
    assert m.Status() == gce_Done
    assert abs(m.Value().RefRadius() - 12.0) <= CONF


def test_gce_MakeConeTest_FromConeAndPoint_NoValidParallelCone_NegativeRadius():
    m = gce_MakeCone(_base(), gp_Pnt(1.0, 0.0, 20.0))
    assert not m.IsDone()
    assert m.Status() == gce_NegativeRadius


def test_gce_MakeConeTest_FromConeAndPoint_TwoCandidates_ChoosesNearestToBaseCone():
    base = _base()
    p = gp_Pnt(5.0, 0.0, -20.0)
    m = gce_MakeCone(base, p)
    assert m.IsDone()
    assert m.Status() == gce_Done
    radius = gp_Lin(base.Axis()).Distance(p)
    v = (p.XYZ() - base.Location().XYZ()).Dot(base.Axis().Direction().XYZ())
    t, c = math.tan(base.SemiAngle()), math.cos(base.SemiAngle())
    c1, c2 = radius - v * t, -radius - v * t
    d1, d2 = abs((c1 - base.RefRadius()) * c), abs((c2 - base.RefRadius()) * c)
    exp = c1 if d1 <= d2 else c2
    assert abs(m.Value().RefRadius() - exp) <= CONF


def test_gce_MakeConeTest_FromTwoPointsAndTwoRadii_YBranch_DoneAndOrthogonalXAxis():
    p1, p2 = gp_Pnt(0, 0, 0), gp_Pnt(0, 10, 10)
    m = gce_MakeCone(p1, p2, 3.0, 2.0)
    assert m.IsDone()
    assert m.Status() == gce_Done
    _check_axis(m.Value(), p1, p2)


def test_gce_MakeConeTest_FromTwoPointsAndTwoRadii_ZBranch_DoneAndOrthogonalXAxis():
    p1, p2 = gp_Pnt(0, 0, 0), gp_Pnt(0, 0, 10)
    m = gce_MakeCone(p1, p2, 4.0, 2.0)
    assert m.IsDone()
    assert m.Status() == gce_Done
    _check_axis(m.Value(), p1, p2)


def test_gce_MakeConeTest_FromFourPoints_YBranch_DoneAndOrthogonalXAxis():
    p1, p2 = gp_Pnt(0, 0, 0), gp_Pnt(0, 10, 10)
    m = gce_MakeCone(p1, p2, gp_Pnt(3, 0, 0), gp_Pnt(5, 4, 4))
    assert m.IsDone()
    assert m.Status() == gce_Done
    _check_axis(m.Value(), p1, p2)


def test_gce_MakeConeTest_FromFourPoints_ZBranch_DoneAndOrthogonalXAxis():
    p1, p2 = gp_Pnt(0, 0, 0), gp_Pnt(0, 0, 10)
    m = gce_MakeCone(p1, p2, gp_Pnt(4, 0, 0), gp_Pnt(2, 0, 5))
    assert m.IsDone()
    assert m.Status() == gce_Done
    _check_axis(m.Value(), p1, p2)
