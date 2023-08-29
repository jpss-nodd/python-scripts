# -*- coding: utf-8 -*-
"""
SCRIPT TO PLOT VIIRS GRIDDED (LEVEL 3) AOD DATA ON A GLOBAL MAP
@author: Dr. Amy Huff (amy.huff@noaa.gov)

**If you use any of the code in this script in your work/research,
please credit the NOAA/NESDIS/STAR Aerosols and Atmospheric Composition
Science Team**

This script opens a VIIRS gridded (Level 3) AOD data file in netCDF4 (.nc)
format and plots AOD on global map, along with the global AOD data max, 
min, and mean, using the "Plate Carree" equidistant cylindrical projection 
with the equator as the standard parallel. The script can accommodate 
daily, weekly, or monthly averaged gridded AOD files, at 0.05°, 0.10°, or 
0.25° resolution. The script can work with operational or reprocessed
gridded AOD data files. The script can process one or more data files, 
making one map plot for each file. If processing multiple files, put all 
the data files in the same directory.

Version history:
v1 (Jun 7 2021): initial release
v2 (May 17 2022): updated to include user-frinedly input prompts
v3 (Aug 28 2023): updated to use the "xarray" package instead of "netcdf4"
and to accomodate the range of available gridded AOD data files

Instructions:  Run the script in a Python conda environment using the 
provided "satellite_aerosol" environment.yml configuration file (recommended).
You will be asked to enter the name  of the directory where VIIRS gridded
AOD files are located, the name of the directory where map image files will 
be saved, the maximum AOD value for displaying data on the plot (1-5), the 
dots per inch (DPI) resolution of the map image files (100-900), and the 
format of the saved map image files (png, jpg, or pdf). If there are no 
errors in any of the entered information, the script will proceed to create 
global AOD map(s).
"""
# Module to set filesystem paths for user's operating system
from pathlib import Path

# Module to manipulate dates and times
import datetime

# Library to work with labeled multi-dimensional arrays
import xarray as xr

# Library to perform array operations
import numpy as np

# Library to make plots
import matplotlib as mpl
from matplotlib import pyplot as plt
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# Library to make maps
import cartopy.feature as cfeature
from cartopy import crs as ccrs


# Check if user has required packages installed
def check_user_packages(packages):
    # Check if user has required package(s) installed
    import pkg_resources
    package_list = packages
    missing_packages = []
    for package in package_list:
        try:
            pkg_resources.get_distribution(package).version
        except:
            missing_packages.append(package)
    # If any missing packages, notify user
    if len(missing_packages) > 0:
        print('The following required packages are not installed:')
        for missing_package in missing_packages:
            print(missing_package)
            
    return len(missing_packages)


# Check user-entered directory for errors
def check_directory(directory_path_name):
    try:
        Path(directory_path_name).exists()
        if Path(directory_path_name).exists() == False:
            error_message = 1  # Directory doesn't exist on user's computer
        elif len(directory_path_name) < 1:
            error_message = 2  # User forgot to enter a directory name
        else:
            error_message = 0
    except:
            error_message = 3  # Syntax error in directory name (<v3.9)

    return error_message


# Interface for user to enter directory name
def user_input_directory_name(directory_query):
    while True:
        # Ask user to enter name of directory
        user_path = input("Enter name of directory " + directory_query + " (e.g., D:/Data/):\n")
        # Check user-entered directory name for errors
        path_error_message = check_directory(user_path)
        # If any errors, ask user to try again
        if path_error_message != 0:
            if path_error_message == 1:
                print('The entered directory does not exist. Try again.')
            elif path_error_message == 2:
                print('The field for the directory is blank. Try again.')
            elif path_error_message == 3:
                print('There is a syntax error in the the directory name. Try again.')
        else:
            break
    
    return user_path


