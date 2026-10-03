# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepTransientReplacements_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.NCollection import NCollection_HArray1
from nanocct.StepBasic import (
    StepBasic_ConversionBasedUnit,
    StepBasic_DimensionalExponents,
    StepBasic_MeasureValueMember,
    StepBasic_MeasureWithUnit,
    StepBasic_ProductDefinition,
    StepBasic_SiPrefix,
    StepBasic_SiUnit,
    StepBasic_SiUnitName,
    StepBasic_Unit,
)
from nanocct.StepData import StepData_LTrue
from nanocct.StepDimTol import StepDimTol_GeometricTolerance, StepDimTol_GeometricToleranceTarget
from nanocct.StepRepr import (
    StepRepr_MakeFromUsageOption,
    StepRepr_ParallelOffset,
    StepRepr_ProductDefinitionShape,
    StepRepr_QuantifiedAssemblyComponentUsage,
    StepRepr_ReprItemAndMeasureWithUnit,
)
from nanocct.StepShape import StepShape_MeasureQualification, StepShape_ValueQualifier
from nanocct.TCollection import TCollection_HAsciiString

MWU = StepBasic_MeasureWithUnit.get_type_descriptor_s
RIMWU = StepRepr_ReprItemAndMeasureWithUnit.get_type_descriptor_s


def _measure_with_unit(value):
    measure = StepBasic_MeasureWithUnit()
    member = StepBasic_MeasureValueMember()
    member.SetName("POSITIVE_LENGTH_MEASURE")
    member.SetReal(value)
    measure.SetValueComponentMember(member)
    si_unit = StepBasic_SiUnit()
    si_unit.Init(False, StepBasic_SiPrefix.StepBasic_spMilli, StepBasic_SiUnitName.StepBasic_sunMetre)
    unit = StepBasic_Unit()
    unit.SetValue(si_unit)
    measure.SetUnitComponent(unit)
    return measure


def _repr_item_and_measure_with_unit(value):
    r = StepRepr_ReprItemAndMeasureWithUnit()
    r.SetMeasureWithUnit(_measure_with_unit(value))
    r.SetName(TCollection_HAsciiString("TestReprItem"))
    return r


@pytest.fixture
def fx():
    class F:
        pass

    f = F()
    f.measure = _measure_with_unit(5.0)
    f.repr_measure = _repr_item_and_measure_with_unit(10.0)
    f.dim_exp = StepBasic_DimensionalExponents()
    f.dim_exp.Init(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    f.name = TCollection_HAsciiString("TestName")
    f.description = TCollection_HAsciiString("TestDescription")
    f.product_definition = StepBasic_ProductDefinition()
    f.product_definition_shape = StepRepr_ProductDefinitionShape()
    f.qualifiers = NCollection_HArray1[StepShape_ValueQualifier](1, 1)
    return f


def _check_measure(value, expected):
    assert value is not None
    assert value.IsKind(MWU())
    assert isinstance(value, StepBasic_MeasureWithUnit)
    assert abs(value.ValueComponent() - expected) <= 1e-7


def _check_repr_measure(value, expected):
    assert value is not None
    assert value.IsKind(RIMWU())
    assert isinstance(value, StepRepr_ReprItemAndMeasureWithUnit)
    assert abs(value.GetMeasureWithUnit().ValueComponent() - expected) <= 1e-7


def test_StepTransientReplacements_ConversionBasedUnit_WorksWithBothTypes(fx):
    unit = StepBasic_ConversionBasedUnit()
    unit.Init(fx.dim_exp, fx.name, fx.measure)
    _check_measure(unit.ConversionFactor(), 5.0)
    unit.SetConversionFactor(fx.repr_measure)
    _check_repr_measure(unit.ConversionFactor(), 10.0)


def test_StepTransientReplacements_GeometricTolerance_WorksWithBothTypes(fx):
    tol = StepDimTol_GeometricTolerance()
    tol.Init(fx.name, fx.description, fx.measure, StepDimTol_GeometricToleranceTarget())
    _check_measure(tol.Magnitude(), 5.0)
    tol.SetMagnitude(fx.repr_measure)
    _check_repr_measure(tol.Magnitude(), 10.0)


def test_StepTransientReplacements_MakeFromUsageOption_WorksWithBothTypes(fx):
    usage = StepRepr_MakeFromUsageOption()
    usage.Init(
        fx.name,
        fx.name,
        True,
        fx.description,
        fx.product_definition,
        fx.product_definition,
        1,
        fx.description,
        fx.measure,
    )
    _check_measure(usage.Quantity(), 5.0)
    usage.SetQuantity(fx.repr_measure)
    _check_repr_measure(usage.Quantity(), 10.0)


def test_StepTransientReplacements_ParallelOffset_WorksWithBothTypes(fx):
    offset = StepRepr_ParallelOffset()
    offset.Init(fx.name, fx.description, fx.product_definition_shape, StepData_LTrue, fx.measure)
    _check_measure(offset.Offset(), 5.0)
    offset.SetOffset(fx.repr_measure)
    _check_repr_measure(offset.Offset(), 10.0)


def test_StepTransientReplacements_QuantifiedAssemblyComponentUsage_WorksWithBothTypes(fx):
    usage = StepRepr_QuantifiedAssemblyComponentUsage()
    usage.Init(
        fx.name,
        fx.name,
        True,
        fx.description,
        fx.product_definition,
        fx.product_definition,
        True,
        fx.name,
        fx.measure,
    )
    _check_measure(usage.Quantity(), 5.0)
    usage.SetQuantity(fx.repr_measure)
    _check_repr_measure(usage.Quantity(), 10.0)


def test_StepTransientReplacements_MeasureQualification_WorksWithBothTypes(fx):
    q = StepShape_MeasureQualification()
    q.Init(fx.name, fx.description, fx.measure, fx.qualifiers)
    _check_measure(q.QualifiedMeasure(), 5.0)
    q.SetQualifiedMeasure(fx.repr_measure)
    _check_repr_measure(q.QualifiedMeasure(), 10.0)


def test_StepTransientReplacements_GetMeasureWithUnit_ExtractsCorrectly(fx):
    def get_measure_with_unit(measure):
        if measure is None:
            return None
        result = None
        if measure.IsKind(MWU()):
            result = measure
        elif measure.IsKind(RIMWU()):
            result = measure.GetMeasureWithUnit()
        return result

    assert get_measure_with_unit(None) is None

    extracted = get_measure_with_unit(fx.measure)
    assert extracted is not None
    assert abs(extracted.ValueComponent() - 5.0) <= 1e-7

    extracted = get_measure_with_unit(fx.repr_measure)
    assert extracted is not None
    assert abs(extracted.ValueComponent() - 10.0) <= 1e-7

    assert get_measure_with_unit(fx.name) is None
