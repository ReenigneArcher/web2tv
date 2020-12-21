# web2tv
This project contains python2 scripts which load and parse tv guide information and return the information in xml format (http://wiki.xmltv.org/index.php/XMLTVFormat) (https://github.com/XMLTV/xmltv/blob/master/xmltv.dtd). You can then use the xml in various other programs such as xTeVe (https://github.com/xteve-project/xTeVe) or other iptv clients that allow epg in xml format. Currently the following sources are supported.
-plext.tv
-pluto.tv

Additionally there are some m3u list generators. The following are supported currently.
-NextPVR
-pluto.tv

This does not work in python 3 yet. If anyone would like to review the code to get it up to python 3 standards that would be welcome.

# plex2xml
Arguments:

'-t', '--token', type=str, nargs=1, required=True, help='Token is required. To obtain token open plex in a Firefox and login. Then right click the page and then click "Inspect Element". Go to the network tab of the inspector. Open the Live TV (From Plex) section. Now sort the inspector by domain and look for the domain that is "epg.provider.plex.tv". Double click the file that begins with grid?. The token is found in the url of this page.'

'-d', '--days', type=int, nargs=1, required=False, default=[7], help='Days of EPG to collect.'

'-p', '--pastdays', type=int, nargs=1, required=False, default=[0], help='Days in past of EPG to collect.'

'-l', '--language', type=str, nargs=1, required=False, default=['en'], help='Plex language... Get from url same as token.'

'-f', '--file', type=str, nargs=1, required=False, default=['plex2xml.xml'], help='Full destination filepath. Default is plex2xml.xml. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-o', '--offset', type=str, nargs=1, required=False, default=['+0000'], help='Timezone offset. Enter "-0500" for EST.'

# plutotv2xml
Arguments:

'-d', '--days', type=int, nargs=1, required=False, default=[1], help='Days of EPG to collect. Pluto.TV only provides roughtly 2 hours of EPG. Increasing this number will have little or no effect.'

'-p', '--pastdays', type=int, nargs=1, required=False, default=[0], help='Days in past of EPG to collect. No airing informationn collected if this is greater than 0.'

'-f', '--file', type=str, nargs=1, required=False, default=['plutotv.xml'], help='Full destination filepath. Default is plutotv.xml. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-o', '--offset', type=str, nargs=1, required=False, default=['-0000'], help='Timezone offset. Enter "-0500" for EST. No offset needed during initial testing.'

# nextpvr2m3u
Arguments:

-f', '--file', type=str, nargs=1, required=False, default=['nextpvr.m3u'], help='Full destination filepath. Default is nextpvr.m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'

'-i', '--ip', type=str, nargs=1, required=False, default=['127.0.0.1'], help='IP Address of NextPVR server. Default is 127.0.0.1'

'--port', type=int, nargs=1, required=False, default=[8866], help='Port number of NextPVR server. Default is 8866.'

'--pin', type=str, nargs=1, required=False, default=['0000'], help='Pin used to access NextPVR api. Default is 0000.'

# plutotv2m3u
Arguments:

'-f', '--file', type=str, nargs=1, required=False, default=['plutotv.m3u'], help='Full destination filepath. Default is plutotv.m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'
