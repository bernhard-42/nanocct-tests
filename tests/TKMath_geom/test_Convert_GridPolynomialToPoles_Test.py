# Translated from OCCT src/FoundationClasses/TKMath/GTests/Convert_GridPolynomialToPoles_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Convert import Convert_GridPolynomialToPoles
from nanocct.NCollection import NCollection_Array1


def _inputs():
    num_coeff = NCollection_Array1[int](1, 2)
    num_coeff.SetValue(1, 2)
    num_coeff.SetValue(2, 2)
    coeffs = NCollection_Array1[float](1, 12)
    for i in range(1, 13):
        coeffs.SetValue(i, 0.0)
    coeffs.SetValue(5, 1.0)
    coeffs.SetValue(7, 1.0)
    poly_u = NCollection_Array1[float](1, 2)
    poly_u.SetValue(1, 0.0)
    poly_u.SetValue(2, 1.0)
    poly_v = NCollection_Array1[float](1, 2)
    poly_v.SetValue(1, 0.0)
    poly_v.SetValue(2, 1.0)
    return num_coeff, coeffs, poly_u, poly_v


def test_Convert_GridPolynomialToPolesTest_SinglePlanarPatch():
    conv = Convert_GridPolynomialToPoles(1, 1, *_inputs())
    assert conv.IsDone() is True
    assert conv.NbUPoles() > 0
    assert conv.NbVPoles() > 0
    assert conv.UDegree() == 1
    assert conv.VDegree() == 1
    assert conv.NbUKnots() > 0
    assert conv.NbVKnots() > 0
    assert conv.Poles().Size() > 0


def test_Convert_GridPolynomialToPolesTest_QueryMethods():
    conv = Convert_GridPolynomialToPoles(1, 1, *_inputs())
    assert conv.IsDone() is True
    uk = conv.UKnots()
    vk = conv.VKnots()
    um = conv.UMultiplicities()
    vm = conv.VMultiplicities()
    assert uk.Size() > 0
    assert vk.Size() > 0
    assert um.Size() > 0
    assert vm.Size() > 0
    assert uk.Length() == conv.NbUKnots()
    assert vk.Length() == conv.NbVKnots()
