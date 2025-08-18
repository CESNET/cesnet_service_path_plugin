"""
Simplified utility functions for handling GIS data using GeoPandas
"""

import os
import tempfile
import zipfile
from pathlib import Path
import logging

import geopandas as gpd
from django.contrib.gis.geos import MultiLineString, LineString
from django.core.exceptions import ValidationError

# Create a logger for this module
logger = logging.getLogger(__name__)


def check_gis_environment():
    """
    Check if GIS environment is properly configured
    Call this in Django shell on production to diagnose issues
    """
    import fiona
    import geopandas as gpd
    import tempfile
    import os

    logger.info("=== GIS Environment Check ===")
    logger.info(f"GeoPandas version: {gpd.__version__}")
    logger.info(f"Fiona version: {fiona.__version__}")
    logger.info(f"Supported drivers: {list(fiona.supported_drivers.keys())}")
    logger.info(f"KML driver available: {'KML' in fiona.supported_drivers}")
    logger.info(f"Temp directory: {tempfile.gettempdir()}")
    logger.info(f"Temp dir writable: {os.access(tempfile.gettempdir(), os.W_OK)}")

    # Test creating a temp file
    try:
        with tempfile.NamedTemporaryFile(suffix=".kml") as tmp:
            logger.info(f"Can create temp files: True ({tmp.name})")
    except Exception as e:
        logger.error(f"Cannot create temp files: {e}")

    return True


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
            if file_format == "kmz":
                # Enhanced KMZ handling for complex files
                gdf = read_kmz_file(temp_file_path)
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


def read_kmz_file(kmz_path):
    """
    Enhanced KMZ file reader that handles complex KMZ structures

    Args:
        kmz_path: Path to KMZ file

    Returns:
        GeoDataFrame: Combined data from all KML files in the KMZ
    """
    logger.debug(f"🔍 Reading KMZ file: {kmz_path}")
    try:
        # First, try direct GeoPandas reading (works for simple KMZ files)
        logger.debug(f"🔍 Attempting direct read of {kmz_path}")
        return gpd.read_file(kmz_path)
    except Exception as e:
        logger.warning(f"🔍 Direct KMZ reading failed: {e}. Trying extraction method...")
        return _read_kmz_by_extraction(kmz_path)


