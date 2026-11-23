# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepGProp_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.BRep import BRep_Builder
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Cut
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from nanocct.BRepGProp import BRepGProp, BRepGProp_Domain, BRepGProp_Face, BRepGProp_Vinert, BRepGProp_VinertGK
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.GCPnts import GCPnts_AbscissaPoint
from nanocct.Geom import Geom_BSplineCurve, Geom_Plane
from nanocct.Geom2d import Geom2d_BSplineCurve
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt, gp_Pnt2d
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Edge


def _props(func, shape, *args):
    props = GProp_GProps()
    func(shape, props, *args)
    return props


def test_BRepGPropTest_LinearProperties_EdgeLength():
    mk = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(3.0, 4.0, 0.0))
    assert mk.IsDone()
    assert abs(_props(BRepGProp.LinearProperties_s, mk.Edge()).Mass() - 5.0) <= Precision.Confusion_s()


def test_BRepGPropTest_SurfaceProperties_BoxFaceArea():
    mk = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
    shape = mk.Shape()
    assert mk.IsDone()
    assert abs(_props(BRepGProp.SurfaceProperties_s, shape).Mass() - 2200.0) <= Precision.Confusion_s()


def test_BRepGPropTest_VolumeProperties_UnitBox():
    mk = BRepPrimAPI_MakeBox(1.0, 1.0, 1.0)
    shape = mk.Shape()
    assert mk.IsDone()
    assert abs(_props(BRepGProp.VolumeProperties_s, shape).Mass() - 1.0) <= Precision.Confusion_s()


def test_BRepGPropTest_VolumeProperties_Sphere():
    r = 5.0
    mk = BRepPrimAPI_MakeSphere(r)
    shape = mk.Shape()
    assert mk.IsDone()
    expected = (4.0 / 3.0) * math.pi * r * r * r
    assert abs(_props(BRepGProp.VolumeProperties_s, shape).Mass() - expected) <= 0.01


def test_BRepGPropTest_VolumeProperties_BoxCenterOfMass():
    mk = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0)
    shape = mk.Shape()
    assert mk.IsDone()
    com = _props(BRepGProp.VolumeProperties_s, shape).CentreOfMass()
    c = Precision.Confusion_s()
    assert abs(com.X() - 5.0) <= c
    assert abs(com.Y() - 5.0) <= c
    assert abs(com.Z() - 5.0) <= c


def test_BRepGPropTest_LinearProperties_SkipShared():
    mk = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0)
    shape = mk.Shape()
    assert mk.IsDone()
    not_skipped = _props(BRepGProp.LinearProperties_s, shape, False)
    skipped = _props(BRepGProp.LinearProperties_s, shape, True)
    assert abs(skipped.Mass() - 120.0) <= Precision.Confusion_s()
    assert abs(not_skipped.Mass() - 240.0) <= Precision.Confusion_s()


def test_BRepGPropTest_OCC49_CylinderHasSymmetryAxis():
    cyl = BRepPrimAPI_MakeCylinder(10.0, 20.0).Shape()
    props = _props(BRepGProp.VolumeProperties_s, cyl)
    assert props.PrincipalProperties().HasSymmetryAxis()


def test_BRepGPropTest_OCC49_CutShapeHasNoSymmetryAxis():
    cyl = BRepPrimAPI_MakeCylinder(10.0, 20.0).Shape()
    box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    cut = BRepAlgoAPI_Cut(cyl, box)
    assert cut.IsDone()
    props = _props(BRepGProp.VolumeProperties_s, cut.Shape())
    assert not props.PrincipalProperties().HasSymmetryAxis()


def test_BRepGPropTest_OCC8797_BSplineLengthConsistencyAbscissaVsLinearProperties():
    poles = NCollection_Array1[gp_Pnt](0, 6)
    for i, (x, y) in enumerate([(0, 0), (1, 1), (2, 1), (3, 0), (4, 1), (5, 1), (6, 0)]):
        poles.SetValue(i, gp_Pnt(float(x), float(y), 0.0))
    knots = NCollection_Array1[float](0, 2)
    for i, k in enumerate([0.0, 0.5, 1.0]):
        knots.SetValue(i, k)
    mults = NCollection_Array1[int](0, 2)
    for i, m in enumerate([4, 3, 4]):
        mults.SetValue(i, m)
    spline = Geom_BSplineCurve(poles, knots, mults, 3)
    assert spline is not None
    assert spline.NbPoles() == 7
    assert spline.NbKnots() == 3
    adaptor = GeomAdaptor_Curve(spline)
    length_abscissa = GCPnts_AbscissaPoint.Length_s(adaptor)
    assert length_abscissa > 0.0
    edge = BRepBuilderAPI_MakeEdge(spline).Edge()
    length_gprop = _props(BRepGProp.LinearProperties_s, edge).Mass()
    assert length_gprop > 0.0
    assert abs(length_abscissa - length_gprop) <= length_gprop * 1e-3


