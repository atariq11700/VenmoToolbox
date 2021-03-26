# VenmoToolbox
  
## This is a small project I made to interact with the venmo api. It is only written in python and uses only the standard library. Credit due to https://github.com/mmohades for the unofficial api documention.  

<br>

### The project structure is as follows:
* `` src/VenmoToolbox.py ``
This is the wrapper for the api. It only provides a means with interacting with the api and returning the response. It does have some error catching but not alot. 

* `` src/VenmoMenu.py `` 
This is a CLI menu that implements the functionality exposed in ``VenmoToolbox.py``.  It has error handling built in. It allows a user to login and perform interactions with the api such as getting a users venmo data, sending and requesting money, converting a venmo user to venmo id and vice versa, sending friend requests, and more.
