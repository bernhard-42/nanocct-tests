# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepClass3d_SolidClassifier_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepClass3d import BRepClass3d_SolidClassifier
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from nanocct.gp import gp_Pnt
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_IN, TopAbs_ON, TopAbs_OUT


def _box():
    mk = BRepPrimAPI_MakeBox(gp_Pnt(0.0, 0.0, 0.0), 10.0, 10.0, 10.0)
    box = mk.Shape()
    assert mk.IsDone()
    return box


def _state(shape, pnt):
    classifier = BRepClass3d_SolidClassifier(shape)
    classifier.Perform(pnt, Precision.Confusion_s())
    return classifier.State()


def test_BRepClass3d_SolidClassifierTest_PointInside_Box():
    assert _state(_box(), gp_Pnt(5.0, 5.0, 5.0)) == TopAbs_IN


def test_BRepClass3d_SolidClassifierTest_PointOutside_Box():
    assert _state(_box(), gp_Pnt(20.0, 20.0, 20.0)) == TopAbs_OUT


def test_BRepClass3d_SolidClassifierTest_PointOnFace_Box():
    assert _state(_box(), gp_Pnt(5.0, 5.0, 0.0)) == TopAbs_ON


def test_BRepClass3d_SolidClassifierTest_PointInside_Sphere():
    mk = BRepPrimAPI_MakeSphere(10.0)
    sphere = mk.Shape()
    assert mk.IsDone()
    assert _state(sphere, gp_Pnt(0.0, 0.0, 0.0)) == TopAbs_IN


def test_BRepClass3d_SolidClassifierTest_PerformInfinitePoint():
    box = _box()
    classifier = BRepClass3d_SolidClassifier(box)
    classifier.PerformInfinitePoint(Precision.Confusion_s())
    assert classifier.State() == TopAbs_OUT
