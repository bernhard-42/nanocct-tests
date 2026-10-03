# Translated from OCCT src/DataExchange/TKDEVRML/GTests/DEVRML_Provider_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# The OCCT tests pass std::ostringstream/std::istringstream through DE_Provider::WriteStreamNode /
# ReadStreamNode. Those nodes are not constructible from Python (only their copy constructor is bound),
# so the "stream" round trips below go through files in tmp_path instead, using the file-path
# overloads of the same Read/Write methods. Empty stream lists are constructible and used as in C++.
import pytest

from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from nanocct.DE import DE_Provider, DE_Wrapper
from nanocct.DEVRML import DEVRML_ConfigurationNode, DEVRML_Provider
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_List, NCollection_Sequence
from nanocct.Poly import Poly_Triangle, Poly_Triangulation
from nanocct.TDF import TDF_Label
from nanocct.TDocStd import TDocStd_Application
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape
from nanocct.XCAFDoc import XCAFDoc_DocumentTool

SHADED = DEVRML_ConfigurationNode.WriteMode_RepresentationType_Shaded
WIREFRAME = DEVRML_ConfigurationNode.WriteMode_RepresentationType_Wireframe
BOTH = DEVRML_ConfigurationNode.WriteMode_RepresentationType_Both


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def _create_triangulated_face():
    nodes = NCollection_Array1[gp_Pnt](1, 4)
    nodes.SetValue(1, gp_Pnt(0.0, 0.0, 0.0))
    nodes.SetValue(2, gp_Pnt(10.0, 0.0, 0.0))
    nodes.SetValue(3, gp_Pnt(10.0, 10.0, 0.0))
    nodes.SetValue(4, gp_Pnt(0.0, 10.0, 0.0))
    tris = NCollection_Array1[Poly_Triangle](1, 2)
    tris.SetValue(1, Poly_Triangle(1, 2, 3))
    tris.SetValue(2, Poly_Triangle(1, 3, 4))
    triangulation = Poly_Triangulation(nodes, tris)
    plane = gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    maker = BRepBuilderAPI_MakeFace(plane, 0.0, 10.0, 0.0, 10.0)
    if not maker.IsDone():
        return TopoDS_Shape()
    face = maker.Face()
    BRep_Builder().UpdateFace(face, triangulation)
    return face


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
    f.provider = DEVRML_Provider(DEVRML_ConfigurationNode())
    f.box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()
    f.sphere = BRepPrimAPI_MakeSphere(5.0).Shape()
    f.face = _create_triangulated_face()
    f.doc = _new_doc()
    return f


def test_DEVRML_ProviderTest_BasicProperties(fx):
    assert fx.provider.GetFormat().ToCString() == "VRML"
    assert fx.provider.GetVendor().ToCString() == "OCC"
    assert fx.provider.GetNode() is not None


def test_DEVRML_ProviderTest_StreamShapeWriteReadWireframe(fx, tmp_path):
    node = fx.provider.GetNode()
    assert isinstance(node, DEVRML_ConfigurationNode)
    node.InternalParameters.WriteRepresentationType = WIREFRAME

    path = tmp_path / "wireframe.vrml"
    assert fx.provider.Write(str(path), fx.box) is True
    content = path.read_bytes()
    assert len(content) > 0
    assert b"#VRML" in content
    # Read-back left out: unlike the stream overload (VrmlAPI_Writer on the shape), the file-path
    # overload wraps the shape in an XCAF document and writes it with the document writer, which
    # emits no geometry for an unmeshed box ("no geometry was extracted" on reading).


def test_DEVRML_ProviderTest_StreamShapeWriteReadShaded(fx, tmp_path):
    fx.provider.GetNode().InternalParameters.WriteRepresentationType = SHADED

    path = tmp_path / "shaded.vrml"
    assert fx.provider.Write(str(path), fx.face) is True
    content = path.read_bytes()
    assert len(content) > 0
    assert b"#VRML" in content

    read_shape = TopoDS_Shape()
    assert fx.provider.Read(str(path), read_shape) is True
    assert not read_shape.IsNull()
    assert _count(read_shape, TopAbs_FACE) > 0


def test_DEVRML_ProviderTest_StreamDocumentWriteRead(fx, tmp_path):
    fx.provider.GetNode().InternalParameters.WriteRepresentationType = SHADED
    label = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main()).AddShape(fx.face)
    assert not label.IsNull()

    path = tmp_path / "document.vrml"
    assert fx.provider.Write(str(path), fx.doc) is True
    content = path.read_bytes()
    assert len(content) > 0
    assert b"#VRML" in content

    new_doc = _new_doc()
    assert fx.provider.Read(str(path), new_doc) is True
    assert len(_labels(new_doc)) > 0


