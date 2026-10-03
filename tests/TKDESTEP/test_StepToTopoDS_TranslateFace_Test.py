# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepToTopoDS_TranslateFace_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.gp import gp_XYZ
from nanocct.NCollection import NCollection_DataMap, NCollection_HArray1, NCollection_HArray2
from nanocct.Standard import Standard_Transient
from nanocct.StepData import StepData_Factors
from nanocct.StepShape import StepShape_TopologicalRepresentationItem
from nanocct.StepToTopoDS import StepToTopoDS_NMTool, StepToTopoDS_Tool, StepToTopoDS_TranslateFace
from nanocct.StepVisual import (
    StepVisual_ComplexTriangulatedFace,
    StepVisual_CoordinatesList,
    StepVisual_FaceOrSurface,
    StepVisual_TriangulatedFace,
    StepVisual_TriangulatedSurfaceSet,
)
from nanocct.TCollection import TCollection_HAsciiString
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Shape
from nanocct.Transfer import Transfer_TransientProcess


def _coords(points):
    arr = NCollection_HArray1[gp_XYZ](1, len(points))
    for i, p in enumerate(points, start=1):
        arr.SetValue(i, gp_XYZ(*p))
    c = StepVisual_CoordinatesList()
    c.Init(TCollection_HAsciiString("coords"), arr)
    return c


def _triangles(tris):
    arr = NCollection_HArray2[int](1, len(tris), 1, 3)
    for i, t in enumerate(tris, start=1):
        for j in range(3):
            arr.SetValue(i, j + 1, t[j])
    return arr


def _normals(norms):
    arr = NCollection_HArray2[float](1, len(norms), 1, 3)
    for i, n in enumerate(norms, start=1):
        for j in range(3):
            arr.SetValue(i, j + 1, n[j])
    return arr


def _int_array(values):
    arr = NCollection_HArray1[int](1, len(values))
    for i, v in enumerate(values, start=1):
        arr.SetValue(i, v)
    return arr


def _transient_array(item):
    arr = NCollection_HArray1[Standard_Transient](1, 1)
    arr.SetValue(1, item)
    return arr


def _mesh(translator):
    assert translator.IsDone()
    face = TopoDS.Face(translator.Value())
    return BRep_Tool.Triangulation_s(face, TopLoc_Location())


@pytest.fixture
def tools():
    tp = Transfer_TransientProcess()
    shape_map = NCollection_DataMap[StepShape_TopologicalRepresentationItem, TopoDS_Shape]()
    tool = StepToTopoDS_Tool()
    tool.Init(shape_map, tp)
    nm_tool = StepToTopoDS_NMTool()
    nm_tool.SetActive(False)
    # keep tp and shape_map alive with the tools
    return tool, nm_tool, tp, shape_map


def _triangulated_face(points, pnmax, tris, normals=None, pnindex=None):
    tf = StepVisual_TriangulatedFace()
    tf.Init(
        TCollection_HAsciiString("face"),
        _coords(points),
        pnmax,
        normals,
        False,
        StepVisual_FaceOrSurface(),
        pnindex,
        _triangles(tris),
    )
    return tf


def _surface_set(points, pnmax, tris, pnindex=None):
    tss = StepVisual_TriangulatedSurfaceSet()
    tss.Init(TCollection_HAsciiString("surfset"), _coords(points), pnmax, None, pnindex, _triangles(tris))
    return tss


def _complex_face(points, pnmax, strips=None, fans=None):
    ctf = StepVisual_ComplexTriangulatedFace()
    ctf.Init(
        TCollection_HAsciiString("complex_face"),
        _coords(points),
        pnmax,
        None,
        False,
        StepVisual_FaceOrSurface(),
        None,
        strips,
        fans,
    )
    return ctf