def _read_kmz_by_extraction(kmz_path):
    """
    Fallback method: extract all KML files and combine them, reading ALL layers
    """
    temp_dir = None
    try:
        logger.debug(f"🔍 Starting KMZ extraction from {kmz_path}")
        logger.debug(f"🔍 KMZ file exists: {Path(kmz_path).exists()}")
        logger.debug(f"🔍 KMZ file size: {Path(kmz_path).stat().st_size if Path(kmz_path).exists() else 'N/A'} bytes")

        # Create temporary directory for extraction with explicit permissions
        temp_dir = tempfile.mkdtemp(prefix="kmz_extract_")
        os.chmod(temp_dir, 0o755)  # Ensure proper permissions
        logger.debug(f"🔍 Created temp directory: {temp_dir}")
        logger.debug(f"🔍 Temp dir writable: {os.access(temp_dir, os.W_OK)}")

        # Extract all KML files from KMZ
        kml_files = extract_all_kml_from_kmz(kmz_path, temp_dir)
        logger.debug(f"🔍 Extracted KML files: {kml_files}")

        if not kml_files:
            raise ValidationError("No KML files found in KMZ archive")

        # Read all KML files and ALL their layers, then combine them
        all_gdfs = []
        for kml_file in kml_files:
            try:
                logger.debug(f"🔍 Processing KML file: {Path(kml_file).name}")
                logger.debug(f"🔍 KML file exists: {Path(kml_file).exists()}")
                logger.debug(
                    f"🔍 KML file size: {Path(kml_file).stat().st_size if Path(kml_file).exists() else 'N/A'} bytes"
                )
                logger.debug(
                    f"🔍 KML file readable: {os.access(kml_file, os.R_OK) if Path(kml_file).exists() else 'N/A'}"
                )

                # Read all layers from this KML file
                layer_gdfs = read_all_kml_layers(kml_file)
                logger.debug(f"🔍 Got {len(layer_gdfs)} layer(s) from {Path(kml_file).name}")
                all_gdfs.extend(layer_gdfs)
                logger.info(f"🔍 Successfully loaded {len(layer_gdfs)} layer(s) from {Path(kml_file).name}")
            except Exception as e:
                logger.error(f"🔍 Could not load {kml_file}: {e}")
                logger.error(f"🔍 Exception type: {type(e)}")
                import traceback

                logger.error(f"🔍 Traceback: {traceback.format_exc()}")
                continue

        logger.debug(f"🔍 Total GeoDataFrames collected: {len(all_gdfs)}")

        if not all_gdfs:
            # Additional debugging before raising error
            logger.error("🔍 No GeoDataFrames were successfully created")
            logger.error(f"🔍 Original KML files found: {kml_files}")
            for kml_file in kml_files:
                if Path(kml_file).exists():
                    logger.error(f"🔍 {kml_file} exists with size {Path(kml_file).stat().st_size}")
                    # Try to read first few lines
                    try:
                        with open(kml_file, "r", encoding="utf-8") as f:
                            first_lines = f.read(500)
                            logger.error(f"🔍 First 500 chars of {Path(kml_file).name}: {repr(first_lines)}")
                    except Exception as read_error:
                        logger.error(f"🔍 Could not read KML file content: {read_error}")
                else:
                    logger.error(f"🔍 {kml_file} does not exist after extraction")

            raise ValidationError("Could not load any layers from the KMZ archive")

        # Combine all GeoDataFrames from all layers
        if len(all_gdfs) == 1:
            combined_gdf = all_gdfs[0]
        else:
            # Concatenate all GeoDataFrames
            combined_gdf = gpd.GeoDataFrame(gpd.pd.concat(all_gdfs, ignore_index=True), crs=all_gdfs[0].crs)
            logger.info(
                f"🔍 Combined {len(all_gdfs)} layer(s) into single GeoDataFrame with {len(combined_gdf)} total features"
            )

        return combined_gdf

    except ValidationError:
        raise  # Re-raise validation errors as-is
    except Exception as e:
        logger.error(f"🔍 Unexpected error in _read_kmz_by_extraction: {e}")
        logger.error(f"🔍 Exception type: {type(e)}")
        import traceback

        logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
        raise ValidationError(f"Failed to extract KMZ file: {str(e)}")

    finally:
        # Clean up temporary directory
        if temp_dir and Path(temp_dir).exists():
            try:
                import shutil

                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.debug(f"🔍 Cleaned up temp directory: {temp_dir}")
            except Exception as cleanup_error:
                logger.warning(f"🔍 Could not clean up temp directory {temp_dir}: {cleanup_error}")


def read_all_kml_layers(kml_file):
    """
    Read all layers from a KML file

    Args:
        kml_file: Path to KML file

    Returns:
        List[GeoDataFrame]: List of GeoDataFrames, one per layer
    """
    import fiona

    layer_gdfs = []

    try:
        logger.debug(f"🔍 Attempting to read layers from {kml_file}")
        logger.debug(f"🔍 File exists: {Path(kml_file).exists()}")

        if not Path(kml_file).exists():
            logger.error(f"🔍 KML file does not exist: {kml_file}")
            return layer_gdfs

        # Get all layer names from the KML file
        try:
            layers = fiona.listlayers(kml_file)
            logger.debug(f"🔍 Found {len(layers)} layer(s) in {Path(kml_file).name}: {layers}")
        except Exception as list_error:
            logger.error(f"🔍 Could not list layers in {kml_file}: {list_error}")
            logger.error(f"🔍 fiona.listlayers exception type: {type(list_error)}")
            # Try fallback immediately
            layers = []

        if layers:
            for layer_name in layers:
                try:
                    logger.debug(f"🔍 Reading layer '{layer_name}'")
                    # Read each layer explicitly
                    gdf = gpd.read_file(kml_file, layer=layer_name)
                    if not gdf.empty:
                        # Add metadata about source
                        gdf["source_kml"] = Path(kml_file).name
                        gdf["source_layer"] = layer_name
                        layer_gdfs.append(gdf)
                        logger.debug(
                            f"🔍 Layer '{layer_name}': {len(gdf)} features, geometry types: {gdf.geometry.geom_type.value_counts().to_dict()}"
                        )
                    else:
                        logger.debug(f"🔍 Layer '{layer_name}': empty")
                except Exception as layer_error:
                    logger.error(f"🔍 Could not read layer '{layer_name}': {layer_error}")
                    logger.error(f"🔍 Layer read exception type: {type(layer_error)}")
                    continue
        else:
            logger.debug("🔍 No layers found or layer listing failed, trying default read")

        # Fallback to default reading if no layers were processed or layer listing failed
        if not layer_gdfs:
            try:
                logger.debug(f"🔍 Attempting default read of {kml_file}")
                gdf = gpd.read_file(kml_file)
                if not gdf.empty:
                    gdf["source_kml"] = Path(kml_file).name
                    gdf["source_layer"] = "default"
                    layer_gdfs.append(gdf)
                    logger.debug(f"🔍 Default read successful: {len(gdf)} features")
                else:
                    logger.debug("🔍 Default read returned empty GeoDataFrame")
            except Exception as fallback_error:
                logger.error(f"🔍 Fallback read also failed: {fallback_error}")
                logger.error(f"🔍 Fallback exception type: {type(fallback_error)}")

                # Try to diagnose the issue
                try:
                    with open(kml_file, "r", encoding="utf-8") as f:
                        content_sample = f.read(1000)
                        logger.error(f"🔍 KML file content sample (first 1000 chars): {repr(content_sample)}")
                except Exception as read_error:
                    logger.error(f"🔍 Could not even read KML file as text: {read_error}")

    except Exception as outer_error:
        logger.error(f"🔍 Outer exception in read_all_kml_layers: {outer_error}")
        logger.error(f"🔍 Outer exception type: {type(outer_error)}")
        import traceback

        logger.error(f"🔍 Full traceback: {traceback.format_exc()}")

    logger.debug(f"🔍 Returning {len(layer_gdfs)} layer GeoDataFrames")
    return layer_gdfs


