# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BRepAlgoAPI_Cut_Test_1.cxx (LGPL-2.1 with the OCCT exception)
import importlib.util
import pathlib
import sys

from nanocct.BRepAlgoAPI import BRepAlgoAPI_Cut
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt, gp_Trsf, gp_Vec
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


def test_BCutSimpleTest1_ComplexProfileReversedReversedVariation3_J1():
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
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -3))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 53000.0)


def test_BCutSimpleTest1_ComplexMultiCutProfileForwardForwardForward_J2():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 175, 250, -40)
    aPrism2 = U.CreateRectangularPrism(gp_Pnt(25, 25, 50), 50, 75, -30)
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate1 = aCutOp1.Shape()
    aPrism3 = U.CreateRectangularPrism(gp_Pnt(100, 150, 50), 50, 75, -30)
    aCutOp2 = BRepAlgoAPI_Cut(aIntermediate1, aPrism3)
    assert aCutOp2.IsDone()
    aIntermediate2 = aCutOp2.Shape()
    aPrism4 = U.CreateRectangularPrism(gp_Pnt(50, -75, 50), 75, 100, -30)
    aResult = U.PerformCut(aIntermediate2, aPrism4)
    U.ValidateResult(aResult, 134500.0)


def test_BCutSimpleTest1_ComplexProfileWithTranslationForwardReversedForward_J3():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 175, 250, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate1 = aCutOp1.Shape()
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 100.0, -150.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aCutOp2 = BRepAlgoAPI_Cut(aIntermediate1, aPrism3)
    assert aCutOp2.IsDone()
    aIntermediate2 = aCutOp2.Shape()
    aProfileOps4 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile4 = U.CreateProfile(aPlane2, aProfileOps4)
    aPrism4 = U.CreatePrism(aProfile4, gp_Vec(0, 0, -30))
    aPrism4 = U.TranslateShape(aPrism4, gp_Vec(-10, 0, 0))
    aResult = U.PerformCut(aIntermediate2, aPrism4)
    U.ValidateResult(aResult, 134500.0)


def test_BCutSimpleTest1_ComplexProfileReversedReversedForward_J4():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 175, 250, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 100.0, -150.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate1 = aCutOp1.Shape()
    aCutOp2 = BRepAlgoAPI_Cut(aIntermediate1, aPrism3)
    assert aCutOp2.IsDone()
    aIntermediate2 = aCutOp2.Shape()
    aProfileOps4 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile4 = U.CreateProfile(aPlane2, aProfileOps4)
    aPrism4 = U.CreatePrism(aProfile4, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate2, aPrism4)
    U.ValidateResult(aResult, 134500.0)


def test_BCutSimpleTest1_ComplexProfileForwardForwardForwardVariation_J5():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 175, 250, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 100.0, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate1 = aCutOp1.Shape()
    aCutOp2 = BRepAlgoAPI_Cut(aIntermediate1, aPrism3)
    assert aCutOp2.IsDone()
    aIntermediate2 = aCutOp2.Shape()
    aProfileOps4 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile4 = U.CreateProfile(aPlane2, aProfileOps4)
    aPrism4 = U.CreatePrism(aProfile4, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate2, aPrism4)
    U.ValidateResult(aResult, 134500.0)


def test_BCutSimpleTest1_ComplexProfileForwardReversedForwardVariation_J6():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 175, 250, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 100.0, -150.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate1 = aCutOp1.Shape()
    aCutOp2 = BRepAlgoAPI_Cut(aIntermediate1, aPrism3)
    assert aCutOp2.IsDone()
    aIntermediate2 = aCutOp2.Shape()
    aProfileOps4 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile4 = U.CreateProfile(aPlane2, aProfileOps4)
    aPrism4 = U.CreatePrism(aProfile4, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate2, aPrism4)
    U.ValidateResult(aResult, 134500.0)


