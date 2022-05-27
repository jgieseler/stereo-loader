# Licensed under a 3-clause BSD style license - see LICENSE.rst

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    pass  # package is not installed

import cdflib
import glob
import os
import pooch
import warnings
import datetime as dt
import numpy as np
import pandas as pd

from sunpy.net import Fido
from sunpy.net import attrs as a
from sunpy.timeseries import TimeSeries


# omit Pandas' PerformanceWarning
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)


def resample_df(df, resample):
    """
    Resample Pandas Dataframe
    """
    try:
        # _ = pd.Timedelta(resample)  # test if resample is proper Pandas frequency
        df = df.resample(resample).mean()
        df.index = df.index + pd.tseries.frequencies.to_offset(pd.Timedelta(resample)/2)
    except ValueError:
        raise Warning(f"Your 'resample' option of [{resample}] doesn't seem to be a proper Pandas frequency!")
    return df


def stereo_sept_download(date, spacecraft, species, viewing, path=None):
    """Download STEREO/SEPT level 2 data file from Kiel university to local path

    Parameters
    ----------
    date : datetime object
        datetime of data to retrieve
    spacecraft : str
        'ahead' or 'behind'
    species : str
        'ele' or 'ion'
    viewing : str
        'sun', 'asun', 'north', 'south' - viewing direction of instrument
    path : str
        local path where the files will be stored

    Returns
    -------
    downloaded_file : str
        full local path to downloaded file
    """

    # add a OS-specific '/' to end end of 'path'
    if path:
        if not path[-1] == os.sep:
            path = f'{path}{os.sep}'

    if species.lower() == 'e':
        species = 'ele'
    if species.lower() == 'p' or species.lower() == 'h' or species.lower() == 'i':
        species = 'ion'

    if spacecraft.lower() == 'ahead' or spacecraft.lower() == 'a':
        base = "http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/ahead/1min/"
    elif spacecraft.lower() == 'behind' or spacecraft.lower() == 'b':
        base = "http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/behind/1min/"

    file = "sept_"+spacecraft.lower()+"_"+species.lower()+"_"+viewing.lower()+"_"+str(date.year)+"_"+date.strftime('%j')+"_1min_l2_v03.dat"

    url = base+str(date.year)+'/'+file

    try:
        downloaded_file = pooch.retrieve(url=url, known_hash=None, fname=file, path=path, progressbar=True)
    except ModuleNotFoundError:
        downloaded_file = pooch.retrieve(url=url, known_hash=None, fname=file, path=path, progressbar=False)

    return downloaded_file


