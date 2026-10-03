# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BOPAlgo_BOP_Test.cxx (LGPL-2.1 with the OCCT exception)
import importlib.util
import pathlib
import sys

from nanocct.BOPAlgo import BOPAlgo_COMMON, BOPAlgo_CUT, BOPAlgo_CUT21, BOPAlgo_FUSE
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace, BRepPrimAPI_MakePrism
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt


def _load_utilities():
    # the pytest.ini import mode (importlib) does not put this directory on sys.path
    name = "_tkbo_BOPTest_Utilities"
    if name not in sys.modules:
        path = pathlib.Path(__file__).with_name("BOPTest_Utilities.py")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


U = _load_utilities()


def test_BOPAlgo_DirectOperationsTest_DirectCut_SphereMinusBox():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aResult = U.PerformDirectBOP(aSphere, aBox, BOPAlgo_CUT)
    assert not (aResult.IsNull())
    aSurfaceArea = U.GetSurfaceArea(aResult)
    assert (aSurfaceArea) > (0.0)


def test_BOPAlgo_DirectOperationsTest_DirectFuse_SpherePlusBox():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aResult = U.PerformDirectBOP(aSphere, aBox, BOPAlgo_FUSE)
    assert not (aResult.IsNull())
    aVolume = U.GetVolume(aResult)
    aSphereVolume = U.GetVolume(aSphere)
    aBoxVolume = U.GetVolume(aBox)
    assert (aVolume) > (aSphereVolume)
    assert (aVolume) > (aBoxVolume)


def test_BOPAlgo_DirectOperationsTest_DirectCommon_OverlappingBoxes():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 2.0, 2.0, 2.0)
    aBox2 = U.CreateBox(gp_Pnt(1, 1, 1), 2.0, 2.0, 2.0)
    aResult = U.PerformDirectBOP(aBox1, aBox2, BOPAlgo_COMMON)
    U.ValidateResult(aResult, -1.0, 1.0)


def test_BOPAlgo_DirectOperationsTest_DirectTUC_IdenticalBoxes():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformDirectBOP(aBox1, aBox2, BOPAlgo_CUT21)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BOPAlgo_DirectOperationsTest_DirectCut_NurbsBoxMinusBox():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, 1, 0), 1.0, 0.5, 1.0)
    aResult = U.PerformDirectBOP(aBox1, aBox2, BOPAlgo_CUT)
    aSurfaceArea = U.GetSurfaceArea(aResult)
    assert (aSurfaceArea) > (0.0)


def test_BOPAlgo_TwoStepOperationsTest_TwoStepCut_SphereMinusBox():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aResult = U.PerformTwoStepBOP(aSphere, aBox, BOPAlgo_CUT)
    aSurfaceArea = U.GetSurfaceArea(aResult)
    assert (aSurfaceArea) > (0.0)


def test_BOPAlgo_TwoStepOperationsTest_TwoStepFuse_SpherePlusBox():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aResult = U.PerformTwoStepBOP(aSphere, aBox, BOPAlgo_FUSE)
    assert not (aResult.IsNull())
    aVolume = U.GetVolume(aResult)
    aSphereVolume = U.GetVolume(aSphere)
    aBoxVolume = U.GetVolume(aBox)
    assert (aVolume) > (aSphereVolume)
    assert (aVolume) > (aBoxVolume)


def test_BOPAlgo_TwoStepOperationsTest_TwoStepCommon_OverlappingBoxes():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 2.0, 2.0, 2.0)
    aBox2 = U.CreateBox(gp_Pnt(1, 1, 1), 2.0, 2.0, 2.0)
    aResult = U.PerformTwoStepBOP(aBox1, aBox2, BOPAlgo_COMMON)
    U.ValidateResult(aResult, -1.0, 1.0)


def test_BOPAlgo_TwoStepOperationsTest_TwoStepTUC_IdenticalBoxes():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformTwoStepBOP(aBox1, aBox2, BOPAlgo_CUT21)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BOPAlgo_ComplexOperationsTest_MultipleIntersectingPrimitives():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.5)
    aCylinder = U.CreateCylinder(0.8, 3.0)
    aBox = U.CreateBox(gp_Pnt(-0.5, -0.5, -0.5), 1.0, 1.0, 1.0)
    aIntermediate = U.PerformDirectBOP(aSphere, aCylinder, BOPAlgo_COMMON)
    assert not (aIntermediate.IsNull())
    aFinalResult = U.PerformDirectBOP(aIntermediate, aBox, BOPAlgo_FUSE)
    aVolume = U.GetVolume(aFinalResult)
    assert (aVolume) > (0.0)


def test_BOPAlgo_ComplexOperationsTest_DirectVsTwoStepComparison():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aDirectResult = U.PerformDirectBOP(aSphere, aBox, BOPAlgo_FUSE)
    aTwoStepResult = U.PerformTwoStepBOP(aSphere, aBox, BOPAlgo_FUSE)
    aDirectVolume = U.GetVolume(aDirectResult)
    aTwoStepVolume = U.GetVolume(aTwoStepResult)
    assert abs((aDirectVolume) - (aTwoStepVolume)) <= (U.myTolerance)


