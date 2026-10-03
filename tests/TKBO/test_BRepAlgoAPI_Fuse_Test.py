# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BRepAlgoAPI_Fuse_Test.cxx (LGPL-2.1 with the OCCT exception)
import importlib.util
import math
import pathlib
import sys

from nanocct.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Ax1, gp_Ax3, gp_Dir, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.TopLoc import TopLoc_Location


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


def test_BFuseSimpleTest_SpherePlusBox_A1():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aResult = U.PerformFuse(aSphere, aBox)
    U.ValidateResult(aResult, 14.6394)


def test_BFuseSimpleTest_RotatedSpherePlusBox_A2():
    aSphere = U.CreateUnitSphere()
    aRotatedSphere = U.RotateStandard(aSphere)
    aBox = U.CreateUnitBox()
    aResult = U.PerformFuse(aRotatedSphere, aBox)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_BoxPlusRotatedSphere_A3():
    aSphere = U.CreateUnitSphere()
    aRotatedSphere = U.RotateStandard(aSphere)
    aBox = U.CreateUnitBox()
    aResult = U.PerformFuse(aBox, aRotatedSphere)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_SpherePlusRotatedBox_A4():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aRotatedBox = U.RotateY(aBox, 90.0)
    aResult = U.PerformFuse(aSphere, aRotatedBox)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_RotatedBoxPlusSphere_A5():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aRotatedBox = U.RotateY(aBox, 90.0)
    aResult = U.PerformFuse(aRotatedBox, aSphere)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_IdenticalNurbsBoxPlusBox_A6():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_IdenticalBoxPlusNurbsBox_A7():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_NurbsBoxPlusLargerBox_A8():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(-0.5, -0.5, -0.5), 2.0, 2.0, 2.0)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 24.0)


def test_BFuseSimpleTest_LargerBoxPlusNurbsBox_A9():
    aBox1 = U.CreateBox(gp_Pnt(-0.5, -0.5, -0.5), 2.0, 2.0, 2.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 24.0)


def test_BFuseSimpleTest_NurbsBoxPlusBox_B1():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 0.5, 1.0, 0.5)
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_BoxPlusNurbsBox_B2():
    aBox1 = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 0.5, 1.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 7.5)


def test_BFuseSimpleTest_NurbsBoxPlusAdjacentBox_B3():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 1.5, 1.0)
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 7.5)


def test_BFuseSimpleTest_AdjacentBoxPlusNurbsBox_B4():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, 0.5, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 8.0)


def test_BFuseSimpleTest_NurbsBoxPlusSmallerBox_B5():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0.25, 0.25, 0.25), 0.5, 0.5, 0.5)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_SmallerBoxPlusNurbsBox_B6():
    aBox1 = U.CreateBox(gp_Pnt(0.25, 0.25, 0.25), 0.5, 0.5, 0.5)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_NurbsBoxPlusPartiallyOverlappingBox_B7():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0.5, 0.5, 0.5), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 7.75)


def test_BFuseSimpleTest_PartiallyOverlappingBoxPlusNurbsBox_B8():
    aBox1 = U.CreateBox(gp_Pnt(0.5, 0.5, 0.5), 1.0, 1.0, 1.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 7.75)


def test_BFuseSimpleTest_NurbsBoxPlusExtendedBox_B9():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(-0.5, -0.5, -0.5), 2.0, 2.0, 2.0)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 24.0)


def test_BFuseSimpleTest_ExtendedBoxPlusNurbsBox_C1():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.5, 0.5, 0.5)
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 7.0)


def test_BFuseSimpleTest_NurbsBoxPlusShiftedBox_C2():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, -0.5, 0), 1.5, 0.5, 0.5)
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 8.5)


def test_BFuseSimpleTest_ShiftedBoxPlusNurbsBox_C3():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0.25, 0, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_NurbsBoxPlusNarrowBox_C4():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0.25, 0.25, 0), 0.5, 0.5, 1.5)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.75)


def test_BFuseSimpleTest_NarrowBoxPlusNurbsBox_C5():
    aBox1 = U.CreateBox(gp_Pnt(0.25, 0.25, 0), 0.5, 0.5, 1.5)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.75)


