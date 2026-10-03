# Translated from OCCT src/DataExchange/TKDESTL/GTests/DESTL_Provider_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# The OCCT tests pass std::ostringstream/std::istringstream through DE_Provider::WriteStreamNode /
# ReadStreamNode. Those nodes are not constructible from Python (only their copy constructor is bound),
# so the "stream" round trips below go through files in tmp_path instead, using the file-path
# overloads of the same Read/Write methods. Empty stream lists are constructible and used as in C++.
import pytest

from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from nanocct.DE import DE_Provider, DE_Wrapper
from nanocct.DESTL import DESTL_ConfigurationNode, DESTL_Provider
from nanocct.gp import gp_Dir, gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_Array1, NCollection_List, NCollection_Sequence
from nanocct.Poly import Poly_Triangle, Poly_Triangulation
from nanocct.TDF import TDF_Label
from nanocct.TDocStd import TDocStd_Application
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape
from nanocct.XCAFDoc import XCAFDoc_DocumentTool


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def _triangulated_face(points, triangles, umax, vmax):
    nodes = NCollection_Array1[gp_Pnt](1, len(points))
    for i, p in enumerate(points, start=1):
        nodes.SetValue(i, gp_Pnt(*p))
    tris = NCollection_Array1[Poly_Triangle](1, len(triangles))
    for i, t in enumerate(triangles, start=1):
        tris.SetValue(i, Poly_Triangle(*t))
    triangulation = Poly_Triangulation(nodes, tris)
    plane = gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    maker = BRepBuilderAPI_MakeFace(plane, 0.0, umax, 0.0, vmax)
    if not maker.IsDone():
        return TopoDS_Shape()
    face = maker.Face()
    BRep_Builder().UpdateFace(face, triangulation)
    return face


def _create_triangulated_face():
    return _triangulated_face(
        [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)],
        [(1, 2, 3), (1, 3, 4)],
        10.0,
        10.0,
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
    f.provider = DESTL_Provider(DESTL_ConfigurationNode())
    f.face = _create_triangulated_face()
    f.doc = _new_doc()
    return f


def test_DESTL_ProviderTest_BasicProperties(fx):
    assert fx.provider.GetFormat().ToCString() == "STL"
    assert fx.provider.GetVendor().ToCString() == "OCC"
    assert fx.provider.GetNode() is not None


def test_DESTL_ProviderTest_StreamShapeWriteRead(fx, tmp_path):
    path = str(tmp_path / "test.stl")
    assert fx.provider.Write(path, fx.face) is True
    content = (tmp_path / "test.stl").read_bytes()
    assert len(content) > 0
    assert b"solid" in content or b"facet" in content

    read_shape = TopoDS_Shape()
    assert fx.provider.Read(path, read_shape) is True
    assert not read_shape.IsNull()
    assert _count(read_shape, TopAbs_FACE) > 0


def test_DESTL_ProviderTest_StreamDocumentWriteRead(fx, tmp_path):
    label = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main()).AddShape(fx.face)
    assert not label.IsNull()

    path = str(tmp_path / "document.stl")
    assert fx.provider.Write(path, fx.doc) is True
    assert len((tmp_path / "document.stl").read_bytes()) > 0

    new_doc = _new_doc()
    assert fx.provider.Read(path, new_doc) is True
    assert len(_labels(new_doc)) > 0


def test_DESTL_ProviderTest_DE_WrapperIntegration(fx, tmp_path):
    wrapper = DE_Wrapper()
    node = DESTL_ConfigurationNode()
    assert wrapper.Bind(node) is True

    path = str(tmp_path / "test.stl")
    assert wrapper.Write(path, fx.face) is True
    assert len((tmp_path / "test.stl").read_bytes()) > 0

    read_shape = TopoDS_Shape()
    wrapper_result = wrapper.Read(path, read_shape)

    direct_provider = DESTL_Provider(node)
    direct_shape = TopoDS_Shape()
    direct_result = direct_provider.Read(path, direct_shape)

    assert wrapper_result == direct_result
    assert read_shape.IsNull() == direct_shape.IsNull()
    if direct_result and not direct_shape.IsNull():
        assert _count(direct_shape, TopAbs_FACE) > 0


def test_DESTL_ProviderTest_ErrorHandling(fx, tmp_path):
    empty_write = NCollection_List[DE_Provider.WriteStreamNode]()
    assert fx.provider.Write(empty_write, fx.face) is False

    empty_read = NCollection_List[DE_Provider.ReadStreamNode]()
    assert fx.provider.Read(empty_read, TopoDS_Shape()) is False

    # Writing a null shape: result unchecked in OCCT
    null_path = str(tmp_path / "null_test.stl")
    fx.provider.Write(null_path, TopoDS_Shape())

    # OCCT reads invalid content from a stream and fails; the file-path overload (the only one usable
    # here) does not check the triangulation and returns true (DESTL_Provider.cxx), so it is not checked.

    assert fx.provider.Write(null_path, None) is False
    assert fx.provider.Read(empty_read, None) is False


