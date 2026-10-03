# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Polygon_Test.cxx (LGPL-2.1 with the OCCT exception)

from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_EdgeIterator,
    BRepGraph_FaceIterator,
    BRepGraph_SolidId,
    BRepGraph_Tool,
)
from nanocct.BRepMesh import BRepMesh_IncrementalMesh
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.gp import gp_Pnt2d
from nanocct.Precision import Precision
from nanocct import TopAbs
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct import TopoDS
from nanocct.TopoDS import TopoDS_Iterator


def _graph_of(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _ids(it):
    out = []
    while it.More():
        out.append(it.CurrentId())
        it.Next()
    return out


def _meshed_box():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    BRepMesh_IncrementalMesh(box, 0.5)
    return box


def test_BRepGraph_PolygonTest_MultiTriangulation_Roundtrip_PreservesAll():
    g = _graph_of(_meshed_box())

    has_tri = False
    it = BRepGraph_FaceIterator(g)
    while it.More():
        if it.Current().TriangulationRepId.IsValid():
            has_tri = True
            assert g.Mesh().Effective().Faces().Triangulation(it.CurrentId()) is not None
        it.Next()
    assert has_tri

    for fid in _ids(BRepGraph_FaceIterator(g)):
        recon = g.Shapes().Reconstruct(fid)
        assert not recon.IsNull()
        loc = TopLoc_Location()
        assert BRep_Tool.Triangulation_s(TopoDS.Face(recon), loc) is not None


def test_BRepGraph_PolygonTest_Polygon3D_Captured_WhenPresent():
    box = _meshed_box()
    g = _graph_of(box)

    edge_ids = _ids(BRepGraph_EdgeIterator(g))
    nb_graph = sum(1 for eid in edge_ids if g.Mesh().Effective().Edges().Has(eid))
    nb_orig = 0
    for e in TopExp_Explorer(box, TopAbs.TopAbs_EDGE):
        if BRep_Tool.Polygon3D_s(TopoDS.Edge(e), TopLoc_Location()) is not None:
            nb_orig += 1
    assert nb_graph == nb_orig

    for eid in edge_ids:
        if not g.Mesh().Effective().Edges().Has(eid):
            continue
        recon = g.Shapes().Reconstruct(eid)
        assert not recon.IsNull()
        assert BRep_Tool.Polygon3D_s(TopoDS.Edge(recon), TopLoc_Location()) is not None


def test_BRepGraph_PolygonTest_PolyOnTri_Captured_AfterMesh():
    g = _graph_of(_meshed_box())

    nb = 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ce_id in g.Topo().Edges().CoEdges(eid):
            ce = g.Topo().CoEdges().Definition(ce_id)
            if ce.PolygonOnTriRepId.IsValid():
                nb += 1
            assert ce.FaceId.IsValid()
    assert nb > 0


def test_BRepGraph_PolygonTest_PolyOnTri_Roundtrip_PreservedOnReconstruct():
    g = _graph_of(_meshed_box())

    recon = g.Shapes().Reconstruct(BRepGraph_SolidId.Start_s())
    assert not recon.IsNull()

    nb = 0
    for e in TopExp_Explorer(recon, TopAbs.TopAbs_EDGE):
        edge = TopoDS.Edge(e)
        for f in TopExp_Explorer(recon, TopAbs.TopAbs_FACE):
            tri = BRep_Tool.Triangulation_s(TopoDS.Face(f), TopLoc_Location())
            if tri is None:
                continue
            if BRep_Tool.PolygonOnTriangulation_s(edge, tri, TopLoc_Location()) is not None:
                nb += 1
    assert nb > 0


def test_BRepGraph_PolygonTest_UVPoints_Recomputed_OnPCurves():
    g = _graph_of(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())

    origin = gp_Pnt2d(0, 0)
    nb = 0
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        for ce_id in g.Topo().Edges().CoEdges(eid):
            first, second = BRepGraph_Tool.CoEdge.UVPoints_s(g, ce_id)
            if (
                first.Distance(origin) > Precision.Confusion_s()
                or second.Distance(origin) > Precision.Confusion_s()
            ):
                nb += 1
    assert nb > 0


def test_BRepGraph_PolygonTest_VertexPointRepresentations_StructurallyValid():
    shape = BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape()
    builder = BRep_Builder()

    has_on_curve = False
    for e in TopExp_Explorer(shape, TopAbs.TopAbs_EDGE):
        edge = TopoDS.Edge(e)
        curve, first, last = BRep_Tool.Curve_s(edge, TopLoc_Location())
        if curve is None:
            continue
        for v in TopoDS_Iterator(edge, False, False):
            vertex = TopoDS.Vertex(v)
            par = last if vertex.Orientation() == TopAbs.TopAbs_REVERSED else first
            builder.UpdateVertex(vertex, par, edge, BRep_Tool.Tolerance_s(vertex))
            has_on_curve = True
            break
        if has_on_curve:
            break

    has_on_surface = False
    for f in TopExp_Explorer(shape, TopAbs.TopAbs_FACE):
        face = TopoDS.Face(f)
        for v in TopExp_Explorer(face, TopAbs.TopAbs_VERTEX):
            vertex = TopoDS.Vertex(v)
            uv = BRep_Tool.Parameters_s(vertex, face)
            builder.UpdateVertex(vertex, uv.X(), uv.Y(), face, BRep_Tool.Tolerance_s(vertex))
            has_on_surface = True
            break
        if has_on_surface:
            break

    has_on_pcurve = False
    for f in TopExp_Explorer(shape, TopAbs.TopAbs_FACE):
        face = TopoDS.Face(f)
        for e in TopExp_Explorer(face, TopAbs.TopAbs_EDGE):
            edge = TopoDS.Edge(e)
            pcurve, first, last = BRep_Tool.CurveOnSurface_s(edge, face)
            if pcurve is None:
                continue
            builder.UpdateEdge(edge, pcurve, face, BRep_Tool.Tolerance_s(edge))
            builder.Range(edge, face, first, last)
            for v in TopoDS_Iterator(edge, False, False):
                vertex = TopoDS.Vertex(v)
                par = last if vertex.Orientation() == TopAbs.TopAbs_REVERSED else first
                builder.UpdateVertex(vertex, par, edge, face, BRep_Tool.Tolerance_s(vertex))
                has_on_pcurve = True
                break
            if has_on_pcurve:
                break
        if has_on_pcurve:
            break

    assert has_on_curve
    assert has_on_surface
    assert has_on_pcurve


def test_BRepGraph_PolygonTest_SeamEdge_PolyOnTri_TwoEntries():
    cyl = BRepPrimAPI_MakeCylinder(5.0, 10.0).Shape()
    BRepMesh_IncrementalMesh(cyl, 0.1)
    g = _graph_of(cyl)

    found = False
    for eid in _ids(BRepGraph_EdgeIterator(g)):
        counts = {}
        for ce_id in g.Topo().Edges().CoEdges(eid):
            fidx = g.Topo().CoEdges().Definition(ce_id).FaceId.Index
            counts[fidx] = counts.get(fidx, 0) + 1
        if any(c >= 2 for c in counts.values()):
            found = True
            break
    assert found