def test_BFuseSimpleTest_NurbsBoxPlusCornerCube_C6():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0.5, 0.5, 0.5), 0.5, 0.5, 0.5)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_CornerCubePlusNurbsBox_C7():
    aBox1 = U.CreateBox(gp_Pnt(0.5, 0.5, 0.5), 0.5, 0.5, 0.5)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)


def test_BFuseSimpleTest_NurbsBoxPlusOffsetCube_C8():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(1, 1, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.25)


def test_BFuseSimpleTest_OffsetCubePlusNurbsBox_C9():
    aBox1 = U.CreateBox(gp_Pnt(1, 1, 0), 0.5, 0.5, 1.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.ConvertToNurbs(aBox2)
    assert not (aBox2.IsNull())
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 6.25)


def test_BFuseSimpleTest_NurbsBoxPlusRotatedNarrowBox_D1():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    r = math.sqrt(2.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), r, 0.25, 1.0)
    aTrsf = gp_Trsf()
    aTrsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), math.pi / 4.0)
    aBox2.Move(TopLoc_Location(aTrsf))
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 6.41789)


def test_BFuseSimpleTest_NurbsBoxPlusRotatedNarrowBoxVariation_D2():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    r = 5.5677643628300219
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), r / 4.0, 0.25, 1.0)
    aTrsf = gp_Trsf()
    aTrsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 34.73 * math.pi / 180.0)
    aBox2.Move(TopLoc_Location(aTrsf))
    aResult = U.PerformFuse(aBox2, aBox1)
    U.ValidateResult(aResult, 6.32953)


def test_BFuseSimpleTest_SpherePlusBox_D3():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aSphere, aBox)
    U.ValidateResult(aResult, 14.6394)


def test_BFuseSimpleTest_BoxPlusSphere_D4():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aBox, aSphere)
    U.ValidateResult(aResult, 14.6394)


def test_BFuseSimpleTest_RotatedSpherePlusBox_D5():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aTrsf1 = gp_Trsf()
    aTrsf2 = gp_Trsf()
    aTrsfCombined = gp_Trsf()
    aTrsf1.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), -math.pi / 2.0)
    aTrsf2.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Y)), -math.pi / 4.0)
    aTrsfCombined = aTrsf2 * aTrsf1
    aSphere.Move(TopLoc_Location(aTrsfCombined))
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aSphere, aBox)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_BoxPlusRotatedSphere_D6():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aTrsf1 = gp_Trsf()
    aTrsf2 = gp_Trsf()
    aTrsfCombined = gp_Trsf()
    aTrsf1.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), -math.pi / 2.0)
    aTrsf2.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Y)), -math.pi / 4.0)
    aTrsfCombined = aTrsf2 * aTrsf1
    aSphere.Move(TopLoc_Location(aTrsfCombined))
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aBox, aSphere)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_SpherePlusRotatedBox_D7():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aTrsf = gp_Trsf()
    aTrsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 1), gp_Dir(gp_Dir.D.Y)), math.pi / 2.0)
    aBox.Move(TopLoc_Location(aTrsf))
    aResult = U.PerformFuse(aSphere, aBox)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_RotatedBoxPlusSphere_D8():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aTrsf = gp_Trsf()
    aTrsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 1), gp_Dir(gp_Dir.D.Y)), math.pi / 2.0)
    aBox.Move(TopLoc_Location(aTrsf))
    aResult = U.PerformFuse(aBox, aSphere)
    U.ValidateResult(aResult, 14.6393)


def test_BFuseSimpleTest_ProfileBasedPrisms_D9():
    aPlane1 = gp_Pln(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.X, 100.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -200.0), U.ProfileOperation(U.ProfileCmd.Y, -200.0), U.ProfileOperation(U.ProfileCmd.X, 100.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, 100))
    aPlane2 = gp_Pln(gp_Ax3(gp_Pnt(0, 0, 100), gp_Dir(gp_Dir.D.Z)))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.X, -100.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, 100))
    aResult = U.PerformFuse(aPrism1, aPrism2)
    U.ValidateResult(aResult, 180000.0)


