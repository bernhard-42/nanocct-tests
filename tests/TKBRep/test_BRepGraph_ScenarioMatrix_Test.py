# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_ScenarioMatrix_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CoEdgeId,
    BRepGraph_CompoundId,
    BRepGraph_CompSolidId,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_ProductId,
    BRepGraph_SolidId,
    BRepGraph_Tool,
    BRepGraph_Validate,
    BRepGraph_VertexId,
    BRepGraph_WireId,
)
from nanocct.BRepGraphInc import BRepGraphInc_Populate
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.Geom import Geom_Plane
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp_Dir, gp_Dir2d, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_Array1, NCollection_IndexedMap
from nanocct.Precision import Precision
from nanocct.TopAbs import (
    TopAbs_COMPOUND,
    TopAbs_EDGE,
    TopAbs_FACE,
    TopAbs_FORWARD,
    TopAbs_REVERSED,
    TopAbs_SHELL,
    TopAbs_SOLID,
    TopAbs_VERTEX,
)
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound, TopoDS_CompSolid, TopoDS_Iterator, TopoDS_Shape, TopoDS_Vertex, TopoDS_Wire
from nanocct.TopTools import TopTools_ShapeMapHasher

CONF = Precision.Confusion_s()


# ---------- helpers ----------


def _area(shape):
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


def _count_sub_shapes(shape, kind):
    m = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(shape, kind, m)
    return m.Extent()


def _graph(shape):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _populate(shape):
    g = BRepGraph()
    BRepGraphInc_Populate.Perform_s(g, shape, False)
    assert not g.IsEmpty()
    return g


def _light_valid(g):
    return BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Lightweight_s()).IsValid()


def _solid0():
    return BRepGraph_NodeId(BRepGraph_NodeId.Kind.Solid, 0)


def _translation(x, y, z):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(x, y, z))
    return t


def _count_seam_edges(g):
    n = 0
    for i in range(g.Topo().Edges().Nb()):
        for ceid in g.Topo().Edges().Relations(BRepGraph_EdgeId(i)).CoEdgeIds:
            if BRepGraph_Tool.CoEdge.SeamPair_s(g, ceid).IsValid():
                n += 1
                break
    return n


def _find_seam_edge(g):
    for i in range(g.Topo().Edges().Nb()):
        eid = BRepGraph_EdgeId(i)
        for ceid in g.Topo().Edges().CoEdges(eid):
            if BRepGraph_Tool.CoEdge.IsSeam_s(g, ceid):
                return eid
    return BRepGraph_EdgeId()


def _split(g, eid, point, param):
    vtx = g.Editor().Vertices().Add(point, 1.0e-7)
    assert vtx.IsValid()
    sub_a = BRepGraph_EdgeId()
    sub_b = BRepGraph_EdgeId()
    g.Editor().Edges().Split(eid, vtx, param, sub_a, sub_b)
    return sub_a, sub_b


def _first_curve_edge(g, need_vertex_refs=False):
    for i in range(g.Topo().Edges().Nb()):
        eid = BRepGraph_EdgeId(i)
        d = g.Topo().Edges().Definition(eid)
        if BRepGraph_Tool.Edge.Degenerated_s(g, eid) or not d.Curve3DRepId.IsValid():
            continue
        if need_vertex_refs and not (d.StartVertexRefId.IsValid() and d.EndVertexRefId.IsValid()):
            continue
        first, last = BRepGraph_Tool.Edge.Range_s(g, eid)
        return eid, 0.5 * (first + last)
    return BRepGraph_EdgeId(), 0.0


# ---------- scenarios ----------


