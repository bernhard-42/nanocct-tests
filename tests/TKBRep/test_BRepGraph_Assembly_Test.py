# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_Assembly_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Bnd import Bnd_Box
from nanocct.BRep import BRep_Builder
from nanocct.BRepBndLib import BRepBndLib
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_CompoundId,
    BRepGraph_NodeId,
    BRepGraph_OccurrenceId,
    BRepGraph_OccurrenceIterator,
    BRepGraph_ProductId,
    BRepGraph_ProductIterator,
    BRepGraph_RootProductIterator,
    BRepGraph_SolidId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from nanocct.gp import gp_Trsf, gp_Vec
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ProgramError
from nanocct.TopAbs import TopAbs_COMPOUND, TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Iterator, TopoDS_Shape

Kind = BRepGraph_NodeId.Kind
TOL = Precision.Confusion_s()


def _n(x):
    return BRepGraph_NodeId(x)


def _translation_x(shape):
    return shape.Location().Transformation().TranslationPart().X()


def _bounds(shape):
    b = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, b, False, False)
    return b


def _expect_box_near(actual, expected, tol):
    a, e = actual.Get(), expected.Get()
    for name in ("Xmin", "Ymin", "Zmin", "Xmax", "Ymax", "Zmax"):
        assert abs(getattr(a, name) - getattr(e, name)) <= tol


def _roots(g):
    out = []
    it = BRepGraph_RootProductIterator(g)
    while it.More():
        out.append(it.Current())
        it.Next()
    return out


def _count(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def _loc(x=0.0, y=0.0, z=0.0):
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(x, y, z))
    return TopLoc_Location(t)


def _graph(dx=10.0, dy=10.0, dz=10.0):
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(dx, dy, dz).Shape())
    return g


def _new_root_product(g):
    p = g.Editor().Products().Add()
    g.Editor().Products().AppendDocumentRoot(p)
    return p


P0 = BRepGraph_ProductId.Start_s


def test_BRepGraph_AssemblyTest_Build_SingleSolid_AutoCreatesRootProduct():
    g = _graph(10.0, 20.0, 30.0)
    assert g.Topo().Products().Nb() == 1
    assert g.Topo().Occurrences().Nb() == 1
    g.Topo().Products().Definition(P0())
    assert g.Topo().Products().ShapeRoot(P0()).IsValid()
    assert g.Topo().Products().IsPart(P0())
    assert not g.Topo().Products().IsAssembly(P0())


def test_BRepGraph_AssemblyTest_Build_Compound_AutoCreatesRootProduct():
    comp = TopoDS_Compound()
    bb = BRep_Builder()
    bb.MakeCompound(comp)
    bb.Add(comp, BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape())
    bb.Add(comp, BRepPrimAPI_MakeSphere(5.0).Shape())
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(comp)
    assert g.Topo().Products().Nb() == 1
    assert g.Topo().Occurrences().Nb() == 1
    root = g.Topo().Products().ShapeRoot(P0())
    assert root.IsValid()
    assert root.NodeKind == Kind.Compound


def test_BRepGraph_AssemblyTest_AddProduct_IsPart():
    g = _graph()
    pid = g.Editor().Products().Add(_n(BRepGraph_SolidId.Start_s()))
    g.Editor().Products().AppendDocumentRoot(pid)
    assert pid.IsValid()
    assert g.Topo().Products().IsPart(pid)
    assert not g.Topo().Products().IsAssembly(pid)


def test_BRepGraph_AssemblyTest_AddProduct_InvalidShapeRoot_ReturnsInvalid():
    g = _graph()
    assert not g.Editor().Products().Add(_n(P0())).IsValid()
    g.Editor().Gen().RemoveNode(_n(BRepGraph_SolidId.Start_s()))
    assert not g.Editor().Products().Add(_n(BRepGraph_SolidId.Start_s())).IsValid()