# Interface for user to enter AOD max value for plot
def user_input_aod_range_max():
    print('\nThe valid data range of VIIRS AOD is [-0.05, 5]. You will be asked to enter the maximum value for plotting AOD data; AODs > this value up to 5 will be plotted, but represented by a single color (e.g., dark red).')
    while True:
        while True:
            # Ask user to enter max AOD value for plot as integer
            try:
                data_range_max = int(input("Enter the maximum value for the AOD plotting range, as an integer from 1 to 5 (1 is the typical value): \n"))
            except ValueError:
                # If user enters float, ask them to try again
                print('Value must be an integer between 1 and 5. Try again.')
            else:
                break
        # If user enters integer outside valid range, ask them to try again
        if data_range_max not in (1, 2, 3, 4, 5):
            print("Value must be 1, 2, 3, 4, or 5. Try again.")
        else:
            break

    return data_range_max


# Interface for user to enter DPI for saved image file
def user_input_image_file_resolution():
    print('\nYou will be asked to enter the dots per inch (DPI) image resolution for the map plots. As DPI increases, image resolution and file size both increase.\nFor reference:\n100 = low resolution\n300 = moderate resolution\n600 = high resolution\n900 = very high resolution')
    while True:
        while True:
            # Ask user to enter DPI value for saved image file
            try:
                file_res = int(input("Enter the DPI as an integer from 100 to 900: \n"))
            except ValueError:
                # If user enters float, ask them to try again
                print('Value must be an integer between 100 and 900. Try again.')
            else:
                break
        # If user enters integer outside valid range, ask them to try again
        if file_res < 100 or file_res > 900:
            print("Value must be between 100 and 900. Try again.")
        else:
            break

    return file_res


# Interface for user to enter format for saved image file
def user_input_image_file_format():
    while True:
        # Ask user to enter format for saved image file
        input_save_format = input("Enter the format for saved map image files (png, jpg, or pdf): \n")
        # If error in user entered format, ask them to try again
        if input_save_format not in ('png', 'jpg', 'pdf'):
            print("Format must be png, jpg, or pdf. Try again.")
        else:
            save_format = '.' + input_save_format
            break

    return save_format


# Create AOD colorbar, auto-positioning w/dimensions of plot
# "cbar_ax.set_position([x0, y0, width, height])" sets colorbar dimensions
# Color map set as Matplotlib "rainbow" with "darkred" as color > AOD max
def aod_colorbar(fig, ax, data_range_max):
    last_axes = plt.gca()
    cbar_ax = fig.add_axes([0, 0, 0, 0])
    plt.draw()
    posn = ax.get_position()
    cbar_ax.set_position([0.35, posn.y0 - 0.06, 0.3, 0.02])
    norm = mpl.colors.Normalize(vmin=0, vmax=data_range_max)
    color_map = plt.get_cmap('rainbow').with_extremes(over='darkred')
    if data_range_max < 5: 
        cb = mpl.colorbar.ColorbarBase(cbar_ax, cmap=color_map, norm=norm, orientation='horizontal', extend='max')
    else:
        cb = mpl.colorbar.ColorbarBase(cbar_ax, cmap=color_map, norm=norm, orientation='horizontal')
    cb.set_label(label='Aerosol Optical Depth', size=8, weight='bold')
    cb.ax.tick_params(labelsize=8)
    plt.sca(last_axes)


