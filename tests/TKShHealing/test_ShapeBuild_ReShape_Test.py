# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeBuild_ReShape_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.NCollection import NCollection_IndexedMap
from nanocct.ShapeBuild import ShapeBuild_ReShape
from nanocct.ShapeFix import ShapeFix_Shape
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Iterator, TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher


def _count_sub_shapes(shape, kind):
    m = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(shape, kind, m)
    return m.Extent()


def _vertex(x, y, z):
    return BRepBuilderAPI_MakeVertex(gp_Pnt(x, y, z)).Vertex()


def test_ShapeBuild_ReShapeTest_Apply_PerformsVertexReplacementOnCompound():
    v1 = _vertex(0, 0, 0)
    v2 = _vertex(1, 0, 0)
    v2_repl = _vertex(1.5, 0, 0)

    parent = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(parent)
    builder.Add(parent, v1)
    builder.Add(parent, v2)

    reshape = ShapeBuild_ReShape()
    reshape.Replace(v2, v2_repl)

    result = reshape.Apply(parent)
    assert not result.IsNull()

    found_replacement = False
    it = TopoDS_Iterator(result)
    while it.More():
        if it.Value().TShape() == v2_repl.TShape():
            found_replacement = True
        assert not (it.Value().TShape() == v2.TShape())
        it.Next()
    assert found_replacement


def test_ShapeBuild_ReShapeTest_Apply_StructuralContainmentWithoutCrash():
    v1 = _vertex(0, 0, 0)
    v2 = _vertex(1, 0, 0)
    v3 = _vertex(2, 0, 0)
    edge = BRepBuilderAPI_MakeEdge(v1, v2).Edge()

    container = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(container)
    builder.Add(container, edge)
    builder.Add(container, v3)

    reshape = ShapeBuild_ReShape()
    reshape.Replace(edge, container)

    result = reshape.Apply(edge)
    assert not result.IsNull()


def test_ShapeFix_ShapeStabilityTest_RepeatedPerformDoesNotMultiplyEdges():
    maker = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0)
    box = maker.Shape()
    assert maker.IsDone()

    nb_edges = _count_sub_shapes(box, TopAbs_EDGE)
    nb_vertices = _count_sub_shapes(box, TopAbs_VERTEX)
    nb_faces = _count_sub_shapes(box, TopAbs_FACE)
    assert nb_edges == 12

    current = box
    for it in range(5):
        fixer = ShapeFix_Shape(current)
        fixer.Perform()
        current = fixer.Shape()
        assert not current.IsNull(), f"iteration {it}"
        assert _count_sub_shapes(current, TopAbs_FACE) == nb_faces, f"iteration {it}"
        assert _count_sub_shapes(current, TopAbs_EDGE) == nb_edges, f"iteration {it}"
        assert _count_sub_shapes(current, TopAbs_VERTEX) == nb_vertices, f"iteration {it}"


def test_ShapeBuild_ReShapeTest_Apply_DiamondSharedVertexInTwoCompounds():
    shared = _vertex(0, 0, 0)
    shared_new = _vertex(0.1, 0, 0)
    other1 = _vertex(1, 0, 0)
    other2 = _vertex(2, 0, 0)

    parent_a = TopoDS_Compound()
    parent_b = TopoDS_Compound()
    grand = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(parent_a)
    builder.Add(parent_a, shared)
    builder.Add(parent_a, other1)
    builder.MakeCompound(parent_b)
    builder.Add(parent_b, shared)
    builder.Add(parent_b, other2)
    builder.MakeCompound(grand)
    builder.Add(grand, parent_a)
    builder.Add(grand, parent_b)

    reshape = ShapeBuild_ReShape()
    reshape.Replace(shared, shared_new)

    result = reshape.Apply(grand)
    assert not result.IsNull()

    nb_repl = 0
    nb_orig = 0
    exp = TopExp_Explorer(result, TopAbs_VERTEX)
    while exp.More():
        if exp.Current().TShape() == shared_new.TShape():
            nb_repl += 1
        if exp.Current().TShape() == shared.TShape():
            nb_orig += 1
        exp.Next()
    assert nb_orig == 0, "Original vertex must be substituted everywhere"
    assert nb_repl == 2, "Replacement must appear in both parentA and parentB"