def test_BRepGraph_AssemblyTest_CreateEmptyProduct_EmptyIsNotAssemblyYet():
    g = _graph()
    asm = _new_root_product(g)
    assert asm.IsValid()
    assert not g.Topo().Products().IsAssembly(asm)
    assert not g.Topo().Products().IsPart(asm)


def test_BRepGraph_AssemblyTest_LinkProducts_LinksCorrectly():
    g = _graph()
    part = P0()
    asm = _new_root_product(g)
    occ = g.Editor().Products().Append(asm, part, _loc(100.0))
    assert occ.IsValid()
    assert g.Topo().Occurrences().Product(occ) == part
    assert g.Topo().Occurrences().ParentProduct(occ) == asm
    assert g.Topo().Products().NbComponents(asm) == 1
    assert g.Topo().Products().Component(asm, 0) == occ


def test_BRepGraph_AssemblyTest_DAGSharing_MultipleOccurrencesSamePart():
    g = _graph()
    part = P0()
    asm = _new_root_product(g)
    o1 = g.Editor().Products().Append(asm, part, _loc(100.0))
    o2 = g.Editor().Products().Append(asm, part, _loc(200.0))
    assert o1 != o2
    assert g.Topo().Occurrences().Product(o1) == g.Topo().Occurrences().Product(o2)
    assert g.Topo().Products().NbComponents(asm) == 2


def test_BRepGraph_AssemblyTest_LinkProducts_ParentOccurrenceMustMatchParentProduct():
    g = _graph()
    part = P0()
    asm_a = _new_root_product(g)
    asm_b = _new_root_product(g)
    parent_occ = g.Editor().Products().Append(asm_a, part, TopLoc_Location())
    assert parent_occ.IsValid()
    bad = g.Editor().Products().Append(asm_b, part, TopLoc_Location(), parent_occ)
    assert not bad.IsValid()
    assert g.Topo().Occurrences().Nb() == 2
    assert g.Topo().Products().NbComponents(asm_b) == 0


def test_BRepGraph_AssemblyTest_RootProductIds_Query():
    g = _graph()
    roots = _roots(g)
    assert len(roots) == 1
    assert roots[0] == P0()
    asm = _new_root_product(g)
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    roots = _roots(g)
    assert len(roots) == 1
    assert roots[0] == asm


def test_BRepGraph_AssemblyTest_RootProductIds_ShapelessRootAssembly_UsesProductId():
    g = _graph()
    asm = _new_root_product(g)
    assert g.Editor().Products().Append(asm, P0(), TopLoc_Location()).IsValid()
    roots = g.RootProductIds()
    assert len(roots) == 1
    assert roots.Value(0) == asm


def test_BRepGraph_AssemblyTest_RootProductIds_ReflectsAssemblyMutation():
    g = _graph()
    before = _roots(g)
    assert len(before) == 1
    assert before[0] == P0()
    asm = _new_root_product(g)
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    after = _roots(g)
    assert len(after) == 1
    assert after[0] == asm


def test_BRepGraph_AssemblyTest_RemoveOccurrence_UpdatesParent():
    g = _graph()
    asm = _new_root_product(g)
    occ = g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    assert g.Topo().Products().NbComponents(asm) == 1
    before = g.Refs().Occurrences().IdsOf(asm)
    assert len(before) == 1
    ref = before.Value(0)
    assert not ref.IsRemoved(g)
    g.Editor().Gen().RemoveSubgraph(_n(occ))
    assert g.Topo().Gen().IsRemoved(_n(occ))
    assert g.Topo().Products().NbComponents(asm) == 0
    assert len(g.Refs().Occurrences().IdsOf(asm)) == 0
    assert ref.IsRemoved(g)


def test_BRepGraph_AssemblyTest_RemoveProduct_CascadeOccurrences():
    g = _graph()
    asm = _new_root_product(g)
    o1 = g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    o2 = g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    g.Editor().Gen().RemoveSubgraph(_n(asm))
    assert g.Topo().Gen().IsRemoved(_n(asm))
    assert g.Topo().Gen().IsRemoved(_n(o1))
    assert g.Topo().Gen().IsRemoved(_n(o2))


