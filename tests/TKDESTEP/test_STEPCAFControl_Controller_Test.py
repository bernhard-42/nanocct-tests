# Translated from OCCT src/DataExchange/TKDESTEP/GTests/STEPCAFControl_Controller_Test.cxx (LGPL-2.1 with the OCCT exception)
# The four OCC33657 tests (OSD_Parallel threading) are not translated.
import io

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.DESTEP import DESTEP_Parameters
from nanocct.gp import gp_Pnt, gp_Trsf
from nanocct.IFSelect import IFSelect_RetDone
from nanocct.NCollection import NCollection_DataMap, NCollection_Sequence
from nanocct.Precision import Precision
from nanocct.Quantity import Quantity_Color, Quantity_NOC_YELLOW
from nanocct.ShapeAnalysis import ShapeAnalysis_ShapeContents
from nanocct.STEPCAFControl import STEPCAFControl_Controller, STEPCAFControl_Reader, STEPCAFControl_Writer
from nanocct.STEPControl import STEPControl_AsIs, STEPControl_Writer
from nanocct.TCollection import TCollection_AsciiString
from nanocct.TDataStd import TDataStd_Name
from nanocct.TDF import TDF_Label
from nanocct.TDocStd import TDocStd_Document
from nanocct.TopAbs import TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.XCAFDoc import XCAFDoc_ColorGen, XCAFDoc_ColorSurf, XCAFDoc_DocumentTool


def _empty_parameter_map():
    return NCollection_DataMap[TCollection_AsciiString, TCollection_AsciiString]()


def test_STEPCAFControl_ControllerTest_STEPControlWriter_InitializesMissingShapeProcessingParameters():
    box = BRepPrimAPI_MakeBox(1.0, 2.0, 3.0).Shape()
    writer = STEPControl_Writer()
    writer.SetShapeFixParameters(_empty_parameter_map())
    assert writer.GetShapeFixParameters().IsEmpty()
    assert writer.Transfer(box, STEPControl_AsIs) == IFSelect_RetDone
    assert not writer.GetShapeFixParameters().IsEmpty()


def test_STEPCAFControl_ControllerTest_STEPCAFControlWriter_InitializesMissingShapeProcessingParameters():
    box = BRepPrimAPI_MakeBox(1.0, 2.0, 3.0).Shape()
    doc = TDocStd_Document("dummy")
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    shape_tool.SetShape(shape_tool.NewShape(), box)

    writer = STEPCAFControl_Writer()
    writer.SetShapeFixParameters(_empty_parameter_map())
    assert writer.GetShapeFixParameters().IsEmpty()
    assert writer.Transfer(doc) is True
    assert not writer.GetShapeFixParameters().IsEmpty()


def _read_back(content):
    read_doc = TDocStd_Document("dummy")
    reader = STEPCAFControl_Reader()
    reader.SetColorMode(True)
    assert reader.ReadStream("", io.StringIO(content)) == IFSelect_RetDone
    assert reader.Transfer(read_doc) is True
    read_tool = XCAFDoc_DocumentTool.ShapeTool_s(read_doc.Main())
    roots = NCollection_Sequence[TDF_Label]()
    read_tool.GetFreeShapes(roots)
    assert not roots.IsEmpty()
    shape = read_tool.GetShape_s(roots.First())
    assert not shape.IsNull()
    return read_doc, shape


