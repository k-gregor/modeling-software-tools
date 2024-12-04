import pandas as pd
import geopandas
from shapely.geometry import Point
from shapely.ops import unary_union
import cartopy.crs as ccrs
from cartopy.io import shapereader
import matplotlib.pyplot as plt
import xarray as xr
import sys

def arcsecs_to_degrees(resolution_str):
    """
    Convert the ISIMIP resolution strings like '1800arcsec' into degrees.
    """
    if resolution_str.endswith("arcsec"):
        arcseconds = int(resolution_str.replace("arcsec", ""))
        return arcseconds / 3600.0
    else:
        raise ValueError("Invalid format. Expected string like '1800arcsec'.")


def get_polygon_for_region(natural_earth_regionname, natural_earth_regiontype):
    name_column = 'name' if natural_earth_regiontype == 'admin_1_states_provinces' else 'NAME'

    shpfilename = shapereader.natural_earth(resolution='10m', category='cultural', name=natural_earth_regiontype)
    df = geopandas.read_file(shpfilename)

    regional_df = df.loc[df[name_column] == natural_earth_regionname]['geometry']
    assert(len(regional_df) > 0), "Polygon is empy! For region "+natural_earth_regionname+' '+natural_earth_regiontype

    return regional_df


def create_gridlist_for_region(tas, poly, regionnames):

    region_gridlist = []
    region_gridlist_cf = []

    x_coords = tas.lon
    y_coords = tas.lat
    grid_points = [Point(x, y) for x in x_coords for y in y_coords]
    grid_points_cf = [(x, y) for x in range(len(x_coords)) for y in range(len(y_coords))]

    print('Assessing', len(grid_points), 'potential grid points')

    for idx, sub_poly in enumerate(poly):
        print('Dealing with sub-polygon', idx+1, 'of', len(poly), ', regionname:', regionnames[idx])

        assert len(sub_poly.bounds['minx'].values) == 1, "Polygon has multiple bounds..."
        assert len(sub_poly.bounds['maxx'].values) == 1, "Polygon has multiple bounds..."
        assert len(sub_poly.bounds['miny'].values) == 1, "Polygon has multiple bounds..."
        assert len(sub_poly.bounds['maxy'].values) == 1, "Polygon has multiple bounds..."

        assert len(sub_poly) == 1, "Sub POLY has more than one entry! That means the code needs to be adapted. Maybe it is because the region consists of multiple polygons?"

        grid_points_within_subpolygon = []
        grid_points_cf_within_subpolygon = []
        for idx, point in enumerate(grid_points):

            if idx % 2000 == 0 and idx>0 :
                print(idx, 'grid points done')

            # the `contains` function of a polygon can be costly, better reduce the amount of calls, so exlude points that are definitely not within the polygon
            if point.x < sub_poly.bounds['minx'].values[0] or point.x > sub_poly.bounds['maxx'].values[0] or point.y < sub_poly.bounds['miny'].values[0] or point.y > sub_poly.bounds['maxy'].values[0]:
                continue

            if sub_poly.iloc[0].contains(point):
                grid_points_within_subpolygon.append(point)
                grid_points_cf_within_subpolygon.append(grid_points_cf[idx])

        print('Found', len(grid_points_within_subpolygon), 'climate data points to be within the given region')

        grid_coordinates = [(point.x, point.y) for point in grid_points_within_subpolygon]

        region_gridlist += grid_coordinates
        region_gridlist_cf += grid_points_cf_within_subpolygon

    return region_gridlist, region_gridlist_cf


def plot_gridlist(resolution_isimip_string, region_poly, gridlist):
    resolution_degrees = arcsecs_to_degrees(resolution_isimip_string)
    fig, ax = plt.subplots(1, 2, figsize=(18, 9), subplot_kw=dict(projection=ccrs.PlateCarree()))
    ax[0].coastlines(alpha=0.2, resolution='110m')
    ax[0].add_geometries(region_poly, crs=ccrs.PlateCarree(), facecolor='navy', edgecolor='0.5')
    ax[1].set_extent([gridlist_df[0].min() - resolution_degrees, gridlist_df[0].max() + resolution_degrees,
                      gridlist_df[1].min() - resolution_degrees, gridlist_df[1].max() + resolution_degrees],
                     crs=ccrs.PlateCarree())
    ax[1].coastlines(alpha=0.2, resolution='110m')
    ax[1].add_geometries(region_poly, crs=ccrs.PlateCarree(), facecolor='None', edgecolor='0.5')
    for point in gridlist:
        ax[1].scatter(x=point[0], y=point[1], color='navy')
    fig.savefig(outputfile + '.png', dpi=300, bbox_inches='tight')


def get_gridlist_from_climate_data_and_region(climate_file, naturalearth_regionnames, naturalearth_regiontype):
    assert isinstance(naturalearth_regionnames, list), "Regionnnames are not provided as list!"

    print('Reading climate data', climate_file)
    climate_data = xr.open_dataset(climate_file)
    subregion_polygons = []
    for subregion_name in naturalearth_regionnames:
        subregion_polygons.append(get_polygon_for_region(subregion_name, naturalearth_regiontype))
    region_poly = unary_union(subregion_polygons)
    gridlist, gridlist_cf = create_gridlist_for_region(climate_data, subregion_polygons, naturalearth_regionnames)

    return region_poly, gridlist, gridlist_cf

if __name__ == "__main__":
    climate_file = sys.argv[1]
    resolution_isimip_string = sys.argv[2]
    regionname = sys.argv[3]
    naturalearth_regionnames = sys.argv[4].split(',')
    naturalearth_regiontype = sys.argv[5]
    outputfile = sys.argv[6]
    outputfile_cf = sys.argv[7]

    assert (regionname in climate_file), f'Region name {regionname} not in climate filename {climate_file}'
    assert (resolution_isimip_string in climate_file), "Resolution does not match climate file"

    print('Create gridlist for', regionname)
    region_poly, gridlist, gridlist_cf = get_gridlist_from_climate_data_and_region(climate_file, naturalearth_regionnames, naturalearth_regiontype)

    print('Write gridlist')
    gridlist_df = pd.DataFrame(gridlist)
    gridlist_df.to_csv(outputfile, sep='\t', index=False, header=False)
    pd.DataFrame(gridlist_cf).to_csv(outputfile_cf, sep='\t', index=False, header=False)

    print('Plot gridlist')
    plot_gridlist(resolution_isimip_string, region_poly, gridlist)

    print('Finished creating gridlist.')
