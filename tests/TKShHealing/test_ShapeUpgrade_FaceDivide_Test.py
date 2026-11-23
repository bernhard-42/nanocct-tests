# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeUpgrade_FaceDivide_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_NurbsConvert
from nanocct.BRepLib import BRepLib
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.GeomAbs import GeomAbs_C2, GeomAbs_G2
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_IndexedMap
from nanocct.Precision import Precision
from nanocct.ShapeFix import ShapeFix
from nanocct.ShapeUpgrade import ShapeUpgrade_FaceDivide, ShapeUpgrade_ShapeDivideClosed
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher


def test_ShapeUpgrade_FaceDivideTest_Perform_WithoutContext_DoesNotCrash():
    for i in range(10):
        size = 10.0 + i * 0.5
        box = BRepPrimAPI_MakeBox(size, size + 5, size + 10).Shape()
        exp = TopExp_Explorer(box, TopAbs_FACE)
        assert exp.More(), "No faces found in box"
        divider = ShapeUpgrade_FaceDivide(TopoDS.Face(exp.Current()))
        divider.Perform()  # EXPECT_NO_THROW


# Perform_Parallel_DoesNotCrash: skipped (OSD_Parallel threading test)


def test_ShapeUpgrade_FaceDivideTest_SplitCylinderRegularityMatchesSecondDerivatives():
    convert = BRepBuilderAPI_NurbsConvert(BRepPrimAPI_MakeCylinder(2.0, 10.0).Face())
    assert convert.IsDone() is True
    divider = ShapeUpgrade_ShapeDivideClosed(convert.Shape())
    assert divider.Perform() is True
    result = divider.Result()
    ShapeFix.SameParameter_s(result, False)
    faces = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(result, TopAbs_FACE, faces)
    assert faces.Extent() == 2
    face1, face2 = TopoDS.Face(faces.FindKey(1)), TopoDS.Face(faces.FindKey(2))
    edges = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(face1, TopAbs_EDGE, edges)
    assert edges.Extent() == 4
    surface1, surface2 = BRep_Tool.Surface_s(face1), BRep_Tool.Surface_s(face2)
    ang = Precision.Angular_s()
    for index in (2, 4):
        edge = TopoDS.Edge(edges.FindKey(index))
        curve1, first1, last1 = BRep_Tool.CurveOnSurface_s(edge, face1)
        curve2, first2, last2 = BRep_Tool.CurveOnSurface_s(edge, face2)
        assert curve1 is not None and curve2 is not None, index
        uv1 = curve1.EvalD0((first1 + last1) * 0.5)
        uv2 = curve2.EvalD0((first2 + last2) * 0.5)
        jet1 = surface1.EvalD2(uv1.X(), uv1.Y())
        jet2 = surface2.EvalD2(uv2.X(), uv2.Y())
        second_difference = (jet1.D2U - jet2.D2U).Magnitude()
        continuity = BRepLib.ContinuityOfFaces_s(edge, face1, face2, ang)
        assert BRepLib.ContinuityOfFaces_s(edge, face2, face1, ang) == continuity, index
        assert BRepLib.ContinuityOfFaces_s(TopoDS.Edge(edge.Reversed()), face1, face2, ang) == continuity, index
        assert BRepLib.ContinuityOfFaces_s(edge, TopoDS.Face(face1.Reversed()), TopoDS.Face(face2.Reversed()),
                                           ang) == continuity, index
        transform = gp_Trsf()
        transform.SetRotation(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 2.0, 3.0)), 0.73)
        transform.SetTranslationPart(gp_Vec(100.0, -200.0, 300.0))
        location = TopLoc_Location(transform)
        assert BRepLib.ContinuityOfFaces_s(TopoDS.Edge(edge.Moved(location)), TopoDS.Face(face1.Moved(location)),
                                           TopoDS.Face(face2.Moved(location)), ang) == continuity, index
        if index == 2:
            assert second_difference > Precision.Confusion_s()
            assert continuity == GeomAbs_G2
        else:
            assert second_difference < Precision.Confusion_s()
            assert continuity == GeomAbs_C2
