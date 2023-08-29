# -*- coding: utf-8 -*-
"""
SCRIPT TO DOWNLOAD VIIRS GRIDDED (LEVEL 3) OPERATIONAL GLOBAL AOD DATA FILES
@author: Dr. Amy Huff (amy.huff@noaa.gov)

**If you use any of the code in this script in your work/research,
please credit the NOAA/NESDIS/STAR Aerosols and Atmospheric Composition
Science Team**

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

Version history:
v0 (May 28 2021): initial release; downloads data from ftp version of 
STAR online data archive
v1 (Nov 1 2021): updated to utilize "requests" libary via www version 
of STAR online data archive
v2 (May 2 2022): updated to include user-friendly input prompts
v3 (Aug 7 2023): revised to point to new online archive URLs & new file
names

Instructions: Run the script in a Python conda environment using the 
provided "satellite_aerosol" environment.yml configuration file (recommended).
You will be asked to enter the observation start and end dates, satellite 
(SNPP or NOAA-20 or both), data averaging time (daily or monthly), data 
resolution (0.10° or 0.25°), and the name  of the directory where downloaded 
files will be saved. If there are no errors in any of the entered information, 
the script will proceed to download VIIRS files to the specified directory. 
If you need to stop the download while it is in progress, press the "control" 
and "c" keys.

"""
# Module for accessing system-specific parameters and functions
import sys

# Module for manipulating dates and times
import datetime

# Module to set filesystem paths appropriate for user's operating system
from pathlib import Path

# Library to access core utilities for Python packages
from packaging.version import parse

# Library to send HTTP requests
import requests

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


# Check if file exists on STAR online data archive
def file_exists(path):
    try: 
        response = requests.head(path)
        status = response.status_code  # status code = 200 if file exists
    except:
        status = 100
    
    return status


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
        entered_satellite = input('Enter the satellite for VIIRS data (SNPP or NOAA-20; to download data from both satellites, enter "both"): \n')
        # If error in entered satellite name, ask user to try again
        if entered_satellite not in ('SNPP', 'NOAA-20', 'both'):
            print('Satellite name was not recognized; must be SNPP or NOAA-20 or "both". Try again.')
        else:
            break
        
    return entered_satellite


# Interface for user to enter VIIRS gridded data resolution
def user_input_resolution():
    while True:
        # Ask user to enter resolution for VIIRS gridded data
        data_resolution = input("Enter the resolution in degrees of the VIIRS gridded data (0.100 or 0.250)\n(monthly data only available at 0.250° resolution): \n")
        # If error in entered resolution, ask user to try again
        if data_resolution not in ('0.100', '0.250'):
            print("Resolution was not recognized; must be 0.100 or 0.250. Try again.")
        else:
            break

    return data_resolution


# Interface for user to enter averaging time for VIIRS data
def user_input_averaging_time():
    while True:
        # Ask user to enter averaging time for VIIRS gridded data
        averaging_time = input("Enter the averaging period for the VIIRS gridded data (daily or monthly): \n")
        # If error in entered averaging time, ask user to try again
        if averaging_time not in ('daily', 'monthly'):
            print("Averaging period was not recognized; must be daily or monthly. Try again.")
        else:
            break

    return averaging_time


# Create list of available daily data file names
def create_daily_names(data_resolution, satellite, date_generated):
     
    # Create list of available data file names
    # If data file exists, add its name to "file_list"
    # Add satellite/date of any missing files to "no_file_list"
    file_list = []
    no_file_list = []
    for date in date_generated:
        file_date = date.strftime('%Y%m%d')
        year = file_date[:4]
        if satellite == 'both':
            sat_list = ['npp', 'noaa20']
            for sat_name in sat_list:
                file_name = 'viirs_eps_' + sat_name + '_aod_' + data_resolution + '_deg_' + file_date + '_nrt.nc'
                if sat_name == 'npp':  
                    url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/snpp/aod/eps/' + year + '/'
                elif sat_name == 'noaa20':
                    url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/noaa20/aod/eps/' + year + '/'
                # Check if file exists
                status = file_exists(url + file_name)
                if status == 200:
                    file_list.append(file_name)
                else:
                    missing = str(sat_name) + '_' + str(file_date)
                    no_file_list.append(missing)
        else:
            if satellite == 'snpp':
                sat_name = 'npp'
            elif satellite == 'noaa20':
                sat_name = 'noaa20'
            file_name = 'viirs_eps_' + sat_name + '_aod_' + data_resolution + '_deg_' + file_date + '_nrt.nc'
            url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/' + satellite + '/aod/eps/' + year + '/'
            # Check if file exists
            status = file_exists(url + file_name)
            if status == 200:
                file_list.append(file_name)
            else:
                missing = str(sat_name) + '_' + str(file_date)
                no_file_list.append(missing)
 
    return file_list, no_file_list


