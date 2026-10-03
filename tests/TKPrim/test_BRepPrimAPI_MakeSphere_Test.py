# Translated from OCCT src/ModelingAlgorithms/TKPrim/GTests/BRepPrimAPI_MakeSphere_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeSphere
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


def test_BRepPrimAPI_MakeSphereTest_FullSphere():
    sph = BRepPrimAPI_MakeSphere(5.0)
    shape = sph.Shape()
    assert sph.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()


def test_BRepPrimAPI_MakeSphereTest_FaceCount():
    sph = BRepPrimAPI_MakeSphere(5.0)
    shape = sph.Shape()
    assert sph.IsDone()
    assert _count(shape, TopAbs_FACE) == 1


def test_BRepPrimAPI_MakeSphereTest_Volume():
    r = 5.0
    sph = BRepPrimAPI_MakeSphere(r)
    shape = sph.Shape()
    assert sph.IsDone()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    assert abs(props.Mass() - (4.0 / 3.0) * math.pi * r * r * r) <= 0.01


def test_BRepPrimAPI_MakeSphereTest_PartialSphere_AngleLimited():
    sph = BRepPrimAPI_MakeSphere(5.0, math.pi)
    shape = sph.Shape()
    assert sph.IsDone()
    assert not shape.IsNull()
    assert BRepCheck_Analyzer(shape).IsValid()
    assert _count(shape, TopAbs_FACE) > 1


def test_BRepPrimAPI_MakeSphereTest_CenterOfMass():
    sph = BRepPrimAPI_MakeSphere(5.0)
    shape = sph.Shape()
    assert sph.IsDone()
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    com = props.CentreOfMass()
    c = Precision.Confusion_s()
    assert abs(com.X()) <= c
    assert abs(com.Y()) <= c
    assert abs(com.Z()) <= c
