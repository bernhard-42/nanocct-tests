# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_ParentExplorer_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_OccurrenceId,
    BRepGraph_OccurrenceRefId,
    BRepGraph_ParentExplorer,
    BRepGraph_ProductId,
    BRepGraph_RefId,
    BRepGraph_ShellId,
    BRepGraph_SolidId,
    BRepGraph_Validate,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound

K = BRepGraph_NodeId.Kind
Mode = BRepGraph_ParentExplorer.TraversalMode
LinkKind = BRepGraph_ParentExplorer.LinkKind


def _graph(shape=None):
    g = BRepGraph()
    g.Clear()
    if shape is None:
        shape = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    g.Shapes().Add(shape)
    assert not g.IsEmpty()
    return g


def _translation_location(x, y, z):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(x, y, z))
    return TopLoc_Location(t)


def _rotation_z_location(angle):
    t = gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), angle)
    return TopLoc_Location(t)


def _probe_points(actual, expected):
    probe = gp_Pnt(3.0, 5.0, 7.0)
    return probe.Transformed(actual.Transformation()), probe.Transformed(expected.Transformation())


def _locations_equivalent(actual, expected):
    a, e = _probe_points(actual, expected)
    return a.Distance(e) <= Precision.Confusion_s()


def _expect_locations_equivalent(actual, expected):
    a, e = _probe_points(actual, expected)
    tol = Precision.Confusion_s()
    assert abs(a.X() - e.X()) <= tol
    assert abs(a.Y() - e.Y()) <= tol
    assert abs(a.Z() - e.Z()) <= tol


def _node_array(node):
    arr = NCollection_Array1[BRepGraph_NodeId](0, 0)
    arr.SetValue(0, BRepGraph_NodeId(node))
    return arr


def test_BRepGraph_ParentExplorerTest_FaceParents_All_CountAndOrder():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s())
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_ShellId.Start_s())
    exp.Next()
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    exp.Next()
    assert exp.More()
    assert exp.Current().DefId.NodeKind == K.Occurrence
    exp.Next()
    assert exp.More()
    assert exp.Current().DefId.NodeKind == K.Product
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_FaceParents_TypedSolid_OneResult():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), K.Solid)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_FaceParents_DirectParents_StopsAtImmediateShell():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), Mode.DirectParents)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_ShellId.Start_s())
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_FaceParents_DirectParents_ExposeChildAndRef():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), Mode.DirectParents)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_ShellId.Start_s())
    assert exp.CurrentChild() == BRepGraph_NodeId(BRepGraph_FaceId.Start_s())
    assert exp.CurrentLinkKind() == LinkKind.Reference
    face_ref = g.Refs().Faces().IdsOf(BRepGraph_ShellId.Start_s()).Value(0)
    assert exp.CurrentRef() == BRepGraph_RefId(face_ref)


def test_BRepGraph_ParentExplorerTest_AvoidKind_Solid_PrunesProducts():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), K.Product, K.Solid, False)
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_AvoidKind_EmitBoundary_ReturnsSolidInsteadOfProducts():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), K.Product, K.Solid, True)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_AvoidKind_SameAsTarget_IsIgnored():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), K.Solid, K.Solid, False)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_AllParents_AvoidSolid_PrunesProducts():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), K.Solid, False)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_ShellId.Start_s())
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_AllParents_AvoidSolidEmitBoundary_ReturnsShellAndSolid():
    g = _graph()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_FaceId.Start_s(), K.Solid, True)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_ShellId.Start_s())
    exp.Next()
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    exp.Next()
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_SharedProduct_ProductParentsKeepDistinctContexts():
    g = _graph()
    products = g.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()
    assert products.Append(assembly, part, _translation_location(10.0, 0.0, 0.0)).IsValid()
    assert products.Append(assembly, part, _translation_location(25.0, 0.0, 0.0)).IsValid()

    locs = []
    for inst in BRepGraph_ParentExplorer(g, BRepGraph_SolidId.Start_s(), K.Product):
        if inst.DefId != BRepGraph_NodeId(part):
            continue
        locs.append(inst.Location)
    assert len(locs) == 2
    assert not locs[0].IsEqual(locs[1])