def stereo_sept_loader(startdate, enddate, spacecraft, species, viewing, resample=None, path=None, all_columns=False):
    """Loads STEREO/SEPT data and returns it as Pandas dataframe together with a dictionary providing the energy ranges per channel

    Parameters
    ----------
    startdate : str
        start date
    enddate : str
        end date
    spacecraft : str
        STEREO spacecraft 'a'head or 'b'ehind
    species : str
        particle species: 'e'lectrons or 'p'rotons (resp. ions)
    viewing : str
        'sun', 'asun', 'north', 'south' - viewing direction of instrument
    resample : str, optional
        resample frequency in format understandable by Pandas, e.g. '1min', by default None
    path : str, optional
        local path where the files are/should be stored, by default None
    all_columns : boolean, optional
        if True provide all availalbe columns in returned dataframe, by default False

    Returns
    -------
    df : Pandas dataframe
        dataframe with either 15 channels of electron or 30 channels of proton/ion fluxes and their respective uncertainties
    channels_dict_df : dict
        Pandas dataframe giving details on the measurement channels
    """

    # catch variation of input parameters:
    if species.lower() == 'e':
        species = 'ele'
    if species.lower() == 'p' or species.lower() == 'h' or species.lower() == 'i':
        species = 'ion'
    if spacecraft.lower() == 'a' or spacecraft.lower() == 'sta':
        spacecraft = 'ahead'
    if spacecraft.lower() == 'b' or spacecraft.lower() == 'stb':
        spacecraft = 'behind'

    if not path:
        path = os.getcwd()+os.sep+'data'
    # create list of files to load:
    dates = pd.date_range(start=startdate, end=enddate, freq='D')
    filelist = []
    for i, doy in enumerate(dates.day_of_year):
        try:
            file = glob.glob(f"{path}{os.sep}sept_{spacecraft}_{species}_{viewing}_{dates[i].year}_{doy}_*.dat")[0]
        except IndexError:
            # print(f"File not found locally from {path}, downloading from http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/")
            file = stereo_sept_download(dates[i], spacecraft, species, viewing, path)
        filelist.append(file)
    filelist = np.sort(filelist)

    # channel dicts from Nina:
    ch_strings = ['45.0-55.0 keV', '55.0-65.0 keV', '65.0-75.0 keV', '75.0-85.0 keV', '85.0-105.0 keV', '105.0-125.0 keV', '125.0-145.0 keV', '145.0-165.0 keV', '165.0-195.0 keV', '195.0-225.0 keV', '225.0-255.0 keV', '255.0-295.0 keV', '295.0-335.0 keV', '335.0-375.0 keV', '375.0-425.0 keV']
    mean_E = []
    for i in range(len(ch_strings)):
        temp  = ch_strings[i].split(' keV')
        clims = temp[0].split('-')
        lower = float(clims[0])
        upper = float(clims[1])
        mean_E.append(np.sqrt(upper*lower))
    #
    echannels = {'bins': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                 'ch_strings': ch_strings,
                 'DE': [0.0100, 0.0100, 0.0100, 0.0100, 0.0200, 0.0200, 0.0200, 0.0200, 0.0300, 0.0300, 0.0300, 0.0400, 0.0400, 0.0400, 0.0500],
                 'mean_E': mean_E}
    pchannels = {'bins': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
                 'ch_strings': ['84.1-92.7 keV', '92.7-101.3 keV', '101.3-110.0 keV', '110.0-118.6 keV', '118.6-137.0 keV', '137.0-155.8 keV', '155.8-174.6 keV', '174.6-192.6 keV', '192.6-219.5 keV', '219.5-246.4 keV', '246.4-273.4 keV', ' 273.4-312.0 keV', '312.0-350.7 keV', '350.7-389.5 keV', '389.5-438.1 keV', '438.1-496.4 keV', '496.4-554.8 keV', ' 554.8-622.9 keV', '622.9-700.7 keV', '700.7-788.3 keV', '788.3-875.8 keV', '875.8- 982.8 keV', '982.8-1111.9 keV', '1111.9-1250.8 keV', '1250.8-1399.7 keV', '1399.7-1578.4 keV', '1578.4-1767.0 keV', '1767.0-1985.3 keV', '1985.3-2223.6 keV', '2223.6-6500.0 keV'],
                 'DE': [0.0086, 0.0086, 0.0087, 0.0086, 0.0184, 0.0188, 0.0188, 0.018, 0.0269, 0.0269, 0.027, 0.0386, 0.0387, 0.0388, 0.0486, 0.0583, 0.0584, 0.0681, 0.0778, 0.0876, 0.0875, 0.107, 0.1291, 0.1389, 0.1489, 0.1787, 0.1886, 0.2183, 0.2383, 4.2764],
                 'mean_E': [88.30, 96.90, 105.56, 114.22, 127.47, 146.10, 164.93, 183.38, 205.61, 232.56, 259.55, 292.06, 330.78, 369.59, 413.09, 466.34, 524.79, 587.86, 660.66, 743.21, 830.90, 927.76, 1045.36, 1179.31, 1323.16, 1486.37, 1670.04, 1872.97, 2101.07, 3801.76]}
    # :channel dicts from Nina

    if species == 'ele':
        channels_dict = echannels
    elif species == 'ion':
        channels_dict = pchannels

    # create Pandas Dataframe from channels_dict:
    channels_dict_df = pd.DataFrame.from_dict(channels_dict)
    channels_dict_df.index = channels_dict_df.bins
    channels_dict_df.drop(columns=['bins'], inplace=True)

    # column names in data files:
    # col_names = ['julian_date', 'year', 'frac_doy', 'hour', 'min', 'sec'] + \
    #             [f'ch_{i}' for i in range(2, len(channels_dict['bins'])+2)] + \
    #             [f'err_ch_{i}' for i in range(2, len(channels_dict['bins'])+2)] + \
    #             ['integration_time']
    col_names = ['julian_date', 'year', 'frac_doy', 'hour', 'min', 'sec'] + \
                [f'ch_{i}' for i in channels_dict_df.index] + \
                [f'err_ch_{i}' for i in channels_dict_df.index] + \
                ['integration_time']

    # read files into Pandas dataframes:
    df = pd.read_csv(filelist[0], header=None, sep='\s+', names=col_names, comment='#')
    if len(filelist) > 1:
        for file in filelist[1:]:
            t_df = pd.read_csv(file, header=None, sep='\s+', names=col_names, comment='#')
            df = pd.concat([df, t_df])

    # generate datetime index from Julian date:
    df.index = pd.to_datetime(df['julian_date'], origin='julian', unit='D')
    df.index.name = 'time'

    # drop some unused columns:
    if not all_columns:
        df = df.drop(columns=['julian_date', 'year', 'frac_doy', 'hour', 'min', 'sec', 'integration_time'])

    # replace bad data with np.nan:
    df = df.replace(-9999.900, np.nan)

    # optional resampling:
    if isinstance(resample, str):
        df = resample_df(df, resample)

    return df, channels_dict_df