def test_StepToTopoDS_TranslateFaceTest_TriangulatedFace_DirectNodes(tools):
    tool, nm_tool = tools[0], tools[1]
    tf = _triangulated_face(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)], 4, [(1, 2, 3), (1, 3, 4)]
    )
    translator = StepToTopoDS_TranslateFace(tf, tool, nm_tool, False, False)
    mesh = _mesh(translator)
    assert mesh is not None
    assert mesh.NbNodes() == 4
    assert mesh.NbTriangles() == 2
    assert not mesh.HasNormals()
    assert abs(mesh.Node(1).X() - 0.0) <= 1e-12
    assert abs(mesh.Node(2).X() - 1.0) <= 1e-12
    assert abs(mesh.Node(3).Y() - 1.0) <= 1e-12
    assert mesh.Triangle(1).Get() == (1, 2, 3)


def test_StepToTopoDS_TranslateFaceTest_TriangulatedFace_WithPnindex(tools):
    tool, nm_tool = tools[0], tools[1]
    tf = _triangulated_face(
        [(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0), (0.0, 10.0, 0.0)],
        4,
        [(1, 2, 3)],
        pnindex=_int_array([2, 3, 4]),
    )
    mesh = _mesh(StepToTopoDS_TranslateFace(tf, tool, nm_tool, False, False))
    assert mesh is not None
    assert mesh.NbNodes() == 3
    assert mesh.NbTriangles() == 1
    assert abs(mesh.Node(1).X() - 10.0) <= 1e-12
    assert abs(mesh.Node(1).Y() - 0.0) <= 1e-12
    assert abs(mesh.Node(2).X() - 10.0) <= 1e-12
    assert abs(mesh.Node(2).Y() - 10.0) <= 1e-12
    assert abs(mesh.Node(3).X() - 0.0) <= 1e-12
    assert abs(mesh.Node(3).Y() - 10.0) <= 1e-12


def test_StepToTopoDS_TranslateFaceTest_TriangulatedSurfaceSet_DirectNodes(tools):
    tool, nm_tool = tools[0], tools[1]
    tss = _surface_set([(0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (1.0, 2.0, 0.0)], 3, [(1, 2, 3)])
    mesh = _mesh(StepToTopoDS_TranslateFace(tss, tool, nm_tool))
    assert mesh is not None
    assert mesh.NbNodes() == 3
    assert mesh.NbTriangles() == 1
    assert abs(mesh.Node(1).X() - 0.0) <= 1e-12
    assert abs(mesh.Node(2).X() - 2.0) <= 1e-12
    assert abs(mesh.Node(3).Y() - 2.0) <= 1e-12


def test_StepToTopoDS_TranslateFaceTest_TriangulatedSurfaceSet_WithPnindex(tools):
    tool, nm_tool = tools[0], tools[1]
    tss = _surface_set(
        [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0), (5.0, 5.0, 0.0), (0.0, 5.0, 0.0)],
        4,
        [(1, 2, 3)],
        pnindex=_int_array([1, 3, 4]),
    )
    mesh = _mesh(StepToTopoDS_TranslateFace(tss, tool, nm_tool))
    assert mesh is not None
    assert mesh.NbNodes() == 3
    assert abs(mesh.Node(1).X() - 0.0) <= 1e-12
    assert abs(mesh.Node(2).X() - 5.0) <= 1e-12
    assert abs(mesh.Node(2).Y() - 5.0) <= 1e-12
    assert abs(mesh.Node(3).X() - 0.0) <= 1e-12
    assert abs(mesh.Node(3).Y() - 5.0) <= 1e-12


def test_StepToTopoDS_TranslateFaceTest_TriangulatedFace_WithNormals(tools):
    tool, nm_tool = tools[0], tools[1]
    tf = _triangulated_face(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
        3,
        [(1, 2, 3)],
        normals=_normals([(0.0, 0.0, 1.0)] * 3),
    )
    mesh = _mesh(StepToTopoDS_TranslateFace(tf, tool, nm_tool, False, False))
    assert mesh is not None
    assert mesh.HasNormals()
    assert abs(mesh.Normal(1).Z() - 1.0) <= 1e-12


