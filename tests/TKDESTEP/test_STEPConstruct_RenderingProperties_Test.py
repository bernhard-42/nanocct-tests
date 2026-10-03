# Translated from OCCT src/DataExchange/TKDESTEP/GTests/STEPConstruct_RenderingProperties_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.NCollection import NCollection_HArray1
from nanocct.Quantity import Quantity_Color, Quantity_ColorRGBA, Quantity_TOC_RGB
from nanocct.STEPConstruct import STEPConstruct_RenderingProperties, STEPConstruct_Styles
from nanocct.StepVisual import (
    StepVisual_RenderingPropertiesSelect,
    StepVisual_SurfaceStyleReflectanceAmbientDiffuseSpecular,
    StepVisual_SurfaceStyleRenderingWithProperties,
    StepVisual_SurfaceStyleTransparent,
    StepVisual_ssmDotShading,
    StepVisual_ssmNormalShading,
)
from nanocct.XCAFDoc import XCAFDoc_VisMaterialCommon

SURFACE_COLOR = (0.8, 0.5, 0.2)
TRANSPARENCY = 0.25
AMBIENT = 0.3
DIFFUSE = 1.0
SPECULAR = 0.8
SPECULAR_EXP = 45.0
SPECULAR_COLOR = (0.9, 0.9, 0.9)


def _color(rgb):
    return Quantity_Color(rgb[0], rgb[1], rgb[2], Quantity_TOC_RGB)


def _surface():
    return _color(SURFACE_COLOR)


def _specular():
    return _color(SPECULAR_COLOR)


def _colors_equal(c1, c2, tol=0.01):
    return (
        abs(c1.Red() - c2.Red()) <= tol
        and abs(c1.Green() - c2.Green()) <= tol
        and abs(c1.Blue() - c2.Blue()) <= tol
    )


def _create_step_rendering_properties():
    surface = STEPConstruct_Styles.EncodeColor_s(_surface())
    transp = StepVisual_SurfaceStyleTransparent()
    transp.Init(TRANSPARENCY)
    spec_color = STEPConstruct_Styles.EncodeColor_s(_specular())
    refl = StepVisual_SurfaceStyleReflectanceAmbientDiffuseSpecular()
    refl.Init(AMBIENT, DIFFUSE, SPECULAR, SPECULAR_EXP, spec_color)

    props = NCollection_HArray1[StepVisual_RenderingPropertiesSelect](1, 2)
    rps1 = StepVisual_RenderingPropertiesSelect()
    rps2 = StepVisual_RenderingPropertiesSelect()
    rps1.SetValue(transp)
    rps2.SetValue(refl)
    props.SetValue(1, rps1)
    props.SetValue(2, rps2)

    result = StepVisual_SurfaceStyleRenderingWithProperties()
    result.Init(StepVisual_ssmNormalShading, surface, props)
    return result


def _create_material():
    m = XCAFDoc_VisMaterialCommon()
    s = _surface()
    m.DiffuseColor = s
    m.Transparency = TRANSPARENCY
    m.AmbientColor = Quantity_Color(s.Red() * AMBIENT, s.Green() * AMBIENT, s.Blue() * AMBIENT, Quantity_TOC_RGB)
    m.SpecularColor = _specular()
    m.Shininess = SPECULAR_EXP / 128.0
    m.IsDefined = True
    return m


def _full_props():
    p = STEPConstruct_RenderingProperties()
    p.Init(_surface(), TRANSPARENCY)
    p.SetAmbientDiffuseAndSpecularReflectance(AMBIENT, DIFFUSE, SPECULAR, SPECULAR_EXP, _specular())
    return p


def test_STEPConstruct_RenderingPropertiesTest_DefaultConstructor():
    p = STEPConstruct_RenderingProperties()
    assert not p.IsDefined()
    assert not p.IsAmbientReflectanceDefined()
    assert not p.IsDiffuseReflectanceDefined()
    assert not p.IsSpecularReflectanceDefined()
    assert not p.IsSpecularExponentDefined()
    assert not p.IsSpecularColourDefined()
    assert p.Transparency() == 0.0
    assert p.RenderingMethod() == StepVisual_ssmNormalShading