def test_BRepGraph_ScenarioMatrix_Box_MutateVertex_ValidateReconstructPopulateRoundTrip():
    box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    orig_area = _area(box)
    g = _graph(box)
    assert _light_valid(g)

    assert g.Topo().Vertices().Nb() > 0
    vid = BRepGraph_VertexId.Start_s()
    old = BRepGraph_Tool.Vertex.Pnt_s(g, vid)
    mut = g.Editor().Vertices().Mut(vid)
    g.Editor().Vertices().SetPoint(mut, gp_Pnt(old.X() + 50.0, old.Y(), old.Z()))
    del mut

    assert _light_valid(g)

    recon = g.Shapes().Reconstruct(_solid0())
    assert not recon.IsNull()
    assert recon.ShapeType() == TopAbs_SOLID
    assert abs(_area(recon) - orig_area) <= orig_area * 0.01

    assert abs(BRepGraph_Tool.Vertex.Pnt_s(g, vid).X() - (old.X() + 50.0)) <= CONF

    mutated = gp_Pnt(old.X() + 50.0, old.Y(), old.Z())
    found = False
    for v in TopExp_Explorer(recon, TopAbs_VERTEX):
        if BRep_Tool.Pnt_s(TopoDS.Vertex(v)).SquareDistance(mutated) < Precision.SquareConfusion_s():
            found = True
            break
    assert found

    rt = _populate(recon)
    assert _light_valid(rt)
    assert rt.Topo().Faces().Nb() == _count_sub_shapes(box, TopAbs_FACE)
    assert rt.Topo().Edges().Nb() == _count_sub_shapes(box, TopAbs_EDGE)


def test_BRepGraph_ScenarioMatrix_Cylinder_SeamEdge_MutationAndBothSubsystemsConsistent():
    cyl = BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape()
    g = _graph(cyl)
    orig = _populate(cyl)

    seam = BRepGraph_EdgeId()
    for i in range(orig.Topo().Edges().Nb()):
        for ceid in orig.Topo().Edges().Relations(BRepGraph_EdgeId(i)).CoEdgeIds:
            if BRepGraph_Tool.CoEdge.SeamPair_s(orig, ceid).IsValid():
                seam = BRepGraph_EdgeId(i)
                break
        if seam.IsValid():
            break
    assert seam.IsValid()
    assert seam.Index < g.Topo().Edges().Nb()

    old_tol = g.Topo().Edges().Definition(seam).Tolerance
    mut = g.Editor().Edges().Mut(seam)
    g.Editor().Edges().SetTolerance(mut, old_tol + 0.5)
    del mut

    assert _light_valid(g)
    recon = g.Shapes().Reconstruct(_solid0())
    assert not recon.IsNull()

    rg = _populate(recon)
    assert rg.Topo().Vertices().Nb() == orig.Topo().Vertices().Nb()
    assert rg.Topo().Edges().Nb() == orig.Topo().Edges().Nb()
    assert rg.Topo().Faces().Nb() == orig.Topo().Faces().Nb()
    assert _count_seam_edges(rg) >= 1
    assert _light_valid(rg)


def test_BRepGraph_ScenarioMatrix_CompSolid_TwoBoxes_BothSubsystemsMutateReconstructRoundTrip():
    bb = BRep_Builder()
    cs = TopoDS_CompSolid()
    bb.MakeCompSolid(cs)
    bb.Add(cs, BRepPrimAPI_MakeBox(4.0, 4.0, 4.0).Shape())
    bb.Add(cs, BRepPrimAPI_MakeBox(3.0, 3.0, 3.0).Shape())
    orig_faces = _count_sub_shapes(cs, TopAbs_FACE)
    orig_edges = _count_sub_shapes(cs, TopAbs_EDGE)

    orig = _populate(cs)
    assert orig.Topo().CompSolids().Nb() == 1
    assert orig.Topo().Solids().Nb() >= 2
    for i in range(orig.Topo().Solids().Nb()):
        assert orig.Topo().Solids().Relations(BRepGraph_SolidId(i)).ParentSolidRefIds.Size() >= 1
    assert _light_valid(orig)

    g = _graph(cs)
    assert _light_valid(g)

    assert g.Topo().Edges().Nb() > 0
    eid = BRepGraph_EdgeId.Start_s()
    tol = g.Topo().Edges().Definition(eid).Tolerance
    mut = g.Editor().Edges().Mut(eid)
    g.Editor().Edges().SetTolerance(mut, tol + 1.0)
    del mut
    assert _light_valid(g)

    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_CompSolidId.Start_s()))
    assert not recon.IsNull()
    assert _count_sub_shapes(recon, TopAbs_FACE) == orig_faces
    assert _count_sub_shapes(recon, TopAbs_EDGE) == orig_edges
    assert _count_sub_shapes(recon, TopAbs_SOLID) == 2

    rg = _populate(recon)
    assert rg.Topo().CompSolids().Nb() == 1
    assert rg.Topo().Solids().Nb() == orig.Topo().Solids().Nb()
    assert rg.Topo().Faces().Nb() == orig.Topo().Faces().Nb()
    assert rg.Topo().Edges().Nb() == orig.Topo().Edges().Nb()
    assert _light_valid(rg)


