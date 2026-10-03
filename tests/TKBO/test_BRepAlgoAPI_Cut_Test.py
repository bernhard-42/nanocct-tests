# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BRepAlgoAPI_Cut_Test.cxx (LGPL-2.1 with the OCCT exception)
import importlib.util
import math
import pathlib
import sys

from nanocct.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeHalfSpace, BRepPrimAPI_MakeSphere
from nanocct.Geom import Geom_BezierSurface
from nanocct.GeomConvert import GeomConvert
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pln, gp_Pnt, gp_Vec
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_Array2
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_COMPOUND, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
from nanocct.TopExp import TopExp_Explorer


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


def countSubShapes(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def test_BCutSimpleTest_SphereMinusBox_A1():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aResult = U.PerformCut(aSphere, aBox)
    U.ValidateResult(aResult, 13.3518)


def test_BCutSimpleTest_RotatedSphereMinusBox_A2():
    aSphere = U.CreateUnitSphere()
    aRotatedSphere = U.RotateStandard(aSphere)
    aBox = U.CreateUnitBox()
    aResult = U.PerformCut(aRotatedSphere, aBox)
    U.ValidateResult(aResult, 13.3517)


def test_BCutSimpleTest_BoxMinusRotatedSphere_A3():
    aSphere = U.CreateUnitSphere()
    aRotatedSphere = U.RotateStandard(aSphere)
    aBox = U.CreateUnitBox()
    aResult = U.PerformCut(aBox, aRotatedSphere)
    U.ValidateResult(aResult, 5.2146)


def test_BCutSimpleTest_SphereMinusRotatedBox_A4():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aRotatedBox = U.RotateY90(aBox)
    aResult = U.PerformCut(aSphere, aRotatedBox)
    U.ValidateResult(aResult, 13.3517)


def test_BCutSimpleTest_RotatedBoxMinusSphere_A5():
    aSphere = U.CreateUnitSphere()
    aBox = U.CreateUnitBox()
    aRotatedBox = U.RotateY90(aBox)
    aResult = U.PerformCut(aRotatedBox, aSphere)
    U.ValidateResult(aResult, 5.2146)


def test_BCutSimpleTest_IdenticalNurbsBoxMinusBox_A6():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aNurbsBox, aBox)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BCutSimpleTest_IdenticalBoxMinusNurbsBox_A7():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aBox, aNurbsBox)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BCutSimpleTest_NurbsBoxMinusLargerBox_A8():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aLargerBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.5, 1.0)
    aResult = U.PerformCut(aNurbsBox, aLargerBox)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BCutSimpleTest_LargerBoxMinusNurbsBox_A9():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aLargerBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.5, 1.0)
    aResult = U.PerformCut(aLargerBox, aNurbsBox)
    U.ValidateResult(aResult, 4.0)


