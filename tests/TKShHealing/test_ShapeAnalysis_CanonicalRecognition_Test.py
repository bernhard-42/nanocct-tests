# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeAnalysis_CanonicalRecognition_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_NurbsConvert,
    BRepBuilderAPI_Sewing,
)
from nanocct.Geom import (
    Geom_BezierCurve,
    Geom_Circle,
    Geom_ConicalSurface,
    Geom_CylindricalSurface,
    Geom_Ellipse,
    Geom_Plane,
    Geom_SphericalSurface,
    Geom_SurfaceOfLinearExtrusion,
)
from nanocct.GeomAPI import GeomAPI_IntSS
from nanocct.GeomConvert import GeomConvert
from nanocct.gp import (
    gp_Ax2,
    gp_Circ,
    gp_Cone,
    gp_Cylinder,
    gp_Dir,
    gp_Elips,
    gp_Lin,
    gp_Pln,
    gp_Pnt,
    gp_Sphere,
)
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.ShapeAnalysis import ShapeAnalysis_CanonicalRecognition

APPROX_TOL = 1.0e-3
BASE_SURF_TOL = 1.0e-7


def _conf():
    return Precision.Confusion_s()


def _nurbs_face(face):
    conv = BRepBuilderAPI_NurbsConvert(face)
    assert conv.IsDone()
    return TopoDS.Face(conv.Shape())


def _nurbs_shape(shape):
    conv = BRepBuilderAPI_NurbsConvert(shape)
    assert conv.IsDone()
    return conv.Shape()


def _face(surf, u1, u2, v1, v2):
    maker = BRepBuilderAPI_MakeFace(surf, u1, u2, v1, v2, _conf())
    assert maker.IsDone()
    return maker.Face()


def _sewn(surf, ranges):
    sewing = BRepBuilderAPI_Sewing()
    for r in ranges:
        sewing.Add(_face(surf, *r))
    sewing.Perform()
    shape = sewing.SewedShape()
    assert not shape.IsNull()
    return shape


def _bezier(dev):
    poles = NCollection_Array1[gp_Pnt](1, 3)
    poles[1] = gp_Pnt(0, 0, 0)
    poles[2] = gp_Pnt(0.5, dev, 0)
    poles[3] = gp_Pnt(1, 0, 0)
    return Geom_BezierCurve(poles)


def _wire_of_three(curve, params):
    edges = []
    for a, b in params:
        maker = BRepBuilderAPI_MakeEdge(curve, a, b)
        assert maker.IsDone()
        edges.append(maker.Edge())
    wmaker = BRepBuilderAPI_MakeWire()
    for e in edges:
        wmaker.Add(e)
    assert wmaker.IsDone()
    return wmaker.Wire()


# --- CanonicalRecognitionApproxTest ---------------------------------------------------------


def test_CanonicalRecognitionApproxTest_PolylineToPlaneRecognition_A1():
    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(gp_Pnt(0, 0, 0))
    poly.Add(gp_Pnt(1, 0, 0))
    poly.Add(gp_Pnt(1, 1, 0))
    poly.Add(gp_Pnt(0, 1, 0))
    poly.Close()
    assert poly.IsDone()
    wire = poly.Wire()

    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(wire)
    pln = gp_Pln()
    assert rec.IsPlane(APPROX_TOL, pln)
    assert abs(abs(pln.Axis().Direction().Z()) - 1.0) <= APPROX_TOL
    assert abs(pln.Location().Z()) <= APPROX_TOL


def test_CanonicalRecognitionApproxTest_CylinderRecognition_A2():
    surf = Geom_CylindricalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(1, 1, 1)), 1.0)
    face = _nurbs_face(_face(surf, 0, 2 * math.pi, 0, 1))
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    cyl = gp_Cylinder()
    assert rec.IsCylinder(APPROX_TOL, cyl)
    assert abs(cyl.Radius() - 1.0) <= APPROX_TOL


def test_CanonicalRecognitionApproxTest_ConicalSurfaceRecognition_A3():
    half = math.pi / 6.0
    surf = Geom_ConicalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), half, 2.0)
    face = _nurbs_face(_face(surf, 0, 2 * math.pi, 0, 3))
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    cone = gp_Cone()
    assert rec.IsCone(APPROX_TOL, cone)
    assert abs(cone.SemiAngle() - half) <= APPROX_TOL


