import os

configfile: "snakemake_config.yml"

models = config["models"]
variables = config["variables"]
resolutions = config["resolutions"]
firstyear = config["firstyear_inclusive"]
lastyear = config["lastyear_inclusive"]

years = list(range(firstyear, lastyear+1))
months = [f"{m:02d}" for m in range(1, 13)]

regions = config["regions"]
lpjguesspath = config["lpjguesspath"]

wildcard_constraints:
    regionname="[^/_]+", # ensure regionname does not contain a "/"
    resolution="[^_]+",
    model="[^_]+", # ensure model does not contain a "_"
    variable="[^_]+",
    year=r"\d{4}",  # Ensures the year wildcard matches exactly 4 digits, otherwise it might interfere with {month} right after it.
    month=r"\d{2}",
    firstyear=r"\d{4}",  # Ensures the year wildcard matches exactly 4 digits, otherwise it might interfere with {month} right after it.
    lastyear=r"\d{4}",  # Ensures the year wildcard matches exactly 4 digits, otherwise it might interfere with {month} right after it.

rule all:
    input:
        expand("isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_global_daily_{year}{month}.nc",
           variable=variables,
           year=years,
           month=months,
           model=models,
           model_upper=[m.upper() for m in models],  # Ensure the uppercase versions are expanded here
           resolution=resolutions,
        ),
        expand("isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_{year}{month}.nc",
           variable=variables,
           year=years,
           month=months,
           model=models,
           model_upper=[m.upper() for m in models],  # Ensure the uppercase versions are expanded here
           resolution=resolutions,
           regionname=list(regions.keys())
        ),
        expand("isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_fullyear_{year}.nc",
            variable=variables,
            year=years,
            model=models,
            model_upper=[m.upper() for m in models],  # Ensure the uppercase versions are expanded here
            resolution=resolutions,
            regionname=list(regions.keys())
        ),
        expand("isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_fullyear_{year}_noleap.nc",
            variable=variables,
            year=years,
            model=models,
            model_upper=[m.upper() for m in models],  # Ensure the uppercase versions are expanded here
            resolution=resolutions,
            regionname=list(regions.keys())
        ),
        expand("isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears.nc",
            variable=variables,
            year=years,
            model=models,
            model_upper=[m.upper() for m in models],  # Ensure the uppercase versions are expanded here
            resolution=resolutions,
            regionname=list(regions.keys())
        ),
        expand("isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears_ncks.nc",
            variable=variables,
            year=years,
            model=models,
            model_upper=[m.upper() for m in models],  # Ensure the uppercase versions are expanded here
            resolution=resolutions,
            regionname=list(regions.keys())
        ),
        expand("lpjguess_instruction_files/{model}_{resolution}_{regionname}.ins",
                model=models,
                resolution=resolutions,
                regionname=list(regions.keys())
        ),
        expand("lpjguess_instruction_files/{model}_{resolution}_{regionname}_gridlist.txt",
                model=models,
                model_upper=[m.upper() for m in models],  # Ensure the uppercase versions are expanded here
                resolution=resolutions,
                regionname=list(regions.keys()),
        ),
        "isimip_prepared_data/co2_obsclim_annual_1850_2021.txt",
        "lpjguess_outputs/cpool.out"

rule download_isimip_climate_data:
    output:
        "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_global_daily_{year}{month}.nc",
    params:
        directory=lambda wildcards: f"isimip_downloaded_data/{wildcards.model.upper()}/",
        url=lambda wildcards: f"https://files.isimip.org/ISIMIP3a/InputData/climate/atmosphere/obsclim/global/daily/historical/{wildcards.model.upper()}/{wildcards.model}_obsclim_{wildcards.variable}_{wildcards.resolution}_global_daily_{wildcards.year}{wildcards.month}.nc"
    shell:
        """
        mkdir -p {params.directory}
        echo "Downloading {params.url} ..."
        wget -nc -P {params.directory} {params.url}
        """

rule crop_isimip_data:
    # no expansion here, because we want to run the shell command for each input file.
    input:
        "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_global_daily_{year}{month}.nc"
    output:
        "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_{year}{month}.nc"
    params:
       minlon = lambda wildcards: [regions[wildcards.regionname]['minlon']],
       maxlon = lambda wildcards: [regions[wildcards.regionname]['maxlon']],
       minlat = lambda wildcards: [regions[wildcards.regionname]['minlat']],
       maxlat = lambda wildcards: [regions[wildcards.regionname]['maxlat']],
    shell:
        """
        echo "{output}"
        cdo sellonlatbox,{params.minlon},{params.maxlon},{params.minlat},{params.maxlat} {input} {output}
        """

rule concat_to_yearly_cropped_isimip_data:
    input:
        lambda wildcards: expand(
            "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_{year}{month}.nc",
            model_upper=wildcards.model.upper(),
            model=wildcards.model,
            variable=wildcards.variable,
            resolution=wildcards.resolution,
            regionname=wildcards.regionname,
            year=wildcards.year,
            month=months # no wildcard here: we want to merge all months!
        )
    output:
        "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_fullyear_{year}.nc"
    shell:
        """
        cdo -O -z zip_9 -mergetime {input} {output}
        """

rule delete_leapdays:
    input:
        "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_fullyear_{year}.nc"
    output:
        "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_fullyear_{year}_noleap.nc"
    shell:
        """
        cdo -O -delete,month=2,day=29 {input} {output}
        """