def test_BFuseSimpleTest_ComplexProfileWithScaling_E1():
    SCALE = 100.0
    aPlane1 = gp_Pln(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.C, 50.0 * SCALE, 180.0), U.ProfileOperation(U.ProfileCmd.X, -100.0 * SCALE), U.ProfileOperation(U.ProfileCmd.C, 50.0 * SCALE, 180.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, 30.0 * SCALE))
    aPlane2 = gp_Pln(gp_Ax3(gp_Pnt(-200.0 * SCALE, -50.0 * SCALE, 0), gp_Dir(gp_Dir.D.Z)))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.X, 300.0 * SCALE), U.ProfileOperation(U.ProfileCmd.Y, 200.0 * SCALE), U.ProfileOperation(U.ProfileCmd.X, -300.0 * SCALE), U.ProfileOperation(U.ProfileCmd.Y, -200.0 * SCALE)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -50.0 * SCALE))
    aResult = U.PerformFuse(aPrism2, aPrism1)
    U.ValidateResult(aResult, 1.85425e+09)


def test_BFuseSimpleTest_AdjacentBoxes_E2():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 3.0, 3.0, 3.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 3, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformFuse(aBox1, aBox2)
    U.ValidateResult(aResult, 58.0)


def test_BFuseSimpleTest_ComplexVertexEdgeWireRevolution_E3():
    aPoints = [gp_Pnt(0, 0, 0), gp_Pnt(9, 0, 0), gp_Pnt(9, 0, 3), gp_Pnt(6.25, 0, 3), gp_Pnt(6, 0, 4), gp_Pnt(0, 0, 4)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aRevolution = U.CreateRevolution(aFace, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 2.0 * math.pi)
    aCylinder = U.CreateCylinder(1.0, 9.0)
    aTrsf = gp_Trsf()
    aTrsf.SetTranslation(gp_Vec(5, 0, -2))
    aCylinder.Move(TopLoc_Location(aTrsf))
    aResult = U.PerformFuse(aRevolution, aCylinder)
    U.ValidateResult(aResult, 740.048)


def test_BFuseSimpleTest_CylinderWithComplexWireRevolution_E4():
    aCylinder = U.CreateCylinder(3.0, 5.0)
    aPoints = [gp_Pnt(0, 3, 2), gp_Pnt(0, 4, 2), gp_Pnt(0, 4, 3), gp_Pnt(0, 3, 3)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aRing = U.CreateRevolution(aFace, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 269.0 * math.pi / 180.0)
    aResult = U.PerformFuse(aCylinder, aRing)
    U.ValidateResult(aResult, 190.356)


def test_BFuseSimpleTest_BoxWithPrismFromVertexEdge_E5():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 2, 0), gp_Pnt(4, 2, 0), gp_Pnt(4, 3, 0), gp_Pnt(3, 3, 0)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromFront_E6():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 2, 0), gp_Pnt(4, 2, 0), gp_Pnt(4, 2, 1), gp_Pnt(3, 2, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 1, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromLeft_E7():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 2, 0), gp_Pnt(3, 3, 0), gp_Pnt(3, 3, 1), gp_Pnt(3, 2, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromTop_E8():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 2, 1), gp_Pnt(4, 2, 1), gp_Pnt(4, 3, 1), gp_Pnt(3, 3, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 0, -1))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromBack_E9():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 3, 0), gp_Pnt(4, 3, 0), gp_Pnt(4, 3, 1), gp_Pnt(3, 3, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromRight_F1():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(4, 2, 0), gp_Pnt(4, 3, 0), gp_Pnt(4, 3, 1), gp_Pnt(4, 2, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(-1, 0, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromBottomDifferent_F2():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(4, 3, 0), gp_Pnt(4, 2, 0), gp_Pnt(3, 2, 0), gp_Pnt(3, 3, 0)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromBottomExternal_F3():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(8, 3, 0), gp_Pnt(9, 3, 0), gp_Pnt(9, 4, 0), gp_Pnt(8, 4, 0)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromFrontExternal_F4():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(8, 3, 0), gp_Pnt(9, 3, 0), gp_Pnt(9, 3, 1), gp_Pnt(8, 3, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 1, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromLeftExternal_F5():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(8, 3, 0), gp_Pnt(8, 4, 0), gp_Pnt(8, 4, 1), gp_Pnt(8, 3, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromTopExternal_F6():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(8, 3, 1), gp_Pnt(9, 3, 1), gp_Pnt(9, 4, 1), gp_Pnt(8, 4, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 0, -1))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromBackExternal_F7():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(8, 4, 0), gp_Pnt(9, 4, 0), gp_Pnt(9, 4, 1), gp_Pnt(8, 4, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromRightExternal_F8():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(9, 3, 0), gp_Pnt(9, 4, 0), gp_Pnt(9, 4, 1), gp_Pnt(9, 3, 1)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(-1, 0, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromBottomTopPosition_F9():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 3, 4), gp_Pnt(4, 3, 4), gp_Pnt(4, 4, 4), gp_Pnt(3, 4, 4)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromFrontTopLevel_G1():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 3, 4), gp_Pnt(4, 3, 4), gp_Pnt(4, 3, 5), gp_Pnt(3, 3, 5)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 1, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromLeftTopLevel_G2():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 3, 4), gp_Pnt(3, 4, 4), gp_Pnt(3, 4, 5), gp_Pnt(3, 3, 5)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromTopTopLevel_G3():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 3, 5), gp_Pnt(4, 3, 5), gp_Pnt(4, 4, 5), gp_Pnt(3, 4, 5)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, 0, -1))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromBackTopLevel_G4():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(3, 4, 4), gp_Pnt(4, 4, 4), gp_Pnt(4, 4, 5), gp_Pnt(3, 4, 5)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_BoxWithPrismFromRightTopLevel_G5():
    aBox = U.CreateBox(gp_Pnt(3, 3, 0), 5.0, 7.0, 4.0)
    aPoints = [gp_Pnt(4, 3, 4), gp_Pnt(4, 4, 4), gp_Pnt(4, 4, 5), gp_Pnt(4, 3, 5)]
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aPrism = U.CreatePrism(aFace, gp_Vec(-1, 0, 0))
    aResult = U.PerformFuse(aBox, aPrism)
    U.ValidateResult(aResult, 170.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromBottom_G6():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 2, 0), gp_Pnt(4, 2, 0), gp_Pnt(4, 3, 0), gp_Pnt(3, 3, 0)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromFront_G7():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 2, 0), gp_Pnt(4, 2, 0), gp_Pnt(4, 2, 1), gp_Pnt(3, 2, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 1, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromLeft_G8():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 2, 0), gp_Pnt(3, 3, 0), gp_Pnt(3, 3, 1), gp_Pnt(3, 2, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromTop_G9():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 2, 1), gp_Pnt(4, 2, 1), gp_Pnt(4, 3, 1), gp_Pnt(3, 3, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 0, -1))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromBackEdge_H1():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 3, 0), gp_Pnt(4, 3, 0), gp_Pnt(4, 3, 1), gp_Pnt(3, 3, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromRightEdge_H2():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(4, 2, 0), gp_Pnt(4, 3, 0), gp_Pnt(4, 3, 1), gp_Pnt(4, 2, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(-1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromBottomCorner_H3():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(8, 3, 0), gp_Pnt(9, 3, 0), gp_Pnt(9, 4, 0), gp_Pnt(8, 4, 0)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromFrontEdge_H4():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(8, 3, 0), gp_Pnt(9, 3, 0), gp_Pnt(9, 3, 1), gp_Pnt(8, 3, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 1, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromLeftEdge_H5():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(8, 3, 0), gp_Pnt(8, 4, 0), gp_Pnt(8, 4, 1), gp_Pnt(8, 3, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromTopEdge_H6():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(8, 3, 1), gp_Pnt(9, 3, 1), gp_Pnt(9, 4, 1), gp_Pnt(8, 4, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 0, -1))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromBackEdgeCorner_H7():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(8, 4, 0), gp_Pnt(9, 4, 0), gp_Pnt(9, 4, 1), gp_Pnt(8, 4, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromRightEdgeCorner_H8():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(9, 3, 0), gp_Pnt(9, 4, 0), gp_Pnt(9, 4, 1), gp_Pnt(9, 3, 1)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(-1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromTopCorner_H9():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 3, 4), gp_Pnt(4, 3, 4), gp_Pnt(4, 4, 4), gp_Pnt(3, 4, 4)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromFrontTopLevel_I1():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 3, 4), gp_Pnt(4, 3, 4), gp_Pnt(4, 3, 5), gp_Pnt(3, 3, 5)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 1, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromLeftTopLevel_I2():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 3, 4), gp_Pnt(3, 4, 4), gp_Pnt(3, 4, 5), gp_Pnt(3, 3, 5)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromTopAbove_I3():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 3, 5), gp_Pnt(4, 3, 5), gp_Pnt(4, 4, 5), gp_Pnt(3, 4, 5)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, 0, -1))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromBackTopLevel_I4():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(3, 4, 4), gp_Pnt(4, 4, 4), gp_Pnt(4, 4, 5), gp_Pnt(3, 4, 5)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithSmallPrismFromRightTopLevel_I5():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 4))
    aSmallPts = [gp_Pnt(4, 3, 4), gp_Pnt(4, 4, 4), gp_Pnt(4, 4, 5), gp_Pnt(4, 3, 5)]
    aSmallWire = U.CreatePolygonWire(aSmallPts, True)
    aSmallFace = U.CreateFaceFromWire(aSmallWire)
    aSmallPrism = U.CreatePrism(aSmallFace, gp_Vec(-1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aSmallPrism)
    U.ValidateResult(aResult, 152.0)


def test_BFuseSimpleTest_LargePrismWithOblongPrismProfile_I6():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [4, 3, 0]), U.ProfileOperation(U.ProfileCmd.P, [0, 1, 0, 1, 0, 0]), U.ProfileOperation(U.ProfileCmd.D, [-1, 0]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.X, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismYDirection_I7():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [3, 3, 3]), U.ProfileOperation(U.ProfileCmd.P, [0, 1, 0, 1, 0, 0]), U.ProfileOperation(U.ProfileCmd.D, [0, -1]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.Y, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismXDirection_I8():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [5, 3, 0]), U.ProfileOperation(U.ProfileCmd.P, [0, 1, 0, 1, 0, 0]), U.ProfileOperation(U.ProfileCmd.D, [-1, 0]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.X, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismYDirectionFinal_I9():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [6, 3, 3]), U.ProfileOperation(U.ProfileCmd.P, [0, 1, 0, 1, 0, 0]), U.ProfileOperation(U.ProfileCmd.D, [0, -1]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.Y, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(0, -1, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismRightSide_J1():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [8, 4, 0]), U.ProfileOperation(U.ProfileCmd.P, [-1, 0, 0, 0, 1, 0]), U.ProfileOperation(U.ProfileCmd.D, [-1, 0]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.X, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismRightSideY_J2():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [8, 3, 3]), U.ProfileOperation(U.ProfileCmd.P, [-1, 0, 0, 0, 1, 0]), U.ProfileOperation(U.ProfileCmd.D, [0, -1]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.Y, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismRightSideX_J3():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [8, 6, 0]), U.ProfileOperation(U.ProfileCmd.P, [-1, 0, 0, 0, 1, 0]), U.ProfileOperation(U.ProfileCmd.D, [-1, 0]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.X, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismRightSideY2_J4():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [8, 7, 3]), U.ProfileOperation(U.ProfileCmd.P, [-1, 0, 0, 0, 1, 0]), U.ProfileOperation(U.ProfileCmd.D, [0, -1]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.Y, 2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(1, 0, 0))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismRightSide_J5():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOblongPrism = U.CreateBox(gp_Pnt(8, 4, 1), 1.0, 2.0, 2.0)
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismRightSide_J6():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOblongPrism = U.CreateBox(gp_Pnt(8, 5, 2), 1.0, 2.0, 2.0)
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismRightSide_J7():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOblongPrism = U.CreateBox(gp_Pnt(8, 6, 1), 1.0, 2.0, 2.0)
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_LargePrismWithOblongPrismTop_J8():
    aBasePts = [gp_Pnt(3, 3, 0), gp_Pnt(8, 3, 0), gp_Pnt(8, 9, 0), gp_Pnt(3, 9, 0)]
    aBaseWire = U.CreatePolygonWire(aBasePts, True)
    aBaseFace = U.CreateFaceFromWire(aBaseWire)
    aBasePrism = U.CreatePrism(aBaseFace, gp_Vec(0, 0, 5))
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [8, 4, 5]), U.ProfileOperation(U.ProfileCmd.P, [0, 0, -1, 1, 0, 0]), U.ProfileOperation(U.ProfileCmd.D, [0, 1]), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.Y, -2), U.ProfileOperation(U.ProfileCmd.C, [1, 180]), U.ProfileOperation(U.ProfileCmd.W, [])]
    aProfileFace = U.CreateProfileFromOperations(aOps)
    aOblongPrism = U.CreatePrism(aProfileFace, gp_Vec(0, 0, 1))
    aResult = U.PerformFuse(aBasePrism, aOblongPrism)
    U.ValidateResult(aResult, 180.283)