def test_CanonicalRecognitionApproxTest_SphericalSurfaceRecognition_A4():
    surf = Geom_SphericalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    face = _nurbs_face(_face(surf, 0, 2 * math.pi, 0, math.pi / 2))
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    sph = gp_Sphere()
    assert rec.IsSphere(APPROX_TOL, sph)
    assert abs(sph.Radius() - 1.0) <= APPROX_TOL


# --- CanonicalRecognitionBaseCurveTest ------------------------------------------------------


def test_CanonicalRecognitionBaseCurveTest_BezierToLineRecognition_A1():
    maker = BRepBuilderAPI_MakeEdge(_bezier(0.0005))
    assert maker.IsDone()
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(maker.Edge())
    lin = gp_Lin()
    assert rec.IsLine(APPROX_TOL, lin)
    assert abs(abs(lin.Direction().X()) - 1.0) <= APPROX_TOL


def test_CanonicalRecognitionBaseCurveTest_BezierToCircleRecognition_A2():
    maker = BRepBuilderAPI_MakeEdge(_bezier(0.0005))
    assert maker.IsDone()
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(maker.Edge())
    circ = gp_Circ()
    assert rec.IsCircle(APPROX_TOL, circ)
    assert circ.Radius() > 0.0


def test_CanonicalRecognitionBaseCurveTest_EllipseToEllipseRecognition_A3():
    ell = Geom_Ellipse(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)), 1.0, 0.5)
    bsp = GeomConvert.CurveToBSplineCurve_s(ell)
    maker = BRepBuilderAPI_MakeEdge(bsp)
    assert maker.IsDone()
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(maker.Edge())
    elips = gp_Elips()
    assert rec.IsEllipse(1.0e-7, elips)
    assert abs(elips.MajorRadius() - 1.0) <= 1.0e-7
    assert abs(elips.MinorRadius() - 0.5) <= 1.0e-7


def test_CanonicalRecognitionBaseCurveTest_MultiSegmentWireToLineRecognition_A4():
    wire = _wire_of_three(_bezier(0.0000005), [(0.0, 0.3), (0.3, 0.7), (0.7, 1.0)])
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(wire)
    lin = gp_Lin()
    assert rec.IsLine(APPROX_TOL, lin)


def test_CanonicalRecognitionBaseCurveTest_MultiSegmentCircleWireRecognition_A5():
    circle = Geom_Circle(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    bsp = GeomConvert.CurveToBSplineCurve_s(circle)
    wire = _wire_of_three(bsp, [(0.0, 1.0), (1.0, 2.5), (2.5, 6.0)])
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(wire)
    circ = gp_Circ()
    assert rec.IsCircle(1.0e-7, circ)
    assert abs(circ.Radius() - 1.0) <= 1.0e-7


def test_CanonicalRecognitionBaseCurveTest_MultiSegmentEllipseWireRecognition_A6():
    ell = Geom_Ellipse(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0)), 1.0, 0.5)
    bsp = GeomConvert.CurveToBSplineCurve_s(ell)
    wire = _wire_of_three(bsp, [(0.0, 1.0), (1.0, 2.5), (2.5, 6.0)])
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(wire)
    elips = gp_Elips()
    assert rec.IsEllipse(1.0e-7, elips)
    assert abs(elips.MajorRadius() - 1.0) <= 1.0e-7
    assert abs(elips.MinorRadius() - 0.5) <= 1.0e-7


# --- CanonicalRecognitionBaseSurfaceTest ----------------------------------------------------