def test_BRepGraph_ScenarioMatrix_Assembly_TwoOccurrences_ValidateDAGReconstructPartPopulate():
    g = _graph(BRepPrimAPI_MakeBox(8.0, 8.0, 8.0).Shape())
    orig_solid = g.Shapes().Original(BRepGraph_SolidId.Start_s())
    assert not orig_solid.IsNull()
    orig_faces = _count_sub_shapes(orig_solid, TopAbs_FACE)

    part = BRepGraph_ProductId.Start_s()
    asm = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(asm)
    assert asm.IsValid()

    occ1 = g.Editor().Products().Append(asm, part, TopLoc_Location(_translation(100.0, 0.0, 0.0)))
    occ2 = g.Editor().Products().Append(asm, part, TopLoc_Location(_translation(0.0, 200.0, 0.0)))
    assert occ1.IsValid()
    assert occ2.IsValid()

    res = BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Lightweight_s())
    assert res.IsValid()
    assert res.NbIssues(BRepGraph_Validate.Severity.Error) == 0

    assert g.Topo().Occurrences().Product(occ1) == part
    assert g.Topo().Occurrences().Product(occ2) == part
    loc1 = g.Topo().Occurrences().OccurrenceLocation(occ1)
    loc2 = g.Topo().Occurrences().OccurrenceLocation(occ2)
    assert abs(loc1.Transformation().TranslationPart().X() - 100.0) <= CONF
    assert abs(loc2.Transformation().TranslationPart().Y() - 200.0) <= CONF

    part_shape = g.Shapes().Reconstruct(_solid0())
    assert not part_shape.IsNull()
    assert _count_sub_shapes(part_shape, TopAbs_FACE) == orig_faces

    pg = _populate(part_shape)
    assert pg.Topo().Solids().Nb() == 1
    assert pg.Topo().Faces().Nb() == orig_faces
    assert _light_valid(pg)


def test_BRepGraph_ScenarioMatrix_Compound_FreeWireFreeEdgeFreeVertex_ValidateAndPopulate():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)

    me1 = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0))
    assert me1.IsDone()
    wire = TopoDS_Wire()
    bb.MakeWire(wire)
    bb.Add(wire, me1.Edge())
    bb.Add(comp, wire)

    me2 = BRepBuilderAPI_MakeEdge(gp_Pnt(20, 0, 0), gp_Pnt(30, 0, 0))
    assert me2.IsDone()
    bb.Add(comp, me2.Edge())

    vtx = TopoDS_Vertex()
    bb.MakeVertex(vtx, gp_Pnt(50, 50, 50), CONF)
    bb.Add(comp, vtx)

    g = _graph(comp)
    assert g.Topo().Compounds().Nb() == 1
    assert g.Topo().Wires().Nb() >= 1
    assert g.Topo().Edges().Nb() >= 2
    assert g.Topo().Vertices().Nb() >= 1
    assert _light_valid(g)

    pg = _populate(comp)
    assert pg.Topo().Compounds().Nb() == 1
    assert pg.Topo().Wires().Nb() >= 1
    assert pg.Topo().Edges().Nb() >= 2
    assert _light_valid(pg)


