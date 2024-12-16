from math import sin, cos, pi, radians, sqrt
import numpy as np

# calculation from https://en.wikipedia.org/wiki/Longitude#Length_of_a_degree_of_longitude
def compute_length_of_longitude(degree_lat):
    assert degree_lat >= -90 and degree_lat <= 90

    a = 6378137.0
    b = 6356752.3142
    e = sqrt((a**2 - b**2)/a**2)
    return (pi * a * cos(radians(degree_lat))) / (180 * sqrt(1 - e ** 2 * (sin(radians(degree_lat)) ** 2)))


# calculation from https://en.wikipedia.org/wiki/Longitude#Length_of_a_degree_of_longitude
def compute_length_of_latitude(degree_lat):
    assert degree_lat >= -90 and degree_lat <= 90

    l_lat = np.abs(111132.954 - 559.822 * cos(2 * radians(degree_lat)) + 1.175 * cos(4 * radians(degree_lat)))
    return l_lat

# trapezoid shape
# lat_frac: length of one gridcell (latitude-wise), e.g. 0.5
def get_area_for_lat(lat, lat_frac = 0.5, lon_frac = 0.5):
    assert lat >= -90 and lat <= 90

    lat_length = compute_length_of_latitude(lat) * lat_frac
    lon_top_length = compute_length_of_longitude(lat + lat_frac / 2)
    lon_bottom_length = compute_length_of_longitude(lat - lat_frac / 2)
    small_lon_length = min(lon_top_length, lon_bottom_length) * lon_frac
    long_lon_length = max(lon_top_length, lon_bottom_length) * lon_frac
    area = lat_length * small_lon_length + lat_length * (long_lon_length - small_lon_length) / 2 #last 2 is for the triangle area

    return area


def get_total_value_per_year(lon_lat_dataset, variable_name, lat_frac=0.5, lon_frac=0.5):
    assert lon_lat_dataset.index.names == ['Lon', 'Lat', 'Year'], "Index does not contain Lon, Lat, Year"
    assert lon_lat_dataset.index.is_unique, "Index is not unique"
    assert np.all(~np.isnan(lon_lat_dataset)), "NaNs in dataset!"

    areas = lon_lat_dataset.index.get_level_values('Lat').map(lambda x: get_area_for_lat(x, lon_frac=lon_frac, lat_frac=lat_frac))
    total_values_per_gridcell = areas * lon_lat_dataset[variable_name]

    return total_values_per_gridcell.groupby('Year').sum()