def test_CanonicalRecognitionBaseSurfaceTest_TrimmedPlaneRecognition_B1():
    face = _nurbs_face(_face(Geom_Plane(gp_Pln()), -1, 1, -1, 1))
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    pln = gp_Pln()
    assert rec.IsPlane(BASE_SURF_TOL, pln)
    assert abs(abs(pln.Axis().Direction().Z()) - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_TrimmedCylinderRecognition_B2():
    surf = Geom_CylindricalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    face = _nurbs_face(_face(surf, 0, 2 * math.pi, -1, 1))
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    cyl = gp_Cylinder()
    assert rec.IsCylinder(BASE_SURF_TOL, cyl)
    assert abs(cyl.Radius() - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_TrimmedConeRecognition_B3():
    semi = math.pi / 6.0
    surf = Geom_ConicalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), semi, 0)
    face = _nurbs_face(_face(surf, 0, 2 * math.pi, -1, 0))
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    cone = gp_Cone()
    assert rec.IsCone(BASE_SURF_TOL, cone)
    assert abs(cone.SemiAngle() - semi) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_ConvertedSphereRecognition_B4():
    sph_surf = Geom_SphericalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    bsp = GeomConvert.SurfaceToBSplineSurface_s(sph_surf)
    maker = BRepBuilderAPI_MakeFace(bsp, _conf())
    assert maker.IsDone()
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(maker.Face())
    sph = gp_Sphere()
    assert rec.IsSphere(BASE_SURF_TOL, sph)
    assert abs(sph.Radius() - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_SewnPlanarSurfaceRecognition_B5():
    sewn = _sewn(
        Geom_Plane(gp_Pln()),
        [(-1, 0, -1, 0), (-1, 0, 0, 1), (0, 1, 0, 1), (0, 1, -1, 0)],
    )
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(_nurbs_shape(sewn))
    pln = gp_Pln()
    assert rec.IsPlane(BASE_SURF_TOL, pln)
    assert abs(abs(pln.Axis().Direction().Z()) - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_SewnCylindricalSurfaceRecognition_B6():
    surf = Geom_CylindricalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    sewn = _sewn(surf, [(0, 3, -1, 0), (0, 3, 0, 1), (3, 6, 0, 1), (3, 6, -1, 0)])
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(_nurbs_shape(sewn))
    cyl = gp_Cylinder()
    assert rec.IsCylinder(BASE_SURF_TOL, cyl)
    assert abs(cyl.Radius() - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_SewnConicalSurfaceRecognition_B7():
    semi = math.pi / 6.0
    surf = Geom_ConicalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), semi, 0)
    sewn = _sewn(surf, [(0, 3, 0, 1), (0, 3, 1, 2), (3, 6, 1, 2), (3, 6, 0, 1)])
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(_nurbs_shape(sewn))
    cone = gp_Cone()
    assert rec.IsCone(BASE_SURF_TOL, cone)
    assert abs(cone.SemiAngle() - semi) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_SewnSphericalSurfaceRecognition_B8():
    sph_surf = Geom_SphericalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    bsp = GeomConvert.SurfaceToBSplineSurface_s(sph_surf)
    sewn = _sewn(bsp, [(0, 3, -1.5, 0), (0, 3, 0, 1.5), (3, 6, 0, 1.5), (3, 6, -1.5, 0)])
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(sewn)
    sph = gp_Sphere()
    assert rec.IsSphere(BASE_SURF_TOL, sph)
    assert abs(sph.Radius() - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_ComplexCylindricalRecognitionWithSection_B9():
    surf = Geom_CylindricalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    sewn = _sewn(surf, [(0, 1, -1, 1), (1, 2, -1, 1), (2, 3, -1, 1), (3, 4, -1, 1)])
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(_nurbs_shape(sewn))
    cyl = gp_Cylinder()
    assert rec.IsCylinder(BASE_SURF_TOL, cyl)
    assert abs(cyl.Radius() - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_ExtrudedCylindricalSurfaceRecognition_B10():
    cyl_surf = Geom_CylindricalSurface(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 1.0)
    plane = Geom_Plane(gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 1)))
    inter = GeomAPI_IntSS(cyl_surf, plane, _conf())
    assert inter.IsDone()
    assert inter.NbLines() > 0
    curve = inter.Line(1)
    assert curve is not None

    ext = Geom_SurfaceOfLinearExtrusion(curve, gp_Dir(0, 0, 1))
    u_min, u_max, _v_min, _v_max = ext.Bounds()
    face = _nurbs_face(_face(ext, u_min, u_max, -1, 1))
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    cyl = gp_Cylinder()
    assert rec.IsCylinder(BASE_SURF_TOL, cyl)
    assert abs(cyl.Radius() - 1.0) <= BASE_SURF_TOL


def test_CanonicalRecognitionBaseSurfaceTest_PlaneDetectionWithGapValidation_Bug33170():
    face = _face(Geom_Plane(gp_Pln()), -1, 1, -1, 1)
    rec = ShapeAnalysis_CanonicalRecognition()
    rec.SetShape(face)
    pln1 = gp_Pln()
    assert rec.IsPlane(0.006, pln1)
    gap1 = rec.GetGap()
    assert gap1 < 0.006
    assert gap1 >= 0.0

    rec.ClearStatus()
    pln2 = gp_Pln()
    assert rec.IsPlane(1.0, pln2)
    gap2 = rec.GetGap()
    assert gap2 < 1.0
    assert gap2 >= 0.0

    assert gap1 == gap2
