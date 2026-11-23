# Translated from OCCT src/DataExchange/TKDESTEP/GTests/STEPCAFControl_DimensionUnits_Test.cxx (LGPL-2.1 with the OCCT exception)
import io

import pytest

from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.DESTEP import DESTEP_Parameters
from nanocct.IFSelect import IFSelect_RetDone
from nanocct.NCollection import NCollection_Sequence
from nanocct.StepBasic import (StepBasic_ConversionBasedUnitAndLengthUnit, StepBasic_MeasureWithUnit,
                               StepBasic_SiUnitAndPlaneAngleUnit, StepBasic_sunRadian)
from nanocct.STEPCAFControl import STEPCAFControl_Controller, STEPCAFControl_Reader, STEPCAFControl_Writer
from nanocct.StepRepr import StepRepr_ReprItemAndMeasureWithUnit
from nanocct.StepShape import StepShape_ToleranceValue
from nanocct.TDF import TDF_Label
from nanocct.TDocStd import TDocStd_Document
from nanocct.UnitsMethods import UnitsMethods_LengthUnit_Inch
from nanocct.XCAFDimTolObjects import (XCAFDimTolObjects_DimensionObject, XCAFDimTolObjects_DimensionType_Size_Angular,
                                       XCAFDimTolObjects_DimensionType_Size_CurveLength)
from nanocct.XCAFDoc import XCAFDoc_Dimension, XCAFDoc_DocumentTool


def _document(is_angle, is_range):
    doc = TDocStd_Document("BinXCAF")
    XCAFDoc_DocumentTool.SetLengthUnit_s(doc, 0.01)              # length inputs are in centimetres
    shape = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()).AddShape(BRepPrimAPI_MakeBox(2.54, 1.0, 1.0).Shape())
    tool = XCAFDoc_DocumentTool.DimTolTool_s(doc.Main())
    label = tool.AddDimension()
    tool.SetDimension(shape, label)
    obj = XCAFDimTolObjects_DimensionObject()
    obj.SetType(XCAFDimTolObjects_DimensionType_Size_Angular if is_angle else XCAFDimTolObjects_DimensionType_Size_CurveLength)
    obj.SetValue(45.0 if is_angle else 2.54)
    if is_range:
        obj.SetLowerBound(30.0 if is_angle else 1.27)
        obj.SetUpperBound(60.0 if is_angle else 3.81)
    else:
        obj.SetLowerTolValue(5.0 if is_angle else 0.127)
        obj.SetUpperTolValue(10.0 if is_angle else 0.254)
    XCAFDoc_Dimension.Set_s(label).SetObject(obj)
    return doc


def _transfer(writer, is_angle, is_range):
    params = DESTEP_Parameters()
    params.WriteSchema = DESTEP_Parameters.WriteMode_StepSchema_AP242DIS
    params.WriteUnit = UnitsMethods_LengthUnit_Inch
    return writer.Transfer(_document(is_angle, is_range), params)


def _measures(model):
    found = {}
    for i in range(1, model.NbEntities() + 1):
        entity = model.Entity(i)
        if isinstance(entity, StepRepr_ReprItemAndMeasureWithUnit) and entity.Name() is not None:
            name = entity.Name().String()
            for key in ("nominal value", "lower limit", "upper limit"):
                if name.IsEqual(key):
                    found[key] = entity.GetMeasureWithUnit()
        if isinstance(entity, StepShape_ToleranceValue):
            lower, upper = entity.LowerBound(), entity.UpperBound()
            found["lower tolerance"] = lower if isinstance(lower, StepBasic_MeasureWithUnit) else None
            found["upper tolerance"] = upper if isinstance(upper, StepBasic_MeasureWithUnit) else None
    return found


def _check_measure(measure, is_angle, is_tolerance, expected):
    assert measure is not None
    assert measure.ValueComponent() == pytest.approx(expected, abs=1.0e-12)
    member = measure.ValueComponentMember()
    assert member is not None
    names = {(True, True): "PLANE_ANGLE_MEASURE", (True, False): "POSITIVE_PLANE_ANGLE_MEASURE",
             (False, True): "LENGTH_MEASURE", (False, False): "POSITIVE_LENGTH_MEASURE"}
    assert member.Name() == names[(is_angle, is_tolerance)]
    unit = measure.UnitComponent().NamedUnit()
    if is_angle:
        assert isinstance(unit, StepBasic_SiUnitAndPlaneAngleUnit)
        assert unit.Name() == StepBasic_sunRadian
        assert unit.HasPrefix() is False
    else:
        assert isinstance(unit, StepBasic_ConversionBasedUnitAndLengthUnit)
        assert unit.Name() is not None
        assert unit.Name().ToCString() == "INCH"


def test_STEPCAFControl_DimensionUnitsTest_WritesInchAndRadianLiterals():
    STEPCAFControl_Controller.Init_s()
    for is_angle in (False, True):
        for is_range in (False, True):
            writer = STEPCAFControl_Writer()
            assert _transfer(writer, is_angle, is_range) is True, (is_angle, is_range)
            m = _measures(writer.ChangeWriter().Model())
            _check_measure(m.get("nominal value"), is_angle, False, 0.7853981633974483 if is_angle else 1.0)
            if is_range:
                _check_measure(m.get("lower limit"), is_angle, False, 0.5235987755982988 if is_angle else 0.5)
                _check_measure(m.get("upper limit"), is_angle, False, 1.0471975511965976 if is_angle else 1.5)
            else:
                _check_measure(m.get("lower tolerance"), is_angle, True, -0.0872664625997165 if is_angle else -0.05)
                _check_measure(m.get("upper tolerance"), is_angle, True, 0.174532925199433 if is_angle else 0.1)


def test_STEPCAFControl_DimensionUnitsTest_ReadsLiteralGenericRadianTolerance():
    STEPCAFControl_Controller.Init_s()
    writer = STEPCAFControl_Writer()
    assert _transfer(writer, True, False) is True
    m = _measures(writer.ChangeWriter().Model())
    for key in ("nominal value", "lower tolerance", "upper tolerance"):
        assert m.get(key) is not None, key
    # Author the radian values independently of the writer's scaling.
    m["nominal value"].ValueComponentMember().SetReal(0.7853981633974483)
    m["lower tolerance"].ValueComponentMember().SetName("PLANE_ANGLE_MEASURE")
    m["lower tolerance"].ValueComponentMember().SetReal(-0.0872664625997165)
    m["upper tolerance"].ValueComponentMember().SetName("PLANE_ANGLE_MEASURE")
    m["upper tolerance"].ValueComponentMember().SetReal(0.174532925199433)
    status, text = writer.WriteStream()
    assert status == IFSelect_RetDone
    reader = STEPCAFControl_Reader()
    assert reader.ReadStream("angular-dimension.stp", io.StringIO(text)) == IFSelect_RetDone
    result = TDocStd_Document("BinXCAF")
    assert reader.Transfer(result) is True
    labels = NCollection_Sequence[TDF_Label]()
    XCAFDoc_DocumentTool.DimTolTool_s(result.Main()).GetDimensionLabels(labels)
    assert labels.Length() == 1
    found, attribute = labels.First().FindAttribute(XCAFDoc_Dimension.GetID_s())
    assert found is True
    obj = attribute.GetObject()
    assert obj is not None
    assert obj.IsDimWithPlusMinusTolerance() is True
    assert obj.GetValue() == pytest.approx(45.0, abs=1.0e-10)
    assert obj.GetLowerTolValue() == pytest.approx(5.0, abs=1.0e-10)
    assert obj.GetUpperTolValue() == pytest.approx(10.0, abs=1.0e-10)