def test_BRepGraph_ScenarioMatrix_Compound_BoxAndCylinder_MutationReconstructAreaRegression():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    box = BRepPrimAPI_MakeBox(6.0, 6.0, 6.0).Shape()
    cyl = BRepPrimAPI_MakeCylinder(3.0, 10.0).Shape()
    bb.Add(comp, box)
    bb.Add(comp, cyl)
    total_area = _area(box) + _area(cyl)

    base = _populate(comp)
    assert base.Topo().Solids().Nb() == 2
    assert base.Topo().Compounds().Nb() == 1
    base_seams = _count_seam_edges(base)
    assert base_seams >= 1

    g = _graph(comp)
    assert g.Topo().Solids().Nb() == 2
    assert _light_valid(g)

    assert g.Topo().Faces().Nb() > 0
    fid = BRepGraph_FaceId.Start_s()
    tol = g.Topo().Faces().Definition(fid).Tolerance
    mut = g.Editor().Faces().Mut(fid)
    g.Editor().Faces().SetTolerance(mut, tol + 0.5)
    del mut
    assert _light_valid(g)

    recon = g.Shapes().Reconstruct(BRepGraph_NodeId(BRepGraph_CompoundId.Start_s()))
    assert not recon.IsNull()
    assert _count_sub_shapes(recon, TopAbs_SOLID) == 2
    assert _count_sub_shapes(recon, TopAbs_FACE) == _count_sub_shapes(comp, TopAbs_FACE)
    assert abs(_area(recon) - total_area) <= total_area * 0.01

    rg = _populate(recon)
    assert rg.Topo().Solids().Nb() == base.Topo().Solids().Nb()
    assert rg.Topo().Faces().Nb() == base.Topo().Faces().Nb()
    assert rg.Topo().Edges().Nb() == base.Topo().Edges().Nb()
    assert _count_seam_edges(rg) == base_seams
    assert _light_valid(rg)


def test_BRepGraph_ScenarioMatrix_Assembly_ThreeLevelNesting_CleanAudit_CycleDetection():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    prods = g.Editor().Products()
    leaf = BRepGraph_ProductId.Start_s()
    mid = prods.Add()
    prods.AppendDocumentRoot(mid)
    root = prods.Add()
    prods.AppendDocumentRoot(root)
    top = prods.Add()
    prods.AppendDocumentRoot(top)

    occ_root = prods.Append(top, root, TopLoc_Location(_translation(0.0, 0.0, 3.0)))
    occ_mid = prods.Append(root, mid, TopLoc_Location(_translation(0.0, 2.0, 0.0)), occ_root)
    occ_leaf = prods.Append(mid, leaf, TopLoc_Location(_translation(1.0, 0.0, 0.0)), occ_mid)
    assert occ_root.IsValid()
    assert occ_mid.IsValid()
    assert occ_leaf.IsValid()

    assert g.Topo().Products().NbComponents(top) == 1
    assert g.Topo().Products().NbComponents(root) == 1
    assert g.Topo().Products().NbComponents(mid) == 1
    assert _light_valid(g)

    c = prods.Add()
    prods.AppendDocumentRoot(c)
    d = prods.Add()
    prods.AppendDocumentRoot(d)
    assert prods.Append(c, d, TopLoc_Location(gp_Trsf())).IsValid()
    assert prods.Append(d, c, TopLoc_Location(gp_Trsf())).IsValid()

    res = BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s())
    assert not res.IsValid()
    assert any(issue.Description.Search("Assembly cycle") >= 0 for issue in res.Issues)


