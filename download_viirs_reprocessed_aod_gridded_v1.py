# -*- coding: utf-8 -*-
"""
SCRIPT TO DOWNLOAD VIIRS GRIDDED (LEVEL 3) REPROCESSED GLOBAL AOD DATA FILES
@author: Dr. Amy Huff (amy.huff@noaa.gov)

**If you use any of the code in this script in your work/research,
please credit the NOAA/NESDIS/STAR Aerosols and Atmospheric Composition
Science Team**

This script will access the JPSS NODD archive of *reprocessed* VIIRS
gridded (level 3) AOD data, and for a range of days entered by the user, 
will download available daily, weekly-averaged, or monthly-averaged 
files. All files have global coverage, contain high quality AOD data only, 
and are in netCDF4 (.nc) format. The daily files are available at 0.05°, 
0.10°, or 0.25° resolution; the weekly and monthly files are available only 
at 0.25° resolution. The reprocessed files were recently generated using
the most recent version of the Enterprise Processing System (EPS) AOD
algorithm, providing a consistent AOD dataset for long-term analysis.

REPROCESSED VIIRS GRIDDED AOD data availablity:
SNPP: 2012-2020
NOAA-20: 2018-2020

Version history:
v1 (Aug 15 2023): initial release

Instructions: Run the script in a Python conda environment using the 
provided "satellite_aerosol" environment.yml configuration file (recommended).
You will be asked to enter the observation start and end dates, satellite 
(SNPP or NOAA-20 or both), data averaging time (daily, weekly, or monthly), 
data resolution (0.05°, 0.10°, or 0.25°), and the name  of the directory 
where downloaded files will be saved. If there are no errors in any of the 
entered information, the script will proceed to download VIIRS files to the 
specified directory. If you need to stop the download while it is in progress, 
press the "control" and "c" keys.

"""
# Module for accessing system-specific parameters and functions
import sys

# Module for manipulating dates and times
import datetime

# Module to set filesystem paths appropriate for user's operating system
from pathlib import Path

# Library to access core utilities for Python packages
from packaging.version import parse

# Library to access AWS S3 as if it were a file system
import s3fs

# Library to create progress bars for loops/functions
from tqdm import tqdm


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


# Check format of user-entered date
def check_date_format(date):
    if len(date) == 8:
        try:
            datetime.date(int(date[:4]), int(date[4:6]), int(date[6:]))
            error_message = 0
        except:
            error_message = 1  # Date not in YYYMMDD format
    else:
        error_message = 2  # Incorrect number of digits in date

    return error_message     


# Check user-entered dates for errors
def check_dates_range(start_date, end_date):
    # Convert start and end dates into datetime.date objects
    start = datetime.date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
    end = datetime.date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:]))
    
    if end < start:
        error_message = 1  # End date is before start date
    else:
        today = datetime.date.today()
        if end > today:
            error_message = 2  # End date is in the future
        else:
            error_message = 0
    
    return error_message


# Interface for user to enter data observation dates
def user_input_observation_dates():
    while True:
        while True:
            # Ask user to enter start date for time period of observations
            # Note: "input()" returns a string
            start_date = input("Enter 8-digit START date for data in YYYYMMDD format: \n")
            # Check format of entered start date
            start_date_error_message = check_date_format(start_date)
            # If any errors in format, ask user to try again
            if start_date_error_message != 0:
                if start_date_error_message == 1:
                    print('Incorrect format for START date: must be "YYYYMMDD". Try again.')
                elif start_date_error_message == 2:
                    print('Incorrect number of digits in START date: must be "YYYYMMDD". Try again.')
            else:
                break
        while True:
            # Ask user to enter end date for time period of observations
            # Note: "input()" returns a string
            end_date = input("Enter 8-digit END date for data in YYYYMMDD format: \n")
            # Check format of entered end date
            end_date_error_message = check_date_format(end_date)
            # If any errors in format, ask user to try again
            if end_date_error_message != 0:
                if end_date_error_message == 1:
                    print('Incorrect format for END date: must be "YYYYMMDD". Try again.')
                elif end_date_error_message == 2:
                    print('Incorrect number of digits in END date: must be "YYYYMMDD". Try again.')
            else:
                break
        # Check for errors in entered start and end dates
        dates_error_message = check_dates_range(start_date, end_date)
        # If any errors in dates, ask user to try again
        if dates_error_message != 0:
            if dates_error_message == 1:
                print('The entered end date is earlier than the start date. Try again.')
            elif dates_error_message == 2:
                print('The entered end date is in the future. Try again.')
        else:
            break
    
    return start_date, end_date