def extract_all_kml_from_kmz(kmz_path, output_dir):
    """
    Extract ALL KML files from a KMZ archive (not just the first one)

    Args:
        kmz_path: Path to the KMZ file
        output_dir: Directory to extract KML files to

    Returns:
        List[str]: List of paths to extracted KML files
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    extracted_files = []

    with zipfile.ZipFile(kmz_path, "r") as kmz:
        kml_files = [f for f in kmz.namelist() if f.endswith(".kml")]

        if not kml_files:
            raise FileNotFoundError("No .kml files found in KMZ archive")

        logger.debug(f"🔍 Found {len(kml_files)} KML file(s) in KMZ: {kml_files}")

        for kml_file in kml_files:
            # Generate unique output filename to avoid conflicts
            output_filename = Path(kml_file).name
            if not output_filename:  # Handle nested paths
                output_filename = kml_file.replace("/", "_").replace("\\", "_")

            output_path = Path(output_dir) / output_filename

            # Handle duplicate filenames by adding counter
            counter = 1
            original_path = output_path
            while output_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                output_path = original_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1

            # Extract the KML file
            with kmz.open(kml_file) as kml_content:
                with open(output_path, "wb") as out_file:
                    out_file.write(kml_content.read())

            extracted_files.append(str(output_path))
            logger.debug(f"🔍 Extracted: {kml_file} -> {output_path}")

    return extracted_files


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
    logger.debug(f"🔍 GeoDataFrame info: {len(gdf)} features")
    logger.debug(f"🔍 Geometry types: {gdf.geometry.geom_type.value_counts().to_dict()}")
    logger.debug(f"🔍 CRS: {gdf.crs}")

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
            logger.error(f"🔍 Error processing geometry {idx}: {e}")
            continue

    if not linestrings:
        raise ValidationError("No valid line geometries could be extracted from the file. Please check file structure.")

    logger.info(f"🔍 Successfully extracted {len(linestrings)} line segments (converted to 2D)")

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

    logger.info(f"🔍 Geometry validation passed: {geometry.num_geom} segments, valid={geometry.valid}")


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


# Legacy function - kept for backward compatibility but now just calls extract_all_kml_from_kmz
def extract_kml_from_kmz(kmz_path, output_kml_path):
    """
    Legacy function - extracts first KML file only
    Consider using extract_all_kml_from_kmz for complex KMZ files
    """
    output_dir = Path(output_kml_path).parent
    kml_files = extract_all_kml_from_kmz(kmz_path, output_dir)

    if kml_files:
        # For backward compatibility, copy first file to expected output path
        import shutil

        shutil.copy2(kml_files[0], output_kml_path)
        return output_kml_path
    else:
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
