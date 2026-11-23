# Translated from OCCT src/DataExchange/TKXCAF/GTests/XCAFDoc_Datum_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.TDocStd import TDocStd_Document
from nanocct.XCAFDoc import XCAFDoc_Datum, XCAFDoc_DocumentTool


def _eq(value):
    # EXPECT_DOUBLE_EQ: equal within a few ULP
    return pytest.approx(value, rel=1e-15, abs=1e-300)


def test_XCAFDoc_DatumTest_PointRoundTripUsesIndependentArray():
    doc = TDocStd_Document("BinXCAF")
    tool = XCAFDoc_DocumentTool.DimTolTool_s(doc.Main())
    for case in (0, 1, 2):
        has_plane, has_point = case != 0, case != 1
        label = tool.AddDatum()
        found, attribute = label.FindAttribute(XCAFDoc_Datum.GetID_s())
        assert found is True, case
        obj = attribute.GetObject()
        if has_plane:
            obj.SetPlane(gp_Ax2(gp_Pnt(6.0, 6.0, 6.0), gp_Dir(0.0, 0.0, 1.0)))
        if has_point:
            obj.SetPoint(gp_Pnt(7.0, 8.0, 9.0))
        attribute.SetObject(obj)
        result = attribute.GetObject()
        assert result is not None, case
        assert result.HasPlane() == has_plane, case
        assert result.HasPoint() == has_point, case
        if has_point:
            assert result.GetPoint().X() == _eq(7.0), case
            assert result.GetPoint().Y() == _eq(8.0), case
            assert result.GetPoint().Z() == _eq(9.0), case