def test_BRepGraph_ParentExplorerTest_DeepProductOccurrenceChain_ComposesToTopProduct():
    g = _graph()
    products = g.Editor().Products()
    child = BRepGraph_ProductId.Start_s()
    expected_x = 0.0
    top = None
    for level in range(1, 7):
        top = products.Add()
        products.AppendDocumentRoot(top)
        assert top.IsValid()
        assert products.Append(top, child, _translation_location(float(level), 0.0, 0.0)).IsValid()
        expected_x += float(level)
        child = top

    found_top = False
    exp = BRepGraph_ParentExplorer(g, BRepGraph_SolidId.Start_s(), K.Product)
    while exp.More():
        if exp.Current().DefId == BRepGraph_NodeId(top):
            found_top = True
            x = exp.LeafLocation().Transformation().TranslationPart().X()
            assert abs(x - expected_x) <= Precision.Confusion_s()
        exp.Next()
    assert found_top


def test_BRepGraph_ParentExplorerTest_DeepProductOccurrenceChain_ReachesNestedOccurrences():
    g = BRepGraph()
    g.Clear()
    products = g.Editor().Products()
    part = products.Add()
    sub = products.Add()
    top = products.Add()
    assert part.IsValid()
    assert sub.IsValid()
    assert top.IsValid()
    part_occ = products.Append(sub, part, TopLoc_Location())
    sub_occ = products.Append(top, sub, TopLoc_Location())
    assert part_occ.IsValid()
    assert sub_occ.IsValid()

    has_part = False
    has_sub = False
    n = 0
    for inst in BRepGraph_ParentExplorer(g, part, K.Occurrence):
        has_part = has_part or inst.DefId == BRepGraph_NodeId(part_occ)
        has_sub = has_sub or inst.DefId == BRepGraph_NodeId(sub_occ)
        n += 1
    assert n == 2
    assert has_part
    assert has_sub


def test_BRepGraph_ParentExplorerTest_DeepCompoundChain_ReachesTopCompound():
    g = _graph()
    child = BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    top = None
    for _ in range(8):
        top = g.Editor().Compounds().Add(_node_array(child))
        assert top.IsValid()
        child = BRepGraph_NodeId(top)

    n = 0
    found_top = False
    for inst in BRepGraph_ParentExplorer(g, BRepGraph_SolidId.Start_s(), K.Compound):
        n += 1
        found_top = found_top or inst.DefId == BRepGraph_NodeId(top)
    assert n == 8
    assert found_top


def test_BRepGraph_ParentExplorerTest_VertexChildOfDeepCompoundChain_ReachesTopCompound():
    g = BRepGraph()
    g.Clear()
    vertex = g.Editor().Vertices().Add(gp_Pnt(1.0, 2.0, 3.0), 1.0e-7)
    assert vertex.IsValid()

    child = BRepGraph_NodeId(vertex)
    top = None
    expected_x = 0.0
    for level in range(1, 5):
        top = g.Editor().Compounds().Add(_node_array(child))
        assert top.IsValid()
        child_refs = g.Refs().Children().IdsOf(top)
        assert child_refs.Size() == 1
        g.Editor().Gen().SetChildRefLocalLocation(
            child_refs.First(), _translation_location(float(level), 0.0, 0.0)
        )
        expected_x += float(level)
        child = BRepGraph_NodeId(top)

    n = 0
    found_top = False
    exp = BRepGraph_ParentExplorer(g, vertex, K.Compound)
    while exp.More():
        n += 1
        if exp.Current().DefId == BRepGraph_NodeId(top):
            found_top = True
            x = exp.LeafLocation().Transformation().TranslationPart().X()
            assert abs(x - expected_x) <= Precision.Confusion_s()
        exp.Next()
    assert n == 4
    assert found_top
    assert g.ValidateRelations()


