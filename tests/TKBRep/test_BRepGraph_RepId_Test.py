# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_RepId_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepGraphInc import (
    BRepGraph_CoEdgeCurve2DRepId,
    BRepGraph_CoEdgePolygon2DRepId,
    BRepGraph_CoEdgePolygonOnTriRepId,
    BRepGraph_EdgeCurve3DRepId,
    BRepGraph_EdgePolygon3DRepId,
    BRepGraph_FaceSurfaceRepId,
    BRepGraph_FaceTriangulationRepId,
    BRepGraph_RepId,
)

Kind = BRepGraph_RepId.Kind


def test_BRepGraph_RepIdTest_DefaultRepId_IsInvalid():
    assert not BRepGraph_RepId().IsValid()


def test_BRepGraph_RepIdTest_TypedDefaultRepId_IsInvalid():
    assert not BRepGraph_EdgeCurve3DRepId().IsValid()
    assert not BRepGraph_FaceSurfaceRepId().IsValid()
    assert not BRepGraph_CoEdgeCurve2DRepId().IsValid()
    assert not BRepGraph_FaceTriangulationRepId().IsValid()


def test_BRepGraph_RepIdTest_TypedRepId_ConvertsToUntyped():
    untyped = BRepGraph_RepId(BRepGraph_EdgeCurve3DRepId(42))
    assert untyped.RepKind == Kind.EdgeCurve3D
    assert untyped.Index == 42


def test_BRepGraph_RepIdTest_KindClassification():
    assert BRepGraph_RepId.IsValidKind_s(Kind.EdgeCurve3D)
    assert BRepGraph_RepId.IsValidKind_s(Kind.FaceSurface)
    assert BRepGraph_RepId.IsValidKind_s(Kind.CoEdgeCurve2D)
    assert BRepGraph_RepId.IsValidKind_s(Kind.FaceTriangulation)


def test_BRepGraph_RepIdTest_ValidRepId_PassesBoundsCheck():
    rep = BRepGraph_FaceSurfaceRepId(5)
    assert rep.IsValid()
    assert rep.IsValid(10)
    assert not rep.IsValid(3)


def test_BRepGraph_RepIdTest_StartId_IsZero():
    start = BRepGraph_EdgeCurve3DRepId.Start_s()
    assert start.IsValid()
    assert start.Index == 0


def test_BRepGraph_RepIdTest_EqualityAndComparison():
    a1 = BRepGraph_EdgeCurve3DRepId(1)
    a2 = BRepGraph_EdgeCurve3DRepId(2)
    a1_copy = BRepGraph_EdgeCurve3DRepId(1)
    assert a1 == a1_copy
    assert a1 != a2
    assert a1 < a2
    assert a1 <= a1_copy
    assert a2 > a1
    assert a1_copy >= a1


def test_BRepGraph_RepIdTest_DifferentKinds_AreNotEqual():
    assert BRepGraph_RepId(Kind.EdgeCurve3D, 0) != BRepGraph_RepId(Kind.FaceSurface, 0)


def test_BRepGraph_RepIdTest_AllTypedAliases_DefaultInvalid():
    assert not BRepGraph_EdgeCurve3DRepId().IsValid()
    assert not BRepGraph_EdgePolygon3DRepId().IsValid()
    assert not BRepGraph_CoEdgeCurve2DRepId().IsValid()
    assert not BRepGraph_CoEdgePolygon2DRepId().IsValid()
    assert not BRepGraph_CoEdgePolygonOnTriRepId().IsValid()
    assert not BRepGraph_FaceSurfaceRepId().IsValid()
    assert not BRepGraph_FaceTriangulationRepId().IsValid()