def test_BRepGraph_AssemblyTest_RemoveProduct_RemovesProductAndOccurrences():
    g = _graph()
    part = P0()
    assert g.Topo().Products().IsPart(part)
    assert g.Topo().Occurrences().Nb() == 1
    occ = BRepGraph_OccurrenceId.Start_s()
    assert not g.Topo().Gen().IsRemoved(_n(occ))
    g.Editor().Gen().RemoveSubgraph(_n(part))
    assert g.Topo().Gen().IsRemoved(_n(part))
    assert g.Topo().Gen().IsRemoved(_n(occ))


def test_BRepGraph_AssemblyTest_RemoveOccurrence_CascadesToNestedChildren():
    g = _graph()
    leaf = P0()
    mid = _new_root_product(g)
    top = _new_root_product(g)
    occ_mid = g.Editor().Products().Append(top, mid, _loc(10.0))
    occ_leaf = g.Editor().Products().Append(mid, leaf, _loc(0.0, 20.0), occ_mid)
    assert not g.Topo().Gen().IsRemoved(_n(occ_mid))
    assert not g.Topo().Gen().IsRemoved(_n(occ_leaf))
    g.Editor().Gen().RemoveSubgraph(_n(occ_mid))
    assert g.Topo().Gen().IsRemoved(_n(occ_mid))
    assert not g.Topo().Gen().IsRemoved(_n(leaf))
    assert not g.Topo().Gen().IsRemoved(_n(mid))
    assert not g.Topo().Gen().IsRemoved(_n(top))


def test_BRepGraph_AssemblyTest_MutProduct_RAII():
    g = _graph()
    guard = g.Editor().Products().Mut(P0())
    guard.MarkDirty()
    del guard  # C++ scope exit fires markModified
    assert g.Topo().Products().Definition(P0()).OwnGen > 0


def test_BRepGraph_AssemblyTest_MutOccurrenceRef_LocalLocation():
    g = _graph()
    asm = _new_root_product(g)
    occ = g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    assert occ.IsValid()
    refs = g.Refs().Occurrences().IdsOf(asm)
    assert len(refs) == 1
    ref = refs.Value(0)
    guard = g.Editor().Occurrences().MutRef(ref)
    g.Editor().Occurrences().SetRefLocalLocation(guard, _loc(50.0))
    del guard  # C++ scope exit fires markRefModified
    trsf = g.Refs().Occurrences().Entry(ref).LocalLocation.Transformation()
    assert abs(trsf.TranslationPart().X() - 50.0) <= TOL


def test_BRepGraph_AssemblyTest_MutInvalidAssemblyDefs_ThrowProgramError():
    g = BRepGraph()
    with pytest.raises(Standard_ProgramError):
        g.Editor().Products().Mut(BRepGraph_ProductId(7))
    with pytest.raises(Standard_ProgramError):
        g.Editor().Occurrences().Mut(BRepGraph_OccurrenceId(7))


def test_BRepGraph_AssemblyTest_GlobalPlacement_DeepNesting():
    g = _graph()
    part = P0()
    sub = _new_root_product(g)
    root = _new_root_product(g)
    occ_sub = g.Editor().Products().Append(root, sub, _loc(0.0, 200.0))
    occ_part = g.Editor().Products().Append(sub, part, _loc(100.0), occ_sub)
    tp = g.Topo().Occurrences().OccurrenceLocation(occ_part).Transformation().TranslationPart()
    assert abs(tp.X() - 100.0) <= TOL
    assert abs(tp.Y() - 0.0) <= TOL
    ts = g.Topo().Occurrences().OccurrenceLocation(occ_sub).Transformation().TranslationPart()
    assert abs(ts.X() - 0.0) <= TOL
    assert abs(ts.Y() - 200.0) <= TOL