# Interface for user to enter directory to save downloaded files
def user_input_directory_name():
    while True:
        # Ask user to enter name of directory to save downloaded files
        user_save_path = input("Enter name of directory to save downloaded files (e.g., D:/Data/):\n")
        # Check user-entered directory name for errors
        save_path_error_message = check_directory(user_save_path)
        # If any errors, ask user to try again
        if save_path_error_message != 0:
            if save_path_error_message == 1:
                print('The directory entered to save files does not exist. Try again.')
            elif save_path_error_message == 2:
                print('The field for the directory to save files is blank. Try again.')
            elif save_path_error_message == 3:
                print('There is a syntax error in the the directory name to save files. Try again.')
        else:
            break
    
    return user_save_path


# Interface for user to enter satellite for VIIRS data
def user_input_satellite():
    while True:
        # Ask user to enter satellite for VIIRS data
        entered_satellite = input('Enter the satellite for VIIRS data (SNPP or NOAA20; to download data from both satellites, enter "both"): \n')
        # If error in entered satellite name, ask user to try again
        if entered_satellite not in ('SNPP', 'NOAA20', 'both'):
            print('Satellite name was not recognized; must be SNPP or NOAA20 or "both". Try again.')
        else:
            break
        
    return entered_satellite


# Interface for user to enter VIIRS gridded data resolution
def user_input_resolution():
    while True:
        # Ask user to enter resolution for VIIRS gridded data
        data_resolution = input("Enter the resolution in degrees of the VIIRS gridded data (0.050, 0.100, or 0.250)\n(weekly & monthly data only available at 0.250° resolution): \n")
        # If error in entered resolution, ask user to try again
        if data_resolution not in ('0.050', '0.100', '0.250'):
            print("Resolution was not recognized; must be 0.050, 0.100, or 0.250. Try again.")
        else:
            break

    return data_resolution


# Interface for user to enter averaging time for VIIRS data
def user_input_averaging_time():
    while True:
        # Ask user to enter averaging time for VIIRS gridded data
        averaging_time = input("Enter the averaging period for the VIIRS gridded data (daily, weekly, or monthly): \n")
        # If error in entered averaging time, ask user to try again
        if averaging_time not in ('daily', 'weekly', 'monthly'):
            print("Averaging period was not recognized; must be daily, weekly, or monthly. Try again.")
        else:
            break

    return averaging_time


# Create list of available daily data file paths & total size of files
def create_daily_list(data_resolution, satellite, date_generated):
     
    # Access AWS using anonymous credentials
    fs = s3fs.S3FileSystem(anon=True)

    # Loop through observation dates & check for files
    nodd_file_list = []
    nodd_total_size = 0
    for date in date_generated:
        file_date = date.strftime('%Y%m%d')
        year = file_date[:4]
        if satellite == 'both':
            sat_list = ['npp', 'noaa20']
            for sat_name in sat_list:
                file_name = 'viirs_eps_' + sat_name + '_aod_' + data_resolution + '_deg_' + file_date + '.nc'
                if sat_name == 'npp':
                    prod_path = 'noaa-jpss/SNPP/VIIRS/SNPP_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/' + data_resolution[:4] + '_Degrees_Daily/' + year + '/'
                elif sat_name == 'noaa20':
                    prod_path = 'noaa-jpss/NOAA20/VIIRS/NOAA20_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/' + data_resolution[:4] + '_Degrees_Daily/' + year + '/'
                # If file exists, add path to list and add file size to total
                if fs.exists(prod_path + file_name) == True:
                    nodd_file_list.extend(fs.ls(prod_path + file_name))
                    nodd_total_size = nodd_total_size + fs.size(prod_path + file_name)  
        else:
            if satellite == 'SNPP':
                sat_name = 'npp'
            elif satellite == 'NOAA20':
                sat_name = 'noaa20'
            file_name = 'viirs_eps_' + sat_name + '_aod_' + data_resolution + '_deg_' + file_date + '.nc'
            prod_path = 'noaa-jpss/' + satellite + '/VIIRS/' + satellite + '_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/' + data_resolution[:4] + '_Degrees_Daily/' + year + '/'
            # If file exists, add path to list and add file size to total
            if fs.exists(prod_path + file_name) == True:
                nodd_file_list.extend(fs.ls(prod_path + file_name))
                nodd_total_size = nodd_total_size + fs.size(prod_path + file_name)
 
    return nodd_file_list, nodd_total_size


