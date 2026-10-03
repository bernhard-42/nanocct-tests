# Translated from OCCT src/FoundationClasses/TKMath/GTests/MathUtils_Functor_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct import MathUtils
from nanocct.math import math_Matrix, math_Vector

THE_TOLERANCE = 1e-10
THE_PI = math.pi


def vec(*coeffs):
    v = math_Vector(1, len(coeffs))
    for i, c in enumerate(coeffs):
        v[i + 1] = c
    return v


def near(a, b, tol=THE_TOLERANCE):
    return abs(a - b) <= tol


# Scalar functor tests


def test_MathUtils_Functor_Scalar_Polynomial_Value():
    poly = MathUtils.Polynomial(vec(1.0, 2.0, 3.0))
    ok, val = poly.Value(0.0)
    assert ok is True and near(val, 1.0)
    ok, val = poly.Value(1.0)
    assert ok is True and near(val, 6.0)
    ok, val = poly.Value(2.0)
    assert ok is True and near(val, 17.0)


def test_MathUtils_Functor_Scalar_Polynomial_Values():
    poly = MathUtils.Polynomial(vec(-2.0, 0.0, 1.0))
    ok, val, der = poly.Values(3.0)
    assert ok is True
    assert near(val, 7.0)
    assert near(der, 6.0)


def test_MathUtils_Functor_Scalar_Rational_Value():
    rat = MathUtils.Rational(vec(1.0, 1.0), vec(1.0, 0.0, 1.0))
    ok, val = rat.Value(0.0)
    assert ok is True and near(val, 1.0)
    ok, val = rat.Value(1.0)
    assert ok is True and near(val, 1.0)
    ok, val = rat.Value(2.0)
    assert ok is True and near(val, 0.6)


def test_MathUtils_Functor_Scalar_Rational_DivisionByZero():
    rat = MathUtils.Rational(vec(0.0, 1.0), vec(-1.0, 1.0))
    ok, _ = rat.Value(1.0)
    assert ok is False


def test_MathUtils_Functor_Scalar_Constant_Value():
    const = MathUtils.Constant(42.0)
    ok, val = const.Value(123.456)
    assert ok is True and near(val, 42.0)
    ok, val, der = const.Values(789.0)
    assert ok is True
    assert near(val, 42.0)
    assert near(der, 0.0)


def test_MathUtils_Functor_Scalar_Linear_Value():
    lin = MathUtils.Linear(2.0, 3.0)
    ok, val = lin.Value(5.0)
    assert ok is True and near(val, 13.0)
    ok, val, der = lin.Values(5.0)
    assert ok is True
    assert near(val, 13.0)
    assert near(der, 2.0)


def test_MathUtils_Functor_Scalar_Sine_Value():
    sine = MathUtils.Sine(1.0, 1.0, 0.0, 0.0)
    ok, val = sine.Value(0.0)
    assert ok is True and near(val, 0.0)
    ok, val = sine.Value(THE_PI / 2.0)
    assert ok is True and near(val, 1.0)


def test_MathUtils_Functor_Scalar_Sine_Values():
    sine = MathUtils.Sine(2.0, 1.0, 0.0, 0.0)
    ok, val, der = sine.Values(0.0)
    assert ok is True
    assert near(val, 0.0)
    assert near(der, 2.0)


def test_MathUtils_Functor_Scalar_Cosine_Value():
    cosine = MathUtils.Cosine(1.0, 1.0, 0.0, 0.0)
    ok, val = cosine.Value(0.0)
    assert ok is True and near(val, 1.0)
    ok, val = cosine.Value(THE_PI)
    assert ok is True and near(val, -1.0)


def test_MathUtils_Functor_Scalar_Exponential_Value():
    exp = MathUtils.Exponential(1.0, 1.0, 0.0)
    ok, val = exp.Value(0.0)
    assert ok is True and near(val, 1.0)
    ok, val = exp.Value(1.0)
    assert ok is True and near(val, math.exp(1.0))


def test_MathUtils_Functor_Scalar_Power_Value():
    power = MathUtils.Power(2.0, 1.0, 0.0)
    ok, val = power.Value(3.0)
    assert ok is True and near(val, 9.0)