def stereo_load(instrument, startdate, enddate, spacecraft='ahead', mag_coord='RTN', sept_species='e', sept_viewing='sun', path=None, resample=None):
    """
    Downloads CDF files via SunPy/Fido from CDAWeb for HET, LET, MAG, and SEPT onboard STEREO

    Parameters
    ----------
    instrument : {str}
        Name of STEREO instrument:
        - 'HET': STEREO IMPACT/HET Level 1 Data
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_HET
        - 'LET': STEREO IMPACT/LET Level 1 Data
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_LET
        - 'MAG': STEREO IMPACT/MAG Magnetic Field Vectors (RTN or SC => mag_coord)
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAG_RTN
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAG_SC
        - 'MAGB': STEREO IMPACT/MAG Burst Mode (~0.03 sec) Magnetic Field Vectors (RTN or SC => mag_coord)
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAGB_RTN
            https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAGB_SC
        - 'SEPT': STEREO IMPACT/SEPT Level 2 Data
    startdate, enddate : {datetime or str}
        Datetime object (e.g., dt.date(2021,12,31) or dt.datetime(2021,4,15)) or "standard"
        datetime string (e.g., "2021/04/15") (enddate must always be later than startdate)
    spacecraft : {str}, optional
        Name of STEREO spacecraft: 'ahead' or 'behind', by default 'ahead'
    mag_coord : {str}, optional
        Coordinate system for MAG: 'RTN' or 'SC', by default 'RTN'
    sept_species : {str}, optional
        Particle species for SEPT: 'e'lectrons or 'p'rotons (resp. ions), by default 'e'
    sept_viewing : {str}, optional
        Viewing direction for SEPT: 'sun', 'asun', 'north', or 'south', by default 'sun'
    path : {str}, optional
        Local path for storing downloaded data, by default None
    resample : {str}, optional
        resample frequency in format understandable by Pandas, e.g. '1min', by default None


    Returns
    -------
    df : {Pandas dataframe}
        See links above for the different datasets for a description of the dataframe columns
    """
    if startdate==enddate:
        print(f'"startdate" and "enddate" must be different!')

    # find name variations
    if spacecraft.lower()=='a' or spacecraft.lower()=='sta':
        spacecraft='ahead'
    if spacecraft.lower()=='b' or spacecraft.lower()=='stb':
        spacecraft='behind'

    if instrument.upper()=='SEPT':
        df, channels_dict_df = stereo_sept_loader(startdate=startdate,
                                                  enddate=enddate,
                                                  spacecraft=spacecraft,
                                                  species=sept_species,
                                                  viewing=sept_viewing,
                                                  resample=resample,
                                                  path=path,
                                                  all_columns=False)
        return df, channels_dict_df
    else:
        # define spacecraft string
        sc = 'ST' + spacecraft.upper()[0]

        # define dataset
        if instrument.upper()[:3]=='MAG':
            dataset = sc + '_L1_' + instrument.upper() + '_' + mag_coord.upper()
        else:
            dataset = sc + '_L1_' + instrument.upper()

        trange = a.Time(startdate, enddate)
        cda_dataset = a.cdaweb.Dataset(dataset)
        try:
            result = Fido.search(trange, cda_dataset)
            downloaded_files = Fido.fetch(result, path=path)  # use Fido.fetch(result, path='/ThisIs/MyPath/to/Data/{file}') to use a specific local folder for saving data files
            downloaded_files.sort()
            data = TimeSeries(downloaded_files, concatenate=True)
            df = data.to_dataframe()
            if isinstance(resample, str):
                df = resample_df(df, resample)
        except RuntimeError:
            print(f'Unable to obtain "{dataset}" data for {startdate}-{enddate}!')
            downloaded_files = []
            df = []
        return df, downloaded_files


# df, meta = stereo_load('sept', '2010/04/17', '2010/04/18', 'a', sept_viewing='asun', resample='10min', path=path)
