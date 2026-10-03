# Translated from OCCT src/FoundationClasses/TKMath/GTests/gp_Quaternion_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import gp as G
from nanocct.gp import gp_Ax2, gp_Dir, gp_EulerSequence, gp_Mat, gp_Pnt, gp_Quaternion, gp_Trsf, gp_Vec, gp_XYZ
from nanocct.Precision import Precision

NAMES = [
    "Extrinsic_XYZ", "Extrinsic_XZY", "Extrinsic_YZX", "Extrinsic_YXZ", "Extrinsic_ZXY", "Extrinsic_ZYX",
    "Intrinsic_XYZ", "Intrinsic_XZY", "Intrinsic_YZX", "Intrinsic_YXZ", "Intrinsic_ZXY", "Intrinsic_ZYX",
    "Extrinsic_XYX", "Extrinsic_XZX", "Extrinsic_YZY", "Extrinsic_YXY", "Extrinsic_ZYZ", "Extrinsic_ZXZ",
    "Intrinsic_XYX", "Intrinsic_XZX", "Intrinsic_YZY", "Intrinsic_YXY", "Intrinsic_ZXZ", "Intrinsic_ZYZ",
]
FIRST = int(G.gp_Extrinsic_XYZ)
LAST = int(G.gp_Intrinsic_ZYZ)


def _quat():
    q = gp_Quaternion()
    q.Set(0.06766916507860499, 0.21848101129786085, 0.11994599260380681, 0.9660744746954637)
    return q


def test_gp_QuaternionTest_OCC25574_EulerAnglesConsistency():
    q = _quat()
    rinv = q.GetMatrix().Inverted()
    ident = gp_Mat()
    ident.SetIdentity()
    for i in range(FIRST, LAST + 1):
        seq = gp_EulerSequence(i)
        alpha, beta, gamma = q.GetEulerAngles(seq)
        q2 = gp_Quaternion()
        q2.SetEulerAngles(seq, alpha, beta, gamma)
        diff = q2.GetMatrix() * rinv - ident
        assert diff.Determinant() <= 1e-5, NAMES[i - FIRST]


def test_gp_QuaternionTest_OCC25574_EulerAxisRotationPreservesAxis():
    for i in range(FIRST, LAST + 1):
        for j in range(3):
            axis = ord(NAMES[i - FIRST][10 + j]) - ord("X")
            assert 0 <= axis <= 2
            angles = [0.0, 0.0, 0.0]
            angles[j] = 0.5 * math.pi
            q2 = gp_Quaternion()
            q2.SetEulerAngles(gp_EulerSequence(i), *angles)
            v = gp_XYZ(0.0, 0.0, 0.0)
            v.SetCoord(axis + 1, 1.0)
            t = gp_Trsf()
            t.SetRotation(q2)
            v2 = gp_XYZ(v.X(), v.Y(), v.Z())
            t.Transforms(v2)
            assert (v - v2).SquareModulus() <= Precision.SquareConfusion_s(), (NAMES[i - FIRST], j)


def test_gp_QuaternionTest_OCC25574_ExtrinsicIntrinsicCorrespondence():
    alpha, beta, gamma = 0.1517461713131, 1.5162198410141, 1.9313156236541
    pairs = [
        (G.gp_Extrinsic_XYZ, G.gp_Intrinsic_ZYX),
        (G.gp_Extrinsic_XZY, G.gp_Intrinsic_YZX),
        (G.gp_Extrinsic_YZX, G.gp_Intrinsic_XZY),
        (G.gp_Extrinsic_YXZ, G.gp_Intrinsic_ZXY),
        (G.gp_Extrinsic_ZXY, G.gp_Intrinsic_YXZ),
        (G.gp_Extrinsic_ZYX, G.gp_Intrinsic_XYZ),
    ]
    q = gp_Quaternion()
    for s1, s2 in pairs:
        q.SetEulerAngles(s1, alpha, beta, gamma)
        gamma2, beta2, alpha2 = q.GetEulerAngles(s2)
        assert abs(alpha - alpha2) <= 1e-5
        assert abs(beta - beta2) <= 1e-5
        assert abs(gamma - gamma2) <= 1e-5


def test_gp_QuaternionTest_OCC25574_YawPitchRollRoundTrip():
    world = gp_Ax2()
    a_alpha = 0.0
    a_beta = -35.0 / 180.0 * math.pi
    a_gamma = 90.0 / 180.0 * math.pi
    rot_z = gp_Quaternion(gp_Vec(world.Direction()), a_alpha)
    rot_y = rot_z.Multiply(gp_Vec(world.YDirection()))
    rot_x = rot_z.Multiply(gp_Vec(world.XDirection()))
    rot_yaw = gp_Quaternion(rot_y, a_beta)
    rot_z2 = rot_yaw.Multiply(gp_Vec(world.Direction()))
    rot_x2 = rot_yaw.Multiply(rot_x)
    rot_roll = gp_Quaternion(rot_x2, a_gamma)
    rot_z3 = rot_roll.Multiply(rot_z2)
    result = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(rot_z3), gp_Dir(rot_x2))
    t = gp_Trsf()
    t.SetDisplacement(gp_Ax2(), result)
    ca, cb, cg = t.GetRotation().GetEulerAngles(G.gp_YawPitchRoll)
    assert abs(a_alpha - ca) <= 1e-5
    assert abs(a_beta - cb) <= 1e-5
    assert abs(a_gamma - cg) <= 1e-5


def test_gp_QuaternionTest_OCC25574_IntrinsicZYX_vs_ExtrinsicXYZ():
    q = _quat()
    a, b, g = q.GetEulerAngles(G.gp_Intrinsic_ZYX)
    a2, b2, g2 = q.GetEulerAngles(G.gp_Extrinsic_XYZ)
    assert abs(a - g2) <= 1e-5
    assert abs(b - b2) <= 1e-5
    assert abs(g - a2) <= 1e-5