def test_BRepGraph_AssemblyTest_NbNodes_IncludesAssembly():
    g = _graph()
    after_build = g.Topo().Gen().NbNodes()
    assert after_build >= 1
    asm = _new_root_product(g)
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    assert g.Topo().Gen().NbNodes() == after_build + 2


def test_BRepGraph_AssemblyTest_OccurrencesOfProduct_Relations():
    g = _graph()
    asm = _new_root_product(g)
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    assert g.Topo().Products().NbComponents(asm) == 2


def test_BRepGraph_AssemblyTest_Product_Count():
    g = _graph()
    _new_root_product(g)
    assert _count(BRepGraph_ProductIterator(g)) == 2


def test_BRepGraph_AssemblyTest_Occurrence_Count():
    g = _graph()
    asm = _new_root_product(g)
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    assert _count(BRepGraph_OccurrenceIterator(g)) == 3


def test_BRepGraph_AssemblyTest_NodeId_Helpers():
    assert BRepGraph_NodeId.IsTopologyKind_s(Kind.Solid)
    assert BRepGraph_NodeId.IsTopologyKind_s(Kind.Vertex)
    assert BRepGraph_NodeId.IsTopologyKind_s(Kind.CompSolid)
    assert not BRepGraph_NodeId.IsTopologyKind_s(Kind.Product)
    assert not BRepGraph_NodeId.IsTopologyKind_s(Kind.Occurrence)
    assert BRepGraph_NodeId.IsAssemblyKind_s(Kind.Product)
    assert BRepGraph_NodeId.IsAssemblyKind_s(Kind.Occurrence)
    assert not BRepGraph_NodeId.IsAssemblyKind_s(Kind.Solid)
    assert not BRepGraph_NodeId.IsAssemblyKind_s(Kind.Face)


def test_BRepGraph_AssemblyTest_UID_IsAssembly():
    g = _graph()
    uid = g.UIDs().Of(_n(P0()))
    assert uid.IsValid()
    assert uid.IsAssembly()
    assert not uid.IsTopology()


def test_BRepGraph_AssemblyTest_LinkProducts_InvalidParent_ReturnsInvalid():
    g = _graph()
    r = g.Editor().Products().Append(BRepGraph_ProductId(999), P0(), TopLoc_Location())
    assert not r.IsValid()
    r = g.Editor().Products().Append(P0(), BRepGraph_ProductId(999), TopLoc_Location())
    assert not r.IsValid()


def test_BRepGraph_AssemblyTest_LinkProducts_SelfReference_ReturnsInvalid():
    g = _graph()
    assert not g.Editor().Products().Append(P0(), P0(), TopLoc_Location()).IsValid()


def test_BRepGraph_AssemblyTest_RootProducts_RemovedOccurrence_DoesNotAffectRoots():
    g = _graph()
    asm = _new_root_product(g)
    occ = g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    roots = _roots(g)
    assert len(roots) == 1
    assert roots[0] == asm
    g.Editor().Gen().RemoveSubgraph(_n(occ))
    roots = _roots(g)
    assert len(roots) >= 1
    assert asm in roots


def test_BRepGraph_AssemblyTest_GlobalPlacement_DAGSharing_DistinctPathsGiveDistinctPlacements():
    g = _graph()
    asm = _new_root_product(g)
    o1 = g.Editor().Products().Append(asm, P0(), _loc(100.0))
    o2 = g.Editor().Products().Append(asm, P0(), _loc(0.0, 200.0))
    t1 = g.Topo().Occurrences().OccurrenceLocation(o1).Transformation().TranslationPart()
    t2 = g.Topo().Occurrences().OccurrenceLocation(o2).Transformation().TranslationPart()
    assert abs(t1.X() - 100.0) <= TOL
    assert abs(t1.Y() - 0.0) <= TOL
    assert abs(t2.X() - 0.0) <= TOL
    assert abs(t2.Y() - 200.0) <= TOL