def test_STEPConstruct_RenderingPropertiesTest_RGBAConstructor():
    p = STEPConstruct_RenderingProperties(Quantity_ColorRGBA(_surface(), 0.75))
    assert p.IsDefined()
    assert not p.IsAmbientReflectanceDefined()
    assert not p.IsDiffuseReflectanceDefined()
    assert not p.IsSpecularReflectanceDefined()
    assert _colors_equal(p.SurfaceColor(), _surface())
    assert abs(p.Transparency() - 0.25) <= 0.001
    assert p.RenderingMethod() == StepVisual_ssmNormalShading


def test_STEPConstruct_RenderingPropertiesTest_StepRenderingPropertiesConstructor():
    p = STEPConstruct_RenderingProperties(_create_step_rendering_properties())
    assert p.IsDefined()
    assert p.IsAmbientReflectanceDefined()
    assert p.IsDiffuseReflectanceDefined()
    assert p.IsSpecularReflectanceDefined()
    assert p.IsSpecularExponentDefined()
    assert p.IsSpecularColourDefined()
    assert _colors_equal(p.SurfaceColor(), _surface())
    assert abs(p.Transparency() - TRANSPARENCY) <= 0.001
    assert abs(p.AmbientReflectance() - AMBIENT) <= 0.001
    assert abs(p.DiffuseReflectance() - DIFFUSE) <= 0.001
    assert abs(p.SpecularReflectance() - SPECULAR) <= 0.001
    assert abs(p.SpecularExponent() - SPECULAR_EXP) <= 0.001
    assert _colors_equal(p.SpecularColour(), _specular())
    assert p.RenderingMethod() == StepVisual_ssmNormalShading


def test_STEPConstruct_RenderingPropertiesTest_MaterialConstructor():
    p = STEPConstruct_RenderingProperties(_create_material())
    assert p.IsDefined()
    assert p.IsAmbientReflectanceDefined()
    assert p.IsDiffuseReflectanceDefined()
    assert p.IsSpecularReflectanceDefined()
    assert p.IsSpecularExponentDefined()
    assert p.IsSpecularColourDefined()
    assert _colors_equal(p.SurfaceColor(), _surface())
    assert abs(p.Transparency() - TRANSPARENCY) <= 0.001
    assert abs(p.AmbientReflectance() - AMBIENT) <= 0.02
    assert abs(p.DiffuseReflectance() - 1.0) <= 0.001


def test_STEPConstruct_RenderingPropertiesTest_SetReflectanceProperties():
    p = STEPConstruct_RenderingProperties()
    p.Init(_surface(), TRANSPARENCY)
    assert p.IsDefined()

    p.SetAmbientReflectance(AMBIENT)
    assert p.IsAmbientReflectanceDefined()
    assert abs(p.AmbientReflectance() - AMBIENT) <= 0.001
    assert not p.IsDiffuseReflectanceDefined()

    p.SetAmbientAndDiffuseReflectance(AMBIENT, DIFFUSE)
    assert p.IsAmbientReflectanceDefined()
    assert p.IsDiffuseReflectanceDefined()
    assert abs(p.AmbientReflectance() - AMBIENT) <= 0.001
    assert abs(p.DiffuseReflectance() - DIFFUSE) <= 0.001
    assert not p.IsSpecularReflectanceDefined()

    p.SetAmbientDiffuseAndSpecularReflectance(AMBIENT, DIFFUSE, SPECULAR, SPECULAR_EXP, _specular())
    assert p.IsAmbientReflectanceDefined()
    assert p.IsDiffuseReflectanceDefined()
    assert p.IsSpecularReflectanceDefined()
    assert p.IsSpecularExponentDefined()
    assert p.IsSpecularColourDefined()
    assert abs(p.AmbientReflectance() - AMBIENT) <= 0.001
    assert abs(p.DiffuseReflectance() - DIFFUSE) <= 0.001
    assert abs(p.SpecularReflectance() - SPECULAR) <= 0.001
    assert abs(p.SpecularExponent() - SPECULAR_EXP) <= 0.001
    assert _colors_equal(p.SpecularColour(), _specular())


