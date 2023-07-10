This package is not maintained any more! Please use https://github.com/serpentine-h2020/SEPpy instead!
======================================================================================================

stereo-loader
=============

Python data loader for some STEREO instruments (i.e., magnetic field and charged particles). At the moment provides released data obtained by SunPy through CDF files from CDAWeb for the following datasets:

- ``'HET'``: STEREO IMPACT/HET Level 1 Data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_HET>`_) 
- ``'LET'``: STEREO IMPACT/LET Level 1 Data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_LET>`_)
- ``'MAG'``: STEREO IMPACT/MAG Magnetic Field Vectors (RTN or SC) (`Info RTN <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAG_RTN>`_, `Info SC <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAG_SC>`_)
- ``'MAGB'``: STEREO IMPACT/MAG Burst Mode (~0.03 sec) Magnetic Field Vectors (RTN or SC) (`Info RTN <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAGB_RTN>`_, `Info SC <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAGB_SC>`_)
- ``'SEPT'``: STEREO IMPACT/SEPT Level 2 Data (`Info 1 <http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/about.txt>`_, `Info 2 <http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/SEPT_L2_description.pdf>`_) [1]_

.. [1] STEREO IMPACT/SEPT Level 2 data is directly obtained through ASCII files from the `server of the instrument team <http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/>`_, not via SunPy/CDAWeb.

Disclaimer
----------
This software is provided "as is", with no guarantee. It is no official data source, and not officially endorsed by the corresponding instrument teams. Please always refer to the instrument descriptions before using the data!


Usage
-----

The standard usecase is to utilize the ``stereo_load`` function, which
returns a Pandas dataframe of the measurements and some metadata.

.. code:: python

   from stereo_loader import stereo_load

   df, meta = stereo_load(instrument='sept',
                          startdate='2010/04/17',
                          enddate='2010/04/18',
                          spacecraft='ahead',
                          mag_coord='RTN',
                          sept_species='e',
                          sept_viewing='asun',
                          path=None,
                          resample='10min',
                          pos_timestamp=None)

Input
~~~~~

-  ``instrument``: ``'HET'``, ``'LET'``, ``'MAG'``, ``'MAGB'``, or ``'SEPT'``. See above for explanation.
-  ``startdate``, ``enddate``: datetime object or "standard" datetime string
-  ``spacecraft``: String, optional. Name of STEREO spacecraft: ``'ahead'`` or ``'behind'``, by default ``'ahead'``.
-  ``mag_coord``: String, optional. Coordinate system for MAG: ``'RTN'`` or ``'SC'``, by default ``'RTN'``.
-  ``sept_species``: String, optional. Particle species for SEPT: ``'e'`` for electrons or ``'p'`` for protons (resp. ions), by default ``'e'``.
-  ``sept_viewing``: String, optional. Viewing direction for SEPT: ``'sun'``, ``'asun'``, ``'north'``, or ``'south'``, by default ``'sun'``.
-  ``path``: String, optional. Local path for storing downloaded data, e.g. ``path='data/stereo/'``. By default ``None``. Default setting saves data according to `sunpy's Fido standards <https://docs.sunpy.org/en/stable/guide/acquiring_data/fido.html#downloading-data>`_. The default setting can be changed according to the corresponding `sunpy documentation <https://docs.sunpy.org/en/stable/guide/customization.html>`_, where the setting that needs to be changed is named ``download_dir`` (e.g., one could set it to a shared directory on a multi-user system).
-  ``resample``: Pandas frequency (e.g., ``'1min'`` or ``'1h'``), or ``None``, optional. Frequency to which the original data is resamepled. By default ``None``.
-  ``pos_timestamp``: String, optional. Change the position of the timestamp: ``'center'`` or ``'start'`` of the accumulation interval, by default ``None``.
-  ``max_conn``: Integer, optional. The number of parallel download slots used by ``Fido.fetch``, by default ``5``.

Return
~~~~~~

-  Pandas dataframe and dictionary of metadata (e.g., energy channels). See info links above for the different datasets for a description of the dataframe columns.


Data folder structure
---------------------

- SEPT: All data files are automatically saved in a ``data`` subfolder in the current working directory if ``path`` is not defined.
- All other instruments: All data files are automatically saved in a ``sunpy`` subfolder of the current user home directory if ``path`` is not defined.


Combine intensitiy for multiple energy channels (SEPT only)
-----------------------------------------------------------

For SEPT measurements, it's possible to combine the intensities of multiple adjacent energy channels with the function ``calc_av_en_flux_SEPT``. It returns a Pandas Dataframe with the arithmetic mean of all intensities and a string providing the corresponding energy range. The following example demonstrates how to build an average channel of SEPT proton energy channels 25 to 30. 

**Note that the channel numbers provided by** ``combine_channels`` **refer to the channel numbers of the SEPT instrument (and not the index number of the variable)! This is escpecially important because for SEPT the lowest channels usually are omitted, and here only channels 2 to 31 are provided!**

.. code:: python

    from stereo_loader import stereo_load, calc_av_en_flux_SEPT
    
    # first, load original data:
    df, channels_dict_df = stereo_load(instrument='sept',
                                       startdate="2021-4-16",
                                       enddate="2021-4-20",
                                       spacecraft='a',
                                       sept_species='p',
                                       sept_viewing='sun',
                                       resample=None,
                                       path=None)
    # define energy channel range that should be combined:
    combine_channels = [25, 30]
    sept_avg_int, sept_avg_chstring = calc_av_en_flux_SEPT(df, channels_dict_df, combine_channels)
    print(sept_avg_chstring)


License
-------

This project is Copyright (c) Jan Gieseler and licensed under
the terms of the BSD 3-clause license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause license. See the licenses folder for
more information.

Acknowledgements
----------------

The development of this software has received funding from the European Union's Horizon 2020 research and innovation programme under grant agreement No 101004159 (SERPENTINE).
