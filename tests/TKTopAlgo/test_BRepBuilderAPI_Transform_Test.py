# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepBuilderAPI_Transform_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepBuilderAPI import BRepBuilderAPI_Transform
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision


def _box(*args):
    mk = BRepPrimAPI_MakeBox(*args)
    box = mk.Shape()
    assert mk.IsDone()
    return box


def _props(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props


def test_BRepBuilderAPI_TransformTest_Translate():
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(100.0, 0.0, 0.0))
    result = BRepBuilderAPI_Transform(_box(10.0, 10.0, 10.0), trsf).Shape()
    assert not result.IsNull()
    com = _props(result).CentreOfMass()
    c = Precision.Confusion_s()
    assert abs(com.X() - 105.0) <= c
    assert abs(com.Y() - 5.0) <= c
    assert abs(com.Z() - 5.0) <= c


def test_BRepBuilderAPI_TransformTest_Rotate():
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), math.pi / 2.0)
    result = BRepBuilderAPI_Transform(_box(10.0, 10.0, 10.0), trsf).Shape()
    assert not result.IsNull()
    com = _props(result).CentreOfMass()
    c = Precision.Confusion_s()
    assert abs(com.X() + 5.0) <= c
    assert abs(com.Y() - 5.0) <= c


def test_BRepBuilderAPI_TransformTest_Scale():
    trsf = gp_Trsf()
    trsf.SetScale(gp_Pnt(0.0, 0.0, 0.0), 2.0)
    result = BRepBuilderAPI_Transform(_box(10.0, 10.0, 10.0), trsf).Shape()
    assert not result.IsNull()
    assert abs(_props(result).Mass() - 8000.0) <= Precision.Confusion_s()


def test_BRepBuilderAPI_TransformTest_Mirror():
    trsf = gp_Trsf()
    trsf.SetMirror(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)))
    result = BRepBuilderAPI_Transform(_box(gp_Pnt(10.0, 0.0, 0.0), 10.0, 10.0, 10.0), trsf).Shape()
    assert not result.IsNull()
    assert _props(result).CentreOfMass().X() < 0.0


def test_BRepBuilderAPI_TransformTest_ShapeValidity():
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(50.0, 50.0, 50.0))
    result = BRepBuilderAPI_Transform(_box(10.0, 10.0, 10.0), trsf).Shape()
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()