# Create list of available monthly data file paths & total size of files
def create_monthly_list(satellite, date_generated):
    
    # Access AWS using anonymous credentials
    fs = s3fs.S3FileSystem(anon=True)

    # Loop through observation dates & check for files
    nodd_file_list = []
    nodd_total_size = 0
    year_month_list = []
    for date in date_generated:
        file_date = date.strftime('%Y%m%d')
        year_month = file_date[:6]
        if year_month not in year_month_list:
            year_month_list.append(year_month)
            if satellite == 'both':
                sat_list = ['snpp', 'noaa20']
                for sat_name in sat_list:
                    file_name = 'viirs_aod_monthly_' + sat_name + '_0.250_deg_' + year_month + '.nc'
                    if sat_name == 'snpp':
                        prod_path = 'noaa-jpss/SNPP/VIIRS/SNPP_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/0.25_Degrees_Monthly/'
                    elif sat_name == 'noaa20':
                        prod_path = 'noaa-jpss/NOAA20/VIIRS/NOAA20_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/0.25_Degrees_Monthly/'
                    # If file exists, add path to list and add file size to total
                    if fs.exists(prod_path + file_name) == True:
                        nodd_file_list.extend(fs.ls(prod_path + file_name))
                        nodd_total_size = nodd_total_size + fs.size(prod_path + file_name)
            else:
                if satellite == 'SNPP':
                    sat_name = 'snpp'
                elif satellite == 'NOAA20':
                    sat_name = 'noaa20'
                file_name = 'viirs_aod_monthly_' + sat_name + '_0.250_deg_' + year_month + '.nc'
                prod_path = 'noaa-jpss/' + satellite + '/VIIRS/' + satellite + '_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/0.25_Degrees_Monthly/'
                # If file exists, add path to list and add file size to total
                if fs.exists(prod_path + file_name) == True:
                    nodd_file_list.extend(fs.ls(prod_path + file_name))
                    nodd_total_size = nodd_total_size + fs.size(prod_path + file_name)

    return nodd_file_list, nodd_total_size


# Create list of available weekly data file paths & total size of files
def create_weekly_list(satellite, date_generated):

    # Access AWS using anonymous credentials
    fs = s3fs.S3FileSystem(anon=True)

    # Loop through observation dates & check for files
    nodd_file_list = []
    nodd_total_size = 0
    for date in date_generated:
        file_date = date.strftime('%Y%m%d')
        year = file_date[:4]
        if satellite == 'both':
            sat_list = ['SNPP', 'NOAA20']
            for sat_name in sat_list:
                prod_path = 'noaa-jpss/' + sat_name + '/VIIRS/' + sat_name + '_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/0.25_Degrees_Weekly/' + year + '/'
                # Get list of all files in given year on NODD
                all_files = fs.ls(prod_path)
                # Loop through files, check if file date falls within observation date range
                for file in all_files:
                    file_start = file.split('/')[-1].split('_')[7].split('.')[0].split('-')[0]
                    file_end = file.split('/')[-1].split('_')[7].split('.')[0].split('-')[1]
                    # If file within observation range, add path to list and add file size to total
                    if file_date >= file_start and file_date <= file_end:
                        if file not in nodd_file_list:
                            nodd_file_list.append(file)
                            nodd_total_size = nodd_total_size + fs.size(file)  
        else:
            prod_path = 'noaa-jpss/' + satellite + '/VIIRS/' + satellite + '_VIIRS_Aerosol_Optical_Depth_Gridded_Reprocessed/0.25_Degrees_Weekly/' + year + '/'
            # Get list of all files in given year on NODD
            all_files = fs.ls(prod_path)
            # Loop through files, check if file date falls within observation date range
            for file in all_files:
                file_start = file.split('/')[-1].split('_')[7].split('.')[0].split('-')[0]
                file_end = file.split('/')[-1].split('_')[7].split('.')[0].split('-')[1]
                # If file within observation range, add path to list and add file size to total
                if file_date >= file_start and file_date <= file_end:
                    if file not in nodd_file_list:
                        nodd_file_list.append(file)
                        nodd_total_size = nodd_total_size + fs.size(file)

    return nodd_file_list, nodd_total_size


