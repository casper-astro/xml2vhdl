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
colorlog                 4.0.2
logging                  0.4.9.6
lxml                     4.3.0
numpy                    1.16.0
pyyaml                   3.13
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
