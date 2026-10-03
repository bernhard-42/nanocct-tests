# Translated from OCCT src/FoundationClasses/TKernel/GTests/UnitsAPI_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.UnitsAPI import UnitsAPI, UnitsAPI_MDTV


def test_UnitsAPI_Test_BUC60727_AnyToLS_Conversion():
    UnitsAPI.SetLocalSystem_s(UnitsAPI_MDTV)
    assert UnitsAPI.AnyToLS_s(3.0, "mm") == 3.0


def test_UnitsAPI_Test_AnyToAny_UnknownUnit():
    assert UnitsAPI.AnyToAny_s(1.0, "unknown_unit", "mm") == 1.0
    assert UnitsAPI.AnyToAny_s(1.0, "mm", "unknown_unit") == 1.0