def test_BFuseSimpleTest_CylinderWithRevolutionRing_J9():
    aCylinder = U.CreateCylinder(3.0, 5.0)
    aRingPts = [gp_Pnt(0, 3, 2), gp_Pnt(0, 4, 2), gp_Pnt(0, 4, 3), gp_Pnt(0, 3, 3)]
    aRingWire = U.CreatePolygonWire(aRingPts, True)
    aRingFace = U.CreateFaceFromWire(aRingWire)
    aAxis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aRing = U.CreateRevolution(aRingFace, aAxis, 269.0 * math.pi / 180.0)
    aResult = U.PerformFuse(aCylinder, aRing)
    U.ValidateResult(aResult, 190.356)


def test_BFuseSimpleTest_ComplexProfileWithRevolution_K1():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 200.0, 200.0, 100.0)
    aOps = [U.ProfileOperation(U.ProfileCmd.O, [50, 0, 0]), U.ProfileOperation(U.ProfileCmd.F, [50, -80]), U.ProfileOperation(U.ProfileCmd.X, 50), U.ProfileOperation(U.ProfileCmd.Y, 5), U.ProfileOperation(U.ProfileCmd.X, 10), U.ProfileOperation(U.ProfileCmd.Y, -25), U.ProfileOperation(U.ProfileCmd.X, -60), U.ProfileOperation(U.ProfileCmd.W, [])]
    aPlane = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.X))
    aProfile = U.CreateProfile(aPlane, aOps)
    aRevAxis = gp_Ax1(gp_Pnt(50, 100, 50), gp_Dir(gp_Dir.D.Z))
    aRevolution = U.CreateRevolution(aProfile, aRevAxis, 2 * math.pi)
    aResult = U.PerformFuse(aBox, aRevolution)
    U.ValidateResult(aResult, 161571)


