pynello
=======

A huge thanks to Oskar Neumann for his `original work <https://forum.fhem.de/index.php/topic,75127.msg668871.html>`_ on the `FHEM <https://fhem.de>`_ integration.

Code sample
-----------

.. code:: python

  from pynello import Nello
  n = Nello(username='me@example.com', password='somethingLong')
  # Get available locations
  n.locations
  # Open the door ("main" ie. first available location)
  n.main_location.open_door()
  # Get the recent activity
  n.main_location.activity
