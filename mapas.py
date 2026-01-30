import geopandas as gpd
from shapely.geometry import Point, Polygon
import pandas as pd
import fiona

fiona.drvsupport.supported_drivers['KML'] = 'rw'
output_file = 'ClientesConfirmacion.csv'
my_map = gpd.read_file('ZonaMendi.kml', driver='KML')
#------------------- funciones-----------------------
def acomoda_coordinates(coord_string):
    try:
        if pd.isna(coord_string):
            return None
        
        lat, lon = map(float, str(coord_string).split(','))
       
        return Point(lon, lat)
    except Exception as e:
        print(f"Error parsing coordinates '{coord_string}': {e}")
        return None

def la_tiene_adentro(geo):
    if geo is None or geo.is_empty:
        return False
    return combined_zone.covers(geo)
#------------------- main-----------------------


locations = pd.read_csv('direccion_f_clientes.csv',sep=';', encoding='utf-8-sig')
print(locations)

locations['geometry'] = locations['Punto gps'].apply(acomoda_coordinates)

print(locations)

gdf_clientes =gpd.GeoDataFrame(locations,geometry='geometry',crs ='EPSG:4326')

if my_map.crs != gdf_clientes.crs:
    print("el sistema es distinto wachin")
    my_map = my_map.to_crs(gdf_clientes.crs)
else:
    print("estas usandolo bien")
#Esta funcion convierte los poligonos del mapa .kml en una zona para leerlo
print("\nCombining all zone polygons...")
from shapely.ops import unary_union
combined_zone = unary_union(my_map.geometry)

gdf_clientes['chequeo gps']=gdf_clientes.geometry.apply(la_tiene_adentro)
print("\nImprimiendo la lista con los clientes")
print(gdf_clientes)
gdf_clientes = gdf_clientes.drop(columns='geometry')
gdf_clientes = gdf_clientes.drop(columns='')
print(gdf_clientes)


gdf_clientes.to_csv('ClientesGpsConfirmado')