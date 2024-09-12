# -*- coding: utf8 -*-
"""

************
``setup.py``
************

`GNU General Public License v3`_ © 2015-2019 University of Oxford & contributors

.. _GNU General Public License v3: _static/LICENSE


"""

import setuptools

if __name__ == "__main__":
    with open("README.rst", "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name="xml2vhdl-ox",
        version="0.2.3",
        author="Department of Physics",
        author_email="xml2vhdl@ox.ac.uk",
        description="XML to VHDL Memory-Mapped Generation",
        long_description=long_description,
        long_description_content_type="text/x-rst",
        url="https://bitbucket.org/ricch/xml2vhdl",
        packages=setuptools.find_packages(),
        include_package_data=True,
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: POSIX :: Linux",
        ],
    )
