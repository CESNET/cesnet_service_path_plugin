"""
Simplified utility functions for handling GIS data using GeoPandas
"""

import tempfile
import zipfile
from pathlib import Path

import geopandas as gpd
from django.contrib.gis.geos import MultiLineString, LineString
from django.core.exceptions import ValidationError


def process_path_file(uploaded_file, file_format):
    """
    Process uploaded path file using GeoPandas and return MultiLineString

    Args:
        uploaded_file: Django uploaded file object
        file_format: Format type ('geojson', 'kml', 'kmz')

    Returns:
        MultiLineString: Validated 2D MultiLineString object
    """
    try:
        # Determine appropriate suffix for temporary file
        if file_format in ["geojson", "json"]:
            suffix = ".geojson"
        elif file_format == "kml":
            suffix = ".kml"
        elif file_format == "kmz":
            suffix = ".kmz"
        else:
            suffix = f".{file_format}"

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            # Reset uploaded file position to beginning
            uploaded_file.seek(0)

            # Write uploaded file content to temporary file
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

            temp_file_path = temp_file.name

        try:
            # Read the file with geopandas - let geopandas auto-detect the format
            # if the suffix is kmz, extract the KML first
            if file_format == "kmz":
                kml_file_path = extract_kml_from_kmz(temp_file_path, temp_file_path.replace(".kmz", ".kml"))
                gdf = gpd.read_file(kml_file_path)
            else:
                gdf = gpd.read_file(temp_file_path)

            # Convert to MultiLineString (automatically converts to 2D)
            multilinestring = gdf_to_multilinestring(gdf)

            # Ensure it's 2D (double-check)
            multilinestring = ensure_2d_geometry(multilinestring)

            # Simple validation using built-in valid property
            validate_path_geometry(multilinestring)

            return multilinestring

        finally:
            # Clean up temporary file
            try:
                Path(temp_file_path).unlink()
            except FileNotFoundError:
                pass  # Ignore cleanup errors

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Error processing {file_format.upper()} file: {str(e)}")


def gdf_to_multilinestring(gdf):
    """
    Convert GeoPandas GeoDataFrame to Django MultiLineString
    Automatically removes Z-coordinates to ensure 2D geometry

    Args:
        gdf: GeoPandas GeoDataFrame

    Returns:
        MultiLineString: Django GIS MultiLineString object (2D only)
    """
    if gdf.empty:
        raise ValidationError("No geometry found in the file")

    # Debug information
    print(f"GeoDataFrame info: {len(gdf)} features")
    print(f"Geometry types: {gdf.geometry.geom_type.value_counts().to_dict()}")
    print(f"CRS: {gdf.crs}")

    # Filter for LineString and MultiLineString geometries
    line_geometries = gdf[gdf.geometry.geom_type.isin(["LineString", "MultiLineString"])]

    if line_geometries.empty:
        # Try to be more flexible - maybe there are other geometry types we can work with
        available_types = gdf.geometry.geom_type.unique().tolist()
        raise ValidationError(
            f"No LineString or MultiLineString geometries found in the file. "
            f"Available geometry types: {available_types}"
        )

    # Collect all LineString segments
    linestrings = []

    for idx, geom in enumerate(line_geometries.geometry):
        try:
            if geom is None or geom.is_empty:
                continue

            if geom.geom_type == "LineString":
                # Convert shapely LineString to Django LineString, remove Z-coordinates
                coords = list(geom.coords)
                # Remove Z-coordinate if present (keep only X, Y)
                coords_2d = [(x, y) for x, y, *_ in coords] if len(coords[0]) > 2 else coords
                if len(coords_2d) >= 2:  # Ensure we have at least 2 points
                    linestrings.append(LineString(coords_2d, srid=4326))

            elif geom.geom_type == "MultiLineString":
                # Extract all LineStrings from MultiLineString
                for line in geom.geoms:
                    coords = list(line.coords)
                    # Remove Z-coordinate if present (keep only X, Y)
                    coords_2d = [(x, y) for x, y, *_ in coords] if len(coords[0]) > 2 else coords
                    if len(coords_2d) >= 2:  # Ensure we have at least 2 points
                        linestrings.append(LineString(coords_2d, srid=4326))

        except Exception as e:
            print(f"Error processing geometry {idx}: {e}")
            continue

    if not linestrings:
        raise ValidationError("No valid line geometries could be extracted from the file. Please check file structure.")

    print(f"Successfully extracted {len(linestrings)} line segments (converted to 2D)")

    # Create MultiLineString from all collected LineStrings
    return MultiLineString(*linestrings)