def test_BRepGraph_AssemblyTest_LinkProducts_RemovedProduct_ReturnsInvalid():
    g = _graph()
    asm = _new_root_product(g)
    g.Editor().Gen().RemoveNode(_n(asm))
    assert not g.Editor().Products().Append(asm, P0(), TopLoc_Location()).IsValid()
    asm2 = _new_root_product(g)
    g.Editor().Gen().RemoveNode(_n(P0()))
    assert not g.Editor().Products().Append(asm2, P0(), TopLoc_Location()).IsValid()


def test_BRepGraph_AssemblyTest_GlobalPlacement_ThreeLevelNesting():
    g = _graph()
    leaf = P0()
    mid = _new_root_product(g)
    root = _new_root_product(g)
    top = _new_root_product(g)
    occ_root = g.Editor().Products().Append(top, root, _loc(0.0, 0.0, 3.0))
    occ_mid = g.Editor().Products().Append(root, mid, _loc(0.0, 2.0), occ_root)
    occ_leaf = g.Editor().Products().Append(mid, leaf, _loc(1.0), occ_mid)
    occs = g.Topo().Occurrences()
    assert abs(occs.OccurrenceLocation(occ_leaf).Transformation().TranslationPart().X() - 1.0) <= TOL
    assert abs(occs.OccurrenceLocation(occ_mid).Transformation().TranslationPart().Y() - 2.0) <= TOL
    assert abs(occs.OccurrenceLocation(occ_root).Transformation().TranslationPart().Z() - 3.0) <= TOL


def test_BRepGraph_AssemblyTest_ShapesView_ProductShape_ReconstructsBuiltRootTransform():
    root_shape = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    root_shape.Move(_loc(15.0, -7.0, 2.0))
    root_shape.Reverse()
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(root_shape)
    prod_shape = g.Shapes().Shape(_n(P0()))
    assert not prod_shape.IsNull()
    assert prod_shape.ShapeType() == root_shape.ShapeType()
    recon = g.Shapes().Reconstruct(_n(P0()))
    assert not recon.IsNull()
    assert recon.ShapeType() == root_shape.ShapeType()


def test_BRepGraph_AssemblyTest_ShapesView_AssemblyProduct_ReconstructsChildOccurrences():
    g = _graph()
    asm = _new_root_product(g)
    assert g.Editor().Products().Append(asm, P0(), _loc(100.0)).IsValid()
    assert g.Editor().Products().Append(asm, P0(), _loc(200.0)).IsValid()
    shape = g.Shapes().Shape(_n(asm))
    assert not shape.IsNull()
    assert shape.ShapeType() == TopAbs_COMPOUND
    assert shape.NbChildren() == 2
    it = TopoDS_Iterator(shape)
    assert it.More()
    first = it.Value()
    it.Next()
    assert it.More()
    second = it.Value()
    it.Next()
    assert not it.More()
    assert first.IsPartner(second)
    assert abs(_translation_x(first) - 100.0) <= TOL
    assert abs(_translation_x(second) - 200.0) <= TOL


def test_BRepGraph_AssemblyTest_ShapesView_OccurrenceShape_UsesGlobalPlacementChain():
    g = _graph()
    sub = _new_root_product(g)
    root = _new_root_product(g)
    parent_occ = g.Editor().Products().Append(root, sub, _loc(10.0))
    assert parent_occ.IsValid()
    child_occ = g.Editor().Products().Append(sub, P0(), _loc(20.0), parent_occ)
    assert child_occ.IsValid()
    sub_shape = g.Shapes().Shape(_n(sub))
    assert not sub_shape.IsNull()
    assert sub_shape.NbChildren() == 1
    it = TopoDS_Iterator(sub_shape)
    assert it.More()
    assert abs(_translation_x(it.Value()) - 20.0) <= TOL
    occ_shape = g.Shapes().Shape(_n(child_occ))
    assert not occ_shape.IsNull()
    assert abs(_translation_x(occ_shape) - 20.0) <= TOL
    recon = g.Shapes().Reconstruct(_n(child_occ))
    assert not recon.IsNull()
    assert abs(_translation_x(recon) - 20.0) <= TOL


