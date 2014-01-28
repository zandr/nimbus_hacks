Just a quick hack to put a tide clock on the Quirky Nimbus using https://github.com/jso/py-wink

By "quick hack", I mean:
 - No Error Handling
 - Doesn't notice that it runs out of data after about 3 days, nor does it refresh the data
 - Initializes the py-wink library with "../config.cfg", which pretty much means it has to live inside your py-wink install.
 - Stays in foreground (while loop with sleep)

Add your client id and client secret to config.cfg, then run login.py to get the right credentials into config.cfg. (this is documented in the py-wink readme)

Get an API key from http://www.wunderground.com/weather/api and add that, along with your location, to tides.cfg. I use a five-digit zip code for a location string.
