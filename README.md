# plex2xml
plex2xml is a python 2 script which will load and parse Live TV (On Plex) guide information back to xml format. This allows you to feed the guide information into a program such as xTeVe (https://github.com/xteve-project/xTeVe) for example.

This does not work in python 3 yet. If anyone would like to review the code to get it up to python 3 standards that would be welcome.

Arguments:
-t, --token     Token is required. To obtain token open plex in a Firefox and login. Then right click the page and then click "Inspect Element". Go to the network tab of the inspector. Open the Live TV (From Plex) section. Now sort the inspector by domain and look for the domain that is "epg.provider.plex.tv". Double click the file that begins with grid?. The token is found in the url of this page.

-d, --days      Days of EPG to collect. Default: 7

-p, --pastdays  Days in past of EPG to collect. Default: 0

-l, --language  Plex language... Get from url same as token. Default: 'en' (no testing has been done in other languages)

-f, --file      Full destination filepath. Default is plex2xml.xml. Full file path can be specified. If only file name is specified then file will be placed in the current working directory. Default: 'plex2xml.xml'

-o, --offset    Timezone offset. Enter "-0500" for EST. Default: +0000 (https://en.wikipedia.org/wiki/List_of_UTC_time_offsets)
