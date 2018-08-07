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