def test_BOPAlgo_DegenerateToolTest_Cut_AxisAlignedThinTool_NearlyPreservesBoxVolume():
    aBox = U.CreateBox(gp_Pnt(0.0, 0.0, 0.0), 100.0, 100.0, 100.0)
    aThin = U.CreateBox(gp_Pnt(-500.0, 25.0, -500.0), 1500.0, 1.0e-6, 1500.0)
    aRes = U.PerformDirectBOP(aBox, aThin, BOPAlgo_CUT)
    aBoxVol = U.GetVolume(aBox)
    aOverlapV = 100.0 * 1.0e-6 * 100.0
    assert not (aRes.IsNull())
    assert abs((U.GetVolume(aRes)) - (aBoxVol - aOverlapV)) <= (1.0e-4)


def test_BOPAlgo_DegenerateToolTest_Fuse_AxisAlignedThinTool_AddsNonOverlappingSlice():
    aBox = U.CreateBox(gp_Pnt(0.0, 0.0, 0.0), 100.0, 100.0, 100.0)
    aThin = U.CreateBox(gp_Pnt(-500.0, 25.0, -500.0), 1500.0, 1.0e-6, 1500.0)
    aRes = U.PerformDirectBOP(aBox, aThin, BOPAlgo_FUSE)
    aBoxVol = U.GetVolume(aBox)
    aThinVol = 1500.0 * 1.0e-6 * 1500.0
    aOverlapV = 100.0 * 1.0e-6 * 100.0
    assert not (aRes.IsNull())
    assert abs((U.GetVolume(aRes)) - (aBoxVol + aThinVol - aOverlapV)) <= (1.0e-4)


def test_BOPAlgo_DegenerateToolTest_Cut_LegitimateThinSlab_NotTreatedAsEmpty():
    aBox = U.CreateBox(gp_Pnt(0.0, 0.0, 0.0), 100.0, 100.0, 100.0)
    aSlab = U.CreateBox(gp_Pnt(0.0, 0.0, 50.0), 100.0, 100.0, 1.0)
    aRes = U.PerformDirectBOP(aBox, aSlab, BOPAlgo_CUT)
    assert not (aRes.IsNull())
    assert abs((U.GetVolume(aRes)) - (U.GetVolume(aBox) - U.GetVolume(aSlab))) <= (U.myTolerance)


def test_BOPAlgo_DegenerateToolTest_Common_SolidAndPlanarFace_Unaffected():
    aBox = U.CreateBox(gp_Pnt(0.0, 0.0, 0.0), 100.0, 100.0, 100.0)
    aPln = gp_Pln(gp_Pnt(0.0, 0.0, 50.0), gp_Dir(0.0, 0.0, 1.0))
    aFaceMaker = BRepBuilderAPI_MakeFace(aPln, -200.0, 200.0, -200.0, 200.0)
    assert aFaceMaker.IsDone()
    aFace = aFaceMaker.Face()
    aRes = U.PerformDirectBOP(aBox, aFace, BOPAlgo_COMMON)
    assert not (aRes.IsNull())
    assert abs((U.GetSurfaceArea(aRes)) - (1.0e4)) <= (1.0)


def test_BOPAlgo_DegenerateToolTest_Cut_BySemiInfinitePrism_Unaffected():
    aBox = U.CreateBox(gp_Pnt(0.0, -1.0, -1.0), 2.0, 2.0, 2.0)
    aPln = gp_Pln(gp_Pnt(-0.5, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
    aFaceMaker = BRepBuilderAPI_MakeFace(aPln, -0.5, 0.5, -0.5, 0.5)
    assert aFaceMaker.IsDone()
    aPrismMaker = BRepPrimAPI_MakePrism(aFaceMaker.Face(), gp_Dir(1.0, 0.0, 0.0), True)
    assert aPrismMaker.IsDone()
    aRes = U.PerformDirectBOP(aBox, aPrismMaker.Shape(), BOPAlgo_CUT)
    assert not (aRes.IsNull())
    assert (U.GetVolume(aRes)) > (1.0)


def test_BOPAlgo_DegenerateToolTest_Common_SolidAndHalfspace_Unaffected():
    aBox = U.CreateBox(gp_Pnt(0.0, 0.0, -30.0), 150.0, 200.0, 200.0)
    aPln = gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    aFaceMaker = BRepBuilderAPI_MakeFace(aPln, -250.0, 250.0, -250.0, 250.0)
    assert aFaceMaker.IsDone()
    aHSMaker = BRepPrimAPI_MakeHalfSpace(aFaceMaker.Face(), gp_Pnt(0.0, 0.0, -100.0))
    aHalfSpace = aHSMaker.Solid()
    aRes = U.PerformDirectBOP(aBox, aHalfSpace, BOPAlgo_COMMON)
    assert not (aRes.IsNull())
    assert (U.GetVolume(aRes)) > (1.0)