# Format map appearance
# "zorder" argument sets drawing order for layers
def map_settings(ax):
    # Draw coastlines/borders
    # Set for "grey" land, "lightgrey" ocean/lakes, "black" borders
    ax.coastlines(resolution='50m', lw=0.5, zorder=3)
    ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='ocean', scale='50m'), facecolor='lightgrey')
    ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='land', scale='50m'), facecolor='grey')
    ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='lakes', scale='50m'), facecolor='lightgrey', edgecolor='black', zorder=1.5)
    ax.add_feature(cfeature.NaturalEarthFeature(category='physical', name='lakes', scale='50m'), facecolor='none', lw=0.5, edgecolor='black', zorder=2.5)
    ax.add_feature(cfeature.NaturalEarthFeature(category='cultural', name='admin_0_countries', scale='50m'), facecolor='none', lw=0.5, edgecolor='black', zorder=2.5)
    ax.add_feature(cfeature.NaturalEarthFeature(category='cultural', name='admin_1_states_provinces', scale='110m'), facecolor='none', lw=0.5, edgecolor='black', zorder=2.5)
    
    # Setup lat/lon grid
    # Set to make global map; adjust if regional zoom-in desired
    lon_ticks = [0, 60, 120, 180, -180, -120, -60]
    lat_ticks = [-90, -60, -30, 0, 30, 60, 90]
    ax.xaxis.set_major_formatter(LongitudeFormatter())
    ax.yaxis.set_major_formatter(LatitudeFormatter())
    ax.set_xticks(lon_ticks, crs=ccrs.PlateCarree())
    ax.set_yticks(lat_ticks, crs=ccrs.PlateCarree())
    
    # Format lat/lon tick marks
    ax.tick_params(length=5, direction='out', labelsize=8, pad=5)
    
    # Set lat/lon boundaries for map
    # [western lon, eastern lon, southern lat, northern lat]
    # Set to make global map; adjust "domain" if regional zoom-in desired
    domain = [180, -180, -90, 90]  
    ax.set_extent(domain, crs=ccrs.PlateCarree())


# Create plot title from data file name    
def create_gridded_vaod_plot_title(file_string):
    # Pull satellite, data resolution, date (reformat) from file name
    if file_string.split('_')[2] == 'monthly':
        gregorian = datetime.datetime.strptime(file_string.split('_')[6][:6], '%Y%m').date()
        date = gregorian.strftime('%B %Y')
        satellite = file_string.split('_')[3]
    elif file_string.split('_')[3] == 'weekly':
        date = 'Week ' + file_string.split('_')[6][4:] + ', ' + file_string.split('_')[6][:4]
        satellite = file_string.split('_')[1]
    else:
        gregorian = datetime.datetime.strptime(file_string.split('_')[6][:8], '%Y%m%d').date()
        date = gregorian.strftime('%d %b %Y')
        satellite = file_string.split('_')[2]
    resolution = file_string.split('_')[4][:4]
    # Reformat satellite name
    if satellite == 'npp' or satellite == 'snpp':
        satellite_name = 'S-NPP'
    elif satellite == 'noaa20':
        satellite_name = 'NOAA-20'
    product_name = 'Aerosol Optical Depth (' + resolution + '\N{DEGREE SIGN} resolution)'
    # Create plot title
    plot_title = satellite_name + '/VIIRS ' + product_name + '  ' + date
        
    return plot_title


# Create name for saved map image file
def create_gridded_vaod_plot_save_name(file_string, save_format):
    # Pull identifying information from file name
    if file_string.split('_')[2] == 'monthly':
        date = file_string.split('_')[6][:6]
        satellite = file_string.split('_')[3]
        averaging = 'monthly_'
    elif file_string.split('_')[3] == 'weekly':
        date = file_string.split('_')[6]
        satellite = file_string.split('_')[1]
        averaging = 'weekly_'
    else:
        date = file_string.split('_')[6][:8]
        satellite = file_string.split('_')[2]
        averaging = 'daily_'
    resolution = file_string.split('_')[4][:4]
    if satellite == 'npp':
        satellite_name = 'snpp'
    else:
        satellite_name = satellite
    if file_string.split('_')[-1].split('.')[0] == 'nrt':
        processing = '_operational'
    else:
        processing = '_reprocessed'
    # Create name for saved map image file
    save_name = satellite_name + '_viirs_aod_' + resolution + '-deg_' + averaging + date + processing + save_format
    
    return save_name


# Calcuate global AOD max, min, and mean values
# Inlcude 4 decimal places for values
def get_aod_stats(aod):
    aod_max = np.format_float_positional(np.max(aod), precision=4)
    aod_min = np.format_float_positional(np.min(aod), precision=4)
    aod_mean = np.format_float_positional(np.mean(aod), precision=4)
    
    return aod_max, aod_min, aod_mean


