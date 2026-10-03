# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeFix_Shape_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.Precision import Precision
from nanocct.ShapeExtend import ShapeExtend_FAIL
from nanocct.ShapeFix import ShapeFix_Shape
from nanocct.TopoDS import TopoDS_Compound


def _box(*args):
    maker = BRepPrimAPI_MakeBox(*args)
    box = maker.Shape()
    assert maker.IsDone()
    return box


def test_ShapeFix_ShapeTest_FixValidBox():
    fixer = ShapeFix_Shape(_box(10.0, 10.0, 10.0))
    fixer.Perform()
    result = fixer.Shape()
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()


def test_ShapeFix_ShapeTest_StatusAfterFix():
    fixer = ShapeFix_Shape(_box(10.0, 10.0, 10.0))
    fixer.Perform()
    assert not fixer.Status(ShapeExtend_FAIL)


def test_ShapeFix_ShapeTest_SetPrecision():
    fixer = ShapeFix_Shape()
    fixer.SetPrecision(0.01)
    fixer.SetMinTolerance(0.001)
    fixer.SetMaxTolerance(0.1)
    tol = Precision.Confusion_s()
    assert abs(fixer.Precision() - 0.01) <= tol
    assert abs(fixer.MinTolerance() - 0.001) <= tol
    assert abs(fixer.MaxTolerance() - 0.1) <= tol


def test_ShapeFix_ShapeTest_FixCompound():
    box1 = _box(10.0, 10.0, 10.0)
    box2 = _box(gp_Pnt(20.0, 0.0, 0.0), 5.0, 5.0, 5.0)
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    builder.Add(compound, box1)
    builder.Add(compound, box2)

    fixer = ShapeFix_Shape(compound)
    fixer.Perform()
    result = fixer.Shape()
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()


def test_ShapeFix_ShapeTest_HealPrismFromSelfIntersectingFace():
    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(gp_Pnt(0.0, 0.0, 0.0))
    poly.Add(gp_Pnt(1.0, 1.0, 0.0))
    poly.Add(gp_Pnt(1.0, 0.0, 0.0))
    poly.Add(gp_Pnt(0.0, 1.0, 0.0))
    poly.Close()
    assert poly.IsDone()

    make_face = BRepBuilderAPI_MakeFace(poly.Wire(), True)
    assert make_face.IsDone()

    make_prism = BRepPrimAPI_MakePrism(make_face.Face(), gp_Vec(0.0, 0.0, 1.0))
    assert make_prism.IsDone()

    fixer = ShapeFix_Shape(make_prism.Shape())
    fixer.Perform()
    assert not fixer.Shape().IsNull()
    assert BRepCheck_Analyzer(fixer.Shape()).IsValid()
