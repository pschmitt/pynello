# pynello

## Public API

This is new prefered way of interacting with Nello devices.

### Get started

Shoot an email to hello@nello.io and ask them to generate a `client_id` for you.

### Code sample

```python
from pynello.public import Nello
n = Nello(client_id='you-need-to-ask-nello-for-this', username='me@example.com', password='somethingLong')

# Get available locations
n.locations
# Open the door ("main" ie. first available location)
n.main_location.open_door()

# Setup a webhook for new events
from pynello.public import NelloApiClient
n = NelloApiClient(client_id='you-need-to-ask-nello-for-this', username='me@example.com', password='somethingLong')
loc_id = n.list_locations().get('data')[0].get('location_id')
n.set_webook(loc_id, 'https://example.com/nello/event')
```

### Upstream documentation

- [Authentication](https://nelloauth.docs.apiary.io)
- [Nello API](https://nellopublicapi.docs.apiary.io/)

## Private API

**This API is deprecated**

A huge thanks to Oskar Neumann for his `original work <https://forum.fhem.de/index.php/topic,75127.msg668871.html>`_ on the `FHEM <https://fhem.de>`_ integration.

### Code sample

```python
from pynello.private import Nello
n = Nello(username='me@example.com', password='somethingLong')

# Get available locations
n.locations

# Open the door ("main" ie. first available location)
n.main_location.open_door()

# Get the recent activity
n.main_location.activity
```