def test_STEPConstruct_RenderingPropertiesTest_CreateRenderingProperties():
    step_props = _full_props().CreateRenderingProperties()
    assert step_props is not None
    assert step_props.RenderingMethod() == StepVisual_ssmNormalShading

    parsed = STEPConstruct_RenderingProperties(step_props)
    assert parsed.IsDefined()
    assert _colors_equal(parsed.SurfaceColor(), _surface())
    assert abs(parsed.Transparency() - TRANSPARENCY) <= 0.001
    assert abs(parsed.AmbientReflectance() - AMBIENT) <= 0.001
    assert abs(parsed.DiffuseReflectance() - DIFFUSE) <= 0.001
    assert abs(parsed.SpecularReflectance() - SPECULAR) <= 0.001
    assert abs(parsed.SpecularExponent() - SPECULAR_EXP) <= 0.001
    assert _colors_equal(parsed.SpecularColour(), _specular())


def test_STEPConstruct_RenderingPropertiesTest_CreateXCAFMaterial():
    m = _full_props().CreateXCAFMaterial()
    assert m.IsDefined
    assert _colors_equal(m.DiffuseColor, _surface())
    assert abs(m.Transparency - TRANSPARENCY) <= 0.001
    s = _surface()
    expected_ambient = Quantity_Color(s.Red() * AMBIENT, s.Green() * AMBIENT, s.Blue() * AMBIENT, Quantity_TOC_RGB)
    assert _colors_equal(m.AmbientColor, expected_ambient)
    assert _colors_equal(m.SpecularColor, _specular())
    assert abs(m.Shininess - SPECULAR_EXP / 128.0) <= 0.01


def test_STEPConstruct_RenderingPropertiesTest_BidirectionalConversion():
    original = _create_material()
    converted = STEPConstruct_RenderingProperties(original).CreateXCAFMaterial()
    assert converted.IsDefined
    assert _colors_equal(converted.DiffuseColor, original.DiffuseColor)
    assert abs(converted.Transparency - original.Transparency) <= 0.001
    assert _colors_equal(converted.AmbientColor, original.AmbientColor, 0.05)
    assert _colors_equal(converted.SpecularColor, original.SpecularColor, 0.05)
    assert abs(converted.Shininess - original.Shininess) <= 0.05


def test_STEPConstruct_RenderingPropertiesTest_InitWithRGBAColor():
    p = STEPConstruct_RenderingProperties()
    p.Init(Quantity_ColorRGBA(Quantity_Color(0.3, 0.6, 0.9, Quantity_TOC_RGB), 0.6))
    assert p.IsDefined()
    assert not p.IsAmbientReflectanceDefined()
    assert not p.IsDiffuseReflectanceDefined()
    assert not p.IsSpecularReflectanceDefined()
    assert _colors_equal(p.SurfaceColor(), Quantity_Color(0.3, 0.6, 0.9, Quantity_TOC_RGB))
    assert abs(p.Transparency() - 0.4) <= 0.001


def test_STEPConstruct_RenderingPropertiesTest_InitWithCustomRenderingMethod():
    p = STEPConstruct_RenderingProperties()
    p.Init(_surface(), TRANSPARENCY)
    p.SetRenderingMethod(StepVisual_ssmDotShading)
    assert p.IsDefined()
    assert _colors_equal(p.SurfaceColor(), _surface())
    assert abs(p.Transparency() - TRANSPARENCY) <= 0.001
    assert p.RenderingMethod() == StepVisual_ssmDotShading