def test_BFuseSimpleTest_BlendBoxWithCylinder_K2():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aCylinder = U.CreateCylinder(100.0, 50.0)
    aResult = U.PerformFuse(aBox, aCylinder)
    U.ValidateResult(aResult, 360686)


def test_BFuseSimpleTest_BlendBoxWithCylinderNegX_K3():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aBlendedBox = U.CreateBlend(aBox, 1, 100.0)
    assert not (aBlendedBox.IsNull())
    anAx3 = gp_Ax3(gp_Pnt(100, 100, 100), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.NX))
    aPlane = gp_Pln(anAx3)
    aCylinder = U.CreateCylinderOnPlane(aPlane, 100.0, 50.0)
    assert not (aCylinder.IsNull())
    aResult = U.PerformFuse(aBlendedBox, aCylinder)
    U.ValidateResult(aResult, 322832)


def test_BFuseSimpleTest_BlendBoxWithCylinderY_K4():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aBlendedBox = U.CreateBlend(aBox, 1, 100.0)
    anAx3 = gp_Ax3(gp_Pnt(100, 100, 100), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.Y))
    aPlane = gp_Pln(anAx3)
    aCylinder = U.CreateCylinderOnPlane(aPlane, 100.0, 50.0)
    aResult = U.PerformFuse(aBlendedBox, aCylinder)
    U.ValidateResult(aResult, 322832)