def validate_path_geometry(geometry):
    """
    Simple validation using Django geometry's built-in valid property

    Args:
        geometry: MultiLineString object to validate

    Raises:
        ValidationError: If geometry is invalid
    """
    if not geometry or geometry.empty:
        raise ValidationError(("❌ Path geometry is empty. Please Check GeoJSON structure."))

    if not isinstance(geometry, MultiLineString):
        raise ValidationError(f"Geometry must be MultiLineString, got {type(geometry)}")

    # Use Django's built-in validation
    if not geometry.valid:
        raise ValidationError(f"Invalid geometry: {geometry.valid_reason}")

    # Basic sanity checks
    if geometry.num_geom == 0:
        raise ValidationError("MultiLineString contains no line segments. Please Check GeoJSON structure.")

    print(f"Geometry validation passed: {geometry.num_geom} segments, valid={geometry.valid}")


def ensure_2d_geometry(geometry):
    """
    Ensure geometry is 2D by removing Z-coordinates if present

    Args:
        geometry: Django GIS geometry object

    Returns:
        geometry: 2D version of the geometry
    """
    if hasattr(geometry, "hasz") and geometry.hasz:
        # Geometry has Z-coordinates, convert to 2D
        if isinstance(geometry, MultiLineString):
            linestrings_2d = []
            for line in geometry:
                coords_2d = [(x, y) for x, y, *_ in line.coords]
                linestrings_2d.append(LineString(coords_2d, srid=geometry.srid))
            return MultiLineString(*linestrings_2d)
        # Add other geometry types as needed

    return geometry


def determine_file_format_from_extension(filename):
    """
    Determine file format from extension

    Args:
        filename: Name of the uploaded file

    Returns:
        str: File format ('geojson', 'kml', 'kmz')
    """
    filename_lower = filename.lower()
    if filename_lower.endswith(".geojson") or filename_lower.endswith(".json"):
        return "geojson"
    elif filename_lower.endswith(".kml"):
        return "kml"
    elif filename_lower.endswith(".kmz"):
        return "kmz"
    else:
        raise ValidationError(f"Unsupported file format. File: {filename}")


def extract_kml_from_kmz(kmz_path, output_kml_path):
    with zipfile.ZipFile(kmz_path, "r") as kmz:
        for file in kmz.namelist():
            if file.endswith(".kml"):
                with kmz.open(file) as kml_file, open(output_kml_path, "wb") as out_file:
                    out_file.write(kml_file.read())
                return output_kml_path
    raise FileNotFoundError("No .kml file found in KMZ archive")


# Utility functions for working with existing segments
def export_segment_paths_as_geojson(segments):
    """
    Export multiple segments' paths as a GeoJSON FeatureCollection using GeoPandas

    Args:
        segments: QuerySet or list of Segment objects

    Returns:
        str: GeoJSON string
    """
    import json
    from shapely.geometry import MultiLineString as ShapelyMultiLineString

    features_data = []

    for segment in segments:
        if segment.path_geometry:
            # Convert Django MultiLineString to Shapely MultiLineString
            coords = []
            for line in segment.path_geometry:
                coords.append(list(line.coords))

            shapely_geom = ShapelyMultiLineString(coords)

            features_data.append(
                {
                    "geometry": shapely_geom,
                    "name": segment.name,
                    "id": segment.pk,
                    "network_label": segment.network_label,
                    "status": segment.status,
                    "length_km": float(segment.path_length_km) if segment.path_length_km else None,
                    "provider": str(segment.provider),
                    "site_a": str(segment.site_a),
                    "site_b": str(segment.site_b),
                    "segment_count": segment.get_path_segment_count(),
                    "total_points": segment.get_total_points(),
                }
            )

    if features_data:
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(features_data, crs="EPSG:4326")
        # Convert to GeoJSON
        return gdf.to_json()
    else:
        # Return empty FeatureCollection
        return json.dumps({"type": "FeatureCollection", "features": []})


# Main processing function for forms
def process_path_data(uploaded_file, file_format=None):
    """
    Main function to process path data from uploaded file

    Args:
        uploaded_file: Django uploaded file object
        file_format: Optional format override, auto-detected if None

    Returns:
        MultiLineString: Validated MultiLineString object
    """
    if file_format is None:
        file_format = determine_file_format_from_extension(uploaded_file.name)

    return process_path_file(uploaded_file, file_format)
