.. include:: ../_static/ou_header.rst

.. _installation:

############
Installation
############

``XML2VHDL`` has been developed for use in a Linux based environment.

.. _prerequisites:

Prerequisites
=============

Required Software
-----------------

The following software is required:

====== =============
``-``  Version
====== =============
python >= 2.7.14
====== =============

.. _python_modules:


Python Modules
--------------

Python Modules are handled by ``pipenv`` and stored in: ``./scripts/python/xml2vhdl/Pipfile``

======================== ==========
Module                   Version
======================== ==========
alabaster                0.7.12
babel                    2.6.0
breathe                  4.11.1
certifi                  2018.11.29
chardet                  3.0.4
colorlog                 4.0.2
docutils                 0.14
idna                     2.8
imagesize                1.1.0
jinja2                   2.10
logging                  0.4.9.6
lxml                     4.3.0
markupsafe               1.1.0
numpy                    1.16.0
packaging                19.0
pygments                 2.3.1
pyparsing                2.3.1
pytz                     2018.9
pyyaml                   3.13
releases                 1.6.1
requests                 2.21.0
semantic-version         2.6.0
six                      1.12.0
snowballstemmer          1.2.1
sphinx                   1.7.9
sphinxcontrib-websupport 1.1.0
typing                   3.6.6
urllib3                  1.24.1
======================== ==========

Installed Tools
---------------

None

Required Environment Variables
==============================

None


Installation Instructions
=========================

1. Checkout/Clone ``xml2vhdl`` from the repository:

.. code-block:: bash

   git clone https://<BITBUCKET_USERNAME>@bitbucket.org/ricch/xml2vhdl.git

2. Navigate to local cloned location:

.. code-block:: bash

   cd xml2vhdl

3. Install the python virtual environment using ``pipenv`` ensuring the version of python meets the
   :ref:`prerequisites`.

.. code-block:: bash

   pipenv install --two

6. Run ``pipenv`` in ``shell`` or ``run`` mode from: ``xml2vhdl`` location:

.. code-block:: bash

   pipenv shell
   python ./xml2vhdl.py
   ## Or:
   pipenv run python ./xml2vhdl.py


Links
=====

* `https://docs.pipenv.org <https://docs.pipenv.org>`_
