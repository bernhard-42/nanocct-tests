# Translated from OCCT src/DataExchange/TKDESTEP/GTests/DESTEP_Provider_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# The OCCT tests pass std::ostringstream/std::istringstream through DE_Provider::WriteStreamNode /
# ReadStreamNode. Those nodes are not constructible from Python (only their copy constructor is bound),
# so the "stream" round trips below go through files in tmp_path instead, using the file-path
# overloads of the same Read/Write methods. Empty stream lists are constructible and used as in C++.
import pytest

from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.DE import DE_Provider, DE_Wrapper
from nanocct.DESTEP import DESTEP_ConfigurationNode, DESTEP_Provider
from nanocct.NCollection import NCollection_List, NCollection_Sequence
from nanocct.TDF import TDF_Label
from nanocct.TDocStd import TDocStd_Application
from nanocct.TopAbs import TopAbs_SOLID
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape
from nanocct.XCAFDoc import XCAFDoc_DocumentTool
from nanocct.XSControl import XSControl_WorkSession


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def _is_valid_step(content):
    return (
        len(content) > 0
        and b"ISO-10303-21;" in content
        and b"HEADER;" in content
        and b"DATA;" in content
        and b"ENDSEC;" in content
    )


def _new_doc():
    return TDocStd_Application().NewDocument("BinXCAF")


def _labels(doc):
    labels = NCollection_Sequence[TDF_Label]()
    XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()).GetShapes(labels)
    return labels


@pytest.fixture
def fx():
    class F:
        pass

    f = F()
    f.provider = DESTEP_Provider(DESTEP_ConfigurationNode())
    f.box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    f.sphere = BRepPrimAPI_MakeSphere(5.0).Shape()
    f.cylinder = BRepPrimAPI_MakeCylinder(3.0, 8.0).Shape()
    f.doc = _new_doc()
    return f


def test_DESTEP_ProviderTest_BasicProperties(fx):
    assert fx.provider.GetFormat().ToCString() == "STEP"
    assert fx.provider.GetVendor().ToCString() == "OCC"
    assert fx.provider.GetNode() is not None


def test_DESTEP_ProviderTest_StreamShapeWriteRead(fx, tmp_path):
    path = tmp_path / "test.step"
    assert fx.provider.Write(str(path), fx.box) is True
    content = path.read_bytes()
    assert _is_valid_step(content)

    read_shape = TopoDS_Shape()
    assert fx.provider.Read(str(path), read_shape) is True
    assert not read_shape.IsNull()
    assert _count(read_shape, TopAbs_SOLID) == _count(fx.box, TopAbs_SOLID)


def test_DESTEP_ProviderTest_StreamDocumentWriteRead(fx, tmp_path):
    label = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main()).AddShape(fx.box)
    assert not label.IsNull()

    path = tmp_path / "document.step"
    assert fx.provider.Write(str(path), fx.doc) is True
    assert _is_valid_step(path.read_bytes())

    new_doc = _new_doc()
    assert fx.provider.Read(str(path), new_doc) is True
    assert len(_labels(new_doc)) > 0


def test_DESTEP_ProviderTest_DE_WrapperIntegration(fx, tmp_path):
    wrapper = DE_Wrapper()
    node = DESTEP_ConfigurationNode()
    assert wrapper.Bind(node) is True

    path = tmp_path / "test.step"
    assert wrapper.Write(str(path), fx.sphere) is True
    assert _is_valid_step(path.read_bytes())

    read_shape = TopoDS_Shape()
    wrapper_result = wrapper.Read(str(path), read_shape)

    direct_shape = TopoDS_Shape()
    direct_result = DESTEP_Provider(node).Read(str(path), direct_shape)

    assert wrapper_result == direct_result
    assert read_shape.IsNull() == direct_shape.IsNull()
    if direct_result and not direct_shape.IsNull():
        assert _count(direct_shape, TopAbs_SOLID) > 0


def test_DESTEP_ProviderTest_MultipleShapesInDocument(fx, tmp_path):
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main())
    assert not shape_tool.AddShape(fx.box).IsNull()
    assert not shape_tool.AddShape(fx.sphere).IsNull()
    assert not shape_tool.AddShape(fx.cylinder).IsNull()

    path = tmp_path / "multi_shapes.step"
    assert fx.provider.Write(str(path), fx.doc) is True
    assert _is_valid_step(path.read_bytes())

    new_doc = _new_doc()
    assert fx.provider.Read(str(path), new_doc) is True
    assert len(_labels(new_doc)) == 3