def test_BRepGraph_ScenarioMatrix_Assembly_SharedPartBetweenTwoRootAssemblies():
    g = _graph(BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape())
    nb_solids = g.Topo().Solids().Nb()
    nb_faces = g.Topo().Faces().Nb()

    prods = g.Editor().Products()
    shared = BRepGraph_ProductId.Start_s()
    asm_a = prods.Add()
    prods.AppendDocumentRoot(asm_a)
    asm_b = prods.Add()
    prods.AppendDocumentRoot(asm_b)
    assert prods.Append(asm_a, shared, TopLoc_Location(_translation(100.0, 0.0, 0.0))).IsValid()
    assert prods.Append(asm_b, shared, TopLoc_Location(_translation(0.0, 100.0, 0.0))).IsValid()

    assert g.Topo().Solids().Nb() == nb_solids
    assert g.Topo().Faces().Nb() == nb_faces
    assert _light_valid(g)

    a_shape = g.Shapes().Shape(BRepGraph_NodeId(asm_a))
    b_shape = g.Shapes().Shape(BRepGraph_NodeId(asm_b))
    assert not a_shape.IsNull()
    assert not b_shape.IsNull()
    assert a_shape.ShapeType() == TopAbs_COMPOUND
    assert b_shape.ShapeType() == TopAbs_COMPOUND
    assert a_shape.NbChildren() == 1
    assert b_shape.NbChildren() == 1
    it_a = TopoDS_Iterator(a_shape)
    it_b = TopoDS_Iterator(b_shape)
    assert it_a.More() and it_b.More()
    assert it_a.Value().ShapeType() == it_b.Value().ShapeType()


def test_BRepGraph_ScenarioMatrix_Compound_MixedAtomicChildren_RelationsCoverage():
    box = BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape()
    free_shell = TopExp_Explorer(box, TopAbs_SHELL).Current()
    free_face = TopExp_Explorer(box, TopAbs_FACE).Current()
    free_edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0)).Edge()
    free_vertex = TopoDS_Vertex()
    bb = BRep_Builder()
    bb.MakeVertex(free_vertex, gp_Pnt(42.0, 13.0, 7.0), CONF)

    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    for s in (box, free_shell, free_face, free_edge, free_vertex):
        bb.Add(comp, s)

    g = _graph(comp)
    assert g.Topo().Compounds().Nb() > 0
    assert _light_valid(g)

    K = BRepGraph_NodeId.Kind
    kinds = set()
    for ref_id in g.Topo().Compounds().Relations(BRepGraph_CompoundId(0)).ChildRefIds:
        kinds.add(g.Refs().Children().Entry(ref_id).ChildNodeId.NodeKind)
    assert K.Solid in kinds
    assert K.Edge in kinds
    assert K.Vertex in kinds

    assert _light_valid(_populate(comp))


def test_BRepGraph_ScenarioMatrix_CompSolid_ThreeBoxes_RelationsPerSolid():
    bb = BRep_Builder()
    cs = TopoDS_CompSolid()
    bb.MakeCompSolid(cs)
    bb.Add(cs, BRepPrimAPI_MakeBox(5.0, 5.0, 5.0).Shape())
    bb.Add(cs, BRepPrimAPI_MakeBox(gp_Pnt(20.0, 0.0, 0.0), 5.0, 5.0, 5.0).Shape())
    bb.Add(cs, BRepPrimAPI_MakeBox(gp_Pnt(40.0, 0.0, 0.0), 5.0, 5.0, 5.0).Shape())

    assert _light_valid(_graph(cs))

    pg = _populate(cs)
    assert pg.Topo().CompSolids().Nb() == 1
    assert pg.Topo().Solids().Nb() >= 3
    for i in range(pg.Topo().Solids().Nb()):
        assert pg.Topo().Solids().Relations(BRepGraph_SolidId(i)).ParentSolidRefIds.Size() == 1
    assert _light_valid(pg)