def test_StepToTopoDS_TranslateFaceTest_TriangulatedFace_SingleNormal(tools):
    tool, nm_tool = tools[0], tools[1]
    tf = _triangulated_face(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
        3,
        [(1, 2, 3)],
        normals=_normals([(0.0, 1.0, 0.0)]),
    )
    mesh = _mesh(StepToTopoDS_TranslateFace(tf, tool, nm_tool, False, False))
    assert mesh is not None
    assert mesh.HasNormals()
    for i in range(1, 4):
        n = mesh.Normal(i)
        assert abs(n.X() - 0.0) <= 1e-12
        assert abs(n.Y() - 1.0) <= 1e-12
        assert abs(n.Z() - 0.0) <= 1e-12


def test_StepToTopoDS_TranslateFaceTest_TriangulatedSurfaceSet_LengthFactor(tools):
    tool, nm_tool = tools[0], tools[1]
    tss = _surface_set([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)], 3, [(1, 2, 3)])
    factors = StepData_Factors()
    factors.InitializeFactors(25.4, 1.0, 1.0)
    mesh = _mesh(StepToTopoDS_TranslateFace(tss, tool, nm_tool, factors))
    assert mesh is not None
    assert abs(mesh.Node(2).X() - 25.4) <= 1e-10
    assert abs(mesh.Node(3).Y() - 25.4) <= 1e-10


def test_StepToTopoDS_TranslateFaceTest_ComplexTriangulatedFace_TriangleStrips(tools):
    tool, nm_tool = tools[0], tools[1]
    strip = _int_array([1, 2, 3, 4])
    ctf = _complex_face(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)], 4, strips=_transient_array(strip)
    )
    mesh = _mesh(StepToTopoDS_TranslateFace(ctf, tool, nm_tool, False, False))
    assert mesh is not None
    assert mesh.NbNodes() == 4
    assert mesh.NbTriangles() == 2


def test_StepToTopoDS_TranslateFaceTest_ComplexTriangulatedFace_TriangleFans(tools):
    tool, nm_tool = tools[0], tools[1]
    fan = _int_array([1, 2, 3, 4, 5])
    ctf = _complex_face(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0)],
        5,
        fans=_transient_array(fan),
    )
    mesh = _mesh(StepToTopoDS_TranslateFace(ctf, tool, nm_tool, False, False))
    assert mesh is not None
    assert mesh.NbNodes() == 5
    assert mesh.NbTriangles() == 3


def test_StepToTopoDS_TranslateFaceTest_NullInput_TessellatedFace(tools):
    tool, nm_tool = tools[0], tools[1]
    translator = StepToTopoDS_TranslateFace()
    translator.Init(theTF=None, theTool=tool, theNMTool=nm_tool, theReadTessellatedWhenNoBRepOnly=False)
    assert not translator.IsDone()


def test_StepToTopoDS_TranslateFaceTest_NullInput_TessellatedSurfaceSet(tools):
    tool, nm_tool = tools[0], tools[1]
    translator = StepToTopoDS_TranslateFace()
    # A positional None picks the first overload, Init(StepShape_FaceSurface, ...), which segfaults on the
    # null handle; the keyword names select the TessellatedSurfaceSet overload, as the C++ static type does.
    translator.Init(theTSS=None, theTool=tool, theNMTool=nm_tool)
    assert not translator.IsDone()


def test_StepToTopoDS_TranslateFaceTest_ComplexTriangulatedFace_DegenerateStrip(tools):
    tool, nm_tool = tools[0], tools[1]
    strip = _int_array([1, 2, 3, 3])
    ctf = _complex_face(
        [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)], 4, strips=_transient_array(strip)
    )
    mesh = _mesh(StepToTopoDS_TranslateFace(ctf, tool, nm_tool, False, False))
    assert mesh is not None
    assert mesh.NbTriangles() == 1
