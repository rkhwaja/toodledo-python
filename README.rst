Overview
========
Python wrapper for the Toodledo v3 API which is documented at http://api.toodledo.com/3/

.. image:: https://travis-ci.org/rkhwaja/toodledo-python.svg?branch=master
   :target: https://travis-ci.org/rkhwaja/toodledo-python

Usage
=====

.. code-block:: python

  toodledo = Toodledo(
    clientId="YourClientId",
    clientSecret="YourClientSecret",
    tokenStorage=TokenStorageFile(YourConfigFile),
    scope="basic tasks notes folders write")

  account = toodledo.GetAccount()

  allTasks = toodledo.GetTasks(params={})

Running tests
=============

To run the tests, set the following environment variables:

- TOODLEDO_TOKEN_STORAGE - path to a json file which will contain the credentials
- TOODLEDO_CLIENT_ID - your client id (see https://api.toodledo.com/3/account/doc_register.php)
- TOODLEDO_CLIENT_SECRET - your client secret (see https://api.toodledo.com/3/account/doc_register.php)

Then generate the credentials json file by running

.. code-block:: bash

  python generate-credentials.py

Then run the tests by executing

.. code-block:: bash

  pytest

in the root directory.
