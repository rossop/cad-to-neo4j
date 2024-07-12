# extractors.py
"""
Extractors Mapping Submodule

This module defines the mapping of CAD element types to their respective extractor classes.
"""

from .sketch import (
    SketchExtractor, 
    SketchPointExtractor, 
    SketchCurveExtractor, 
    SketchLineExtractor, 
    ProfileExtractor,
    SketchCircleExtractor,
    SketchArcExtractor,
    SketchEllipseExtractor,
    SketchEllipticalArcExtractor,
    SketchFittedSplineExtractor,
    SketchFixedSplineExtractor,
) 
from .sketch.dimension import (
    SketchDimensionExtractor,
    SketchAngularDimensionExtractor,
    SketchConcentricCircleDimensionExtractor,
    SketchDiameterDimensionExtractor,
    SketchDistanceBetweenLineAndPlanarSurfaceDimensionExtractor,
    SketchDistanceBetweenPointAndSurfaceDimensionExtractor,
    SketchEllipseMajorRadiusDimensionExtractor,
    SketchEllipseMinorRadiusDimensionExtractor,
    SketchLinearDiameterDimensionExtractor,
    SketchLinearDimensionExtractor,
    SketchOffsetCurvesDimensionExtractor,
    SketchOffsetDimensionExtractor,
    SketchRadialDimensionExtractor,
    SketchTangentDistanceDimensionExtractor
)
from .sketch.constraint import (
    GeometricConstraintExtractor, 
    VerticalConstraintExtractor, 
    HorizontalConstraintExtractor, 
    MidPointConstraintExtractor, 
    PerpendicularConstraintExtractor, 
    CoincidentConstraintExtractor, 
    OffsetConstraintExtractor,
    CoincidentToSurfaceConstraintExtractor,
    CollinearConstraintExtractor,
    ConcentricConstraintExtractor,
    EqualConstraintExtractor,
    HorizontalPointsConstraintExtractor,
    LineOnPlanarSurfaceConstraintExtractor,
    LineParallelToPlanarSurfaceConstraintExtractor,
    CircularPatternConstraintExtractor,
    ParallelConstraintExtractor,
    SymmetryConstraintExtractor,
    TangentConstraintExtractor,
)
from .feature import (
    FeatureExtractor,
    ExtrudeFeatureExtractor, 
    RevolveFeatureExtractor, 
    HoleFeatureExtractor,
    FilletFeatureExtractor,
    ChamferFeatureExtractor,
    BoxFeatureExtractor,
)
from .construction_geometry import ConstructionPlaneExtractor, ConstructionAxisExtractor, ConstructionPointExtractor
from .brep import (
    BRepEntityExtractor,
    BRepBodyExtractor, 
    BRepFaceExtractor, 
    BRepEdgeExtractor,
    BRepVertexExtractor,
)

__all__ = ['EXTRACTORS', 'ENTITY_MAP']

