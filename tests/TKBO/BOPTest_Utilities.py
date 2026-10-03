# Translated from OCCT src/ModelingAlgorithms/TKBO/GTests/BOPTest_Utilities.pxx (LGPL-2.1 with the OCCT exception)
# Helpers shared by the TKBO test files: BOPTest_Utilities (as module functions) plus the fixture methods
# of BRepAlgoAPI_TestBase / BOPAlgo_TestBase (PerformCut/Fuse/Common, PerformDirectBOP/TwoStepBOP, ValidateResult).
import enum
import math

from nanocct import TopoDS
from nanocct.BOPAlgo import BOPAlgo_BOP, BOPAlgo_PaveFiller
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_NurbsConvert,
    BRepBuilderAPI_Transform,
)
from nanocct.BRepFilletAPI import BRepFilletAPI_MakeFillet
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakePrism,
    BRepPrimAPI_MakeRevol,
    BRepPrimAPI_MakeSphere,
)
from nanocct.ChFi3d import ChFi3d_Rational
from nanocct.ElSLib import ElSLib
from nanocct.GeomAbs import GeomAbs_C1
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Ax3, gp_Circ, gp_Dir, gp_Pln, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec, gp_Vec2d
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_List
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Edge, TopoDS_Face, TopoDS_Shape

DEFAULT_TOLERANCE = 1.0e-6
DEFAULT_FUZZY_VALUE = 1.0e-8
myTolerance = DEFAULT_TOLERANCE


class ProfileCmd(enum.Enum):
    O = 0
    P = 1
    F = 2
    X = 3
    Y = 4
    L = 5
    XX = 6
    YY = 7
    T = 8
    TT = 9
    R = 10
    RR = 11
    D = 12
    C = 13
    W = 14
    WW = 15


class ProfileOperation:
    def __init__(self, cmd, *params):
        self.cmd = cmd
        if len(params) == 1 and isinstance(params[0], (list, tuple)):
            self.params = [float(p) for p in params[0]]
        else:
            self.params = [float(p) for p in params]


def GetSurfaceArea(shape):
    if shape.IsNull():
        return 0.0
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


def GetVolume(shape):
    if shape.IsNull():
        return 0.0
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def IsEmpty(shape, tolerance=DEFAULT_TOLERANCE):
    return GetSurfaceArea(shape) <= tolerance


def CreateUnitBox():
    return BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape()


def CreateBox(corner, x, y, z):
    return BRepPrimAPI_MakeBox(corner, float(x), float(y), float(z)).Shape()


def CreateUnitSphere():
    return BRepPrimAPI_MakeSphere(1.0).Shape()


def CreateSphere(center, radius):
    return BRepPrimAPI_MakeSphere(center, float(radius)).Shape()


def CreateCylinder(radius, height):
    return BRepPrimAPI_MakeCylinder(float(radius), float(height)).Shape()


def CreateCone(r1, r2, height):
    return BRepPrimAPI_MakeCone(float(r1), float(r2), float(height)).Shape()


def ConvertToNurbs(shape):
    conv = BRepBuilderAPI_NurbsConvert(shape)
    if not conv.IsDone():
        return TopoDS_Shape()
    return conv.Shape()


def CreatePolygonFace(p1, p2, p3, p4):
    poly = BRepBuilderAPI_MakePolygon()
    poly.Add(p1)
    poly.Add(p2)
    poly.Add(p3)
    poly.Add(p4)
    poly.Close()
    if not poly.IsDone():
        return TopoDS_Shape()
    return BRepBuilderAPI_MakeFace(poly.Wire()).Shape()


def _transform(shape, trsf):
    return BRepBuilderAPI_Transform(shape, trsf).Shape()


def RotateShape(shape, axis, angle):
    trsf = gp_Trsf()
    trsf.SetRotation(axis, float(angle))
    return _transform(shape, trsf)


def TranslateShape(shape, vector):
    trsf = gp_Trsf()
    trsf.SetTranslation(vector)
    return _transform(shape, trsf)


def CreateVertex(pnt):
    return BRepBuilderAPI_MakeVertex(pnt).Vertex()


