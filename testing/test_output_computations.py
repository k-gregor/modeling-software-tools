import pytest

import output_computations as target
import pandas as pd
import numpy as np

TOLERANCE = 0.0001

def test_length_of_longitude_northern_hemisphere():
    assert target.compute_length_of_longitude(0) == pytest.approx(111320, rel=TOLERANCE)
    assert target.compute_length_of_longitude(15) == pytest.approx(107550, rel=TOLERANCE)
    assert target.compute_length_of_longitude(30) == pytest.approx(96486, rel=TOLERANCE)
    assert target.compute_length_of_longitude(45) == pytest.approx(78847, rel=TOLERANCE)
    assert target.compute_length_of_longitude(60) == pytest.approx(55800, rel=TOLERANCE)
    assert target.compute_length_of_longitude(75) == pytest.approx(28902, rel=TOLERANCE)
    assert target.compute_length_of_longitude(90) == pytest.approx(0, abs=1e-10)

def test_length_of_longitude_southern_hemisphere():
    assert target.compute_length_of_longitude(-15) == pytest.approx(107551, rel=TOLERANCE)
    assert target.compute_length_of_longitude(-30) == pytest.approx(96486, rel=TOLERANCE)
    assert target.compute_length_of_longitude(-45) == pytest.approx(78847, rel=TOLERANCE)
    assert target.compute_length_of_longitude(-60) == pytest.approx(55800, rel=TOLERANCE)
    assert target.compute_length_of_longitude(-75) == pytest.approx(28902, rel=TOLERANCE)
    assert target.compute_length_of_longitude(-90) == pytest.approx(0, abs=TOLERANCE)



def test_length_of_latitude():
    assert target.compute_length_of_latitude(0) == pytest.approx(110574, rel=TOLERANCE)
    assert target.compute_length_of_latitude(15) == pytest.approx(110649, rel=TOLERANCE)
    assert target.compute_length_of_latitude(30) == pytest.approx(110852, rel=TOLERANCE)
    assert target.compute_length_of_latitude(45) == pytest.approx(111132, rel=TOLERANCE)
    assert target.compute_length_of_latitude(60) == pytest.approx(111412, rel=TOLERANCE)
    assert target.compute_length_of_latitude(75) == pytest.approx(111618, rel=TOLERANCE)
    assert target.compute_length_of_latitude(90) == pytest.approx(111694, rel=TOLERANCE)

    assert target.compute_length_of_latitude(-15) == pytest.approx(110649, rel=TOLERANCE)
    assert target.compute_length_of_latitude(-30) == pytest.approx(110852, rel=TOLERANCE)
    assert target.compute_length_of_latitude(-45) == pytest.approx(111132, rel=TOLERANCE)
    assert target.compute_length_of_latitude(-60) == pytest.approx(111412, rel=TOLERANCE)
    assert target.compute_length_of_latitude(-75) == pytest.approx(111618, rel=TOLERANCE)
    assert target.compute_length_of_latitude(-90) == pytest.approx(111694, rel=TOLERANCE)

def test_aggregation_of_ones_result_in_total_area_for_each_year():
    cpool_bavaria_data = pd.read_csv('testing/testing_resources/bavaria_cpool_two_years.out', sep='\\s+').set_index(['Lon', 'Lat', 'Year'])
    total_value = target.get_total_value_per_year(cpool_bavaria_data, variable_name='VegC')

    bavaria_area_km2 = 70_550
    m2_to_km2 = 1_000_000

    # allowing for a large tolerance here, because the simulation outputs are in 0.5 degree resolution.
    # so the aggregation will result in the total area of the simulated region, but only roughly.
    assert total_value.loc[2019]/m2_to_km2 == pytest.approx(bavaria_area_km2, rel=0.05)
    assert total_value.loc[2020]/m2_to_km2 == pytest.approx(bavaria_area_km2, rel=0.05)
