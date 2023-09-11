# Scripts to Utilize Access to JPSS data on the AWS Public Repository

This repository contains useful Python scripts for downloading, analyzing, and visualizing JPSS Level 2 and Level 3 products.


## Pre-Requisites
If you are new to Python, we recommend installing [Anaconda Python](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/). For additional installation tips and tricks, please reference these [instructions from past JPSS training](https://www.star.nesdis.noaa.gov/atmospheric-composition-training/software_anaconda_install.php).

You will need several addition to the packages included in Anaconda/Miniconda. We recommend using Python environments to ensure the following scripts run successfully. We have included an environment file (```satellite_aerosol.yml```). Instructions for setting up Python environments can be [found here](https://www.star.nesdis.noaa.gov/atmospheric-composition-training/software_create_environment.php).

## About the datasets
The code in this repository generally uses VIIRS Aerosol Optical Depth (AOD) [Level 2 and Level 3](https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_processing_levels.php) data products. However, this code is adaptable for all JPSS products that are part of the NODD.

## Scripts
### download_viirs_operational_aod_gridded_v3.py
This script will access the NOAA/NESDIS/STAR online archive of the
*operational* VIIRS gridded (level 3) AOD data, and for a range of days 
entered by the user, will download available daily or monthly-averaged 
files. All files have global coverage, contain high quality AOD data only, 
and are in netCDF4 (.nc) format. The daily files are available in 0.10° 
or 0.25° resolution, and the monthly files are available only in 0.25° 
resolution. The operational files were created with near-real time latency 
(designated by the "nrt" suffix in the file name) using the version of the 
EPS AOD algorithm that was current at that time.

**OPERATIONAL VIIRS GRIDDED AOD data availablity: Oct 29 2022-present**

**Instructions**: Run the script in a Python conda environment using the 
provided "satellite_aerosol" environment.yml configuration file (recommended).
You will be asked to enter the observation start and end dates, satellite 
(SNPP or NOAA-20 or both), data averaging time (daily or monthly), data 
resolution (0.10° or 0.25°), and the name  of the directory where downloaded 
files will be saved. If there are no errors in any of the entered information, 
the script will proceed to download VIIRS files to the specified directory. 
If you need to stop the download while it is in progress, press the "control" 
and "c" keys.

### python-scripts/download_viirs_reprocessed_aod_gridded_v1.py
A unique feature of the AOD product is that the entire record [has been reprocessed](https://www.star.nesdis.noaa.gov/atmospheric-composition-training/satellite_data_operational_reprocessed.php). This dataset is more appropriate for users who are interested in a stable, long-term record.

### python-scripts/visualize_viirs_aod_gridded_v3.py

This script opens a VIIRS gridded (Level 3) AOD data file in netCDF4 (.nc)
format and plots AOD on global map, along with the global AOD data max, 
min, and mean, using the "Plate Carree" equidistant cylindrical projection 
with the equator as the standard parallel. The script can accommodate 
daily, weekly, or monthly averaged gridded AOD files, at 0.05°, 0.10°, or 
0.25° resolution. The script can work with operational or reprocessed
gridded AOD data files. The script can process one or more data files, 
making one map plot for each file. If processing multiple files, put all 
the data files in the same directory.

**Instructions**:  Run the script in a Python conda environment using the 
provided "satellite_aerosol" environment.yml configuration file (recommended).
You will be asked to enter the name  of the directory where VIIRS gridded
AOD files are located, the name of the directory where map image files will 
be saved, the maximum AOD value for displaying data on the plot (1-5), the 
dots per inch (DPI) resolution of the map image files (100-900), and the 
format of the saved map image files (png, jpg, or pdf). If there are no 
errors in any of the entered information, the script will proceed to create 
global AOD map(s).