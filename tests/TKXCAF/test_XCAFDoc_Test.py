# Translated from OCCT src/DataExchange/TKXCAF/GTests/XCAFDoc_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Standard import Standard_GUID
from nanocct.TDataStd import TDataStd_Name
from nanocct.TDocStd import TDocStd_Application
from nanocct.XCAFDoc import XCAFDoc, XCAFDoc_DocumentTool, XCAFDoc_ShapeTool

NULL_GUID = "00000000-0000-0000-0000-000000000000"


def test_XCAFDoc_Test_OCC738_ShapeRefGUID():
    guid = XCAFDoc.ShapeRefGUID_s()
    assert guid != Standard_GUID(NULL_GUID)
    assert not (guid == Standard_GUID(NULL_GUID))


def test_XCAFDoc_Test_OCC738_AssemblyGUID():
    guid = XCAFDoc.AssemblyGUID_s()
    assert guid != Standard_GUID(NULL_GUID)
    assert not (guid == Standard_GUID(NULL_GUID))


@pytest.fixture
def auto_naming_guard():
    saved = XCAFDoc_ShapeTool.AutoNaming_s()
    yield
    XCAFDoc_ShapeTool.SetAutoNaming_s(saved)


def test_XCAFDoc_Test_OCC23595_AutoNaming(auto_naming_guard):
    app = TDocStd_Application()
    doc = app.NewDocument("XmlXCAF")
    assert doc is not None

    sh_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    assert XCAFDoc_ShapeTool.AutoNaming_s() is True

    XCAFDoc_ShapeTool.SetAutoNaming_s(True)
    label1 = sh_tool.AddShape(BRepPrimAPI_MakeBox(100.0, 200.0, 300.0).Shape())
    found, _attr = label1.FindAttribute(TDataStd_Name.GetID_s())
    assert found is True

    XCAFDoc_ShapeTool.SetAutoNaming_s(False)
    label2 = sh_tool.AddShape(BRepPrimAPI_MakeBox(300.0, 200.0, 100.0).Shape())
    found, _attr = label2.FindAttribute(TDataStd_Name.GetID_s())
    assert found is False