def test_DEVRML_ProviderTest_StreamDocumentMultipleShapes(fx, tmp_path):
    fx.provider.GetNode().InternalParameters.WriteRepresentationType = SHADED
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main())
    assert not shape_tool.AddShape(fx.face).IsNull()
    assert not shape_tool.AddShape(fx.sphere).IsNull()

    path = tmp_path / "multi_shapes.vrml"
    assert fx.provider.Write(str(path), fx.doc) is True
    content = path.read_bytes()
    assert len(content) > 0
    assert b"#VRML" in content

    new_doc = _new_doc()
    assert fx.provider.Read(str(path), new_doc) is True
    assert len(_labels(new_doc)) > 0


def test_DEVRML_ProviderTest_DE_WrapperIntegration(fx, tmp_path):
    wrapper = DE_Wrapper()
    node = DEVRML_ConfigurationNode()
    node.InternalParameters.WriteRepresentationType = SHADED
    assert wrapper.Bind(node) is True

    path = tmp_path / "test.vrml"
    assert wrapper.Write(str(path), fx.face) is True
    content = path.read_bytes()
    assert len(content) > 0
    assert b"#VRML" in content

    read_shape = TopoDS_Shape()
    wrapper_result = wrapper.Read(str(path), read_shape)

    direct_shape = TopoDS_Shape()
    direct_result = DEVRML_Provider(node).Read(str(path), direct_shape)

    assert wrapper_result == direct_result
    assert read_shape.IsNull() == direct_shape.IsNull()
    if direct_result and not direct_shape.IsNull():
        assert _count(direct_shape, TopAbs_FACE) > 0
    elif wrapper_result and not read_shape.IsNull():
        assert _count(read_shape, TopAbs_FACE) > 0


def test_DEVRML_ProviderTest_DE_WrapperDocumentOperations(fx, tmp_path):
    wrapper = DE_Wrapper()
    node = DEVRML_ConfigurationNode()
    node.InternalParameters.WriteRepresentationType = SHADED
    assert wrapper.Bind(node) is True

    label = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main()).AddShape(fx.face)
    assert not label.IsNull()

    path = tmp_path / "doc.vrml"
    assert wrapper.Write(str(path), fx.doc) is True
    content = path.read_bytes()
    assert len(content) > 0
    assert b"#VRML" in content

    new_doc = _new_doc()
    if wrapper.Read(str(path), new_doc):
        assert len(_labels(new_doc)) > 0
    else:
        test_doc = _new_doc()
        if DEVRML_Provider(node).Read(str(path), test_doc):
            assert len(_labels(test_doc)) > 0


def test_DEVRML_ProviderTest_ErrorHandling(fx, tmp_path):
    empty_write = NCollection_List[DE_Provider.WriteStreamNode]()
    assert fx.provider.Write(empty_write, fx.box) is False

    empty_read = NCollection_List[DE_Provider.ReadStreamNode]()
    assert fx.provider.Read(empty_read, TopoDS_Shape()) is False

    # Null-shape write left out: the file-path overload puts the shape in an XCAF document, and
    # XCAFDoc_ShapeTool::AddShape(null shape) segfaults (null TShape->ShapeType(), in C++ as well).

    invalid = tmp_path / "invalid.vrml"
    invalid.write_text("This is not valid VRML content")
    assert fx.provider.Read(str(invalid), TopoDS_Shape()) is False

    assert fx.provider.Write(str(tmp_path / "null_doc.vrml"), None) is False
    assert fx.provider.Read(empty_read, None) is False


def test_DEVRML_ProviderTest_ConfigurationModes(fx):
    node = fx.provider.GetNode()
    assert isinstance(node, DEVRML_ConfigurationNode)

    node.InternalParameters.WriteRepresentationType = WIREFRAME
    assert node.InternalParameters.WriteRepresentationType == WIREFRAME
    node.InternalParameters.WriteRepresentationType = SHADED
    assert node.InternalParameters.WriteRepresentationType == SHADED
    node.InternalParameters.WriteRepresentationType = BOTH
    assert node.InternalParameters.WriteRepresentationType == BOTH

    v1 = DEVRML_ConfigurationNode.WriteMode_WriterVersion_1
    v2 = DEVRML_ConfigurationNode.WriteMode_WriterVersion_2
    node.InternalParameters.WriterVersion = v1
    assert node.InternalParameters.WriterVersion == v1
    node.InternalParameters.WriterVersion = v2
    assert node.InternalParameters.WriterVersion == v2

    assert fx.provider.GetFormat().ToCString() == "VRML"
    assert fx.provider.GetVendor().ToCString() == "OCC"