def test_BRepGraph_ParentExplorerTest_MixedProductOccurrenceAndCompoundChain_PreservesLocations():
    g = _graph()
    comp1_loc = _translation_location(2.0, 0.0, 0.0)
    comp2_loc = _rotation_z_location(0.25)
    comp3_loc = _translation_location(0.0, 3.0, 0.0)
    occ1_loc = _translation_location(0.0, 0.0, 5.0)
    occ2_loc = _rotation_z_location(-0.5)

    compounds = g.Editor().Compounds()
    comp1 = compounds.Add(_node_array(BRepGraph_SolidId.Start_s()))
    assert comp1.IsValid()
    assert g.Refs().Children().IdsOf(comp1).Size() == 1
    g.Editor().Gen().SetChildRefLocalLocation(g.Refs().Children().IdsOf(comp1).First(), comp1_loc)

    comp2 = compounds.Add(_node_array(comp1))
    assert comp2.IsValid()
    assert g.Refs().Children().IdsOf(comp2).Size() == 1
    g.Editor().Gen().SetChildRefLocalLocation(g.Refs().Children().IdsOf(comp2).First(), comp2_loc)

    comp3 = compounds.Add(_node_array(comp2))
    assert comp3.IsValid()
    assert g.Refs().Children().IdsOf(comp3).Size() == 1
    g.Editor().Gen().SetChildRefLocalLocation(g.Refs().Children().IdsOf(comp3).First(), comp3_loc)

    products = g.Editor().Products()
    part = products.Add(comp3)
    products.AppendDocumentRoot(part)
    mid = products.Add()
    products.AppendDocumentRoot(mid)
    top = products.Add()
    products.AppendDocumentRoot(top)
    assert part.IsValid()
    assert mid.IsValid()
    assert top.IsValid()

    occ1 = products.Append(mid, part, occ1_loc)
    occ2 = products.Append(top, mid, occ2_loc)
    assert occ1.IsValid()
    assert occ2.IsValid()

    to_part = occ2_loc * occ1_loc
    to_comp3 = to_part
    to_comp2 = to_comp3 * comp3_loc
    to_comp1 = to_comp2 * comp2_loc
    to_solid = to_comp1 * comp1_loc

    expectations = {
        BRepGraph_NodeId(top): TopLoc_Location(),
        BRepGraph_NodeId(occ2): occ2_loc,
        BRepGraph_NodeId(mid): occ2_loc,
        BRepGraph_NodeId(occ1): to_part,
        BRepGraph_NodeId(part): to_part,
        BRepGraph_NodeId(comp3): to_comp3,
        BRepGraph_NodeId(comp2): to_comp2,
        BRepGraph_NodeId(comp1): to_comp1,
    }
    found = set()
    exp = BRepGraph_ParentExplorer(g, BRepGraph_SolidId.Start_s())
    while exp.More():
        if _locations_equivalent(exp.LeafLocation(), to_solid):
            current = exp.Current().DefId
            if current in expectations:
                found.add(current)
                _expect_locations_equivalent(exp.Current().Location, expectations[current])
        exp.Next()
    assert found == set(expectations)


def test_BRepGraph_ParentExplorerTest_ShapeRootDirectParent_IsOccurrenceNotProductShortcut():
    g = _graph()
    assert g.Topo().Products().Nb() > 0
    part = BRepGraph_ProductId(0)
    assert g.Topo().Products().NbComponents(part) == 1
    root_occ = g.Topo().Products().Component(part, 0)
    assert root_occ.IsValid()

    exp = BRepGraph_ParentExplorer(g, BRepGraph_SolidId.Start_s(), Mode.DirectParents)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(root_occ)
    assert exp.CurrentChild() == BRepGraph_NodeId(BRepGraph_SolidId.Start_s())
    assert exp.CurrentLinkKind() == LinkKind.Structural
    assert not exp.CurrentRef().IsValid()
    exp.Next()
    assert not exp.More()

    product_exp = BRepGraph_ParentExplorer(g, BRepGraph_SolidId.Start_s(), K.Product)
    assert product_exp.More()
    assert product_exp.Current().DefId == BRepGraph_NodeId(part)


def test_BRepGraph_ParentExplorerTest_TargetProductAvoidCompound_StopsAtCompound():
    bb = BRep_Builder()
    comp = TopoDS_Compound()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    g = _graph(comp)
    assert g.Topo().Products().Nb() > 0
    exp = BRepGraph_ParentExplorer(g, BRepGraph_SolidId.Start_s(), K.Product, K.Compound, False)
    assert not exp.More()


def test_BRepGraph_ParentExplorerTest_OccurrenceParent_ExposeOccurrenceRef():
    g = _graph()
    products = g.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()
    occ = products.Append(assembly, part, TopLoc_Location())
    assert occ.IsValid()

    exp = BRepGraph_ParentExplorer(g, occ, K.Product, Mode.DirectParents)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(assembly)
    assert exp.CurrentChild() == BRepGraph_NodeId(occ)
    assert exp.CurrentLinkKind() == LinkKind.Reference
    occ_ref = g.Refs().Occurrences().IdsOf(assembly).Value(0)
    assert exp.CurrentRef() == BRepGraph_RefId(occ_ref)