def test_BCutSimpleTest_NurbsBoxMinusBox_B1():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox1 = U.ConvertToNurbs(aBox1)
    assert not (aBox1.IsNull())
    aBox2 = U.CreateBox(gp_Pnt(0, 1, 0), 1.0, 0.5, 1.0)
    aResult = U.PerformCut(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_BoxMinusNurbsBox_B2():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aBox = U.CreateBox(gp_Pnt(0, 1, 0), 1.0, 0.5, 1.0)
    aResult = U.PerformCut(aBox, aNurbsBox)
    U.ValidateResult(aResult, 4.0)


def test_BCutSimpleTest_NurbsBoxMinusAdjacentBox_B3():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aAdjacentBox = U.CreateBox(gp_Pnt(1, 1, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aNurbsBox, aAdjacentBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_AdjacentBoxMinusNurbsBox_B4():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aAdjacentBox = U.CreateBox(gp_Pnt(1, 1, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aAdjacentBox, aNurbsBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_NurbsBoxMinusSmallerBox_B5():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aSmallerBox = U.CreateBox(gp_Pnt(0, 0, 0), 0.5, 1.0, 0.5)
    aResult = U.PerformCut(aNurbsBox, aSmallerBox)
    U.ValidateResult(aResult, 5.5)


def test_BCutSimpleTest_SmallerBoxMinusNurbsBox_B6():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aSmallerBox = U.CreateBox(gp_Pnt(0, 0, 0), 0.5, 1.0, 0.5)
    aResult = U.PerformCut(aSmallerBox, aNurbsBox)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BCutSimpleTest_NurbsBoxMinusPartiallyOverlappingBox_B7():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aPartialBox = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformCut(aNurbsBox, aPartialBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_PartiallyOverlappingBoxMinusNurbsBox_B8():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aPartialBox = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformCut(aPartialBox, aNurbsBox)
    U.ValidateResult(aResult, 2.5)


def test_BCutSimpleTest_NurbsBoxMinusExtendedBox_B9():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aExtendedBox = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 1.5, 1.0)
    aResult = U.PerformCut(aNurbsBox, aExtendedBox)
    U.ValidateResult(aResult, 4.0)


def test_BCutSimpleTest_ExtendedBoxMinusNurbsBox_C1():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aExtendedBox = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 1.5, 1.0)
    aResult = U.PerformCut(aExtendedBox, aNurbsBox)
    U.ValidateResult(aResult, 2.5)


def test_BCutSimpleTest_NurbsBoxMinusShiftedBox_C2():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aShiftedBox = U.CreateBox(gp_Pnt(0, 0.5, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aNurbsBox, aShiftedBox)
    U.ValidateResult(aResult, 4.0)


def test_BCutSimpleTest_ShiftedBoxMinusNurbsBox_C3():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aShiftedBox = U.CreateBox(gp_Pnt(0, 0.5, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aShiftedBox, aNurbsBox)
    U.ValidateResult(aResult, 4.0)


def test_BCutSimpleTest_NurbsBoxMinusNarrowBox_C4():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aNarrowBox = U.CreateBox(gp_Pnt(0, 0.25, 0), 1.0, 0.5, 1.0)
    aResult = U.PerformCut(aNurbsBox, aNarrowBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_NarrowBoxMinusNurbsBox_C5():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aNarrowBox = U.CreateBox(gp_Pnt(0, 0.25, 0), 1.0, 0.5, 1.0)
    aResult = U.PerformCut(aNarrowBox, aNurbsBox)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BCutSimpleTest_NurbsBoxMinusCornerCube_C6():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aCornerCube = U.CreateBox(gp_Pnt(0, 0, 0), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aNurbsBox, aCornerCube)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_CornerCubeMinusNurbsBox_C7():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aCornerCube = U.CreateBox(gp_Pnt(0, 0, 0), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aCornerCube, aNurbsBox)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BCutSimpleTest_NurbsBoxMinusOffsetCube_C8():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetCube = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aNurbsBox, aOffsetCube)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_OffsetCubeMinusNurbsBox_C9():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetCube = U.CreateBox(gp_Pnt(0, -0.5, 0), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aOffsetCube, aNurbsBox)
    U.ValidateResult(aResult, 1.5)


def test_BCutSimpleTest_NurbsBoxMinusOffsetCornerCube_D1():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetCornerCube = U.CreateBox(gp_Pnt(0, -0.5, -0.5), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aNurbsBox, aOffsetCornerCube)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_OffsetCornerCubeMinusNurbsBox_D2():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetCornerCube = U.CreateBox(gp_Pnt(0, -0.5, -0.5), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aOffsetCornerCube, aNurbsBox)
    U.ValidateResult(aResult, 1.5)


def test_BCutSimpleTest_NurbsBoxMinusShiftedCornerCube_D3():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aShiftedCornerCube = U.CreateBox(gp_Pnt(-0.5, -0.5, -0.5), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aNurbsBox, aShiftedCornerCube)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_ShiftedCornerCubeMinusNurbsBox_D4():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aShiftedCornerCube = U.CreateBox(gp_Pnt(-0.5, -0.5, -0.5), 0.5, 0.5, 0.5)
    aResult = U.PerformCut(aShiftedCornerCube, aNurbsBox)
    U.ValidateResult(aResult, 1.5)


def test_BCutSimpleTest_NurbsBoxMinusExtendedXBox_D5():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aExtendedXBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.5, 0.5, 0.5)
    aResult = U.PerformCut(aNurbsBox, aExtendedXBox)
    U.ValidateResult(aResult, 5.5)


def test_BCutSimpleTest_ExtendedXBoxMinusNurbsBox_D6():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aExtendedXBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.5, 0.5, 0.5)
    aResult = U.PerformCut(aExtendedXBox, aNurbsBox)
    U.ValidateResult(aResult, 1.5)


def test_BCutSimpleTest_NurbsBoxMinusOffsetExtendedXBox_D7():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetExtendedXBox = U.CreateBox(gp_Pnt(0, -0.5, 0), 1.5, 0.5, 0.5)
    aResult = U.PerformCut(aNurbsBox, aOffsetExtendedXBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_OffsetExtendedXBoxMinusNurbsBox_D8():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetExtendedXBox = U.CreateBox(gp_Pnt(0, -0.5, 0), 1.5, 0.5, 0.5)
    aResult = U.PerformCut(aOffsetExtendedXBox, aNurbsBox)
    U.ValidateResult(aResult, 3.5)


def test_BCutSimpleTest_NurbsBoxMinusShiftedNarrowBox_D9():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aShiftedNarrowBox = U.CreateBox(gp_Pnt(0.25, 0, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformCut(aNurbsBox, aShiftedNarrowBox)
    U.ValidateResult(aResult, 6.5)


def test_BCutSimpleTest_ShiftedNarrowBoxMinusNurbsBox_E1():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aShiftedNarrowBox = U.CreateBox(gp_Pnt(0.25, 0, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformCut(aShiftedNarrowBox, aNurbsBox)
    U.ValidateResult(aResult, -1.0, -1.0, True)


def test_BCutSimpleTest_NurbsBoxMinusOffsetShiftedNarrowBox_E2():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetShiftedNarrowBox = U.CreateBox(gp_Pnt(0.25, -0.5, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformCut(aNurbsBox, aOffsetShiftedNarrowBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_OffsetShiftedNarrowBoxMinusNurbsBox_E3():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetShiftedNarrowBox = U.CreateBox(gp_Pnt(0.25, -0.5, 0), 0.5, 0.5, 1.0)
    aResult = U.PerformCut(aOffsetShiftedNarrowBox, aNurbsBox)
    U.ValidateResult(aResult, 2.5)


def test_BCutSimpleTest_NurbsBoxMinusExtendedYShiftedNarrowBox_E4():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aExtendedYShiftedNarrowBox = U.CreateBox(gp_Pnt(0.25, 0, 0), 0.5, 1.5, 1.0)
    aResult = U.PerformCut(aNurbsBox, aExtendedYShiftedNarrowBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_ExtendedYShiftedNarrowBoxMinusNurbsBox_E5():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aExtendedYShiftedNarrowBox = U.CreateBox(gp_Pnt(0.25, 0, 0), 0.5, 1.5, 1.0)
    aResult = U.PerformCut(aExtendedYShiftedNarrowBox, aNurbsBox)
    U.ValidateResult(aResult, 2.5)


def test_BCutSimpleTest_NurbsBoxMinusRightHalfBox_E6():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aRightHalfBox = U.CreateBox(gp_Pnt(0.5, 0, 0), 1.0, 1.0, 0.5)
    aResult = U.PerformCut(aNurbsBox, aRightHalfBox)
    U.ValidateResult(aResult, 5.5)


def test_BCutSimpleTest_RightHalfBoxMinusNurbsBox_E7():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aRightHalfBox = U.CreateBox(gp_Pnt(0.5, 0, 0), 1.0, 1.0, 0.5)
    aResult = U.PerformCut(aRightHalfBox, aNurbsBox)
    U.ValidateResult(aResult, 2.5)


def test_BCutSimpleTest_NurbsBoxMinusOffsetRightHalfBox_E8():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetRightHalfBox = U.CreateBox(gp_Pnt(0.5, 0, -0.5), 1.0, 1.0, 0.5)
    aResult = U.PerformCut(aNurbsBox, aOffsetRightHalfBox)
    U.ValidateResult(aResult, 6.0)


def test_BCutSimpleTest_OffsetRightHalfBoxMinusNurbsBox_E9():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    assert not (aNurbsBox.IsNull())
    aOffsetRightHalfBox = U.CreateBox(gp_Pnt(0.5, 0, -0.5), 1.0, 1.0, 0.5)
    aResult = U.PerformCut(aOffsetRightHalfBox, aNurbsBox)
    U.ValidateResult(aResult, 4.0)


def test_BCutSimpleTest_NurbsBoxMinusRotatedRectangularBox_F1():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = math.sqrt(2.0)
    aRectangularBox = U.CreateBox(gp_Pnt(0, 0, 0), r, r / 2.0, 1.0)
    aRectangularBox = U.RotateShape(aRectangularBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 45.0 * math.pi / 180.0)
    aResult = U.PerformCut(aNurbsBox, aRectangularBox)
    U.ValidateResult(aResult, 4.41421)


def test_BCutSimpleTest_RotatedRectangularBoxMinusNurbsBox_F2():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = math.sqrt(2.0)
    aRectangularBox = U.CreateBox(gp_Pnt(0, 0, 0), r, r / 2.0, 1.0)
    aRectangularBox = U.RotateShape(aRectangularBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 45.0 * math.pi / 180.0)
    aResult = U.PerformCut(aRectangularBox, aNurbsBox)
    U.ValidateResult(aResult, 5.82843)


def test_BCutSimpleTest_NurbsBoxMinusRotatedSquareBox_F3():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = math.sqrt(2.0) / 2.0
    aSquareBox = U.CreateBox(gp_Pnt(0, 0, 0), r, r, 1.0)
    aSquareBox = U.RotateShape(aSquareBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 45.0 * math.pi / 180.0)
    aResult = U.PerformCut(aNurbsBox, aSquareBox)
    U.ValidateResult(aResult, 5.91421)


def test_BCutSimpleTest_RotatedSquareBoxMinusNurbsBox_F4():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = math.sqrt(2.0) / 2.0
    aSquareBox = U.CreateBox(gp_Pnt(0, 0, 0), r, r, 1.0)
    aSquareBox = U.RotateShape(aSquareBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 45.0 * math.pi / 180.0)
    aResult = U.PerformCut(aSquareBox, aNurbsBox)
    U.ValidateResult(aResult, 2.91421)


def test_BCutSimpleTest_NurbsBoxMinusRotatedThinBox_F5():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = math.sqrt(2.0)
    aThinBox = U.CreateBox(gp_Pnt(0, 0, 0), r, 0.25, 1.0)
    aThinBox = U.RotateShape(aThinBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 45.0 * math.pi / 180.0)
    aResult = U.PerformCut(aNurbsBox, aThinBox)
    U.ValidateResult(aResult, 7.03921)


def test_BCutSimpleTest_RotatedThinBoxMinusNurbsBox_F6():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = math.sqrt(2.0)
    aThinBox = U.CreateBox(gp_Pnt(0, 0, 0), r, 0.25, 1.0)
    aThinBox = U.RotateShape(aThinBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 45.0 * math.pi / 180.0)
    aResult = U.PerformCut(aThinBox, aNurbsBox)
    U.ValidateResult(aResult, 1.83211)


def test_BCutSimpleTest_NurbsBoxMinusRotatedNarrowBox_F7():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = 5.5677643628300219
    aNarrowBox = U.CreateBox(gp_Pnt(0, 0, 0), r / 4.0, 0.25, 1.0)
    aNarrowBox = U.RotateShape(aNarrowBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 34.73 * math.pi / 180.0)
    aResult = U.PerformCut(aNurbsBox, aNarrowBox)
    U.ValidateResult(aResult, 7.21677)


def test_BCutSimpleTest_RotatedNarrowBoxMinusNurbsBox_F8():
    aNurbsBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aNurbsBox = U.ConvertToNurbs(aNurbsBox)
    r = 5.5677643628300219
    aNarrowBox = U.CreateBox(gp_Pnt(0, 0, 0), r / 4.0, 0.25, 1.0)
    aNarrowBox = U.RotateShape(aNarrowBox, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), 34.73 * math.pi / 180.0)
    aResult = U.PerformCut(aNarrowBox, aNurbsBox)
    U.ValidateResult(aResult, 1.54631)


def test_BCutSimpleTest_SphereMinusBox_F9():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aSphere, aBox)
    U.ValidateResult(aResult, 13.3518)


def test_BCutSimpleTest_BoxMinusSphere_G1():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aBox, aSphere)
    U.ValidateResult(aResult, 5.2146)


def test_BCutSimpleTest_RotatedSphereMinusBox_G2():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aSphere = U.RotateShape(aSphere, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), -90.0 * math.pi / 180.0)
    aSphere = U.RotateShape(aSphere, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Y)), -45.0 * math.pi / 180.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aSphere, aBox)
    U.ValidateResult(aResult, 13.3517)


def test_BCutSimpleTest_BoxMinusRotatedSphere_G3():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aSphere = U.RotateShape(aSphere, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), -90.0 * math.pi / 180.0)
    aSphere = U.RotateShape(aSphere, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Y)), -45.0 * math.pi / 180.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aBox, aSphere)
    U.ValidateResult(aResult, 5.2146)


def test_BCutSimpleTest_SphereMinusRotatedBox_G4():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox = U.RotateShape(aBox, gp_Ax1(gp_Pnt(0, 0, 1), gp_Dir(gp_Dir.D.Y)), 90.0 * math.pi / 180.0)
    aResult = U.PerformCut(aSphere, aBox)
    U.ValidateResult(aResult, 13.3517)


def test_BCutSimpleTest_RotatedBoxMinusSphere_G5():
    aSphere = U.CreateSphere(gp_Pnt(0, 0, 0), 1.0)
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox = U.RotateShape(aBox, gp_Ax1(gp_Pnt(0, 0, 1), gp_Dir(gp_Dir.D.Y)), 90.0 * math.pi / 180.0)
    aResult = U.PerformCut(aBox, aSphere)
    U.ValidateResult(aResult, 5.2146)


def test_BCutSimpleTest_ComplexProfileRevolOperation_G6():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 100.0, 100.0, 40.0)
    aPlane = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps = [U.ProfileOperation(U.ProfileCmd.F, 50.0, 20.0), U.ProfileOperation(U.ProfileCmd.Y, 50.0), U.ProfileOperation(U.ProfileCmd.C, 10.0, 180.0), U.ProfileOperation(U.ProfileCmd.Y, -50.0), U.ProfileOperation(U.ProfileCmd.C, 10.0, 180.0)]
    aProfile = U.CreateProfile(aPlane, aProfileOps)
    aRevolution = U.CreateRevolution(aProfile, gp_Ax1(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Y)), 2.0 * math.pi)
    aResult = U.PerformCut(aBox, aRevolution)
    U.ValidateResult(aResult, 41187.4)


def test_BCutSimpleTest_BoxMinusTranslatedBox_G7():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 3.0, 3.0, 3.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 3, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCut(aBox1, aBox2)
    U.ValidateResult(aResult, 54.0)


def test_BCutSimpleTest_BoxMinusPrism_G8():
    aBoxMb = U.CreateBox(gp_Pnt(-0.5, -0.5, -0.5), 1.0, 1.0, 1.0)
    aFace = U.GetFaceByIndex(aBoxMb, 1)
    aSemiInfPrism = U.CreatePrism(aFace, gp_Vec(1000.0, 0.0, 0.0))
    aBoxAb = U.CreateBox(gp_Pnt(0, -1, -1), 2.0, 2.0, 2.0)
    aResult = U.PerformCut(aBoxAb, aSemiInfPrism)
    U.ValidateResult(aResult, 30.0)


def test_BCutSimpleTest_ComplexCylinderConeOperation_G9():
    aCylinder = U.CreateCylinder(9.0, 3.0)
    aCone = U.CreateCone(7.0, 6.0, 4.0)
    aFuseOp = BRepAlgoAPI_Fuse(aCylinder, aCone)
    assert aFuseOp.IsDone()
    aBody = aFuseOp.Shape()
    aSmallCylinder = U.CreateCylinder(1.0, 9.0)
    aSmallCylinder = U.TranslateShape(aSmallCylinder, gp_Vec(5.0, 0.0, -2.0))
    aResult = U.PerformCut(aBody, aSmallCylinder)
    U.ValidateResult(aResult, 727.481)


def test_BCutSimpleTest_ComplexPolygonPrismMinusBox_H1():
    aPoints = []
    aPoints.append(gp_Pnt(0, 0, 0))
    aPoints.append(gp_Pnt(1, 0, 0))
    aPoints.append(gp_Pnt(1, 3, 0))
    aPoints.append(gp_Pnt(2, 3, 0))
    aPoints.append(gp_Pnt(2, 0, 0))
    aPoints.append(gp_Pnt(3, 0, 0))
    aPoints.append(gp_Pnt(3, 5, 0))
    aPoints.append(gp_Pnt(0, 5, 0))
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aSolid = U.CreatePrism(aFace, gp_Vec(0, 0, 2))
    aBox = U.CreateBox(gp_Pnt(-1, 2, 1), 5.0, 1.0, 3.0)
    aResult = U.PerformCut(aSolid, aBox)
    U.ValidateResult(aResult, 68.0)


def test_BCutSimpleTest_ComplexPolygonPrismMinusBox_H2():
    aPoints = []
    aPoints.append(gp_Pnt(0, 0, 0))
    aPoints.append(gp_Pnt(1, 0, 0))
    aPoints.append(gp_Pnt(1, 3, 0))
    aPoints.append(gp_Pnt(2, 3, 0))
    aPoints.append(gp_Pnt(2, 0, 0))
    aPoints.append(gp_Pnt(3, 0, 0))
    aPoints.append(gp_Pnt(3, 5, 0))
    aPoints.append(gp_Pnt(0, 5, 0))
    aWire = U.CreatePolygonWire(aPoints, True)
    aFace = U.CreateFaceFromWire(aWire)
    aSolid = U.CreatePrism(aFace, gp_Vec(0, 0, 2))
    aBox = U.CreateBox(gp_Pnt(-1, 2, 1), 5.0, 1.0, 3.0)
    aResult = U.PerformCut(aSolid, aBox)
    U.ValidateResult(aResult, 68.0)


def test_BCutSimpleTest_ComplexCylinderConeOperationPro13307_H3():
    aCylinder = U.CreateCylinder(9.0, 3.0)
    aCone = U.CreateCone(7.0, 6.0, 4.0)
    aFuseOp = BRepAlgoAPI_Fuse(aCylinder, aCone)
    assert aFuseOp.IsDone()
    aBody = aFuseOp.Shape()
    aSmallCylinder = U.CreateCylinder(1.0, 9.0)
    aSmallCylinder = U.TranslateShape(aSmallCylinder, gp_Vec(5.0, 0.0, -2.0))
    aResult = U.PerformCut(aBody, aSmallCylinder)
    U.ValidateResult(aResult, 727.481)


def test_BCutSimpleTest_ComplexProfileForwardForward_H4():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileForwardForwardVariation_H5():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileForwardReversed_H6():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileForwardReversedVariation_H7():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileReversedForward_H8():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.Y, -200.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileReversedForwardVariation_H9():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.Y, -200.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileReversedReversed_I1():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.Y, -200.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileReversedReversedVariation_I2():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.Y, -200.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest_ComplexProfileForwardForwardVariation2_I3():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.F, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 52000.0)


def test_BCutSimpleTest_ComplexProfileForwardForwardVariation3_I4():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.F, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -3))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 53000.0)