# Interface for user to download files
def get_files(date_generated, satellite, data_resolution, averaging_time, save_path):
    
    print('\nGenerating list of available files...')
    # Generate list of available data files
    if averaging_time == 'monthly':
        file_list, total_size = create_monthly_list(satellite, date_generated)
    elif averaging_time == 'weekly':
        file_list, total_size = create_weekly_list(satellite, date_generated)
    else:
        file_list, total_size = create_daily_list(data_resolution, satellite, date_generated)
    
    # List available data file names, with option to download files
    if len(file_list) > 0:
        # Print information about download
        print('\nTotal number of available files:', str(len(file_list)))
        print('Approximate total size of download: ',  int(total_size/1.0E6), ' MB', sep='')
        print('\nData files will be saved to:', save_path)
        
        # Ask user if they want to download the available data files
        # If yes, download files to specified directory
        download_question = '\nWould you like to download the files?\nType "yes" or "no" and hit "Enter"\n'
        ask_download = input(download_question)
        if ask_download in ['yes', 'YES', 'Yes', 'y', 'Y']:
            # User can press "control + c" buttons to stop download
            print('\nTo stop download prior to completion, press "Ctrl+C"\n')
            # Flush buffer if Python version < v3.9 to avoid glitch in tqdm library
            if parse(sys.version.split(' ')[0]) < parse('3.9'):
                sys.stdout.flush()
            # Access AWS using anonymous credentials
            fs = s3fs.S3FileSystem(anon=True)
            try:
                for file in tqdm(file_list, total=len(file_list), unit='files', 
                                bar_format="{desc}Downloading:{percentage:3.0f}%|{bar}|{n_fmt}/{total_fmt}[{elapsed}<{remaining}]"):
                    fs.get(file, (save_path / file.split('/')[-1]).as_posix())  # Download file
                print('Download complete!')
            except KeyboardInterrupt:
                print('\nDownload was interrupted by user.')
        else:
            print('\nFiles are not being downloaded.')
    else:
        print('\nNo files retrieved. Check settings and try again.')


# Main function
if __name__ == '__main__':
    
    # Check if user has required packages installed
    packages = ['s3fs', 'tqdm', 'packaging']
    number_missing = check_user_packages(packages)
    if number_missing > 0:
        print('\nYou must install the indicated package(s) in order to run the script.')
    else:
        # Enter observation date(s) range
        start_date, end_date = user_input_observation_dates()
        # Create list of dates for obseration period in datetime format
        start = datetime.date(int(start_date[:4]), int(start_date[4:6]), int(start_date[6:]))
        end = datetime.date(int(end_date[:4]), int(end_date[4:6]), int(end_date[6:]))
        date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days + 1)]
        # Enter satellite for VIIRS data
        satellite = user_input_satellite()
        # Enter averaging time of VIIRS data
        averaging_time = user_input_averaging_time()
        # Enter resolution of VIIRS data
        data_resolution = user_input_resolution()
        # Enter directory to save downloaded files
        user_save_path = user_input_directory_name()
        # Set directory name as pathlib.Path object
        save_path = Path(user_save_path)
        # Proceed to get list of available files, with option to download
        get_files(date_generated, satellite, data_resolution, averaging_time, save_path)