def test_STEPConstruct_RenderingPropertiesTest_MaterialConvertible():
    p = STEPConstruct_RenderingProperties()
    assert not p.IsMaterialConvertible()
    p.Init(_surface(), TRANSPARENCY)
    assert not p.IsMaterialConvertible()
    p.SetAmbientDiffuseAndSpecularReflectance(AMBIENT, DIFFUSE, SPECULAR, SPECULAR_EXP, _specular())
    assert p.IsMaterialConvertible()


def test_STEPConstruct_RenderingPropertiesTest_NullInputs():
    p = STEPConstruct_RenderingProperties()
    null_props: StepVisual_SurfaceStyleRenderingWithProperties | None = None
    p.Init(null_props)
    assert not p.IsDefined()

    null_material = XCAFDoc_VisMaterialCommon()
    null_material.IsDefined = False
    assert not STEPConstruct_RenderingProperties(null_material).IsDefined()


def test_STEPConstruct_RenderingPropertiesTest_CreateAmbientOnlyProperties():
    p = STEPConstruct_RenderingProperties()
    p.Init(_surface(), TRANSPARENCY)
    p.SetAmbientReflectance(AMBIENT)
    step_props = p.CreateRenderingProperties()
    assert step_props is not None

    parsed = STEPConstruct_RenderingProperties(step_props)
    assert parsed.IsDefined()
    assert parsed.IsAmbientReflectanceDefined()
    assert not parsed.IsDiffuseReflectanceDefined()
    assert not parsed.IsSpecularReflectanceDefined()
    assert _colors_equal(parsed.SurfaceColor(), _surface())
    assert abs(parsed.Transparency() - TRANSPARENCY) <= 0.001
    assert abs(parsed.AmbientReflectance() - AMBIENT) <= 0.001


def test_STEPConstruct_RenderingPropertiesTest_CreateAmbientAndDiffuseProperties():
    p = STEPConstruct_RenderingProperties()
    p.Init(_surface(), TRANSPARENCY)
    p.SetAmbientAndDiffuseReflectance(AMBIENT, DIFFUSE)
    step_props = p.CreateRenderingProperties()
    assert step_props is not None

    parsed = STEPConstruct_RenderingProperties(step_props)
    assert parsed.IsDefined()
    assert parsed.IsAmbientReflectanceDefined()
    assert parsed.IsDiffuseReflectanceDefined()
    assert not parsed.IsSpecularReflectanceDefined()
    assert _colors_equal(parsed.SurfaceColor(), _surface())
    assert abs(parsed.Transparency() - TRANSPARENCY) <= 0.001
    assert abs(parsed.AmbientReflectance() - AMBIENT) <= 0.001
    assert abs(parsed.DiffuseReflectance() - DIFFUSE) <= 0.001


def test_STEPConstruct_RenderingPropertiesTest_NonStandardSpecularColor():
    m = _create_material()
    custom = Quantity_Color(0.1, 0.8, 0.2, Quantity_TOC_RGB)
    m.SpecularColor = custom
    p = STEPConstruct_RenderingProperties(m)
    assert p.IsSpecularColourDefined()
    assert _colors_equal(p.SpecularColour(), custom)
    assert _colors_equal(p.CreateXCAFMaterial().SpecularColor, custom, 0.05)


def test_STEPConstruct_RenderingPropertiesTest_ExtremeValues():
    p = STEPConstruct_RenderingProperties()
    p.Init(_surface(), 1.0)
    assert abs(p.Transparency() - 1.0) <= 0.001
    p.SetAmbientDiffuseAndSpecularReflectance(0.0, 2.0, 1.0, 256.0, _specular())
    m = p.CreateXCAFMaterial()
    assert abs(m.AmbientColor.Red() - 0.0) <= 0.001
    assert abs(m.AmbientColor.Green() - 0.0) <= 0.001
    assert abs(m.AmbientColor.Blue() - 0.0) <= 0.001
    assert abs(m.Shininess - 1.0) <= 0.1
