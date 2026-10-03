# Translated from OCCT src/ModelingAlgorithms/TKHelix/GTests/HelixBRep_BuilderHelix_Integration_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct import TopoDS
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.GeomAbs import GeomAbs_C1, GeomAbs_C2
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.HelixBRep import HelixBRep_BuilderHelix
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import Standard_ConstructionError
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_WIRE
from nanocct.TopExp import TopExp_Explorer

TOL = 1.0e-4


def _axis():
    return gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0))


def _array(values, kind=float):
    arr = NCollection_Array1[kind](1, len(values))
    for i, v in enumerate(values, start=1):
        arr[i] = v
    return arr


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def _wire_length(shape):
    props = GProp_GProps()
    BRepGProp.LinearProperties_s(shape, props)
    return props.Mass()


def _validate_helix_wire(wire, expected_length, tolerance=0.05):
    assert not wire.IsNull()
    assert wire.ShapeType() == TopAbs_WIRE
    assert _count(wire, TopAbs_EDGE) > 0
    length = _wire_length(wire)
    if expected_length > 0:
        assert abs(length - expected_length) <= expected_length * tolerance


def test_HelixBRepTest_TCL_Test_A1_PureCylindricalHelix():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, _array([100.0]), _array([5.0]), _array([False], bool))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    wire = b.Shape()
    assert not wire.IsNull()
    assert wire.ShapeType() == TopAbs_WIRE
    circ = math.pi * 100.0
    expected = (100.0 / 20.0) * math.sqrt(circ * circ + 20.0 * 20.0)
    _validate_helix_wire(TopoDS.Wire(wire), expected)


def test_HelixBRepTest_TCL_Test_B1_CompositeCylindricalHelix():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), _array([100.0, 100.0]), _array([100.0]), _array([20.0]), _array([True], bool))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    wire = b.Shape()
    assert not wire.IsNull()
    circ = math.pi * 100.0
    expected = (100.0 / 20.0) * math.sqrt(circ * circ + 20.0 * 20.0)
    _validate_helix_wire(TopoDS.Wire(wire), expected)


def test_HelixBRepTest_TCL_Test_C1_SpiralHelix():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(
        _axis(), 100.0, 20.0, _array([20.0, 60.0, 20.0]), _array([2.0, 6.0, 2.0]), _array([False, False, False], bool)
    )
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    wire = b.Shape()
    assert not wire.IsNull()
    _validate_helix_wire(TopoDS.Wire(wire), 0)


def test_HelixBRepTest_TCL_Test_F1_Helix2Interface():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, _array([10.0, 10.0, 10.0]), _array([2.0, 6.0, 2.0]))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    wire = b.Shape()
    assert not wire.IsNull()
    circ = math.pi * 100.0
    expected = (2.0 + 6.0 + 2.0) * math.sqrt(circ * circ + 10.0 * 10.0)
    _validate_helix_wire(TopoDS.Wire(wire), expected)


def test_HelixBRepTest_TCL_Test_E1_CustomerExample():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(
        _axis(),
        _array([150.0, 150.0, 150.0, 123.0, 123.0, 123.0]),
        _array([0.75 * 13.0, 2.1 * 64.0, 2.25 * 50.0, 2.5 * 45.0, 0.75 * 13.0]),
        _array([0.75, 2.1, 2.25, 2.5, 0.75]),
        _array([False] * 5, bool),
    )
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    wire = b.Shape()
    assert not wire.IsNull()
    _validate_helix_wire(TopoDS.Wire(wire), 0)


def test_HelixBRepTest_ErrorConditions_InvalidDimensions():
    b = HelixBRep_BuilderHelix()
    with pytest.raises(Standard_ConstructionError):
        b.SetParameters(_axis(), _array([100.0, 100.0, 100.0]), _array([50.0]), _array([10.0]), _array([True], bool))


def test_HelixBRepTest_ErrorConditions_TurnsInterface():
    b = HelixBRep_BuilderHelix()
    with pytest.raises(Standard_ConstructionError):
        b.SetParameters(_axis(), 100.0, _array([10.0, 10.0]), _array([5.0]))


def test_HelixBRepTest_ApproximationQuality():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 50.0, _array([50.0]), _array([10.0]), _array([True], bool))
    tight = 1.0e-6
    b.SetApproxParameters(tight, 8, GeomAbs_C2)
    b.Perform()
    assert b.ErrorStatus() == 0
    reached = b.ToleranceReached()
    assert reached > 0.0
    assert reached < tight * 1000


def test_HelixBRepTest_ParameterValidation():
    b = HelixBRep_BuilderHelix()
    heights = _array([1.0e-8])
    pitches = _array([10.0])
    is_pitches = _array([True], bool)
    b.SetParameters(_axis(), 50.0, heights, pitches, is_pitches)
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() != 0

    heights[1] = 50.0
    pitches[1] = 0.0
    b.SetParameters(_axis(), 50.0, heights, pitches, is_pitches)
    b.Perform()
    assert b.ErrorStatus() != 0


def test_HelixBRepTest_MultiPartContinuity():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(
        _axis(), _array([80.0, 60.0, 40.0]), _array([40.0, 40.0]), _array([8.0, 12.0]), _array([True, True], bool)
    )
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    shape = b.Shape()
    assert not shape.IsNull()
    assert shape.ShapeType() == TopAbs_WIRE
    assert _count(shape, TopAbs_EDGE) > 1
    wire = TopoDS.Wire(shape)
    check = BRepCheck_Analyzer(wire)
    assert check.IsValid()