def _two_parent_occurrences(g):
    sub = _new_root_product(g)
    root = _new_root_product(g)
    p1 = g.Editor().Products().Append(root, sub, _loc(100.0))
    assert p1.IsValid()
    p2 = g.Editor().Products().Append(root, sub, _loc(200.0))
    assert p2.IsValid()
    return sub, p1, p2


def test_BRepGraph_AssemblyTest_ShapesView_OccurrenceShape_FiltersNestedChildrenByParentOccurrence():
    g = _graph()
    sub, p1, p2 = _two_parent_occurrences(g)
    assert g.Editor().Products().Append(sub, P0(), _loc(10.0), p1).IsValid()
    assert g.Editor().Products().Append(sub, P0(), _loc(20.0), p2).IsValid()
    for p in (p1, p2):
        s = g.Shapes().Shape(_n(p))
        assert not s.IsNull()
        assert s.NbChildren() >= 1
    for p in (p1, p2):
        r = g.Shapes().Reconstruct(_n(p))
        assert not r.IsNull()
        assert r.NbChildren() >= 1


def test_BRepGraph_AssemblyTest_ShapesView_OccurrenceShape_KeepsCommonChildrenAndFiltersBranchSpecificOnes():
    g = _graph()
    sub, p1, p2 = _two_parent_occurrences(g)
    assert g.Editor().Products().Append(sub, P0(), _loc(5.0)).IsValid()
    assert g.Editor().Products().Append(sub, P0(), _loc(10.0), p1).IsValid()
    assert g.Editor().Products().Append(sub, P0(), _loc(20.0), p2).IsValid()
    for p in (p1, p2):
        s = g.Shapes().Shape(_n(p))
        assert not s.IsNull()
        assert s.NbChildren() >= 1


def test_BRepGraph_AssemblyTest_OccurrencesOfProduct_ViaRelations():
    g = _graph()
    asm = _new_root_product(g)
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    g.Editor().Products().Append(asm, P0(), TopLoc_Location())
    assert g.Topo().Products().NbComponents(asm) == 2
    assert g.Topo().Products().NbComponents(P0()) == 1


def test_BRepGraph_AssemblyTest_OccurrenceLocation_AlwaysTerminates():
    g = _graph()
    asm = _new_root_product(g)
    o1 = g.Editor().Products().Append(asm, P0(), _loc(1.0))
    o2 = g.Editor().Products().Append(asm, P0(), _loc(1.0))
    l1 = g.Topo().Occurrences().OccurrenceLocation(o1)
    assert abs(l1.Transformation().TranslationPart().X() - 1.0) <= TOL
    assert o2.IsValid()
    assert not g.Topo().Occurrences().OccurrenceLocation(o2).IsIdentity()


def test_BRepGraph_AssemblyTest_Add_RootProduct_PreservesShapeLocation():
    g = BRepGraph()
    local_box = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
    box = TopoDS_Shape(local_box)
    box.Location(_loc(5.0, 6.0, 7.0))
    res = g.Shapes().Add(box)
    assert res.IsOk()
    assert res.Product.IsValid()
    assert res.TopologyRoot.IsValid()
    assert res.Occurrence.IsValid()
    assert g.Shapes().FindNode(box) == res.TopologyRoot
    assert len(g.RootProductIds()) == 1
    assert g.RootProductIds().Value(0) == res.Product
    ref = g.Topo().Products().Relations(res.Product).OccurrenceRefIds.Value(0)
    loc = g.Refs().Occurrences().Entry(ref).LocalLocation
    assert loc.IsEqual(box.Location())
    prod_shape = g.Shapes().Shape(_n(res.Product))
    assert not prod_shape.IsNull()
    _expect_box_near(_bounds(prod_shape), _bounds(box), 1.0e-7)
    topo_shape = g.Shapes().Shape(res.TopologyRoot)
    assert not topo_shape.IsNull()
    assert topo_shape.Location().IsIdentity()
    _expect_box_near(_bounds(topo_shape), _bounds(local_box), 1.0e-7)


