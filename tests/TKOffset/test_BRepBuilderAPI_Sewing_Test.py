# Translated from OCCT src/ModelingAlgorithms/TKOffset/GTests/BRepBuilderAPI_Sewing_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Sewing
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def _box():
    maker = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0)
    box = maker.Shape()
    assert maker.IsDone()
    return box


def _sew_two_faces():
    exp = TopExp_Explorer(_box(), TopAbs_FACE)
    assert exp.More()
    face1 = TopoDS.Face(exp.Current())
    exp.Next()
    assert exp.More()
    face2 = TopoDS.Face(exp.Current())
    sewing = BRepBuilderAPI_Sewing()
    sewing.Add(face1)
    sewing.Add(face2)
    sewing.Perform()
    return sewing


def test_BRepBuilderAPI_SewingTest_SewTwoFaces():
    assert not _sew_two_faces().SewedShape().IsNull()


def test_BRepBuilderAPI_SewingTest_NbFreeEdges():
    assert _sew_two_faces().NbFreeEdges() > 0


def test_BRepBuilderAPI_SewingTest_NbDegeneratedShapes():
    assert _sew_two_faces().NbDegeneratedShapes() == 0


def test_BRepBuilderAPI_SewingTest_SetTolerance():
    sewing = BRepBuilderAPI_Sewing()
    sewing.SetTolerance(0.01)
    assert abs(sewing.Tolerance() - 0.01) <= Precision.Confusion_s()


def test_BRepBuilderAPI_SewingTest_SewAllBoxFaces():
    sewing = BRepBuilderAPI_Sewing()
    for face in TopExp_Explorer(_box(), TopAbs_FACE):
        sewing.Add(face)
    sewing.Perform()
    assert not sewing.SewedShape().IsNull()
    assert sewing.NbFreeEdges() == 0