EXTRACTORS = {
    'adsk::fusion::Sketch': SketchExtractor,
    'adsk::fusion::SketchPoint': SketchPointExtractor,
    'adsk::fusion::SketchCurve': SketchCurveExtractor,
    'adsk::fusion::SketchCircle': SketchCircleExtractor,
    'adsk::fusion::SketchArc': SketchArcExtractor,
    'adsk::fusion::SketchEllipse': SketchEllipseExtractor,
    'adsk::fusion::SketchEllipticalArc': SketchEllipticalArcExtractor,
    'adsk::fusion::SketchFittedSpline': SketchFittedSplineExtractor,
    'adsk::fusion::SketchFixedSpline': SketchFixedSplineExtractor,
    'adsk::fusion::SketchLine': SketchLineExtractor,
    'adsk::fusion::SketchDimension': SketchDimensionExtractor,
    'adsk::fusion::SketchAngularDimension': SketchAngularDimensionExtractor,
    'adsk::fusion::SketchConcentricCircleDimension': SketchConcentricCircleDimensionExtractor,
    'adsk::fusion::SketchDiameterDimension': SketchDiameterDimensionExtractor,
    'adsk::fusion::SketchDistanceBetweenLineAndPlanarSurfaceDimension': SketchDistanceBetweenLineAndPlanarSurfaceDimensionExtractor,
    'adsk::fusion::SketchDistanceBetweenPointAndSurfaceDimension': SketchDistanceBetweenPointAndSurfaceDimensionExtractor,
    'adsk::fusion::SketchEllipseMajorRadiusDimension': SketchEllipseMajorRadiusDimensionExtractor,
    'adsk::fusion::SketchEllipseMinorRadiusDimension': SketchEllipseMinorRadiusDimensionExtractor,
    'adsk::fusion::SketchLinearDiameterDimension': SketchLinearDiameterDimensionExtractor,
    'adsk::fusion::SketchLinearDimension': SketchLinearDimensionExtractor,
    'adsk::fusion::SketchOffsetCurvesDimension': SketchOffsetCurvesDimensionExtractor,
    'adsk::fusion::SketchOffsetDimension': SketchOffsetDimensionExtractor,
    'adsk::fusion::SketchRadialDimension': SketchRadialDimensionExtractor,
    'adsk::fusion::SketchTangentDistanceDimension': SketchTangentDistanceDimensionExtractor,
    'adsk::fusion::Profile': ProfileExtractor,
    'adsk::fusion::ExtrudeFeature': ExtrudeFeatureExtractor, 
    'adsk::fusion::RevolveFeature': RevolveFeatureExtractor, 
    'adsk::fusion::HoleFeature': HoleFeatureExtractor, 
    'adsk::fusion::FilletFeature': FilletFeatureExtractor, 
    'adsk::fusion::ChamferFeature': ChamferFeatureExtractor, 
    'adsk::fusion::BoxFeature': BoxFeatureExtractor, 
    'adsk::fusion::BRepBody': BRepBodyExtractor, 
    'adsk::fusion::BRepShell': BRepEntityExtractor, # TODO change to ShellExtractor
    'adsk::fusion::BRepLump': BRepEntityExtractor, # TODO change to LumpExtractor
    'adsk::fusion::BRepFace': BRepFaceExtractor,
    'adsk::fusion::BRepEdge': BRepEdgeExtractor,
    'adsk::fusion::BRepVertex': BRepVertexExtractor,
    'adsk::fusion::ConstructionPlane': ConstructionPlaneExtractor,
    'adsk::fusion::ConstructionAxis': ConstructionAxisExtractor,
    'adsk::fusion::ConstructionPoint': ConstructionPointExtractor,
    'adsk::fusion::GeometricConstraint' : GeometricConstraintExtractor,
    'adsk::fusion::VerticalConstraint' : VerticalConstraintExtractor,
    'adsk::fusion::HorizontalConstraint' : HorizontalConstraintExtractor,
    'adsk::fusion::MidPointConstraint' : MidPointConstraintExtractor,
    'adsk::fusion::PerpendicularConstraint' : PerpendicularConstraintExtractor,
    'adsk::fusion::ParallelConstraint' : ParallelConstraintExtractor,
    'adsk::fusion::SymmetryConstraint' : SymmetryConstraintExtractor,
    'adsk::fusion::TangentConstraint' : TangentConstraintExtractor,
    'adsk::fusion::CoincidentConstraint' : CoincidentConstraintExtractor,
    'adsk::fusion::OffsetConstraint' : OffsetConstraintExtractor,
    'adsk::fusion::LineOnPlanarSurfaceConstraint': LineOnPlanarSurfaceConstraintExtractor,
    'adsk::fusion::LineParallelToPlanarSurfaceConstraint': LineParallelToPlanarSurfaceConstraintExtractor,
    'adsk::fusion::CircularPatternConstraint': CircularPatternConstraintExtractor,
    'adsk::fusion::CoincidentToSurfaceConstraint': CoincidentToSurfaceConstraintExtractor,
    'adsk::fusion::CollinearConstraint': CollinearConstraintExtractor,
    'adsk::fusion::ConcentricConstraint': ConcentricConstraintExtractor,
    'adsk::fusion::EqualConstraint': EqualConstraintExtractor,
    'adsk::fusion::HorizontalPointsConstraint': HorizontalPointsConstraintExtractor,
}

ENTITY_MAP = {
    'shell': ('shells', BRepEntityExtractor), # TODO change to ShellExtractor
    'lump': ('lumps', BRepEntityExtractor), # TODO change to LumpExtractor
    'face': ('faces', BRepFaceExtractor),
    'edge': ('edges', BRepEdgeExtractor),
    'vertex': ('vertices', BRepVertexExtractor), 
}
