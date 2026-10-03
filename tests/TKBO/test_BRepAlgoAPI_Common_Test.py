# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BRepAlgoAPI_Common_Test.cxx (LGPL-2.1 with the OCCT exception)
import importlib.util
import pathlib
import sys

from nanocct.gp import gp_Pnt


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


def test_BOPCommonSimpleTest_IdenticalBoxes_A1():
    aBox1 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aBox2 = U.CreateBox(gp_Pnt(0, 0, 0), 1.0, 1.0, 1.0)
    aResult = U.PerformCommon(aBox1, aBox2)
    U.ValidateResult(aResult, 6.0)
