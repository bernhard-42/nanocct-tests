# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_CompPolynomialToPoles_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Convert import Convert_CompPolynomialToPoles
from nanocct.NCollection import NCollection_Array1, NCollection_HArray1, NCollection_HArray2


def _arr_f(values):
    a = NCollection_Array1[float](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


def test_Convert_CompPolynomialToPolesTest_SingleLinearPolynomial():
    conv = Convert_CompPolynomialToPoles(1, 1, 1, _arr_f([1.0, 2.0]), _arr_f([-1.0, 1.0]), _arr_f([-1.0, 1.0]))
    assert conv.IsDone() is True
    assert conv.Degree() == 1
    assert conv.NbKnots() == 2
    assert conv.NbPoles() > 0


def test_Convert_CompPolynomialToPolesTest_SingleQuadraticPolynomial():
    conv = Convert_CompPolynomialToPoles(1, 2, 2, _arr_f([0.0, 0.0, 1.0]), _arr_f([0.0, 1.0]), _arr_f([0.0, 1.0]))
    assert conv.IsDone() is True
    assert conv.Degree() == 2


def test_Convert_CompPolynomialToPolesTest_TwoSpansUniformContinuity():
    num_coeff = NCollection_HArray1[int](1, 2)
    num_coeff.SetValue(1, 2)
    num_coeff.SetValue(2, 2)
    coeffs = NCollection_HArray1[float](1, 4)
    for i, v in enumerate([0.0, 1.0, 1.0, -1.0], 1):
        coeffs.SetValue(i, v)
    poly = NCollection_HArray2[float](1, 2, 1, 2)
    poly.SetValue(1, 1, 0.0)
    poly.SetValue(1, 2, 1.0)
    poly.SetValue(2, 1, 0.0)
    poly.SetValue(2, 2, 1.0)
    true_int = NCollection_HArray1[float](1, 3)
    for i, v in enumerate([0.0, 0.5, 1.0], 1):
        true_int.SetValue(i, v)
    conv = Convert_CompPolynomialToPoles(2, 0, 1, 1, num_coeff, coeffs, poly, true_int)
    assert conv.IsDone() is True
    assert conv.Degree() == 1
    assert conv.NbKnots() == 3


def test_Convert_CompPolynomialToPolesTest_ThreeDimensional():
    conv = Convert_CompPolynomialToPoles(3, 1, 1, _arr_f([0.0, 0.0, 0.0, 1.0, 2.0, 3.0]), _arr_f([0.0, 1.0]),
                                         _arr_f([0.0, 1.0]))
    assert conv.IsDone() is True
    assert conv.Degree() == 1
    poles = conv.Poles()
    assert poles.RowLength() == 3