def test_MathUtils_Functor_Scalar_Power_NonInteger():
    power = MathUtils.Power(0.5, 1.0, 0.0)
    ok, val = power.Value(4.0)
    assert ok is True and near(val, 2.0)
    ok, _ = power.Value(-4.0)
    assert ok is False


def test_MathUtils_Functor_Scalar_Gaussian_Value():
    gauss = MathUtils.Gaussian(1.0, 0.0, 1.0)
    ok, val = gauss.Value(0.0)
    assert ok is True and near(val, 1.0)
    ok, val = gauss.Value(1.0)
    assert ok is True and near(val, math.exp(-0.5))


# Vector functor tests


def test_MathUtils_Functor_Vector_Rosenbrock_Value():
    ok, val = MathUtils.Rosenbrock().Value(vec(1.0, 1.0))
    assert ok is True and near(val, 0.0)


def test_MathUtils_Functor_Vector_Rosenbrock_AwayFromMinimum():
    ok, val = MathUtils.Rosenbrock().Value(vec(0.0, 0.0))
    assert ok is True and near(val, 1.0)


def test_MathUtils_Functor_Vector_Rosenbrock_Gradient():
    grad = math_Vector(1, 2)
    assert MathUtils.Rosenbrock().Gradient(vec(1.0, 1.0), grad) is True
    assert near(grad(1), 0.0)
    assert near(grad(2), 0.0)


def test_MathUtils_Functor_Vector_Sphere_Value():
    ok, val = MathUtils.Sphere().Value(vec(1.0, 2.0, 3.0))
    assert ok is True and near(val, 14.0)


def test_MathUtils_Functor_Vector_Sphere_Gradient():
    grad = math_Vector(1, 3)
    assert MathUtils.Sphere().Gradient(vec(1.0, 2.0, 3.0), grad) is True
    assert near(grad(1), 2.0)
    assert near(grad(2), 4.0)
    assert near(grad(3), 6.0)


def test_MathUtils_Functor_Vector_Booth_Value():
    ok, val = MathUtils.Booth().Value(vec(1.0, 3.0))
    assert ok is True and near(val, 0.0)


def test_MathUtils_Functor_Vector_Beale_Value():
    ok, val = MathUtils.Beale().Value(vec(3.0, 0.5))
    assert ok is True and near(val, 0.0)


def test_MathUtils_Functor_Vector_Himmelblau_Value():
    ok, val = MathUtils.Himmelblau().Value(vec(3.0, 2.0))
    assert ok is True and near(val, 0.0)


def test_MathUtils_Functor_Vector_Rastrigin_Value():
    ok, val = MathUtils.Rastrigin().Value(vec(0.0, 0.0))
    assert ok is True and near(val, 0.0)


def test_MathUtils_Functor_Vector_Ackley_Value():
    ok, val = MathUtils.Ackley().Value(vec(0.0, 0.0))
    assert ok is True and near(val, 0.0)


def _identity2():
    a = math_Matrix(1, 2, 1, 2, 0.0)
    a[1, 1] = 1.0
    a[2, 2] = 1.0
    return a


def test_MathUtils_Functor_Vector_QuadraticForm_Value():
    quad = MathUtils.QuadraticForm(_identity2(), math_Vector(1, 2, 0.0), 0.0)
    ok, val = quad.Value(vec(3.0, 4.0))
    assert ok is True and near(val, 25.0)


def test_MathUtils_Functor_Vector_QuadraticForm_Gradient():
    quad = MathUtils.QuadraticForm(_identity2(), math_Vector(1, 2, 0.0), 0.0)
    grad = math_Vector(1, 2)
    assert quad.Gradient(vec(3.0, 4.0), grad) is True
    assert near(grad(1), 6.0)
    assert near(grad(2), 8.0)


def test_MathUtils_Functor_Vector_LinearResidual_Value():
    res = MathUtils.LinearResidual(_identity2(), vec(3.0, 4.0))
    ok, val = res.Value(vec(3.0, 4.0))
    assert ok is True and near(val, 0.0)


def test_MathUtils_Functor_Vector_LinearResidual_NonZero():
    res = MathUtils.LinearResidual(_identity2(), vec(3.0, 4.0))
    ok, val = res.Value(vec(0.0, 0.0))
    assert ok is True and near(val, 25.0)