def test_BRepGraph_ParentExplorerTest_OccurrenceParents_SetRefOccurrenceDefRejectsSharing():
    g = _graph()
    products = g.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    asm1 = products.Add()
    products.AppendDocumentRoot(asm1)
    asm2 = products.Add()
    products.AppendDocumentRoot(asm2)
    assert part.IsValid()
    assert asm1.IsValid()
    assert asm2.IsValid()

    ref1 = BRepGraph_OccurrenceRefId()
    ref2 = BRepGraph_OccurrenceRefId()
    occ1 = products.Append(asm1, part, TopLoc_Location(), BRepGraph_OccurrenceId(), ref1)
    occ2 = products.Append(asm2, part, TopLoc_Location(), BRepGraph_OccurrenceId(), ref2)
    assert occ1.IsValid()
    assert occ2.IsValid()
    assert ref1.IsValid()
    assert ref2.IsValid()

    g.Editor().Occurrences().SetRefChildOccurrenceId(ref2, occ1)
    assert g.Refs().Occurrences().Entry(ref2).ChildOccurrenceId == occ2
    assert g.ValidateRelations()

    audit = BRepGraph_Validate.Perform_s(g, BRepGraph_Validate.Options.Audit_s())
    assert audit.IsValid()


def test_BRepGraph_ParentExplorerTest_ProductParents_ImmediateOccurrence_IsStructural():
    g = _graph()
    products = g.Editor().Products()
    part = products.Add(BRepGraph_SolidId.Start_s())
    products.AppendDocumentRoot(part)
    assembly = products.Add()
    products.AppendDocumentRoot(assembly)
    assert part.IsValid()
    assert assembly.IsValid()
    occ = products.Append(assembly, part, TopLoc_Location())
    assert occ.IsValid()

    exp = BRepGraph_ParentExplorer(g, part, Mode.DirectParents)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(occ)
    assert exp.CurrentChild() == BRepGraph_NodeId(part)
    assert exp.CurrentLinkKind() == LinkKind.Structural
    assert not exp.CurrentRef().IsValid()


def test_BRepGraph_ParentExplorerTest_CoEdgeParents_ImmediateWireIsVisible():
    g = _graph()
    wire_refs = g.Refs().Wires().IdsOf(BRepGraph_FaceId.Start_s())
    assert wire_refs.Size() > 0
    wire = g.Refs().Wires().Entry(wire_refs.Value(0)).ChildWireId
    coedges = g.Topo().Wires().Relations(wire).CoEdgeIds
    assert coedges.Size() > 0
    coedge = coedges.Value(0)

    exp = BRepGraph_ParentExplorer(g, coedge)
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(wire)
    assert exp.CurrentLinkKind() == LinkKind.Structural
    assert not exp.CurrentRef().IsValid()
    exp.Next()
    assert exp.More()
    assert exp.Current().DefId == BRepGraph_NodeId(BRepGraph_FaceId.Start_s())


def test_BRepGraph_ParentExplorerTest_CoEdgeChildOfCompound_ImmediateCompoundIsVisible():
    g = _graph()
    wire = g.Refs().Wires().Entry(g.Refs().Wires().IdsOf(BRepGraph_FaceId.Start_s()).First()).ChildWireId
    coedge = g.Topo().Wires().Relations(wire).CoEdgeIds.First()
    compound = g.Editor().Compounds().Add(_node_array(coedge))
    assert compound.IsValid()

    has_wire = False
    has_compound = False
    exp = BRepGraph_ParentExplorer(g, coedge, Mode.DirectParents)
    while exp.More():
        if exp.Current().DefId == BRepGraph_NodeId(wire):
            has_wire = True
        if exp.Current().DefId == BRepGraph_NodeId(compound):
            has_compound = True
            assert exp.CurrentLinkKind() == LinkKind.Reference
            assert exp.CurrentRef().IsValid()
        exp.Next()
    assert has_wire
    assert has_compound


def test_BRepGraph_ParentExplorerTest_ProductRoot_HasNoParents():
    g = _graph()
    root = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(root)
    assert root.IsValid()
    assert not BRepGraph_ParentExplorer(g, root).More()