# Plot VIIRS gridded AOD on a map
def plot_gridded_aod(file, data_range_max, file_res, save_path):
    
    # Set up figure and map projection: PlateCarree(central_longitude)
    # Equidistant cylindrical projection w/equator as the standard parallel
    fig = plt.figure(figsize=(8, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Format map
    map_settings(ax)
   
    # Add AOD color bar (auto-positioning w/dimensions of plot)
    aod_colorbar(fig, ax, data_range_max)

    # Set colormap & normalization for plotting data
    # Color map set as Matplotlib "rainbow" with "darkred" as color > AOD max
    norm = mpl.colors.Normalize(vmin=0, vmax=data_range_max)
    cmap = plt.get_cmap('rainbow').with_extremes(over='darkred')

    # Open file using xarray (automatically closes file when done)
    with xr.open_dataset(file, engine='netcdf4') as ds:

        # Create pseudo-color plot
        # Get max, min, mean AOD
        if file.name.split('_')[2] == 'monthly':
            ax.pcolormesh(ds.lon, ds.lat, ds.aod, cmap=cmap, norm=norm, zorder=2,
                        transform=ccrs.PlateCarree())
            aod_max, aod_min, aod_mean = get_aod_stats(ds.aod)
        elif file.name.split('_')[3] == 'weekly':
            ax.pcolormesh(ds.lon, ds.lat, ds.aod.where(ds.aod >= -0.05), cmap=cmap, 
                        norm=norm, zorder=2, transform=ccrs.PlateCarree())
            aod_max, aod_min, aod_mean = get_aod_stats(ds.aod.where(ds.aod >= -0.05))
        else:
            ax.pcolormesh(ds.lon, ds.lat, ds.AOD550, cmap=cmap, norm=norm, zorder=2,
                        transform=ccrs.PlateCarree())
            aod_max, aod_min, aod_mean = get_aod_stats(ds.AOD550)
    
    # Print max, min, mean AOD in "lightgrey" text box on plot
    text_string = 'max AOD = ' + str(aod_max) + '\nmin AOD = ' + str(aod_min) + '\nmean AOD = ' + str(aod_mean)
    box_properties = dict(boxstyle='round', facecolor='lightgrey')
    ax.text(0.75, 0.025, text_string, transform=ax.transAxes, fontsize=7, ha='left', bbox=box_properties, zorder=4)
    
    # Add plot title
    plt.title(create_gridded_vaod_plot_title(file.name), pad=8, ma='center', size=8, weight='bold')
    
    # Save figure to specified directory using specified data format
    save_name = create_gridded_vaod_plot_save_name(file.name, save_format)
    fig.savefig(save_path / save_name, bbox_inches='tight', dpi=file_res)
    
    # Close plot
    plt.close()


# Main function
if __name__ == "__main__":
    
    # Check if user has required packages installed
    packages = ['xarray', 'cartopy', 'matplotlib']
    number_missing = check_user_packages(packages)
    if number_missing > 0:
        print('\nYou must install the indicated package(s) in order to run the script.')
    else:
        # Enter directory where VIIRS AOD files are located
        user_file_path = user_input_directory_name('where VIIRS AOD data files are located')
        # Set directory name as pathlib.Path object
        file_path = Path(user_file_path)
        # Enter directory to save downloaded files
        user_save_path = user_input_directory_name('where map image files will be saved')
        # Set directory name as pathlib.Path object
        save_path = Path(user_save_path)
        # Enter AOD max value range for plotting data
        data_range_max = user_input_aod_range_max()
        # Enter DPI resolution for map image files
        file_res = user_input_image_file_resolution()
        # Enter file format for saved map image files
        save_format = user_input_image_file_format()
        # Collect all the gridded AOD .nc files in specified directory
        file_list = sorted(file_path.glob('*aod*.nc'))
        # Loop through files, plotting data from each file
        for file in file_list:
            print('\nNow plotting:', file.name)  # Print the file name
            plot_gridded_aod(file, data_range_max, file_res, save_path)
        print('\nDone!') 