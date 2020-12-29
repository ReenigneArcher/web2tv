# web2tv
This project contains python2 scripts which load and parse tv guide information and return the information in xml format (http://wiki.xmltv.org/index.php/XMLTVFormat) (https://github.com/XMLTV/xmltv/blob/master/xmltv.dtd). You can then use the xml in various other programs such as xTeVe (https://github.com/xteve-project/xTeVe) or other iptv clients that allow epg in xml format. Currently the following sources are supported.
-plext.tv
-pluto.tv

Additionally there are some m3u list generators. The following are supported currently.
-NextPVR
-pluto.tv
-m3u (convert m3u for use with Streamlink)

This does not work in python 3 yet. If anyone would like to review the code to get it up to python 3 standards that would be welcome.

# plex
description="Python script to convert plex livetv guide into xml/m3u format.", formatter_class=argparse.RawTextHelpFormatter)

'-t', '--token', type=str, nargs=1, required=True, help='Token is required. Follow Plex instructions for finding the token. https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/#toc-0')

'-d', '--days', type=int, nargs=1, required=False, default=[7], help='Days of info to collect. Max if 21.'

'-p', '--pastdays', type=int, nargs=1, required=False, default=[0], help='Days in past of info to collect. Max is 1.'

'-l', '--language', type=str, nargs=1, required=False, default=['en'], help='Plex language... Get from url same as token.'

#xml arguments

'-x', '--xmlFile', type=str, nargs=1, required=False, default=['plex2.xml'], help='Full destination filepath for xml. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-o', '--offset', type=str, nargs=1, required=False, default=['+0000'], help='Timezone offset. Enter "-0500" for EST.'

'--xml', action='store_true', required=False, help='Generate the xml file.'
    
#m3u arguments

'-m', '--m3uFile', type=str, nargs=1, required=False, default=['plex2.m3u'], help='Full destination filepath for m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'

'--m3u', action='store_true', required=False, help='Generate the m3u file.'

'--streamlink', action='store_true', required=False, help='Generate the stream urls for use with Streamlink.'

# plutotv2xml
description="Python script to convert pluto tv guide into xml format."

'-e', '--epgHours', type=int, nargs=1, required=False, default=[10], help='Hours of EPG to collect. Pluto.TV only provides a few hours of EPG. Max allowed is 12.'

'-f', '--file', type=str, nargs=1, required=False, default=['plutotv.xml'], help='Full destination filepath. Default is plutotv.xml. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-o', '--offset', type=str, nargs=1, required=False, default=['-0000'], help='Timezone offset. Enter "-0500" for EST. Used to correct times in final xml file. Not needed during initial testing.'

'-t', '--timezone', type=str, nargs=1, required=False, default=['-0000'], help='Timezone offset. Enter "-0500" for EST. Used when grabbing guide data from pluto.tv.'

# nextpvr2m3u
description="Python script to convert pluto tv channels into m3u format."

-f', '--file', type=str, nargs=1, required=False, default=['nextpvr.m3u'], help='Full destination filepath. Default is nextpvr.m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'

'-i', '--ip', type=str, nargs=1, required=False, default=['127.0.0.1'], help='IP Address of NextPVR server. Default is 127.0.0.1'

'--port', type=int, nargs=1, required=False, default=[8866], help='Port number of NextPVR server. Default is 8866.'

'--pin', type=str, nargs=1, required=False, default=['0000'], help='Pin used to access NextPVR api. Default is 0000.'

'--streamlink', action='store_true', required=False, help='Generate the stream urls for use with Streamlink.'

# plutotv2m3u
description="Python script to convert pluto tv channels into m3u format."

'-f', '--file', type=str, nargs=1, required=False, default=['plutotv.m3u'], help='Full destination filepath. Default is plutotv.m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'

'--streamlink', action='store_true', required=False, help='Generate the stream urls for use with Streamlink.'

# webm3u2m3u
description="Python script to convert m3u for use with streamlink."

'-i', '--inFile', type=str, nargs=1, required=False, default=['streamlink.m3u'], help='Full input file filepath. Full file path can be specified. If only file name is specified then file will be used from the current working directory if it exists.'
    
'-o', '--outFile', type=str, nargs=1, required=False, default=['streamlink.m3u'], help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--protocol', type=str, nargs=1, required=False, default=['httpstream://'], help='Stream url protocol.'