def test_BCutSimpleTest1_ComplexProfileReversedReversedForwardVariation_J7():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 175, 250, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 100.0, -150.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0)]
    aProfile3 = U.CreateProfile(aPlane2, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate1 = aCutOp1.Shape()
    aCutOp2 = BRepAlgoAPI_Cut(aIntermediate1, aPrism3)
    assert aCutOp2.IsDone()
    aIntermediate2 = aCutOp2.Shape()
    aProfileOps4 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile4 = U.CreateProfile(aPlane2, aProfileOps4)
    aPrism4 = U.CreatePrism(aProfile4, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate2, aPrism4)
    U.ValidateResult(aResult, 134500.0)


def test_BCutSimpleTest1_SameOrientedProfileForwardForward_J8():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -10), gp_Dir(gp_Dir.D.Z))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_SameOrientedProfileForwardForwardWithReversed_J9():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -10), gp_Dir(gp_Dir.D.Z))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_SameOrientedProfileForwardReversed_K1():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_SameOrientedProfileForwardObjectReversedTool_K2():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_SameOrientedProfileReversedObjectForwardTool_K3():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.Y, -200.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -10), gp_Dir(gp_Dir.D.Z))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_SameOrientedProfileReversedObjectReversedTool_K4():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 40.0), U.ProfileOperation(U.ProfileCmd.Y, -200.0), U.ProfileOperation(U.ProfileCmd.X, 150.0), U.ProfileOperation(U.ProfileCmd.Y, 200.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, -40))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.P, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0), U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -25.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -10), gp_Dir(gp_Dir.D.Z))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_SameOrientedProfileForwardReversedRepeated_K5():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_SameOrientedProfileForwardObjectReversedToolVar_K6():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, -10.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_ComplexMultiStepProfileAllForward_K7():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 175, 250, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate1 = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 20.0), U.ProfileOperation(U.ProfileCmd.F, 100.0, -150.0), U.ProfileOperation(U.ProfileCmd.Y, -75.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, 75.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aCutOp2 = BRepAlgoAPI_Cut(aIntermediate1, aPrism3)
    assert aCutOp2.IsDone()
    aIntermediate2 = aCutOp2.Shape()
    aPlane4 = gp_Pln(gp_Pnt(0, 0, 25), gp_Dir(gp_Dir.D.Z))
    aProfileOps4 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 25.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 75.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile4 = U.CreateProfile(aPlane4, aProfileOps4)
    aPrism4 = U.CreatePrism(aProfile4, gp_Vec(0, 0, -5))
    aResult = U.PerformCut(aIntermediate2, aPrism4)
    U.ValidateResult(aResult, 145250.0)


def test_BCutSimpleTest1_DiffOrientedProfileAllForward_K8():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -125.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -50.0), U.ProfileOperation(U.ProfileCmd.X, -75.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 98000.0)


def test_BCutSimpleTest1_DiffOrientedProfileAllForwardVar_K9():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, -125.0), U.ProfileOperation(U.ProfileCmd.X, 50.0), U.ProfileOperation(U.ProfileCmd.Y, -50.0), U.ProfileOperation(U.ProfileCmd.X, -50.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_DiffOrientedProfileAllForward_L1():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 25.0), U.ProfileOperation(U.ProfileCmd.X, 25.0), U.ProfileOperation(U.ProfileCmd.Y, -280.0), U.ProfileOperation(U.ProfileCmd.X, -25.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_DiffOrientedProfileForwardObjectReversedTool_L2():
    aPrism1 = U.CreateRectangularPrism(gp_Pnt(0, 0, 40), 150, 200, -40)
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 50), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 50.0), U.ProfileOperation(U.ProfileCmd.F, 25.0, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 100.0), U.ProfileOperation(U.ProfileCmd.X, 75.0), U.ProfileOperation(U.ProfileCmd.Y, -100.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -30))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, 20), gp_Dir(gp_Dir.D.Z))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 20.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, 255.0), U.ProfileOperation(U.ProfileCmd.Y, -280.0), U.ProfileOperation(U.ProfileCmd.X, 25.0), U.ProfileOperation(U.ProfileCmd.Y, 280.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, 30))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 97000.0)


