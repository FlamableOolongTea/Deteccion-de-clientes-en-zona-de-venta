#!/usr/bin/env python3
"""
Script to check if client coordinates are inside the sales zone defined in a KML file.
Uses geopandas, shapely, pandas, and fiona.
"""

import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd
import fiona

# Enable KML support in fiona
fiona.supported_drivers['KML'] = 'rw'

def parse_coordinates(coord_string):
    """
    Parse coordinate string from CSV (format: 'lat,lon')
    Returns a Point geometry or None if invalid
    """
    try:
        if pd.isna(coord_string):
            return None
        # Split by comma and convert to float
        lat, lon = map(float, str(coord_string).split(','))
        # Create Point with lon, lat order (standard for GIS)
        return Point(lon, lat)
    except Exception as e:
        print(f"Error parsing coordinates '{coord_string}': {e}")
        return None

def main():
    # File paths
    csv_file = 'direccion_f_clientes.csv'
    kml_file = 'ZonaMendi.kml'
    output_file = 'clientes_con_zonaC.csv'
    
    print("Loading client data from CSV...")
    # Read CSV with semicolon separator and handle encoding
    df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
    
    print(f"Loaded {len(df)} clients")
    print(f"Columns: {df.columns.tolist()}")
    
    # Create geometry column from GPS coordinates
    print("\nParsing GPS coordinates...")
    df['geometry'] = df['Punto gps'].apply(parse_coordinates)
    
    # Count valid coordinates
    valid_coords = df['geometry'].notna().sum()
    print(f"Valid coordinates: {valid_coords}/{len(df)}")
    
    # Create GeoDataFrame with WGS84 coordinate system (EPSG:4326)
    gdf_clients = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
    
    # Load KML file
    print("\nLoading KML zone polygons...")
    gdf_zones = gpd.read_file(kml_file, driver='KML')
    
    print(f"Loaded {len(gdf_zones)} zones from KML")
    if 'Name' in gdf_zones.columns:
        print(f"Zone names: {gdf_zones['Name'].tolist()}")
    
    # Ensure both GeoDataFrames use the same CRS
    if gdf_zones.crs != gdf_clients.crs:
        print(f"Converting zone CRS from {gdf_zones.crs} to {gdf_clients.crs}")
        gdf_zones = gdf_zones.to_crs(gdf_clients.crs)
    
    # Combine all polygons into one unified zone using unary_union
    print("\nCombining all zone polygons...")
    from shapely.ops import unary_union
    combined_zone = unary_union(gdf_zones.geometry)
    
    # Check if each client point is inside the combined zone
    print("\nChecking which clients are inside the zone...")
    def point_in_zone(geom):
        if geom is None or geom.is_empty:
            return False
        return combined_zone.contains(geom)
    
    gdf_clients['Inside_Zone'] = gdf_clients['geometry'].apply(point_in_zone)
    
    # Count results
    inside_count = gdf_clients['Inside_Zone'].sum()
    outside_count = (~gdf_clients['Inside_Zone']).sum()
    
    print(f"\nResults:")
    print(f"  Clients inside zone: {inside_count}")
    print(f"  Clients outside zone: {outside_count}")
    
    # Prepare output dataframe (drop geometry column for CSV export)
    output_df = gdf_clients.drop(columns=['geometry'])
    
    # Save to CSV
    print(f"\nSaving results to {output_file}...")
    output_df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
    
    print("Done!")
    
    # Display sample results
    print("\nSample results (first 10 clients):")
    print(output_df[['Codigo', 'Punto gps', 'Inside_Zone']].head(10))
    
    print("\nSummary by Inside_Zone:")
    print(output_df['Inside_Zone'].value_counts())

if __name__ == "__main__":
    main()