rule combine_to_single_input_file:
    input:
        lambda wildcards: expand(
            "isimip_downloaded_data/{model_upper}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_fullyear_{year}_noleap.nc",
            model_upper=wildcards.model.upper(),
            model=wildcards.model,
            variable=wildcards.variable,
            resolution=wildcards.resolution,
            regionname=wildcards.regionname,
            year=years # no wildcard here: we want to merge all years!
        )
    output:
        "isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears_{firstyear}_{lastyear}.nc",
    shell:
        """
        # merge yearly to total data and apply scale factor using unpack function.
        cdo -O -z zip_9 -unpack -mergetime {input} {output}
        """

rule cycle_data:
    # the sole purpose of this rule is to cycle the climate data. LPJ-GUESS requires 30 years of climate data, but
    # for this example, we do not want to download 30 years worth of data, so we just repeat the one year that was
    # downloaded and prepared in the previous rules.
    input:
        lambda wildcards: expand(
            "isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears_{firstyear}_{lastyear}.nc",
            model_upper=wildcards.model.upper(),
            model=wildcards.model,
            variable=wildcards.variable,
            resolution=wildcards.resolution,
            regionname=wildcards.regionname,
            firstyear=firstyear, # no wildcard here: we only call it once for every combination of the variables other than the years variables
            lastyear=lastyear,
        )
    output:
        "isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears.nc",
    run:
        repeated_inputs = " ".join([f"{input}"] * 31)
        shell(f"cdo -settaxis,1990-01-01,00:00:00,1day -copy {repeated_inputs} {output}")

#TODO remove this once the new LPJ is released
rule adapt_floating_point_precision:
    input:
        "isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears.nc",
    output:
        "isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears_ncks.nc",
    params:
       rounding_factor = lambda wildcards: 100 if wildcards.resolution == '1800arcsec' else 100000,
    shell:
        """
        echo "test"
        # make sure that the dimensions have only 10 significant digits, otherwise it could happen that in one file it is
        # 8.24986035815 and in the other 8.24986035814999. LPJ-GUESS will complain about this.
        ncap2 -O -s 'lon=round(lon*{params.rounding_factor})/{params.rounding_factor}; lat=round(lat*{params.rounding_factor})/{params.rounding_factor}' {input} {output}
        """


rule create_gridlist:
    input:
        "create_gridlist_for_region.py",
        lambda wildcards: expand("isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears_ncks.nc",
            model=wildcards.model,
            resolution=resolutions,
            regionname=list(regions.keys()),
            variable=variables,
        )
    params:
       natural_earth_name= lambda wildcards: [regions[wildcards.regionname]['natural_earth_name']],
       natural_earth_level= lambda wildcards: [regions[wildcards.regionname]['natural_earth_level']],
    output:
        "lpjguess_instruction_files/{model}_{resolution}_{regionname}_gridlist.txt",
        "lpjguess_instruction_files/{model}_{resolution}_{regionname}_gridlist_cf.txt",
    shell:
        """
        python create_gridlist_for_region.py {wildcards.model} {wildcards.resolution} {wildcards.regionname} {params.natural_earth_name} {params.natural_earth_level} {output[0]} {output[1]}
        """

rule download_isimip_co2_data:
    output:
        "isimip_prepared_data/co2_obsclim_annual_1850_2021.txt",
    shell:
        """
        wget -nc -P isimip_prepared_data/ https://files.isimip.org/ISIMIP3a/InputData/climate/atmosphere_composition/co2/obsclim/co2_obsclim_annual_1850_2021.txt
        """

rule prepare_model_instruction_files:
    input:
        "lpjguess_instruction_files/template.ins",
        lambda wildcards: expand("isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears_ncks.nc",
            model=wildcards.model,
            resolution=wildcards.resolution,
            regionname=wildcards.regionname,
            variable=variables
        )
    output:
        "lpjguess_instruction_files/{model}_{resolution}_{regionname}.ins"
    params:
        pwd = os.getcwd()
    shell:
        """
        echo "test"
        sed -e 's;<MODEL>;{wildcards.model};g' -e 's;<RESOLUTION>;{wildcards.resolution};g' -e 's;<REGION>;{wildcards.regionname};g' -e 's;<LPJGUESSPATH>;{lpjguesspath};g' -e 's;<FIRSTYEAR>;{firstyear};g' -e 's;<LASTYEAR>;{lastyear};g' -e 's;<ISIMIP_DIR>;{params.pwd};g' lpjguess_instruction_files/template.ins > {output}
        """

rule run_lpj_guess:
    input:
        lambda wildcards: expand("lpjguess_instruction_files/{model}_{resolution}_{regionname}.ins",
            model=models,
            resolution=resolutions,
            regionname=list(regions.keys())
        ),
        lambda wildcards: expand("lpjguess_instruction_files/{model}_{resolution}_{regionname}_gridlist.txt",
            model=models,
            resolution=resolutions,
            regionname=list(regions.keys())
        ),
        lambda wildcards: expand("isimip_prepared_data/{model}/{model}_obsclim_{variable}_{resolution}_{regionname}_daily_allyears_ncks.nc",
            model=models,
            resolution=resolutions,
            regionname=list(regions.keys()),
            variable=variables
        )
    output:
        "lpjguess_outputs/cpool.out"
    shell:
        """
        sudo docker run -it \
            --mount type=bind,src=./isimip_prepared_data,target=/isimip_prepared_data   \
            --mount type=bind,src=./lpjguess_instruction_files,target=/lpjguess_instruction_files   \
            --mount type=bind,src=./lpjguess_outputs,target=/lpjguess_outputs   \
            kgregor-lpjguess-image cmake-build-release/guess -input cf /lpjguess_instruction_files/chelsa-w5e5_1800arcsec_bavaria.ins
        """