def _seam_pairs_symmetric(g):
    n = 0
    for i in range(g.Topo().CoEdges().Nb()):
        ceid = BRepGraph_CoEdgeId(i)
        pair = BRepGraph_Tool.CoEdge.SeamPair_s(g, ceid)
        if not pair.IsValid():
            continue
        n += 1
        assert BRepGraph_Tool.CoEdge.SeamPair_s(g, pair) == ceid
        assert g.Topo().CoEdges().Definition(pair).ChildEdgeId == g.Topo().CoEdges().Definition(ceid).ChildEdgeId
    return n


def test_BRepGraph_ScenarioMatrix_Sphere_SeamCoEdgePair_Bidirectional():
    sphere = BRepPrimAPI_MakeSphere(10.0).Shape()
    pg = _populate(sphere)
    n_before = _seam_pairs_symmetric(pg)
    assert n_before > 0

    g = _graph(sphere)
    assert _light_valid(g)
    recon = g.Shapes().Reconstruct(_solid0())
    assert not recon.IsNull()
    rg = _populate(recon)
    assert _seam_pairs_symmetric(rg) == n_before


def _check_bidirectional_on_edge(g, eid):
    for ceid in g.Topo().Edges().CoEdges(eid):
        pair = BRepGraph_Tool.CoEdge.SeamPair_s(g, ceid)
        if not pair.IsValid():
            continue
        assert BRepGraph_Tool.CoEdge.SeamPair_s(g, pair) == ceid


def test_BRepGraph_ScenarioMatrix_Cylinder_SeamEdgeSplit_AuditStable():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())
    seam = _find_seam_edge(g)
    assert seam.IsValid()
    assert not BRepGraph_Tool.Edge.Degenerated_s(g, seam)
    first, last = BRepGraph_Tool.Edge.Range_s(g, seam)
    assert first < last

    sub_a, sub_b = _split(g, seam, gp_Pnt(5.0, 0.0, 7.5), 0.5 * (first + last))
    assert sub_a.IsValid()
    assert sub_b.IsValid()
    assert _light_valid(g)
    _check_bidirectional_on_edge(g, sub_a)
    _check_bidirectional_on_edge(g, sub_b)


def test_BRepGraph_ScenarioMatrix_EditorFaceBoundPCurveCoEdge_RelationsAndLookup():
    g = BRepGraph()
    g.Clear()
    ed = g.Editor()
    v0 = ed.Vertices().Add(gp_Pnt(0.0, 0.0, 0.0), 1.0e-7)
    v1 = ed.Vertices().Add(gp_Pnt(1.0, 0.0, 0.0), 1.0e-7)
    assert v0.IsValid()
    assert v1.IsValid()
    eid = ed.Edges().Add(v0, v1, None, 0.0, 1.0, 1.0e-7)
    assert eid.IsValid()
    wire_ce = ed.CoEdges().Add(eid, TopAbs_FORWARD)
    assert wire_ce.IsValid()

    arr = NCollection_Array1[BRepGraph_CoEdgeId](0, 0)
    arr.SetValue(0, wire_ce)
    wid = ed.Wires().Add(arr)
    assert wid.IsValid()

    plane = Geom_Plane(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    fid = ed.Faces().Add(plane, wid, NCollection_Array1[BRepGraph_WireId](), 1.0e-7)
    assert fid.IsValid()

    curve2d = Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0))
    pc_ce = ed.CoEdges().Add(eid, fid, curve2d, 0.0, 1.0, TopAbs_REVERSED)
    assert pc_ce.IsValid()

    d = g.Topo().CoEdges().Definition(pc_ce)
    assert d.ChildEdgeId == eid
    assert d.FaceId == fid
    assert d.Orientation.IsReversed
    assert d.Curve2DRepId.IsValid()

    assert BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, fid) == pc_ce
    assert BRepGraph_Tool.Edge.FindPCurveCoEdgeId_s(g, eid, fid, TopAbs_REVERSED) == pc_ce

    assert pc_ce in list(g.Topo().Edges().CoEdges(eid))
    assert fid in list(g.Topo().Edges().FacesOf(eid))

    assert g.ValidateRelations()
    assert _light_valid(g)


