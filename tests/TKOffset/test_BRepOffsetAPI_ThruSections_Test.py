# Translated from OCCT src/ModelingAlgorithms/TKOffset/GTests/BRepOffsetAPI_ThruSections_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepFill import BRepFill_ThruSectionErrorStatus_ProfilesInconsistent
from nanocct.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from nanocct.gp import gp, gp_Ax2, gp_Circ, gp_Dir, gp_Lin, gp_Pnt
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def _capsule_wire(x):
    left = gp_Circ(gp_Ax2(gp_Pnt(x, 0.0, 0.0), gp.DZ_s(), gp.DX_s()), 5.0)
    right = gp_Circ(gp_Ax2(gp_Pnt(x + 10.0, 0.0, 0.0), gp.DZ_s(), gp.DX_s()), 5.0)
    wire = BRepBuilderAPI_MakeWire()
    wire.Add(BRepBuilderAPI_MakeEdge(left, 0.5 * math.pi, 1.5 * math.pi).Edge())
    wire.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(x, -5.0, 0.0), gp_Pnt(x + 10.0, -5.0, 0.0)).Edge())
    wire.Add(BRepBuilderAPI_MakeEdge(right, 1.5 * math.pi, 2.5 * math.pi).Edge())
    wire.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(x + 10.0, 5.0, 0.0), gp_Pnt(x, 5.0, 0.0)).Edge())
    return wire.Wire()


def _wire(edge):
    return BRepBuilderAPI_MakeWire(edge).Wire()


def test_BRepOffsetAPI_ThruSectionsTest_RepeatedClosedSectionPreservesGeneratedFaces():
    first = _capsule_wire(0.0)
    circle = gp_Circ(gp_Ax2(gp_Pnt(50.0, 0.0, 15.0), gp.DX_s(), gp_Dir(0.0, 0.0, -1.0)), 3.0)
    loft = BRepOffsetAPI_ThruSections()
    loft.SetMaxDegree(5)
    loft.AddWire(first)
    loft.AddWire(_wire(BRepBuilderAPI_MakeEdge(circle).Edge()))
    loft.AddWire(_capsule_wire(90.0))
    loft.AddWire(first)
    loft.Build()
    assert loft.IsDone() is True
    assert loft.Shape().IsNull() is False
    assert BRepCheck_Analyzer(loft.Shape()).IsValid() is True
    exp = TopExp_Explorer(first, TopAbs_EDGE)
    while exp.More():
        generated = loft.Generated(exp.Current())
        assert generated.IsEmpty() is False
        for face in generated:
            assert face.IsNull() is False
            assert face.ShapeType() == TopAbs_FACE
        exp.Next()


def test_BRepOffsetAPI_ThruSectionsTest_UnboundedSectionReturnsFailure():
    first = _wire(BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0)).Edge())
    line = gp_Lin(gp_Pnt(0.0, 0.0, 10.0), gp.DX_s())
    full_line = BRepBuilderAPI_MakeEdge(line).Edge()
    half_line = BRepBuilderAPI_MakeEdge(line, 0.0, Precision.Infinite_s()).Edge()
    for edge in (full_line, half_line):
        unbounded = _wire(edge)
        for check in (False, True):
            loft = BRepOffsetAPI_ThruSections()
            loft.CheckCompatibility(check)
            loft.AddWire(first)
            loft.AddWire(unbounded)
            loft.Build()
            assert loft.IsDone() is False, check
            assert loft.GetStatus() == BRepFill_ThruSectionErrorStatus_ProfilesInconsistent, check


def test_BRepOffsetAPI_ThruSectionsTest_BoundedOpenSectionsBuildFace():
    first = _wire(BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0)).Edge())
    last = _wire(BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 10.0), gp_Pnt(10.0, 0.0, 10.0)).Edge())
    for check in (False, True):
        loft = BRepOffsetAPI_ThruSections()
        loft.CheckCompatibility(check)
        loft.AddWire(first)
        loft.AddWire(last)
        loft.Build()
        assert loft.IsDone() is True, check
        assert loft.Shape().IsNull() is False, check
        assert BRepCheck_Analyzer(loft.Shape()).IsValid() is True, check
        exp = TopExp_Explorer(loft.Shape(), TopAbs_FACE)
        assert exp.More() is True, check
        exp.Next()
        assert exp.More() is False, check