def test_DESTEP_ProviderTest_DifferentBRepGeometries(fx, tmp_path):
    contents = {}
    for name, shape in (("box", fx.box), ("sphere", fx.sphere), ("cylinder", fx.cylinder)):
        path = tmp_path / f"{name}.step"
        assert fx.provider.Write(str(path), shape) is True
        contents[name] = path.read_bytes()

    for c in contents.values():
        assert _is_valid_step(c)
    assert contents["box"] != contents["sphere"]
    assert contents["box"] != contents["cylinder"]
    assert contents["sphere"] != contents["cylinder"]

    for name in ("box", "sphere"):
        read_shape = TopoDS_Shape()
        assert fx.provider.Read(str(tmp_path / f"{name}.step"), read_shape) is True
        assert not read_shape.IsNull()


def test_DESTEP_ProviderTest_DE_WrapperFileExtensions(fx, tmp_path):
    wrapper = DE_Wrapper()
    assert wrapper.Bind(DESTEP_ConfigurationNode()) is True

    for i, name in enumerate(["test.step", "test.STEP", "test.stp", "test.STP"]):
        # separate sub-directories: the names collide on a case-insensitive file system
        sub = tmp_path / str(i)
        sub.mkdir()
        path = sub / name
        assert wrapper.Write(str(path), fx.box) is True, name
        content = path.read_bytes()
        assert len(content) > 0, name
        assert _is_valid_step(content), name

        read_shape = TopoDS_Shape()
        assert wrapper.Read(str(path), read_shape) is True, name
        assert not read_shape.IsNull(), name


def test_DESTEP_ProviderTest_ErrorHandling(fx, tmp_path):
    empty_write = NCollection_List[DE_Provider.WriteStreamNode]()
    assert fx.provider.Write(empty_write, fx.box) is False

    empty_read = NCollection_List[DE_Provider.ReadStreamNode]()
    assert fx.provider.Read(empty_read, TopoDS_Shape()) is False

    null_path = tmp_path / "null_test.step"
    assert fx.provider.Write(str(null_path), TopoDS_Shape()) is False

    invalid = tmp_path / "invalid.step"
    invalid.write_text("This is not valid STEP content")
    assert fx.provider.Read(str(invalid), TopoDS_Shape()) is False

    assert fx.provider.Write(str(null_path), None) is False
    assert fx.provider.Read(empty_read, None) is False


def test_DESTEP_ProviderTest_ConfigurationModes(fx):
    node = fx.provider.GetNode()
    assert isinstance(node, DESTEP_ConfigurationNode)

    assert fx.provider.GetFormat().ToCString() == "STEP"
    assert fx.provider.GetVendor().ToCString() == "OCC"

    new_provider = DESTEP_Provider(DESTEP_ConfigurationNode())
    assert new_provider.GetFormat().ToCString() == "STEP"
    assert new_provider.GetVendor().ToCString() == "OCC"
    assert new_provider.GetNode() is not None


def test_DESTEP_ProviderTest_WorkSessionIntegration(fx, tmp_path):
    ws = XSControl_WorkSession()

    path = tmp_path / "ws_test.step"
    ok, ws = fx.provider.Write(str(path), fx.box, ws)
    assert ok is True
    assert _is_valid_step(path.read_bytes())

    read_shape = TopoDS_Shape()
    ok, ws = fx.provider.Read(str(path), read_shape, ws)
    assert ok is True
    assert not read_shape.IsNull()


def test_DESTEP_ProviderTest_DocumentWorkSessionIntegration(fx, tmp_path):
    label = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main()).AddShape(fx.sphere)
    assert not label.IsNull()

    ws = XSControl_WorkSession()
    path = tmp_path / "doc_ws_test.step"
    ok, ws = fx.provider.Write(str(path), fx.doc, ws)
    assert ok is True
    assert _is_valid_step(path.read_bytes())

    new_doc = _new_doc()
    ok, ws = fx.provider.Read(str(path), new_doc, ws)
    assert ok is True
    assert len(_labels(new_doc)) > 0
