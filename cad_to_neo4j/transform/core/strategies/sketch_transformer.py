"""
Sketch Relationships Transformer

This module provides the transformation logic for sketch relationships.

Classes:
    - SketchTransformer: A class to handle sketch-based transformations.
"""
import traceback
from ..base_transformer import BaseTransformer

class SketchTransformer(BaseTransformer):
    """
    SketchTransformer

    A class to handle sketch-based transformations.

    Methods:
        transform(execute_query): Runs all sketch-related transformation methods.
    """
    def transform(self, execute_query):
        """
        Runs all sketch-related transformation methods.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: The result values from the query execution.
        """
        results = {}
        results['create_sketch_relationships'] = self.create_sketch_relationships(execute_query)
        results['create_sketch_axis_and_origin_for_all_sketches'] = self.create_sketch_axis_and_origin_for_all_sketches(execute_query)
        results['create_sketch_dimensions_relationships'] = self.create_sketch_dimensions_relationships(execute_query)
        results['create_sketch_geometric_constraints'] = self.create_sketch_geometric_constraints(execute_query)
        return results

    def create_sketch_relationships(self, execute_query):
        """
        Creates relationships between sketch entities.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        queries = [
            r"""
            // Match existing SketchEntity nodes with a non-null parentSketch
            MATCH (se)
            WHERE ('SketchEntity' IN labels(se) 
                OR 'SketchDimension' IN labels(se) 
                OR 'GeometricConstraint' IN labels(se) 
                OR 'Profile' IN labels(se)) 
                AND se.parentSketch IS NOT NULL 
            
            // Match existing Sketch node where entityToken matches parentSketch of SketchEntity
            MATCH (s:Sketch {entityToken: se.parentSketch})

            // Create the relationship from Sketch to SketchEntity
            MERGE (s)-[:CONTAINS]->(se)
            """,
            r"""
            MATCH (sp:`SketchPoint`)
            WHERE sp.connectedEntities IS NOT NULL
            UNWIND sp.connectedEntities AS entity_token
            MATCH (se {entityToken: entity_token})
            WHERE NOT 'SketchCurve' IN labels(se)
            MERGE (sp)-[:CONNECTED_TO]->(se)
            """,
            r"""
            MATCH (sc:`SketchCurve`)
            WHERE sc.startPoint IS NOT NULL AND sc.endPoint IS NOT NULL
            MATCH (sp1 {entityToken: sc.startPoint})
            MATCH (sp2 {entityToken: sc.endPoint})
            MERGE (sc)-[:STARTS_AT]->(sp1)
            MERGE (sc)-[:ENDS_AT]->(sp2)
            """,
            r"""
            MATCH (s:`Sketch`)-[:CONTAINS]->(p:`Profile`)
            WHERE p.profileCurves IS NOT NULL
            UNWIND p.profileCurves AS curve_token
            MATCH (sc {entityToken: curve_token})
            MERGE (p)-[:CONTAINS]->(sc)
            """,
            r"""
            MATCH (sc:`SketchLine`)
            WHERE sc.startPoint IS NOT NULL AND sc.endPoint IS NOT NULL

            // Ensure that the startPoint and endPoint nodes exist
            WITH sc, sc.startPoint AS startPointToken, sc.endPoint AS endPointToken
            MATCH (sp1 {entityToken: startPointToken})
            MATCH (sp2 {entityToken: endPointToken})

            // Create relationships
            MERGE (sc)-[:STARTS_AT]->(sp1)
            MERGE (sc)-[:ENDS_AT]->(sp2)

            RETURN sc, sp1, sp2
            """,
            r"""
            MATCH (circle)
            WHERE circle.centerPoint IS NOT NULL
            MATCH (center {entityToken: circle.centerPoint})
            MERGE (circle)-[:CENTERED_ON]->(center)
            REMOVE circle.centerPoint
            RETURN circle, center
            """,
            r"""
            MATCH (se:SketchEntity)
            WHERE se.referencedEntity IS NOT NULL
            MATCH (re:SketchEntity)
            WHERE re.entityToken = se.referencedEntity
            MERGE (re)-[:PROJECTED_TO]->(se)
            RETURN se,re
            """,
        ]
        results = []
        self.logger.info('Creating sketch relationships')
        for query in queries:
            try:
                results.extend(execute_query(query))
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results

    def create_sketch_dimensions_relationships(self, execute_query):
        """
        Creates 'DIMENSIONED' relationships between sketch entities and their corresponding dimensions.

        This function connects any node with a sketchDimensions property to all the SketchDimension nodes
        that share the same entityToken as the ones in the list under the sketchDimensions property.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            list: The result values from the query execution.
        """
        cypher_queries = [
            """
            MATCH (d)
            WHERE ('SketchDimension' IN labels(d) OR 'SketchLinearDimension' IN labels(d)) 
                AND d.entityOne IS NOT NULL 
                AND d.entityTwo IS NOT NULL
            MATCH (a {entityToken: d.entityOne})
            MATCH (b {entityToken: d.entityTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.entityOne, d.entityTwo
            """,
            """
            MATCH (d)
            WHERE (d:SketchAngularDimension) 
                AND d.lineOne IS NOT NULL 
                AND d.lineTwo IS NOT NULL
            MATCH (a {entityToken: d.lineOne})
            MATCH (b {entityToken: d.lineTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.lineOne, d.lineTwo
            """,   
            """
            MATCH (d)
            WHERE (d:SketchConcentricCircleDimension) 
                AND d.circleOne IS NOT NULL 
                AND d.circleTwo IS NOT NULL
            MATCH (a {entityToken: d.circleOne})
            MATCH (b {entityToken: d.circleTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.circleOne, d.circleTwo
            """,   
            """
            MATCH (d)
            WHERE ('SketchDiameterDimension' IN labels(d) OR 'SketchRadialDimension' IN labels(d))
                AND d.entity IS NOT NULL 
            MATCH (a {entityToken: d.entity})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(a)
            REMOVE d.entity
            """,
            """
            MATCH (d)
            WHERE (d:SketchDistanceBetweenLineAndPlanarSurfaceDimension) 
                AND d.line IS NOT NULL 
                AND d.planarSurface IS NOT NULL
            MATCH (a {entityToken: d.line})
            MATCH (b {entityToken: d.planarSurface})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.line, d.planarSurface
            """,   
            """
            MATCH (d)
            WHERE (d:SketchDistanceBetweenPointAndSurfaceDimension) 
                AND d.point IS NOT NULL 
                AND d.surface IS NOT NULL
            MATCH (a {entityToken: d.point})
            MATCH (b {entityToken: d.surface})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.point, d.surface
            """,   
            """
            MATCH (d)
            WHERE (d:SketchLinearDiameterDimension) 
                AND d.line IS NOT NULL 
                AND d.entityTwo IS NOT NULL
            MATCH (a {entityToken: d.line})
            MATCH (b {entityToken: d.entityTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(b)
            REMOVE d.line, d.entityTwo
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetCurvesDimension) 
                AND d.offsetConstraint IS NOT NULL 
            MATCH (c {entityToken: d.offsetConstraint})
            MERGE (c)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.offsetConstraint
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetCurvesDimension) 
                AND d.offsetConstraint IS NOT NULL 
            MATCH (c {entityToken: d.offsetConstraint})
            MERGE (c)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.offsetConstraint
            """,   
            """
            MATCH (d)
            WHERE (d:SketchOffsetDimension) 
                AND d.line IS NOT NULL 
                AND d.entityTwo IS NOT NULL 
            MATCH (a {entityToken: d.line})
            MATCH (c {entityToken: d.entityTwo})
            MERGE (a)-[:DIMENSIONED]->(d)
            MERGE (d)-[:DIMENSIONED]->(c)
            REMOVE d.line, d.entityTwo
            """,
            #  Redundancy check for Circle entities dimensions
            """
            // Query to create DIMENSIONED relationships using the dimensions property of SketchCircle

            // Unwind dimensions and create DIMENSIONED relationships from dimension to circle
            MATCH (circle:SketchCircle)
            UNWIND circle.dimensions AS dimension_id
            MATCH (dim:SketchDimension {entityToken: dimension_id})
            WHERE NOT (dim)-[:DIMENSIONED]->(circle)
            MERGE (dim)-[:DIMENSIONED]->(circle)
            RETURN circle, dim;
            """,
            """
            // Unwind dimensions and create DIMENSIONED relationships from circle to dimension
            MATCH (circle:SketchCircle)
            UNWIND circle.dimensions AS dimension_id
            MATCH (dim:SketchDimension {entityToken: dimension_id})
            WHERE NOT (circle)-[:DIMENSIONED]->(dim)
            MERGE (circle)-[:DIMENSIONED]->(dim)
            REMOVE circle.dimensions
            RETURN circle, dim;
            """
        ]
        
        results = []
        self.logger.info('Creating relationships between sketch entities and their dimensions')
        for query in cypher_queries:
            try:
                results.extend(execute_query(query))
            except Exception as e:
                    self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results

    def create_sketch_geometric_constraints(self, execute_query):
        """
        Creates relationships between entities and their geometric constraints based on various properties.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            dict: A dictionary containing the results of all transformations.
        """
        queries = [ 
            # Creates relationships for CircularPatternConstraint entities.
            """
            MATCH (c:CircularPatternConstraint)
            WHERE c.entities IS NOT NULL AND c.createdEntities IS NOT NULL AND c.centerPoint IS NOT NULL
            UNWIND c.entities AS entity_token
            MATCH (se {entityToken: entity_token}) // Source Entities
            WITH c, se
            UNWIND c.createdEntities AS created_entity_token
            MATCH (te {entityToken: created_entity_token}) // Target Entities
            WITH c, se, te
            MATCH (ce {entityToken: c.centerPoint}) // Center Point
            MERGE (se)-[:CONSTRAINED]->(c)
            MERGE (c)-[:CONSTRAINED]->(te)
            MERGE (ce)-[:CONSTRAINED]->(c)
            REMOVE c.entities, c.createdEntities, c.centerPoint
            RETURN c, se, te, ce
            """,
            # Creates relationships for VerticalConstraint entities with yAxis.
            """   
            MATCH (vc:VerticalConstraint)
            WHERE vc.line IS NOT NULL
            UNWIND vc.line AS entity_token
            MATCH (se {entityToken: entity_token}) // Source Entities
            MATCH (sa:SketchAxis {name: 'y'}) // Target SketchAxis
            WITH vc, se, sa
            MATCH (vc)<-[:CONTAINS]-(s:Sketch)-[:CONTAINS]->(sa)
            MERGE (se)-[:CONSTRAINED]->(vc)
            MERGE (vc)-[:CONSTRAINED]->(sa)
            REMOVE vc.line
            RETURN vc, se, sa
            """,
            # Creates relationships for HorizontalConstraint entities with xAxis.
            """
            MATCH (hc:HorizontalConstraint)
            WHERE hc.line IS NOT NULL
            UNWIND hc.line AS entity_token
            MATCH (se {entityToken: entity_token}) // Source Entities
            MATCH (sa:SketchAxis {name: 'x'}) // Target SketchAxis
            WITH hc, se, sa
            MATCH (hc)<-[:CONTAINS]-(s:Sketch)-[:CONTAINS]->(sa)
            MERGE (se)-[:CONSTRAINED]->(hc)
            MERGE (hc)-[:CONSTRAINED]->(sa)
            // REMOVE hc.line
            RETURN hc, se, sa
            """,
            # Creates relationships for PerpendicularConstraint entities linking lineOne and lineTwo.
            """
            MATCH (pc:PerpendicularConstraint)
            WHERE pc.lineOne IS NOT NULL AND pc.lineTwo IS NOT NULL
            MATCH (source {entityToken: pc.lineOne}) // Source Entity
            MATCH (target {entityToken: pc.lineTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(pc)
            MERGE (pc)-[:CONSTRAINED]->(target)
            REMOVE pc.lineOne, pc.lineTwo
            RETURN pc, source, target
            """,
            # Creates relationships for CoincidentConstraint entities linking point and entity.
            """
            MATCH (cc:CoincidentConstraint)
            WHERE cc.point IS NOT NULL AND cc.entity IS NOT NULL
            MATCH (source {entityToken: cc.point}) // Source Entity
            MATCH (target {entityToken: cc.entity}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(cc)
            MERGE (cc)-[:CONSTRAINED]->(target)
            REMOVE cc.point, cc.entity
            RETURN cc, source, target
            """,
            # Creates relationships for CollinearConstraint entities linking lineOne and lineTwo.
            """
            MATCH (cc:CollinearConstraint)
            WHERE cc.lineOne IS NOT NULL AND cc.lineTwo IS NOT NULL
            MATCH (source {entityToken: cc.lineOne}) // Source Entity
            MATCH (target {entityToken: cc.lineTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(cc)
            MERGE (cc)-[:CONSTRAINED]->(target)
            REMOVE cc.lineOne, cc.lineTwo
            RETURN cc, source, target
            """,
            # Creates relationships for EqualConstraint entities linking curveOne and curveTwo.
            """
            MATCH (ec:EqualConstraint)
            WHERE ec.curveOne IS NOT NULL AND ec.curveTwo IS NOT NULL
            MATCH (source {entityToken: ec.curveOne}) // Source Entity
            MATCH (target {entityToken: ec.curveTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(ec)
            MERGE (ec)-[:CONSTRAINED]->(target)
            REMOVE ec.curveOne, ec.curveTwo
            RETURN ec, source, target
            """,
            # Creates relationships for ParallelConstraint entities linking lineOne and lineTwo.
            """
            MATCH (pc:ParallelConstraint)
            WHERE pc.lineOne IS NOT NULL AND pc.lineTwo IS NOT NULL
            MATCH (source {entityToken: pc.lineOne}) // Source Entity
            MATCH (target {entityToken: pc.lineTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(pc)
            MERGE (pc)-[:CONSTRAINED]->(target)
            REMOVE pc.lineOne, pc.lineTwo
            RETURN pc, source, target
            """,
            # reates relationships for SymmetryConstraint entities linking entityOne, entityTwo, and symmetry_line.
            """
            MATCH (sc:SymmetryConstraint)
            WHERE sc.entityOne IS NOT NULL AND sc.entityTwo IS NOT NULL AND sc.symmetry_line IS NOT NULL
            MATCH (source {entityToken: sc.entityOne}) // Source Entity
            MATCH (target {entityToken: sc.entityTwo}) // Target Entity
            MATCH (symmetry_line {entityToken: sc.symmetry_line}) // Symmetry Line
            MERGE (source)-[:CONSTRAINED]->(sc)
            MERGE (sc)-[:CONSTRAINED]->(target)
            MERGE (symmetry_line)-[:CONSTRAINED]->(sc)
            REMOVE sc.entityOne, sc.entityTwo, sc.symmetry_line
            RETURN sc, source, target, symmetry_line
            """,
            # Creates relationships for TangentConstraint entities linking curveOne and curveTwo.
            """
            MATCH (tc:TangentConstraint)
            WHERE tc.curveOne IS NOT NULL AND tc.curveTwo IS NOT NULL
            MATCH (source {entityToken: tc.curveOne}) // Source Entity
            MATCH (target {entityToken: tc.curveTwo}) // Target Entity
            MERGE (source)-[:CONSTRAINED]->(tc)
            MERGE (tc)-[:CONSTRAINED]->(target)
            REMOVE tc.curveOne, tc.curveTwo
            RETURN tc, source, target
            """,
        ]
        
        results = []
        self.logger.info('Creating geometric constraints')
        for query in queries:
            try:
                results.extend(execute_query(query))
            except Exception as e:
                self.logger.error(f'Exception executing query: {query}\n{e}\n{traceback.format_exc()}')
        return results

    def create_sketch_axis_and_origin_for_all_sketches(self, execute_query):
        """
        Matches all existing Sketch nodes, extracts axis and origin information,
        and creates SketchAxis and SketchOrigin nodes with relationships.

        Args:
            execute_query (function): Function to execute a Cypher query.

        Returns:
            None
        """
        self.logger.info("Creating sketch axis and origin nodes for all sketches")
        query = """
            MATCH (sketch:Sketch)
            WITH sketch, sketch.origin AS origin_position, sketch.x_direction AS x_axis_vector, sketch.y_direction AS y_axis_vector, sketch.origin_point AS origin_entityToken
            MERGE (origin:SketchEntity {entityToken: origin_entityToken})
            ON CREATE SET origin.position = origin_position
            ON MATCH SET origin :SketchOrigin
            SET origin :SketchEntity
            MERGE (x_axis:SketchAxis:SketchEntity {name: 'x', vector: x_axis_vector})
            MERGE (y_axis:SketchAxis:SketchEntity {name: 'y', vector: y_axis_vector})
            MERGE (x_axis)-[:STARTS_WITH]->(origin)
            MERGE (y_axis)-[:STARTS_WITH]->(origin)
            MERGE (y_axis)-[:PERPENDICULAR_TO]->(x_axis)
            MERGE (sketch)-[:CONTAINS]->(x_axis)
            MERGE (sketch)-[:CONTAINS]->(y_axis)
            MERGE (sketch)-[:CONTAINS]->(origin)
            """
        try:
            execute_query(query)
        except Exception as e:
            self.logger.error(f"Error creating sketch axis and origin nodes for all sketches: {e}")
