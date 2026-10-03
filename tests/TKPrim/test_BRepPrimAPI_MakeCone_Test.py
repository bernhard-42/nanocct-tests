# Translated from OCCT src/ModelingAlgorithms/TKPrim/GTests/BRepPrimAPI_MakeCone_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeCone
from nanocct.gp import gp_Ax2
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def test_BRepPrimAPI_MakeConeTest_FullCone():
    cone = BRepPrimAPI_MakeCone(gp_Ax2(), 5.0, 0.0, 10.0)
    shape = cone.Shape()
    assert cone.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeConeTest_TruncatedCone():
    cone = BRepPrimAPI_MakeCone(gp_Ax2(), 5.0, 2.0, 10.0)
    shape = cone.Shape()
    assert cone.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeConeTest_FullConeFaceCount():
    cone = BRepPrimAPI_MakeCone(gp_Ax2(), 5.0, 0.0, 10.0)
    shape = cone.Shape()
    assert cone.IsDone()
    assert _count(shape, TopAbs_FACE) == 2


def test_BRepPrimAPI_MakeConeTest_TruncatedConeFaceCount():
    cone = BRepPrimAPI_MakeCone(gp_Ax2(), 5.0, 2.0, 10.0)
    shape = cone.Shape()
    assert cone.IsDone()
    assert _count(shape, TopAbs_FACE) == 3


def test_BRepPrimAPI_MakeConeTest_TruncatedConeVolume():
    r1, r2, h = 5.0, 2.0, 10.0
    cone = BRepPrimAPI_MakeCone(gp_Ax2(), r1, r2, h)
    shape = cone.Shape()
    assert cone.IsDone()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    expected = math.pi * h / 3.0 * (r1 * r1 + r1 * r2 + r2 * r2)
    assert abs(props.Mass() - expected) <= Precision.Confusion_s()


def test_BRepPrimAPI_MakeConeTest_PartialCone():
    cone = BRepPrimAPI_MakeCone(gp_Ax2(), 5.0, 2.0, 10.0, math.pi)
    shape = cone.Shape()
    assert cone.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
    assert _count(shape, TopAbs_FACE) > 3
