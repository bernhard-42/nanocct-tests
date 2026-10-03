# Translated from OCCT src/FoundationClasses/TKernel/GTests/Standard_Failure_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import Standard_Failure, Standard_OutOfRange


def test_Standard_Failure_Test_OCC670_ExceptionWithoutMessage():
    # C++ throws Standard_OutOfRange("test") itself; here OCCT throws it (index out of range)
    caught = False
    try:
        NCollection_Array1[int](1, 2).Value(5)
    except Standard_Failure as exc:
        caught = True
        assert isinstance(exc, Standard_OutOfRange)
        assert str(exc) != ""
    assert caught