def test_BRepGPropTest_LinearProperties_DegenerateEdgeWithBSplinePCurveNoCrash():
    plane = Geom_Plane(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    poles = NCollection_Array1[gp_Pnt2d](1, 4)
    poles.SetValue(1, gp_Pnt2d(0.0, 0.0))
    poles.SetValue(2, gp_Pnt2d(0.1, 0.05))
    poles.SetValue(3, gp_Pnt2d(0.2, -0.05))
    poles.SetValue(4, gp_Pnt2d(0.3, 0.0))
    knots = NCollection_Array1[float](1, 2)
    knots.SetValue(1, 0.0)
    knots.SetValue(2, 1.0)
    mults = NCollection_Array1[int](1, 2)
    mults.SetValue(1, 4)
    mults.SetValue(2, 4)
    pcurve = Geom2d_BSplineCurve(poles, knots, mults, 3)
    builder = BRep_Builder()
    edge = TopoDS_Edge()
    builder.MakeEdge(edge)
    builder.UpdateEdge(edge, pcurve, plane, TopLoc_Location(), Precision.Confusion_s())
    builder.Range(edge, plane, TopLoc_Location(), pcurve.FirstParameter(), pcurve.LastParameter())
    builder.Degenerated(edge, True)
    props = _props(BRepGProp.LinearProperties_s, edge)
    assert math.isfinite(props.Mass())
    assert props.Mass() >= 0.0


def _block_face():
    builder = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0.0, 0.0, 2.0), gp_Dir(0.0, 0.0, 1.0)), 0.0, 3.0, 0.0, 4.0)
    assert builder.IsDone() is True
    return builder.Face()


def test_BRepGPropTest_VolumePropertiesByPlane_OffsetPlane_Inertia():
    face = _block_face()
    plane = gp_Pln(gp_Pnt(0.0, 0.0, 1.0), gp_Dir(0.0, 0.0, 1.0))
    vinert = BRepGProp_Vinert(BRepGProp_Face(face), BRepGProp_Domain(face), plane, gp_Pnt(1.5, 2.0, 1.5))
    inertia = vinert.MatrixOfInertia()
    assert inertia.Value(1, 1) == pytest.approx(17.0, abs=1e-10)
    assert inertia.Value(2, 2) == pytest.approx(10.0, abs=1e-10)
    assert inertia.Value(3, 3) == pytest.approx(25.0, abs=1e-10)


def test_BRepGPropTest_VolumePropertiesByPlane_OffsetPlane_MassAndCentre():
    face = _block_face()
    plane = gp_Pln(gp_Pnt(0.0, 0.0, 1.0), gp_Dir(0.0, 0.0, 1.0))
    for location in (gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(0.0, 0.0, 4.0)):
        gk = BRepGProp_VinertGK(BRepGProp_Face(face), BRepGProp_Domain(face), plane, location, 1.0e-8, True)
        assert gk.Mass() == pytest.approx(12.0, abs=1e-8), location.Z()
        assert gk.CentreOfMass().X() == pytest.approx(1.5, abs=1e-8), location.Z()
        assert gk.CentreOfMass().Y() == pytest.approx(2.0, abs=1e-8), location.Z()
        assert gk.CentreOfMass().Z() == pytest.approx(1.5, abs=1e-8), location.Z()


def _expect_gprops_near(actual, expected, tol):
    assert actual.Mass() == pytest.approx(expected.Mass(), abs=tol)
    for axis in ("X", "Y", "Z"):
        assert getattr(actual.CentreOfMass(), axis)() == pytest.approx(getattr(expected.CentreOfMass(), axis)(), abs=tol)
    a, e = actual.MatrixOfInertia(), expected.MatrixOfInertia()
    for row in range(1, 4):
        for col in range(1, 4):
            assert a.Value(row, col) == pytest.approx(e.Value(row, col), abs=tol), (row, col)


def test_BRepGPropTest_VinertByPlane_BoxVolume_KeepsMassAndCentre():
    face = _block_face()
    reference = gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    location = gp_Pnt(0.0, 0.0, 0.0)
    # The volume between the face and the reference plane is a 3 x 4 x 2 block.
    block = GProp_GProps()
    BRepGProp.VolumeProperties_s(BRepPrimAPI_MakeBox(3.0, 4.0, 2.0).Shape(), block)
    fixed = BRepGProp_Vinert(BRepGProp_Face(face), BRepGProp_Domain(face), reference, location)
    adaptive = BRepGProp_Vinert(BRepGProp_Face(face), BRepGProp_Domain(face), reference, location, 1.0e-8)
    for props in (fixed, adaptive):
        assert props.Mass() == pytest.approx(24.0, abs=1e-10)
        assert props.CentreOfMass().X() == pytest.approx(1.5, abs=1e-10)
        assert props.CentreOfMass().Y() == pytest.approx(2.0, abs=1e-10)
        assert props.CentreOfMass().Z() == pytest.approx(1.0, abs=1e-10)
        _expect_gprops_near(props, block, 1.0e-9)
