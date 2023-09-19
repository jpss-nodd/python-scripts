#!/usr/bin/env python
# coding: utf-8
# Authors: Rebekah Esmaili (STC) and Amy Huff (IMSG)

import s3fs
import datetime
from pathlib import Path
import os

directory_path = Path.cwd()
subdir = 'data'

# Create a new directory because it does not exist
isExist = os.path.exists(directory_path / subdir)
if not isExist:
   os.makedirs(directory_path / subdir)

# Connect to the AWS S3 bucket
fs = s3fs.S3FileSystem(anon=True)

# Download NUCAPS -----------------------------------------------
bucket = 'noaa-jpss'
satellite = 'NOAA20'
sensor = 'SOUNDINGS'
product = 'NOAA20_NUCAPS-EDR'
# other choices: NOAA20_NUCAPS-EDR, NOAA20_NUCAPS-CCR, NOAA20_NUCAPS-OLR

# use specific date
year = 2023
month = 4
day = 22

start_time = '0000'
end_time = '2359'

# Optional: use today's date 
# dt = datetime.datetime.now()
# year = dt.strftime('%Y')
# month = dt.strftime('%m')
# day = dt.strftime('%d')

# one_hour_ago = dt - datetime.timedelta(hours=1)
# start_time = one_hour_ago.strftime('%H%m')
# end_time = dt.strftime('%H%m')

files_path = bucket + '/' + satellite + '/'  + sensor + '/' + product + '/' + str(year) + '/' + str(month).zfill(2) + '/' + str(day).zfill(2)
files = fs.ls(files_path)

matches = [file for file in files if (file.split('/')[-1].split('_')[3][9:13] >= start_time and file.split('/')[-1].split('_')[3][9:13] <= end_time)]

for match in matches:
    print("Downloading: ", match)
    fs.get(match, str(directory_path / subdir / match.split('/')[-1]))