def CreateEdge(p1, p2):
    return BRepBuilderAPI_MakeEdge(p1, p2).Edge()


def CreatePolygonWire(points, close=True):
    poly = BRepBuilderAPI_MakePolygon()
    for p in points:
        poly.Add(p)
    if close:
        poly.Close()
    return poly.Wire()


def CreateProfile(plane, operations):
    mk_wire = BRepBuilderAPI_MakeWire()
    cur = gp_Pnt2d(0, 0)
    cur_dir = gp_Vec2d(1, 0)
    first_set = False
    first = gp_Pnt2d(0, 0)
    working = gp_Pln(plane.Position())

    def add_line(a, b):
        p1 = ElSLib.Value_s(a.X(), a.Y(), working)
        p2 = ElSLib.Value_s(b.X(), b.Y(), working)
        mk_wire.Add(BRepBuilderAPI_MakeEdge(p1, p2).Edge())

    for op in operations:
        prm = op.params
        if op.cmd == ProfileCmd.O:
            if len(prm) >= 3:
                origin = gp_Pnt(prm[0], prm[1], prm[2])
                ax3 = gp_Ax3(origin, working.Axis().Direction(), working.XAxis().Direction())
                working = gp_Pln(ax3)
                if not first_set:
                    cur = gp_Pnt2d(0.0, 0.0)
                    first = gp_Pnt2d(cur.X(), cur.Y())
                    first_set = True
        elif op.cmd == ProfileCmd.P:
            if len(prm) >= 6:
                normal = gp_Dir(gp_Vec(prm[0], prm[1], prm[2]))
                xdir = gp_Dir(gp_Vec(prm[3], prm[4], prm[5]))
                working = gp_Pln(gp_Ax3(working.Location(), normal, xdir))
        elif op.cmd == ProfileCmd.F:
            if len(prm) >= 2:
                cur = gp_Pnt2d(prm[0], prm[1])
                first = gp_Pnt2d(cur.X(), cur.Y())
                first_set = True
        elif op.cmd == ProfileCmd.X:
            if len(prm) > 0:
                if not first_set:
                    cur = gp_Pnt2d(0.0, 0.0)
                    first = gp_Pnt2d(0.0, 0.0)
                    first_set = True
                new = gp_Pnt2d(cur.X() + prm[0], cur.Y())
                add_line(cur, new)
                cur = new
                cur_dir = gp_Vec2d(1 if prm[0] > 0 else -1, 0)
        elif op.cmd == ProfileCmd.Y:
            if len(prm) > 0:
                if not first_set:
                    cur = gp_Pnt2d(0.0, 0.0)
                    first = gp_Pnt2d(0.0, 0.0)
                    first_set = True
                new = gp_Pnt2d(cur.X(), cur.Y() + prm[0])
                add_line(cur, new)
                cur = new
                cur_dir = gp_Vec2d(0, 1 if prm[0] > 0 else -1)
        elif op.cmd == ProfileCmd.C:
            if len(prm) >= 2:
                radius = abs(prm[0])
                angle_deg = prm[1]
                angle_rad = angle_deg * math.pi / 180.0
                if abs(angle_deg) >= 360.0:
                    center2d = cur if first_set else gp_Pnt2d(0, 0)
                    center3d = ElSLib.Value_s(center2d.X(), center2d.Y(), working)
                    circ = gp_Circ(gp_Ax2(center3d, working.Axis().Direction()), radius)
                    mk_wire.Add(BRepBuilderAPI_MakeEdge(circ).Edge())
                    cur = gp_Pnt2d(center2d.X() + radius, center2d.Y())
                    cur_dir = gp_Vec2d(0, 1)
                    first_set = True
                else:
                    if not first_set:
                        cur = gp_Pnt2d(0.0, 0.0)
                        cur_dir = gp_Vec2d(1, 0)
                        first = gp_Pnt2d(0.0, 0.0)
                        first_set = True
                    normal = gp_Vec2d(-cur_dir.Y(), cur_dir.X())
                    center = cur.Translated(normal * radius)
                    start_angle = math.atan2(cur.Y() - center.Y(), cur.X() - center.X())
                    end_angle = start_angle + angle_rad
                    end = gp_Pnt2d(center.X() + radius * math.cos(end_angle),
                                   center.Y() + radius * math.sin(end_angle))
                    p1 = ElSLib.Value_s(cur.X(), cur.Y(), working)
                    p2 = ElSLib.Value_s(end.X(), end.Y(), working)
                    c3 = ElSLib.Value_s(center.X(), center.Y(), working)
                    circ = gp_Circ(gp_Ax2(c3, working.Axis().Direction()), radius)
                    mk_wire.Add(BRepBuilderAPI_MakeEdge(circ, p1, p2).Edge())
                    cur = end
                    cur_dir = gp_Vec2d(math.cos(end_angle + math.pi / 2), math.sin(end_angle + math.pi / 2))
        elif op.cmd == ProfileCmd.D:
            if len(prm) >= 2:
                cur_dir = gp_Vec2d(prm[0], prm[1])
                cur_dir.Normalize()
        # W and all other commands: nothing to do (as in the C++ helper)

    if first_set and not cur.IsEqual(first, Precision.Confusion_s()):
        add_line(cur, first)

    assert mk_wire.IsDone(), "Profile wire creation failed"
    wire = mk_wire.Wire()
    mk_face = BRepBuilderAPI_MakeFace(wire)
    assert mk_face.IsDone(), "Profile face creation failed"
    return mk_face.Face()


