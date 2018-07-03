Overview
========
Python wrapper for the Toodledo v3 API which is documented at http://api.toodledo.com/3/

Usage
=====

.. code:: python

toodledo = Toodledo(clientId="YourClientId", clientSecret="YourClientSecret", tokenStorage=TokenStorageFile(YourConfigFile, scope="basic tasks notes folders write")

account = toodledo.GetAccount()

allTasks = toodledo.GetTasks(params={})
