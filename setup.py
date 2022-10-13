#!/usr/bin/env python

#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2022 Marine Institute
#       Diego Pereiro
#
#       diego.pereiro@marine.ie
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------

import os
import setuptools

here = os.path.abspath(os.path.dirname(__file__))
exec(open(os.path.join(here, 'opendrift/version.py')).read())

setuptools.setup(
    name        = 'OpenDrift',
    description = 'OpenDrift - a framework for ocean trajectory modeling',
    author      = 'Knut-Frode Dagestad / MET Norway',
    url         = 'https://github.com/OpenDrift/opendrift',
    download_url = 'https://github.com/OpenDrift/opendrift',
    version = __version__,
    license = 'GPLv2',
    install_requires = [
        'numpy',
        'scipy',
        'matplotlib',
        'netCDF4',
        'pyproj',
        'cartopy',
    ],
    packages = setuptools.find_packages(),
    include_package_data = True,
    setup_requires = ['setuptools_scm'],
    tests_require = ['pytest'],
    scripts = ['opendrift/scripts/hodograph.py',
               'opendrift/scripts/readerinfo.py',
               'opendrift/scripts/opendrift_plot.py',
               'opendrift/scripts/opendrift_animate.py',
               'opendrift/scripts/opendrift_gui.py',
               'opendrift/scripts/mp4_to_gif.bash']
)