def test_DESTL_ProviderTest_ConfigurationModes(fx):
    node = fx.provider.GetNode()
    assert isinstance(node, DESTL_ConfigurationNode)

    node.InternalParameters.WriteAscii = True
    assert node.InternalParameters.WriteAscii is True
    node.InternalParameters.WriteAscii = False
    assert node.InternalParameters.WriteAscii is False

    node.InternalParameters.ReadMergeAngle = 45.0
    assert node.InternalParameters.ReadMergeAngle == 45.0

    assert fx.provider.GetFormat().ToCString() == "STL"
    assert fx.provider.GetVendor().ToCString() == "OCC"


def test_DESTL_ProviderTest_AsciiVsBinaryModes(fx, tmp_path):
    node = fx.provider.GetNode()

    node.InternalParameters.WriteAscii = True
    assert fx.provider.Write(str(tmp_path / "ascii_test.stl"), fx.face) is True
    ascii_content = (tmp_path / "ascii_test.stl").read_bytes()
    assert len(ascii_content) > 0
    assert b"solid" in ascii_content

    node.InternalParameters.WriteAscii = False
    assert fx.provider.Write(str(tmp_path / "binary_test.stl"), fx.face) is True
    binary_content = (tmp_path / "binary_test.stl").read_bytes()
    assert len(binary_content) > 0

    assert ascii_content != binary_content


def test_DESTL_ProviderTest_MultipleShapesInDocument(fx, tmp_path):
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(fx.doc.Main())
    label1 = shape_tool.AddShape(fx.face)
    label2 = shape_tool.AddShape(fx.face)
    assert not label1.IsNull()
    assert not label2.IsNull()

    path = str(tmp_path / "multi_shapes.stl")
    assert fx.provider.Write(path, fx.doc) is True
    assert len((tmp_path / "multi_shapes.stl").read_bytes()) > 0

    new_doc = _new_doc()
    assert fx.provider.Read(path, new_doc) is True
    assert len(_labels(new_doc)) > 0


def test_DESTL_ProviderTest_TriangulatedFaceHandling(fx, tmp_path):
    path = str(tmp_path / "triangulated_face.stl")
    assert fx.provider.Write(path, fx.face) is True
    content = (tmp_path / "triangulated_face.stl").read_bytes()
    assert len(content) > 100

    read_shape = TopoDS_Shape()
    assert fx.provider.Read(path, read_shape) is True
    assert not read_shape.IsNull()


def test_DESTL_ProviderTest_DE_WrapperFileExtensions(fx, tmp_path):
    wrapper = DE_Wrapper()
    assert wrapper.Bind(DESTL_ConfigurationNode()) is True

    for i, name in enumerate(["test.stl", "test.STL", "mesh.stl"]):
        # separate sub-directories: test.stl and test.STL collide on a case-insensitive file system
        sub = tmp_path / str(i)
        sub.mkdir()
        path = str(sub / name)
        assert wrapper.Write(path, fx.face) is True, name
        assert len((sub / name).read_bytes()) > 0, name

        read_shape = TopoDS_Shape()
        assert wrapper.Read(path, read_shape) is True, name
        assert not read_shape.IsNull(), name


def test_DESTL_ProviderTest_StreamErrorConditions(fx):
    empty_write = NCollection_List[DE_Provider.WriteStreamNode]()
    assert fx.provider.Write(empty_write, fx.face) is False

    empty_read = NCollection_List[DE_Provider.ReadStreamNode]()
    assert fx.provider.Read(empty_read, TopoDS_Shape()) is False

    # OCCT reads invalid content from a stream and fails; the file-path overload (the only one usable
    # here) does not check the triangulation and returns true (DESTL_Provider.cxx), so it is not checked.


def test_DESTL_ProviderTest_ConfigurationParameterValidation(fx):
    node = fx.provider.GetNode()

    node.InternalParameters.ReadMergeAngle = 30.0
    assert node.InternalParameters.ReadMergeAngle == 30.0
    node.InternalParameters.ReadMergeAngle = 0.0
    assert node.InternalParameters.ReadMergeAngle == 0.0
    node.InternalParameters.ReadMergeAngle = 90.0
    assert node.InternalParameters.ReadMergeAngle == 90.0

    node.InternalParameters.ReadBRep = True
    assert node.InternalParameters.ReadBRep is True
    node.InternalParameters.ReadBRep = False
    assert node.InternalParameters.ReadBRep is False


def test_DESTL_ProviderTest_MultipleTriangulatedFaces(fx, tmp_path):
    triangle_face = _triangulated_face(
        [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0), (2.5, 5.0, 0.0)], [(1, 2, 3)], 5.0, 5.0
    )

    p1 = str(tmp_path / "face1.stl")
    assert fx.provider.Write(p1, fx.face) is True
    content1 = (tmp_path / "face1.stl").read_bytes()

    p2 = str(tmp_path / "face2.stl")
    assert fx.provider.Write(p2, triangle_face) is True
    content2 = (tmp_path / "face2.stl").read_bytes()

    assert len(content1) > 0
    assert len(content2) > 0
    assert content1 != content2

    s1 = TopoDS_Shape()
    assert fx.provider.Read(p1, s1) is True
    assert not s1.IsNull()
    s2 = TopoDS_Shape()
    assert fx.provider.Read(p2, s2) is True
    assert not s2.IsNull()