def CreateProfileFromOperations(operations):
    return CreateProfile(gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z)), operations)


def CreateRectangularProfile(corner, x, y):
    pts = [
        corner,
        gp_Pnt(corner.X() + x, corner.Y(), corner.Z()),
        gp_Pnt(corner.X() + x, corner.Y() + y, corner.Z()),
        gp_Pnt(corner.X(), corner.Y() + y, corner.Z()),
    ]
    return CreatePolygonWire(pts, True)


def CreateFaceFromWire(wire):
    mk = BRepBuilderAPI_MakeFace(wire)
    if not mk.IsDone():
        return TopoDS_Shape()
    return mk.Shape()


def CreatePrism(profile, direction):
    mk = BRepPrimAPI_MakePrism(profile, direction)
    if not mk.IsDone():
        return TopoDS_Shape()
    return mk.Shape()


def CreateRectangularPrism(corner, x, y, z):
    wire = CreateRectangularProfile(corner, x, y)
    face = CreateFaceFromWire(wire)
    return CreatePrism(face, gp_Vec(0, 0, z))


def CreateRevolution(profile, axis, angle):
    mk = BRepPrimAPI_MakeRevol(profile, axis, float(angle))
    assert mk.IsDone(), "Revolution operation failed"
    return mk.Shape()


def GetFaceByIndex(shape, index):
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    i = 1
    while exp.More():
        if i == index:
            return TopoDS.Face(exp.Current())
        i += 1
        exp.Next()
    return TopoDS_Face()


def _rotate_about(shape, axis_dir, angle_deg, origin=None):
    if origin is None:
        origin = gp_Pnt(0, 0, 0)
    trsf = gp_Trsf()
    trsf.SetRotation(gp_Ax1(origin, gp_Dir(axis_dir)), angle_deg * math.pi / 180.0)
    return _transform(shape, trsf)


def RotateZ(shape, angle_deg):
    return _rotate_about(shape, gp_Dir.D.Z, angle_deg)


def RotateY(shape, angle_deg):
    return _rotate_about(shape, gp_Dir.D.Y, angle_deg)


def RotateX(shape, angle_deg):
    return _rotate_about(shape, gp_Dir.D.X, angle_deg)


def RotateStandard(shape):
    return RotateY(RotateZ(shape, -90.0), -45.0)


def Translate(shape, dx, dy, dz):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(dx, dy, dz))
    return _transform(shape, trsf)


def RotateY90(shape):
    return _rotate_about(shape, gp_Dir.D.Y, 90.0, gp_Pnt(0, 0, 1))


