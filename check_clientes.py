#!/usr/bin/env python3
"""
Script to check if client coordinates are inside the sales zone defined in a KML file.
Uses pure Python without external GIS libraries.
"""

import pandas as pd
import xml.etree.ElementTree as ET
from typing import List, Tuple

class Point:
    """Simple Point class for coordinates"""
    def __init__(self, lon: float, lat: float):
        self.lon = lon
        self.lat = lat
    
    def __repr__(self):
        return f"Point({self.lon}, {self.lat})"

class Polygon:
    """Simple Polygon class with point-in-polygon test"""
    def __init__(self, coordinates: List[Tuple[float, float]]):
        self.coordinates = coordinates
    
    def contains_point(self, point: Point) -> bool:
        """
        Ray casting algorithm to determine if point is inside polygon
        https://en.wikipedia.org/wiki/Point_in_polygon
        """
        x, y = point.lon, point.lat
        n = len(self.coordinates)
        inside = False
        
        p1x, p1y = self.coordinates[0]
        for i in range(1, n + 1):
            p2x, p2y = self.coordinates[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside

def parse_kml_coordinates(coord_string: str) -> List[Tuple[float, float]]:
    """
    Parse KML coordinate string into list of (lon, lat) tuples
    KML format: 'lon,lat,elevation lon,lat,elevation ...'
    """
    coords = []
    for coord_set in coord_string.strip().split():
        parts = coord_set.split(',')
        if len(parts) >= 2:
            try:
                lon, lat = float(parts[0]), float(parts[1])
                coords.append((lon, lat))
            except ValueError:
                continue
    return coords

def load_kml_polygons(kml_file: str) -> List[Polygon]:
    """Load all polygons from KML file"""
    tree = ET.parse(kml_file)
    root = tree.getroot()
    
    # Define KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    polygons = []
    
    # Find all Polygon elements
    for polygon_elem in root.findall('.//kml:Polygon', ns):
        # Get outer boundary coordinates
        outer_boundary = polygon_elem.find('.//kml:outerBoundaryIs//kml:coordinates', ns)
        if outer_boundary is not None and outer_boundary.text:
            coords = parse_kml_coordinates(outer_boundary.text)
            if len(coords) >= 3:  # Valid polygon needs at least 3 points
                polygons.append(Polygon(coords))
    
    return polygons

def parse_client_coordinates(coord_string) -> Point:
    """
    Parse coordinate string from CSV (format: 'lat,lon')
    Returns a Point or None if invalid
    """
    try:
        if pd.isna(coord_string):
            return None
        # Split by comma and convert to float
        lat, lon = map(float, str(coord_string).split(','))
        return Point(lon, lat)
    except Exception as e:
        print(f"Error parsing coordinates '{coord_string}': {e}")
        return None

def point_in_any_polygon(point: Point, polygons: List[Polygon]) -> bool:
    """Check if point is inside any of the polygons"""
    if point is None:
        return False
    
    for polygon in polygons:
        if polygon.contains_point(point):
            return True
    return False

def main():
    # File paths
    csv_file = 'C:/Proyects/PuntoGps/direccion_f_clientes.csv'
    kml_file = 'C:/Proyects/PuntoGps/ZonaMendi.kml'
    output_file = 'C:/Proyects/PuntoGps/clientes_con_zona.csv'
    
    print("Loading client data from CSV...")
    # Read CSV with semicolon separator and handle encoding
    df = pd.read_csv(csv_file, sep=';', encoding='utf-8-sig')
    
    print(f"Loaded {len(df)} clients")
    print(f"Columns: {df.columns.tolist()}")
    
    # Load KML polygons
    print("\nLoading KML zone polygons...")
    polygons = load_kml_polygons(kml_file)
    print(f"Loaded {len(polygons)} polygons from KML")
    
    # Parse client coordinates
    print("\nParsing GPS coordinates...")
    df['_point'] = df['Punto gps'].apply(parse_client_coordinates)
    
    # Count valid coordinates
    valid_coords = df['_point'].notna().sum()
    print(f"Valid coordinates: {valid_coords}/{len(df)}")
    
    # Check if each client point is inside any zone
    print("\nChecking which clients are inside the zone...")
    df['Inside_Zone'] = df['_point'].apply(lambda p: point_in_any_polygon(p, polygons))
    
    # Count results
    inside_count = df['Inside_Zone'].sum()
    outside_count = (~df['Inside_Zone']).sum()
    
    print(f"\nResults:")
    print(f"  Clients inside zone: {inside_count}")
    print(f"  Clients outside zone: {outside_count}")
    
    # Remove temporary column
    output_df = df.drop(columns=['_point'])
    
    # Save to CSV
    print(f"\nSaving results to {output_file}...")
    output_df.to_csv(output_file, sep=';', index=False, encoding='utf-8-sig')
    
    print("Done!")
    
    # Display sample results
    print("\nSample results (first 10 clients):")
    print(output_df[['Codigo', 'Punto gps', 'Inside_Zone']].head(10).to_string())
    
    print("\nSummary by Inside_Zone:")
    print(output_df['Inside_Zone'].value_counts())
    
    return output_df

if __name__ == "__main__":
    result = main()