def test_BFuseSimpleTest_BlendBoxWithCylinderNegY_K5():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aBlendedBox = U.CreateBlend(aBox, 1, 100.0)
    anAx3 = gp_Ax3(gp_Pnt(100, 100, 100), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.NY))
    aPlane = gp_Pln(anAx3)
    aCylinder = U.CreateCylinderOnPlane(aPlane, 100.0, 50.0)
    aResult = U.PerformFuse(aBlendedBox, aCylinder)
    U.ValidateResult(aResult, 322832)


def test_BFuseSimpleTest_BlendBoxWithCylinderBottomX_K6():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aBlendedBox = U.CreateBlend(aBox, 1, 100.0)
    anAx3 = gp_Ax3(gp_Pnt(100, 100, 0), gp_Dir(gp_Dir.D.NZ), gp_Dir(gp_Dir.D.X))
    aPlane = gp_Pln(anAx3)
    aCylinder = U.CreateCylinderOnPlane(aPlane, 100.0, 50.0)
    aResult = U.PerformFuse(aBlendedBox, aCylinder)
    U.ValidateResult(aResult, 322832)


def test_BFuseSimpleTest_BlendBoxWithCylinderBottomNegX_K7():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aBlendedBox = U.CreateBlend(aBox, 1, 100.0)
    anAx3 = gp_Ax3(gp_Pnt(100, 100, 0), gp_Dir(gp_Dir.D.NZ), gp_Dir(gp_Dir.D.NX))
    aPlane = gp_Pln(anAx3)
    aCylinder = U.CreateCylinderOnPlane(aPlane, 100.0, 50.0)
    aResult = U.PerformFuse(aBlendedBox, aCylinder)
    U.ValidateResult(aResult, 322832)