def test_BRepGraph_ScenarioMatrix_Cylinder_SeamEdgeSplit_CoEdgeFaceIncidence():
    g = _graph(BRepPrimAPI_MakeCylinder(5.0, 15.0).Shape())
    seam = _find_seam_edge(g)
    assert seam.IsValid()
    first, last = BRepGraph_Tool.Edge.Range_s(g, seam)
    sub_a, sub_b = _split(g, seam, gp_Pnt(5.0, 0.0, 7.5), 0.5 * (first + last))
    assert sub_a.IsValid()
    assert sub_b.IsValid()

    for sub in (sub_a, sub_b):
        coedges = g.Topo().Edges().CoEdges(sub)
        assert coedges.Size() > 0
        for ceid in coedges:
            d = g.Topo().CoEdges().Definition(ceid)
            assert d.Curve2DRepId.IsValid()
            assert d.FaceId.IsValid()
            assert d.ChildEdgeId == sub
            ce_first, ce_last = BRepGraph_Tool.CoEdge.Range_s(g, ceid)
            assert ce_first < ce_last

    assert _light_valid(g)


def test_BRepGraph_ScenarioMatrix_BoxEdgeSplit_BoundaryVertexRetirement():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    eid, param = _first_curve_edge(g, need_vertex_refs=True)
    assert eid.IsValid()
    pre_start = g.Topo().Edges().Definition(eid).StartVertexRefId
    pre_end = g.Topo().Edges().Definition(eid).EndVertexRefId
    assert pre_start.IsValid()
    assert pre_end.IsValid()
    assert not pre_start.IsRemoved(g)
    assert not pre_end.IsRemoved(g)

    sub_a, sub_b = _split(g, eid, gp_Pnt(5.0, 10.0, 15.0), param)
    assert sub_a.IsValid()
    assert sub_b.IsValid()
    assert pre_start.IsRemoved(g)
    assert pre_end.IsRemoved(g)
    assert _light_valid(g)


def test_BRepGraph_ScenarioMatrix_BoxEdgeSplit_SubEdgesHaveNoOriginal():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    eid, param = _first_curve_edge(g)
    assert eid.IsValid()
    assert g.Shapes().HasOriginal(BRepGraph_NodeId(eid))

    sub_a, sub_b = _split(g, eid, gp_Pnt(5.0, 10.0, 15.0), param)
    assert sub_a.IsValid()
    assert sub_b.IsValid()
    assert not g.Shapes().HasOriginal(BRepGraph_NodeId(sub_a))
    assert not g.Shapes().HasOriginal(BRepGraph_NodeId(sub_b))
    assert g.Shapes().Original(BRepGraph_NodeId(sub_a)).IsNull()
    assert g.Shapes().Original(BRepGraph_NodeId(sub_b)).IsNull()


def test_BRepGraph_ScenarioMatrix_BoxEdgeSplit_ShapeReconstructsSubEdge():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    eid, param = _first_curve_edge(g)
    assert eid.IsValid()
    sub_a, sub_b = _split(g, eid, gp_Pnt(5.0, 10.0, 15.0), param)
    a_shape = g.Shapes().Shape(BRepGraph_NodeId(sub_a))
    b_shape = g.Shapes().Shape(BRepGraph_NodeId(sub_b))
    assert not a_shape.IsNull()
    assert not b_shape.IsNull()
    assert a_shape.ShapeType() == TopAbs_EDGE
    assert b_shape.ShapeType() == TopAbs_EDGE


def test_BRepGraph_ScenarioMatrix_EditorAddedVertex_HasNoOriginal():
    g = _graph(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    vid = g.Editor().Vertices().Add(gp_Pnt(42.0, 42.0, 42.0), 1.0e-7)
    assert vid.IsValid()
    assert not g.Shapes().HasOriginal(BRepGraph_NodeId(vid))
    assert g.Shapes().Original(BRepGraph_NodeId(vid)).IsNull()