def test_BCutSimpleTest_ComplexProfileForwardReversedVariation2_I5():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.F, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 52000.0)


def test_BCutSimpleTest_ComplexProfileForwardReversedVariation3_I6():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.F, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -150.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 52000.0)


def test_BCutSimpleTest_ComplexProfileReversedForwardVariation2_I7():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.F, 0.0, -50.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 52000.0)


def test_BCutSimpleTest_ComplexProfileReversedForwardVariation3_I8():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.F, 0.0, -50.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 52000.0)


def test_BCutSimpleTest_ComplexProfileReversedReversedVariation2_I9():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 40), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.F, 0.0, -50.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 52000.0)


def test_BRepAlgoAPI_CutTest_Bug825_SphereHalfSpaceCut():
    aSize = 50.0
    aPoles = NCollection_Array2[gp_Pnt](1, 2, 1, 2)
    aPoles.SetValue(1, 1, gp_Pnt(-aSize, 0, -aSize))
    aPoles.SetValue(1, 2, gp_Pnt(-aSize, 0, aSize))
    aPoles.SetValue(2, 1, gp_Pnt(aSize, 0, -aSize))
    aPoles.SetValue(2, 2, gp_Pnt(aSize, 0, aSize))
    aBezSurf = Geom_BezierSurface(aPoles)
    aBSpSurf = GeomConvert.SurfaceToBSplineSurface_s(aBezSurf)
    aFaceMaker = BRepBuilderAPI_MakeFace(aBSpSurf, Precision.Confusion_s())
    assert aFaceMaker.IsDone()
    aFace = aFaceMaker.Face()
    aHSpaceMaker = BRepPrimAPI_MakeHalfSpace(aFace, gp_Pnt(0, aSize, 0))
    assert aHSpaceMaker.IsDone()
    aHsp = aHSpaceMaker.Solid()
    aSph1 = BRepPrimAPI_MakeSphere(gp_Pnt(0.0, 0.0, 0.0), 25.0).Shape()
    aSph2 = BRepPrimAPI_MakeSphere(gp_Pnt(0.0, 0.00001, 0.0), 25.0).Shape()
    aCut1 = BRepAlgoAPI_Cut(aSph1, aHsp)
    assert aCut1.IsDone()
    aResult1 = aCut1.Shape()
    assert not (aResult1.IsNull())
    aCut2 = BRepAlgoAPI_Cut(aSph2, aHsp)
    assert aCut2.IsDone()
    aResult2 = aCut2.Shape()
    assert not (aResult2.IsNull())
    aProps1 = GProp_GProps()
    BRepGProp.SurfaceProperties_s(aResult1, aProps1)
    assert abs((aProps1.Mass()) - (5890.42)) <= (5.89042)
    assert (countSubShapes(aResult1, TopAbs_FACE)) == (2)
    assert (countSubShapes(aResult1, TopAbs_SHELL)) == (1)
    assert (countSubShapes(aResult1, TopAbs_SOLID)) == (1)
    assert (aResult1.ShapeType()) == (TopAbs_COMPOUND)
    aProps2 = GProp_GProps()
    BRepGProp.SurfaceProperties_s(aResult2, aProps2)
    assert abs((aProps2.Mass()) - (5890.42)) <= (5.89042)
    assert (countSubShapes(aResult2, TopAbs_FACE)) == (2)
    assert (countSubShapes(aResult2, TopAbs_SHELL)) == (1)
    assert (countSubShapes(aResult2, TopAbs_SOLID)) == (1)
    assert (aResult2.ShapeType()) == (TopAbs_COMPOUND)