def test_BFuseSimpleTest_BlendBoxWithCylinderBottomY_K8():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aBlendedBox = U.CreateBlend(aBox, 1, 100.0)
    anAx3 = gp_Ax3(gp_Pnt(100, 100, 0), gp_Dir(gp_Dir.D.NZ), gp_Dir(gp_Dir.D.Y))
    aPlane = gp_Pln(anAx3)
    aCylinder = U.CreateCylinderOnPlane(aPlane, 100.0, 50.0)
    aResult = U.PerformFuse(aBlendedBox, aCylinder)
    U.ValidateResult(aResult, 322832)


def test_BFuseSimpleTest_BlendBoxWithCylinderBottomNegY_K9():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 300.0, 300.0, 100.0)
    aBlendedBox = U.CreateBlend(aBox, 1, 100.0)
    anAx3 = gp_Ax3(gp_Pnt(100, 100, 0), gp_Dir(gp_Dir.D.NZ), gp_Dir(gp_Dir.D.NY))
    aPlane = gp_Pln(anAx3)
    aCylinder = U.CreateCylinderOnPlane(aPlane, 100.0, 50.0)
    aResult = U.PerformFuse(aBlendedBox, aCylinder)
    U.ValidateResult(aResult, 322832)


def test_BFuseSimpleTest_OCC277_FuseAndCommonOfOverlappingBoxes():
    aBox1Maker = BRepPrimAPI_MakeBox(100, 100, 100)
    aBox2Maker = BRepPrimAPI_MakeBox(gp_Pnt(50, 50, 50), 200, 200, 200)
    aShape1 = aBox1Maker.Shape()
    aShape2 = aBox2Maker.Shape()
    aFuseOp = BRepAlgoAPI_Fuse(aShape1, aShape2)
    aFuseResult = aFuseOp.Shape()
    assert not (aFuseResult.IsNull())
    aCommonOp = BRepAlgoAPI_Common(aShape1, aShape2)
    aCommonResult = aCommonOp.Shape()
    assert not (aCommonResult.IsNull())
