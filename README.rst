stereo-loader
===============

Python data loader for some STEREO instruments (i.e., magnetic field and charged particles). At the moment provides released data obtained by SunPy through CDF files from CDAWeb for the following datasets:

- ``'HET'``: STEREO IMPACT/HET Level 1 Data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_HET>`_) 
- ``'LET'``: STEREO IMPACT/LET Level 1 Data (`Info <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_LET>`_)
- ``'MAG'``: STEREO IMPACT/MAG Magnetic Field Vectors (RTN or SC) (`Info RTN <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAG_RTN>`_, `Info SC <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAG_SC>`_)
- ``'MAGB'``: STEREO IMPACT/MAG Burst Mode (~0.03 sec) Magnetic Field Vectors (RTN or SC) (`Info RTN <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAGB_RTN>`_, `Info SC <https://cdaweb.gsfc.nasa.gov/misc/NotesS.html#STA_L1_MAGB_SC>`_)
- ``'SEPT'``: STEREO IMPACT/SEPT Level 2 Data (`Info 1 <http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/about.txt>`_, `Info 2 <http://www2.physik.uni-kiel.de/STEREO/data/sept/level2/SEPT_L2_description.pdf>`_)

Installation
------------

stereo_loader requires python >= 3.6 and SunPy >= 3.1.3

It can be installed from this repository using pip:

.. code:: bash

    pip install git+https://github.com/jgieseler/stereo-loader

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
                          resample='10min')

Input
~~~~~

-  ``instrument``: ``'HET'``, ``'LET'``, ``'MAG'``, ``'MAGB'``, or ``'SEPT'``. See above for explanation.
-  ``startdate``, ``enddate``: datetime object or "standard" datetime string
-  ``spacecraft``: String, optional. Name of STEREO spacecraft: ``'ahead'`` or ``'behind'``, by default ``'ahead'``.
-  ``mag_coord``: String, optional. Coordinate system for MAG: ``'RTN'`` or ``'SC'``, by default ``'RTN'``.
-  ``sept_species``: String, optional. Particle species for SEPT: ``'e'`` for electrons or ``'p'`` for protons (resp. ions), by default ``'e'``.
-  ``sept_viewing``: String, optional. Viewing direction for SEPT: ``'sun'``, ``'asun'``, ``'north'``, or ``'south'``, by default ``'sun'``.
-  ``path``: String, optional. Local path for storing downloaded data, e.g. ``path='data/wind/3dp/'``. By default `None`. Default setting saves data according to `sunpy's Fido standards <https://docs.sunpy.org/en/stable/guide/acquiring_data/fido.html#downloading-data>`_.
-  ``resample``: Pandas frequency (e.g., ``'1min'`` or ``'1h'``), or ``None``, optional. Frequency to which the original data is resamepled. By default ``None``.

Return
~~~~~~

-  Pandas dataframe and metadata (latter might be empty at the moment). See info links above for the different datasets for a description of the dataframe columns.


Data folder structure
---------------------

- SEPT: All data files are automatically saved in a ``data`` subfolder in the current working directory if ``path`` is not defined.
- All other instruments: All data files are automatically saved in a ``sunpy`` subfolder of the current user home directory if ``path`` is not defined.


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
