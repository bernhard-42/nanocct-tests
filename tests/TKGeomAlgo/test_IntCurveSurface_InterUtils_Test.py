# Translated from OCCT src/ModelingAlgorithms/TKGeomAlgo/GTests/IntCurveSurface_InterUtils_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: the cases that call IntCurveSurface_InterUtils.pxx, a private header that OCCT does not install and
# that no installed header includes, so nothing of it is bound:
# - SortingPreservesDistinctParameterTriples, SortingPreservesEqualComponentsAndDuplicates,
#   SortingPreservesLargeSeedSets: its inline function SortStartPoints;
# - SectionPointToParameters_DegenerateFaceFallsBackToLongestEdge: its function template SectionPointToParameters, on
#   the test's own polyhedron and polygon classes;
# - TransitionIsIndependentOfParameterScale, TransitionPreservesAngularTangency: its function template
#   ComputeTransitions, on OCCT's curve and surface tools;
# - TransitionHandlesExtremeAndZeroDerivatives, TransitionHandlesObliqueAndNearlyParallelDerivatives,
#   TransitionPreservesObliqueAngularTangencyAcrossScales: ComputeTransitions on std::array<gp_Vec, 3> with the test's
#   own tool class.
from nanocct.Geom import Geom_BSplineCurve, Geom_Plane
from nanocct.GeomAdaptor import GeomAdaptor_Curve, GeomAdaptor_Surface
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt
from nanocct.IntCurveSurface import IntCurveSurface_HInter, IntCurveSurface_In, IntCurveSurface_Out
from nanocct.NCollection import NCollection_Array1

CONF = 1e-7  # Precision::Confusion()


def test_IntCurveSurface_InterUtilsTest_SlowCurvePlaneCrossingRetainsTransition():
    poles = NCollection_Array1[gp_Pnt](2)
    # `aPoles.ChangeAt(i) = gp_Pnt(...)`: assign through the returned reference
    poles.ChangeAt(0).SetXYZ(gp_Pnt(0, 0, -1).XYZ())
    poles.ChangeAt(1).SetXYZ(gp_Pnt(0, 0, 1).XYZ())
    # ChangeAt of a double element is not bound; Lower() is 0, so SetValue(i) writes the same slot
    knots = NCollection_Array1[float](2)
    knots.SetValue(0, 0)
    knots.SetValue(1, 1.0e9)
    multiplicities = NCollection_Array1[int](2)
    multiplicities.Init(2)
    curve = Geom_BSplineCurve(poles, knots, multiplicities, 1)
    surface = GeomAdaptor_Surface(Geom_Plane(gp_Pln(gp_Pnt(), gp_Dir(0, 0, 1))))
    intersector = IntCurveSurface_HInter()
    for iteration in range(2):
        adaptor = GeomAdaptor_Curve(curve)
        intersector.Perform(adaptor, surface)
        assert intersector.IsDone()
        assert intersector.NbPoints() == 1
        assert abs(intersector.Point(1).Pnt().Distance(gp_Pnt())) <= CONF
        # The knot range is 1e9, so this parameter check allows a few double ULPs.
        assert abs(intersector.Point(1).W() - 5.0e8) <= 1.0e-6
        expected = IntCurveSurface_Out if iteration == 0 else IntCurveSurface_In
        assert intersector.Point(1).Transition() == expected
        curve.Reverse()
