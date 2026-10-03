# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepAdaptor_CompCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.BRepAdaptor import BRepAdaptor_CompCurve
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from nanocct.GC import GC_MakeArcOfCircle
from nanocct.Geom import Geom_Circle, Geom_TrimmedCurve
from nanocct.gp import gp, gp_Ax2, gp_Circ, gp_Dir, gp_Pnt, gp_Vec
from nanocct.TopAbs import TopAbs_REVERSED, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Edge


def test_BRepAdaptor_CompCurve_Test_OCC5696_EdgeMethod():
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(2, 0, 0)).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    curve = BRepAdaptor_CompCurve(wire)
    par = (curve.FirstParameter() + curve.LastParameter()) / 2.0
    found = TopoDS_Edge()
    par_edge = curve.Edge(par, found)
    assert not found.IsNull()
    assert 0.0 <= par_edge <= 2.0
    assert abs(1.0 - par_edge) <= 0.01


def test_BRepAdaptor_CompCurve_Test_OCC29430_ArcBoundaryPoints():
    r45, r225 = math.pi / 4.0, 3.0 * math.pi / 4.0
    arc = GC_MakeArcOfCircle(
        gp_Circ(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.X)), 1.0), r45, r225, True
    )
    edge = BRepBuilderAPI_MakeEdge(arc.Value()).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    curve = BRepAdaptor_CompCurve(wire)
    start = curve.Value(curve.FirstParameter())
    end = curve.Value(curve.LastParameter())
    verts = [BRep_Tool.Pnt_s(TopoDS.Vertex(v)) for v in TopExp_Explorer(wire, TopAbs_VERTEX)]
    assert len(verts) >= 1
    assert any(start.Distance(v) < 1.0e-7 for v in verts)
    assert any(end.Distance(v) < 1.0e-7 for v in verts)
    assert start.Distance(end) > 1.0e-7


def test_BRepAdaptor_CompCurve_Test_OCC30869_ReversedEdgeBoundaryPoints():
    ax2 = gp_Ax2(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(0.0, -1.0, 0.0), gp_Dir(0.0, 0.0, -1.0))
    circle = Geom_Circle(ax2, 1.0)
    t1 = math.pi / 2.0
    t2 = 3.0 * math.pi / 2.0
    trimmed = Geom_TrimmedCurve(circle, t1, t2)
    edge = BRepBuilderAPI_MakeEdge(trimmed).Edge()
    edge.Orientation(TopAbs_REVERSED)
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    bacc = BRepAdaptor_CompCurve(wire)
    pf, pl = gp_Pnt(), gp_Pnt()
    vf, vl = gp_Vec(), gp_Vec()
    bacc.D1(bacc.FirstParameter(), pf, vf)
    bacc.D1(bacc.LastParameter(), pl, vl)
    if vf.SquareMagnitude() > gp.Resolution_s():
        vf.Normalize()
    if vl.SquareMagnitude() > gp.Resolution_s():
        vl.Normalize()

    ref = Geom_Circle(gp_Ax2(gp_Pnt(1.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0), gp_Dir(0.0, 0.0, -1.0)), 1.0)
    rp1, rp2 = gp_Pnt(), gp_Pnt()
    rv1, rv2 = gp_Vec(), gp_Vec()
    ref.D1(t1, rp1, rv1)
    ref.D1(t2, rp2, rv2)
    if rv1.SquareMagnitude() > gp.Resolution_s():
        rv1.Normalize()
    if rv2.SquareMagnitude() > gp.Resolution_s():
        rv2.Normalize()

    tol = 1.0e-7
    for a, b in ((pf, rp1), (vf, rv1), (pl, rp2), (vl, rv2)):
        assert abs(a.X() - b.X()) <= tol
        assert abs(a.Y() - b.Y()) <= tol
        assert abs(a.Z() - b.Z()) <= tol
