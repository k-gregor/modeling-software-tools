import pytest
from shapely.geometry import Point
import xarray as xr

from create_gridlist_for_region import arcsecs_to_degrees, get_polygon_for_region, get_gridlist_from_climate_data_and_region

TOLERANCE = 0.00001
BERLIN_LAT, BERLIN_LON = 52.5098016,13.4135867
MUNICH_LAT, MUNICH_LON = 48.1397434,11.6083029
PARIS_LAT, PARIS_LON = 48.8519125,2.3443399

def test_arcsecs_to_degrees():
    assert arcsecs_to_degrees('1800arcsec') == 0.5
    assert arcsecs_to_degrees('300arcsec') == pytest.approx(0.083333, TOLERANCE)

def test_bad_format_raises_error():
    with pytest.raises(ValueError):
        arcsecs_to_degrees('wronginput')

def test_retrieved_region_contains_expected_coordinates_for_countries():

    germany_polygon = get_polygon_for_region('Germany', 'admin_0_countries')

    assert germany_polygon.iloc[0].contains(Point(BERLIN_LON, BERLIN_LAT)) == True
    assert germany_polygon.iloc[0].contains(Point(MUNICH_LON, MUNICH_LAT)) == True
    assert germany_polygon.iloc[0].contains(Point(PARIS_LON, PARIS_LAT)) == False

def test_retrieved_region_contains_expected_coordinates_for_states():

    berlin_polygon = get_polygon_for_region('Berlin', 'admin_1_states_provinces')

    assert berlin_polygon.iloc[0].contains(Point(BERLIN_LON, BERLIN_LAT)) == True
    assert berlin_polygon.iloc[0].contains(Point(MUNICH_LON, MUNICH_LAT)) == False

def test_create_gridlist_for_region_gets_climate_coordinates_within_region():

    # dummy_temp.nc contains one single grid cell aroud Munich
    _, gridlist_points_in_germany, _ = get_gridlist_from_climate_data_and_region('testing/testing_resources/dummy_temp.nc', ['Germany'], 'admin_0_countries')
    assert len(gridlist_points_in_germany) == 1

    _, gridlist_points_in_france_and_germany, _ = get_gridlist_from_climate_data_and_region('testing/testing_resources/dummy_temp.nc', ['France', 'Germany'], 'admin_0_countries')
    assert len(gridlist_points_in_france_and_germany) == 1

    _, gridlist_points_in_france, _ = get_gridlist_from_climate_data_and_region('testing/testing_resources/dummy_temp.nc', ['France'], 'admin_0_countries')
    assert len(gridlist_points_in_france) == 0