def CreateBlend(shape, edge_index, radius):
    exp = TopExp_Explorer(shape, TopAbs_EDGE)
    i = 1
    target = TopoDS_Edge()
    while exp.More():
        if i == edge_index:
            target = TopoDS.Edge(exp.Current())
            break
        i += 1
        exp.Next()
    if target.IsNull():
        return shape
    fillet = BRepFilletAPI_MakeFillet(shape, ChFi3d_Rational)
    fillet.SetParams(1e-2, 1.0e-4, 1.0e-5, 1.0e-4, 1.0e-5, 1.0e-3)
    fillet.SetContinuity(GeomAbs_C1, 1.0e-2)
    fillet.Add(float(radius), target)
    fillet.Build()
    if not fillet.IsDone():
        return TopoDS_Shape()
    return fillet.Shape()


def CreateCylinderOnPlane(plane, radius, height):
    ax2 = plane.Position().Ax2()
    mk = BRepPrimAPI_MakeCylinder(ax2, float(radius), float(height))
    mk.Build()
    if not mk.IsDone():
        return TopoDS_Shape()
    return mk.Shape()


# ---- BRepAlgoAPI_TestBase fixture methods ----

def PerformCut(obj, tool):
    op = BRepAlgoAPI_Cut(obj, tool)
    assert op.IsDone(), "BRepAlgoAPI_Cut operation failed"
    return op.Shape()


def PerformFuse(s1, s2):
    op = BRepAlgoAPI_Fuse(s1, s2)
    assert op.IsDone(), "BRepAlgoAPI_Fuse operation failed"
    return op.Shape()


def PerformCommon(s1, s2):
    op = BRepAlgoAPI_Common(s1, s2)
    assert op.IsDone(), "BRepAlgoAPI_Common operation failed"
    return op.Shape()


def ValidateResult(result, expected_area=-1.0, expected_volume=-1.0, expected_empty=False):
    if expected_empty:
        assert IsEmpty(result, myTolerance), "Result should be empty"
        return
    assert not result.IsNull(), "Result shape should not be null"
    if expected_area >= 0.0:
        area = GetSurfaceArea(result)
        # OCCT's own tolerance for the surface area is 5000.0
        assert abs(area - expected_area) <= 5000.0, f"Surface area mismatch: {area} vs {expected_area}"
    if expected_volume >= 0.0:
        vol = GetVolume(result)
        assert abs(vol - expected_volume) <= myTolerance, f"Volume mismatch: {vol} vs {expected_volume}"


# ---- BOPAlgo_TestBase fixture methods ----

def PerformDirectBOP(s1, s2, op):
    bop = BOPAlgo_BOP()
    bop.AddArgument(s1)
    bop.AddTool(s2)
    bop.SetOperation(op)
    bop.SetFuzzyValue(DEFAULT_FUZZY_VALUE)
    bop.SetRunParallel(False)
    bop.SetNonDestructive(False)
    bop.Perform()
    assert not bop.HasErrors(), "Direct BOP operation failed"
    return bop.Shape()


def PreparePaveFiller(s1, s2):
    args = NCollection_List[TopoDS_Shape]()
    args.Append(s1)
    args.Append(s2)
    filler = BOPAlgo_PaveFiller()
    filler.SetArguments(args)
    filler.SetFuzzyValue(DEFAULT_FUZZY_VALUE)
    filler.SetRunParallel(False)
    filler.SetNonDestructive(False)
    filler.Perform()
    assert not filler.HasErrors(), "PaveFiller preparation failed"
    return filler


def PerformBOPWithPaveFiller(filler, op):
    bop = BOPAlgo_BOP()
    args = filler.Arguments()
    assert args.Extent() == 2, "Wrong number of arguments"
    bop.AddArgument(args.First())
    bop.AddTool(args.Last())
    bop.SetOperation(op)
    bop.SetRunParallel(False)
    bop.PerformWithFiller(filler)
    assert not bop.HasErrors(), "BOP operation with PaveFiller failed"
    return bop.Shape()


def PerformTwoStepBOP(s1, s2, op):
    filler = PreparePaveFiller(s1, s2)
    return PerformBOPWithPaveFiller(filler, op)