def test_STEPCAFControl_ControllerTest_OCC23951_WriteDocumentWithVisibility():
    STEPCAFControl_Controller.Init_s()
    doc = TDocStd_Document("dummy")
    box = BRepPrimAPI_MakeBox(1, 1, 1).Shape()
    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    lab1 = shape_tool.NewShape()
    shape_tool.SetShape(lab1, box)
    TDataStd_Name.Set_s(lab1, "Box1")
    yellow = Quantity_Color(Quantity_NOC_YELLOW)
    XCAFDoc_DocumentTool.ColorTool_s(doc.Main()).SetColor(lab1, yellow, XCAFDoc_ColorGen)
    XCAFDoc_DocumentTool.ColorTool_s(doc.Main()).SetVisibility(lab1, False)

    writer = STEPCAFControl_Writer()
    assert writer.Transfer(doc) is True
    status, content = writer.WriteStream()
    assert status == IFSelect_RetDone
    assert len(content) > 0
    assert "DRAUGHTING_PRE_DEFINED_COLOUR('yellow')" in content
    assert "INVISIBILITY" in content

    read_doc, result = _read_back(content)

    src = ShapeAnalysis_ShapeContents()
    src.Perform(box)
    res = ShapeAnalysis_ShapeContents()
    res.Perform(result)
    assert res.NbSolids() == src.NbSolids()
    assert res.NbFaces() == src.NbFaces()
    assert res.NbEdges() == src.NbEdges()
    assert res.NbVertices() == src.NbVertices()

    color_tool = XCAFDoc_DocumentTool.ColorTool_s(read_doc.Main())
    read_color = Quantity_Color()
    found = False
    exp = TopExp_Explorer(result, TopAbs_FACE)
    while exp.More():
        if color_tool.GetColor(exp.Current(), XCAFDoc_ColorSurf, read_color) or color_tool.GetColor(
            exp.Current(), XCAFDoc_ColorGen, read_color
        ):
            found = True
            break
        exp.Next()
    if not found:
        found = color_tool.GetColor(result, XCAFDoc_ColorGen, read_color) or color_tool.GetColor(
            result, XCAFDoc_ColorSurf, read_color
        )
    assert found
    assert abs(read_color.Red() - yellow.Red()) <= 0.05
    assert abs(read_color.Green() - yellow.Green()) <= 0.05
    assert abs(read_color.Blue() - yellow.Blue()) <= 0.05


def test_STEPCAFControl_ControllerTest_OCC23950_WriteDocumentWithVertexName():
    STEPCAFControl_Controller.Init_s()
    doc = TDocStd_Document("dummy")
    vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(75, 0, 0)).Shape()
    loc = TopLoc_Location(gp_Trsf())

    shape_tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    lab1 = shape_tool.NewShape()
    shape_tool.SetShape(lab1, vertex)
    TDataStd_Name.Set_s(lab1, "Point1")
    assembly = shape_tool.NewShape()
    TDataStd_Name.Set_s(assembly, "ASSEMBLY")
    component = shape_tool.AddComponent(assembly, lab1, loc)
    shape_tool.UpdateAssemblies()

    yellow = Quantity_Color(Quantity_NOC_YELLOW)
    XCAFDoc_DocumentTool.ColorTool_s(doc.Main()).SetColor(component, yellow, XCAFDoc_ColorGen)
    XCAFDoc_DocumentTool.ColorTool_s(doc.Main()).SetVisibility(component, False)

    params = DESTEP_Parameters()
    params.WriteVertexMode = DESTEP_Parameters.WriteMode_VertexMode_SingleVertex

    writer = STEPCAFControl_Writer()
    assert writer.Transfer(doc, params) is True
    status, content = writer.WriteStream()
    assert status == IFSelect_RetDone
    assert len(content) > 0
    assert "Point1" in content
    assert "DRAUGHTING_PRE_DEFINED_COLOUR('yellow')" in content
    assert "INVISIBILITY" in content

    _read_doc, root = _read_back(content)
    exp = TopExp_Explorer(root, TopAbs_VERTEX)
    assert exp.More()
    pnt = BRep_Tool.Pnt_s(TopoDS.Vertex(exp.Current()))
    tol = Precision.Confusion_s()
    assert abs(pnt.X() - 75.0) <= tol
    assert abs(pnt.Y() - 0.0) <= tol
    assert abs(pnt.Z() - 0.0) <= tol
