# Translated from OCCT src/ModelingAlgorithms/TKPrim/GTests/BRepPrimAPI_MakeTorus_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeTorus
from nanocct.Geom import Geom_ToroidalSurface
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer

M_PI_2 = math.pi / 2.0


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def _create_and_check_partial_torus(r1, r2, angle1, angle2, angle=2.0 * math.pi):
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    mk = BRepPrimAPI_MakeTorus(axis, r1, r2, angle1, angle2, angle)
    shape = mk.Shape()
    if not mk.IsDone() or shape.IsNull():
        return False
    return BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeTorusTest_FullTorus():
    mk = BRepPrimAPI_MakeTorus(10.0, 2.0)
    shape = mk.Shape()
    assert mk.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
    assert _count(shape, TopAbs_FACE) == 1


def test_BRepPrimAPI_MakeTorusTest_PartialTorusAngleOnly():
    mk = BRepPrimAPI_MakeTorus(10.0, 2.0, math.pi)
    shape = mk.Shape()
    assert mk.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
    assert _count(shape, TopAbs_FACE) == 3


def test_BRepPrimAPI_MakeTorusTest_LateralFaceParameterization():
    r1, r2 = 5.0, 1.0
    mk = BRepPrimAPI_MakeTorus(r1, r2)
    shape = mk.Shape()
    assert mk.IsDone()
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    assert exp.More()
    face = TopoDS.Face(exp.Current())
    surf = BRep_Tool.Surface_s(face)
    assert isinstance(surf, Geom_ToroidalSurface)
    assert abs(surf.MajorRadius() - r1) <= 1e-10
    assert abs(surf.MinorRadius() - r2) <= 1e-10
    pnt = gp_Pnt()
    surf.D0(0.0, M_PI_2, pnt)
    assert abs(pnt.Z() - r2) <= 1e-10
    surf.D0(0.0, -M_PI_2, pnt)
    assert abs(pnt.Z() + r2) <= 1e-10


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_SymmetricAroundZero():
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    mk = BRepPrimAPI_MakeTorus(axis, 1.0, 0.1, -M_PI_2, M_PI_2, 2.094)
    shape = mk.Shape()
    assert mk.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
    assert _count(shape, TopAbs_FACE) == 5


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_SmallSymmetricRange():
    assert _create_and_check_partial_torus(10.0, 2.0, -math.pi / 4.0, math.pi / 4.0, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_Bug23612():
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    mk = BRepPrimAPI_MakeTorus(axis, 10.0, 2.0, M_PI_2, 3.0 * M_PI_2, math.pi / 4.0)
    shape = mk.Shape()
    assert mk.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_ZeroTo180():
    assert not _create_and_check_partial_torus(10.0, 2.0, 0.0, math.pi, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_Minus180ToZero():
    assert not _create_and_check_partial_torus(10.0, 2.0, -math.pi, 0.0, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_180To360():
    assert not _create_and_check_partial_torus(10.0, 2.0, math.pi, 2 * math.pi, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_PositiveRange():
    assert not _create_and_check_partial_torus(10.0, 2.0, math.pi / 4.0, 3.0 * math.pi / 4.0, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_NegativeRange():
    assert not _create_and_check_partial_torus(10.0, 2.0, -3.0 * math.pi / 4.0, -math.pi / 4.0, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_AsymmetricCrossingZero():
    assert _create_and_check_partial_torus(10.0, 2.0, -math.pi / 6.0, math.pi / 3.0, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_PartialTorus_SmallPositiveRange():
    assert _create_and_check_partial_torus(10.0, 2.0, math.pi / 6.0, math.pi / 3.0, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_RootCause_HeightOrderingAssumption():
    r1, r2 = 10.0, 2.0

    def height(a):
        return r2 * math.sin(a)

    v_min, v_max = -M_PI_2, M_PI_2
    assert height(v_max) > height(v_min)
    assert _create_and_check_partial_torus(r1, r2, v_min, v_max, math.pi / 4.0)

    v_min, v_max = M_PI_2, 3.0 * M_PI_2
    assert height(v_max) < height(v_min)
    assert _create_and_check_partial_torus(r1, r2, v_min, v_max, math.pi / 4.0)

    v_min, v_max = math.pi / 4.0, 3.0 * math.pi / 4.0
    assert abs(height(v_max) - height(v_min)) <= 1e-10
    assert not _create_and_check_partial_torus(r1, r2, v_min, v_max, math.pi / 4.0)


def test_BRepPrimAPI_MakeTorusTest_FullTorus_EqualHeights():
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    mk = BRepPrimAPI_MakeTorus(axis, 10.0, 2.0, 0.0, math.pi)
    shape = mk.Shape()
    assert mk.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
