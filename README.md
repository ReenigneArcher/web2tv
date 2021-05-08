# web2tv
This project contains python scripts which load and parse tv guide information and return the information in xml format (http://wiki.xmltv.org/index.php/XMLTVFormat) (https://github.com/XMLTV/xmltv/blob/master/xmltv.dtd). You can then use the xml in various other programs such as xTeVe (https://github.com/xteve-project/xTeVe) or other iptv clients that allow epg in xml format.

Additionally there are scripts which generate m3u lists as well as some helper scripts.

________________
*EPG Generation*
- plex.tv (plex.py)
- pluto.tv (plutotv.py)
________________
*M3U Generation*
- NextPVR (nextpvr.py)
- plex.tv (plex.py)
-  pluto.tv (plutotv.py)
-  m3u (convert m3u for use with Streamlink)
________________
*Helper Scripts*
-  Plex DVR (update_plexDVR.py)

All scripts were tested using Python 3.8


# m3u_modder
description="Python script to convert m3u for use with streamlink."

'-i', '--inFile', type=str, nargs=1, required=False, default=['streamlink.m3u'], help='Full input file filepath. Full file path can be specified. If only file name is specified then file will be used from the current working directory if it exists.'
    
'-o', '--outFile', type=str, nargs=1, required=False, default=['streamlink.m3u'], help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--protocol', type=str, nargs=1, required=False, default=['httpstream://'], help='Stream url protocol.'

# nextpvr
description="Python script to convert pluto tv channels into m3u format."

-f', '--file', type=str, nargs=1, required=False, default=['nextpvr.m3u'], help='Full destination filepath. Default is nextpvr.m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'

'-i', '--ip', type=str, nargs=1, required=False, default=['127.0.0.1'], help='IP Address of NextPVR server. Default is 127.0.0.1'

'--port', type=int, nargs=1, required=False, default=[8866], help='Port number of NextPVR server. Default is 8866.'

'--pin', type=str, nargs=1, required=False, default=['0000'], help='Pin used to access NextPVR api. Default is 0000.'

'--streamlink', action='store_true', required=False, help='Generate the stream urls for use with Streamlink.'


# plex
description="Python script to convert plex livetv guide into xml/m3u format."

'-t', '--token', type=str, nargs=1, required=True, help='Token is required. Follow Plex instructions for finding the token. https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/#toc-0')

'-d', '--days', type=int, nargs=1, required=False, default=[7], help='Days of info to collect. Max if 21.'

'-p', '--pastdays', type=int, nargs=1, required=False, default=[0], help='Days in past of info to collect. Max is 1.'

'-l', '--language', type=str, nargs=1, required=False, default=['en'], help='Plex language... Get from url same as token.'

#xml arguments

'-x', '--xmlFile', type=str, nargs=1, required=False, default=['plex2.xml'], help='Full destination filepath for xml. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'--xml', action='store_true', required=False, help='Generate the xml file.'
    
#m3u arguments

'-m', '--m3uFile', type=str, nargs=1, required=False, default=['plex2.m3u'], help='Full destination filepath for m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'

'--m3u', action='store_true', required=False, help='Generate the m3u file.'

'--streamlink', action='store_true', required=False, help='Generate the stream urls for use with Streamlink.'


# plutotv
description="Python script to convert pluto tv guide into xml/m3u format."

'-e', '--epgHours', type=int, nargs=1, required=False, default=[10], help='Hours of EPG to collect. Pluto.TV only provides a few hours of EPG. Max allowed is 12.'

#xml arguments

'-x', '--xmlFile', type=str, nargs=1, required=False, default=['plutotv.xml'], help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'--xml', action='store_true', required=False, help='Generate the xml file.'
    
#m3u arguments

'-m', '--m3uFile', type=str, nargs=1, required=False, default=['plutotv.m3u'], help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.'

'-p', '--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.'

'-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.'

'-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.'

'--m3u', action='store_true', required=False, help='Generate the m3u file.'

'--streamlink', action='store_true', required=False, help='Generate the stream urls for use with Streamlink.'


# update_plexDVR
description="Python script to refresh Plex DVR guide(s)."

'-u', '--uri', type=str, nargs=1, required=False, default=['http://127.0.0.1:32400'], help='Uri to access plex.'

'-t', '--token', type=str, nargs=1, required=True, default=[''], help='Plex server token'