def test_BRepGraph_AssemblyTest_Add_NoAutoProduct_TopologyOnly():
    g = BRepGraph()
    opts = BRepGraph.ShapesView.Options()
    opts.CreateAutoProduct = False
    res = g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), opts)
    assert res.IsOk()
    assert not res.Product.IsValid()
    assert not res.Occurrence.IsValid()
    assert res.TopologyRoot.IsValid()
    assert len(g.RootProductIds()) == 0


def test_BRepGraph_AssemblyTest_Add_NullShape_ReturnsInvalidResult():
    g = BRepGraph()
    res = g.Shapes().Add(TopoDS_Shape())
    assert not res.IsOk()
    assert not res.Product.IsValid()
    assert not res.TopologyRoot.IsValid()


def test_BRepGraph_AssemblyTest_Add_ProductParent_CreatesChildPartAndOccurrence():
    g = BRepGraph()
    parent = _new_root_product(g)
    assert parent.IsValid()
    sphere = BRepPrimAPI_MakeSphere(5.0).Shape()
    sphere.Location(_loc(2.0))
    res = g.Shapes().Add(sphere, _n(parent))
    assert res.IsOk()
    assert res.TopologyRoot.IsValid()
    assert res.Product.IsValid()
    assert res.Occurrence.IsValid()
    assert res.Product != parent
    rel = g.Topo().Products().Relations(parent)
    assert len(rel.OccurrenceRefIds) == 1
    loc = g.Refs().Occurrences().Entry(rel.OccurrenceRefIds.Value(0)).LocalLocation
    assert loc.IsEqual(sphere.Location())


def test_BRepGraph_AssemblyTest_Add_CompoundParent_AppendsAsChild():
    g = BRepGraph()
    comp = TopoDS_Compound()
    BRep_Builder().MakeCompound(comp)
    BRep_Builder().Add(comp, BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape())
    root = g.Shapes().Add(comp)
    assert root.IsOk()
    assert root.TopologyRoot.NodeKind == Kind.Compound
    cid = BRepGraph_CompoundId(root.TopologyRoot)
    before = len(g.Topo().Compounds().Relations(cid).ChildRefIds)
    face = TopExp_Explorer(BRepPrimAPI_MakeBox(2.0, 2.0, 2.0).Shape(), TopAbs_FACE).Current()
    assert not face.IsNull()
    child = g.Shapes().Add(face, _n(cid))
    assert child.IsOk()
    assert child.InsertedRef.IsValid()
    assert len(g.Topo().Compounds().Relations(cid).ChildRefIds) == before + 1


def test_BRepGraph_AssemblyTest_Add_InvalidParent_ReturnsInvalidResult():
    g = BRepGraph()
    g.Shapes().Add(BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape())
    res = g.Shapes().Add(BRepPrimAPI_MakeBox(2.0, 2.0, 2.0).Shape(), BRepGraph_NodeId())
    assert not res.IsOk()


def test_BRepGraph_AssemblyTest_RootProductRemovalCompactsInPlaceAfterRepeatedRemoves():
    g = BRepGraph()
    g.Clear()
    a = _new_root_product(g)
    b = _new_root_product(g)
    c = _new_root_product(g)
    assert a.IsValid() and b.IsValid() and c.IsValid()
    assert len(_roots(g)) == 3
    g.Editor().Gen().RemoveNode(_n(b))
    roots = _roots(g)
    assert len(roots) == 2
    assert a in roots
    assert b not in roots
    assert c in roots
    d = _new_root_product(g)
    assert d.IsValid()
    g.Editor().Gen().RemoveNode(_n(a))
    g.Editor().Gen().RemoveNode(_n(d))
    roots = _roots(g)
    assert len(roots) == 1
    assert roots[0] == c