def test_BCutSimpleTest1_RolexCaseForwardForward_L3():
    aPlane1 = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    aProfileOps1 = [U.ProfileOperation(U.ProfileCmd.C, 60.0, 360.0)]
    aProfile1 = U.CreateProfile(aPlane1, aProfileOps1)
    aPrism1 = U.CreatePrism(aProfile1, gp_Vec(0, 0, 20))
    aPlane2 = gp_Pln(gp_Pnt(0, 0, 20), gp_Dir(gp_Dir.D.Z))
    aProfileOps2 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 20.0), U.ProfileOperation(U.ProfileCmd.F, 10.0, -20.0), U.ProfileOperation(U.ProfileCmd.C, 40.0, 360.0)]
    aProfile2 = U.CreateProfile(aPlane2, aProfileOps2)
    aPrism2 = U.CreatePrism(aProfile2, gp_Vec(0, 0, -6))
    aCutOp1 = BRepAlgoAPI_Cut(aPrism1, aPrism2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aPlane3 = gp_Pln(gp_Pnt(0, 0, -1), gp_Dir(gp_Dir.D.X))
    aProfileOps3 = [U.ProfileOperation(U.ProfileCmd.O, 0.0, 0.0, 23.0), U.ProfileOperation(U.ProfileCmd.F, 50.0, -10.0), U.ProfileOperation(U.ProfileCmd.C, -30.0, 360.0)]
    aProfile3 = U.CreateProfile(aPlane3, aProfileOps3)
    aPrism3 = U.CreatePrism(aProfile3, gp_Vec(0, 0, -9))
    aResult = U.PerformCut(aIntermediate, aPrism3)
    U.ValidateResult(aResult, 30153.0)


def test_BCutSimpleTest1_RolexCaseForwardObjectReversedTool_L4():
    aCylinder1 = U.CreateCylinder(60.0, 20.0)
    aTrsf2 = gp_Trsf()
    aTrsf2.SetTranslation(gp_Vec(0, 0, 20))
    aCylinder2 = U.CreateCylinder(40.0, 6.0).Moved(TopLoc_Location(aTrsf2))
    aCutOp1 = BRepAlgoAPI_Cut(aCylinder1, aCylinder2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aTrsf3 = gp_Trsf()
    aTrsf3.SetTranslation(gp_Vec(0, 0, 14))
    aCylinder3 = U.CreateCylinder(30.0, 9.0).Moved(TopLoc_Location(aTrsf3))
    aResult = U.PerformCut(aIntermediate, aCylinder3)
    U.ValidateResult(aResult, 30153.0)


def test_BCutSimpleTest1_RolexCaseForwardReversed_L5():
    aCylinder1 = U.CreateCylinder(60.0, 20.0)
    aTrsf2 = gp_Trsf()
    aTrsf2.SetTranslation(gp_Vec(0, 0, 20))
    aCylinder2 = U.CreateCylinder(40.0, 6.0).Moved(TopLoc_Location(aTrsf2))
    aCutOp1 = BRepAlgoAPI_Cut(aCylinder1, aCylinder2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aTrsf3 = gp_Trsf()
    aTrsf3.SetTranslation(gp_Vec(0, 0, 23))
    aCylinder3 = U.CreateCylinder(30.0, 9.0).Moved(TopLoc_Location(aTrsf3))
    aResult = U.PerformCut(aIntermediate, aCylinder3)
    U.ValidateResult(aResult, 30153.0)


def test_BCutSimpleTest1_RolexCaseForwardReversedVar_L6():
    aCylinder1 = U.CreateCylinder(60.0, 20.0)
    aTrsf2 = gp_Trsf()
    aTrsf2.SetTranslation(gp_Vec(0, 0, 20))
    aCylinder2 = U.CreateCylinder(40.0, 6.0).Moved(TopLoc_Location(aTrsf2))
    aCutOp1 = BRepAlgoAPI_Cut(aCylinder1, aCylinder2)
    assert aCutOp1.IsDone()
    aIntermediate = aCutOp1.Shape()
    aTrsf3 = gp_Trsf()
    aTrsf3.SetTranslation(gp_Vec(0, 0, 14))
    aCylinder3 = U.CreateCylinder(30.0, 9.0).Moved(TopLoc_Location(aTrsf3))
    aResult = U.PerformCut(aIntermediate, aCylinder3)
    U.ValidateResult(aResult, 30153.0)


def test_BCutSimpleTest1_SimpleCylinderCutOperation_L8():
    aCylinder1 = U.CreateCylinder(20.0, 100.0)
    aTrsf = gp_Trsf()
    aTrsf.SetTranslation(gp_Vec(0, 0, 50))
    aCylinder2 = U.CreateCylinder(20.0, 100.0).Moved(TopLoc_Location(aTrsf))
    aResult = U.PerformCut(aCylinder1, aCylinder2)
    U.ValidateResult(aResult, 8796.46)


def test_BCutSimpleTest1_ComplexFaceBasedOperation_L9():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 10.0, 10.0, 10.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 10), 5.0, 5.0, 5.0)
    aResult = U.PerformCut(aBox1, aBox2)
    U.ValidateResult(aResult, 750.0)


def test_BCutSimpleTest1_ComplexFaceBasedCompSolidOperation_M1():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 10.0, 10.0, 10.0)
    aBox2 = U.CreateBox(gp_Pnt(2, 2, 10), 5.0, 5.0, 5.0)
    aResult = U.PerformCut(aBox1, aBox2)
    U.ValidateResult(aResult, 750.0)


def test_BCutSimpleTest1_BoxCutCylinderThenCutByBox_M2():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 10.0, 10.0, 10.0)
    aBoxCopy = aBox
    aTrsf = gp_Trsf()
    aTrsf.SetTranslation(gp_Vec(5, 5, -2))
    aCylinder = U.CreateCylinder(2.0, 4.0).Moved(TopLoc_Location(aTrsf))
    aIntermediate = U.PerformCut(aBoxCopy, aCylinder)
    aResult = U.PerformCut(aIntermediate, aBox)
    assert aResult.IsNull()  or  U.GetSurfaceArea(aResult) < 0.1


def test_BCutSimpleTest1_BoxCutByPreviousResult_M3():
    aBox = U.CreateBox(gp_Pnt(0, 0, 0), 10.0, 10.0, 10.0)
    aBoxCopy = aBox
    aTrsf = gp_Trsf()
    aTrsf.SetTranslation(gp_Vec(5, 5, -2))
    aCylinder = U.CreateCylinder(2.0, 4.0).Moved(TopLoc_Location(aTrsf))
    aIntermediate = U.PerformCut(aBoxCopy, aCylinder)
    aResult = U.PerformCut(aBox, aIntermediate)
    U.ValidateResult(aResult, 50.2655)