# Create list of available monthly data file names
def create_monthly_names(satellite, date_generated):
    
    # Create list of available data file names
    # If data file exists, add its name to "file_list"
    # Add satellite/date of any missing files to "no_file_list"
    file_list = []
    no_file_list = []
    year_month_list = []
    for date in date_generated:
        file_date = date.strftime('%Y%m%d')
        year_month = file_date[:6]
        if year_month not in year_month_list:
            year_month_list.append(year_month)
            if satellite == 'both':
                sat_list = ['snpp', 'noaa20']
                for sat_name in sat_list:
                    file_name = 'viirs_aod_monthly_' + sat_name + '_0.250_' + year_month + '_nrt.nc'
                    url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/' + sat_name + '/aod_monthly/'
                    # Check if file exists
                    status = file_exists(url + file_name)
                    if status == 200:
                        file_list.append(file_name)
                    else:
                        missing = str(sat_name) + '_' + str(year_month)
                        no_file_list.append(missing)
            else:
                file_name = 'viirs_aod_monthly_' + satellite + '_0.250_' + year_month + '_nrt.nc'
                url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/' + satellite + '/aod_monthly/'
                # Check if file exists
                status = file_exists(url + file_name)
                if status == 200:
                    file_list.append(file_name)
                else:
                    missing = str(satellite) + '_' + str(year_month)
                    no_file_list.append(missing)

    return file_list, no_file_list


# Loop to download data files
def download_data(file_list, averaging_time, save_path):
    
    # User can press "control + c" buttons to stop download
    print('\nTo stop download prior to completion, press "Ctrl+C"\n')
    
    # Flush buffer if Python version < v3.9 to avoid glitch in tqdm library
    if parse(sys.version.split(' ')[0]) < parse('3.9'):
        sys.stdout.flush()
    
    # Loop through file names and download file to specified directory
    # Display download progress bar using tqdm library
    try:
        # Loop through file names and download file to specified directory
        for file_name in tqdm(file_list, unit='files', bar_format="{desc}Downloading:{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}[{elapsed}<{remaining}]"):
            if averaging_time == 'daily':
                year = file_name.split('_')[6][:4]
                sat_stem = file_name.split('_')[2]
                if sat_stem == 'noaa20':
                    url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/noaa20/aod/eps/' + year + '/'
                else:
                    url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/snpp/aod/eps/' + year + '/'
            else:
                sat_stem = file_name.split('_')[3]
                url = 'https://www.star.nesdis.noaa.gov/pub/smcd/VIIRS_Aerosol/viirs_aerosol_gridded_data/' + sat_stem + '/aod_monthly/'
            response = requests.get(url + file_name)
            with open(save_path / file_name, 'wb') as file:
                file.write(response.content)
        print('\nDownload complete!')
    except KeyboardInterrupt:
        print('\nDownload was interrupted by user.')

# Interface for user to download files
def get_files(date_generated, satellite, data_resolution, averaging_time, save_path):
    
    print('\nGenerating list of available files...')
    # Generate lists of available data files and satellites/dates for which no files available
    if averaging_time == 'monthly':
        file_list, no_file_list = create_monthly_names(satellite, date_generated)
    else:
        file_list, no_file_list = create_daily_names(data_resolution, satellite, date_generated)
    
    # List dates for which files are not available (if any)
    if len(no_file_list) > 0:
        print('\nNo data files are available for the following satellites/dates:')
        for entry in no_file_list:
            satellite_name, date_name = entry.split('_')
            print(satellite_name, date_name)
    
    # List available data file names, with option to download files
    if len(file_list) > 0:
        print('\nList of available data files:')
        for file_name in file_list:
            print(file_name)
        # Print directory where files will be saved
        print('\nData files will be saved to:', save_path)
        # Ask user if they want to download the available data files
        # If yes, download files to specified directory
        download_question = 'Would you like to download the ' + str(len(file_list)) + ' files?\nType "yes" or "no" and hit "Enter"\n'
        download_files = input(download_question)
        if download_files in ['yes', 'YES', 'Yes', 'y', 'Y']:
            download_data(file_list, averaging_time, save_path)
        else:
            print('Files are not being downloaded.')
    else:
        print('\nNo data files are available for download. Check settings and try again.')


# Main function
if __name__ == '__main__':
    
    # Check if user has required packages installed
    packages = ['requests', 'tqdm', 'packaging']
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
        entered_satellite = user_input_satellite()
        # Convert entered satellite name to format used in VIIRS file name
        if entered_satellite == 'SNPP':
            satellite = 'snpp'
        elif entered_satellite == 'NOAA-20':
            satellite = 'noaa20'
        else:
            satellite = 'both'
        # Enter averaging time of VIIRS data
        averaging_time = user_input_averaging_time()
        # Enter resolution of VIIRS data
        data_resolution = user_input_resolution()
        # Enter directory to save downloaded files
        user_save_path = user_input_directory_name()
        # Set directory name as pathlib.Path object
        save_path = Path(user_save_path)
        # Proceed to list files, with option to download
        get_files(date_generated, satellite, data_resolution, averaging_time, save_path)