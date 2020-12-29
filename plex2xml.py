# -*- coding: utf-8 -*-

import argparse
import urllib2
import time
from datetime import datetime, date
import json
import cgi

#url variables
type = '1%2C4'

#xml constants
source_info_url = '"https://epg.provider.plex.tv/"'
source_info_name = '"plex.tv"'
generator_info_name = '"web2tv"'
generator_info_url = '"https://github.com/ReenigneArcher/web2tv"'

if __name__ == '__main__':
    def quote_remover(string):
        if string.startswith('"') and string.endswith('"'):
            string = string[1:-1]
        elif string.startswith("'") and string.endswith("'"):
            string = string[1:-1]
        else:
            string = string
        return string
    
    def find_between_split(s, start, end):
        try:
            return (s.split(start))[1].split(end)[0]
        except IndexError:
            return ""

    def GetListOfSubstrings(stringSubject,string1,string2):
        MyList = []
        intstart=0
        strlength=len(stringSubject)
        continueloop = 1
        while(intstart < strlength and continueloop == 1):
            intindex1=stringSubject.find(string1,intstart)
            if(intindex1 != -1): #The substring was found, lets proceed
                intindex1 = intindex1+len(string1)
                intindex2 = stringSubject.find(string2,intindex1)
                if(intindex2 != -1):
                    subsequence=stringSubject[intindex1:intindex2]
                    MyList.append(subsequence)
                    intstart=intindex2+len(string2)
                else:
                    continueloop=0
            else:
                continueloop=0
        return MyList

    def load_url(url):
        URL_Req = urllib2.Request(url)
        
        try:
            URL_Response = urllib2.urlopen(URL_Req)
            URL_Source = URL_Response.read()
        except urllib2.HTTPError as e: #https://www.programcreek.com/python/example/68989/requests.HTTPError
            URL_Source = ""
        
        URL_Source = URL_Source.replace('\t', '') #remove tabs
        
        return URL_Source
    
    def load_json(url):
        req = urllib2.Request(url)
        req.add_header("Accept",'application/json')
        opener = urllib2.build_opener()
        f = opener.open(req)
        result = json.loads(f.read())
        return result
    
    def fix(text):
        text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace') #https://stackoverflow.com/a/1061702/11214013
        return text
    
    #argparse
    parser = argparse.ArgumentParser(description="Python script to convert plex livetv guide into xml format.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--token', type=str, nargs=1, required=True, help='Token is required. Follow Plex instructions for finding the token. https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/#toc-0')
    parser.add_argument('-d', '--days', type=int, nargs=1, required=False, default=[7], help='Days of EPG to collect. Max if 21.')
    parser.add_argument('-p', '--pastdays', type=int, nargs=1, required=False, default=[0], help='Days in past of EPG to collect. Max is 1.')
    parser.add_argument('-l', '--language', type=str, nargs=1, required=False, default=['en'], help='Plex language... Get from url same as token.')
    parser.add_argument('-f', '--file', type=str, nargs=1, required=False, default=['plex2xml.xml'], help='Full destination filepath. Default is plex2xml.xml. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    parser.add_argument('-o', '--offset', type=str, nargs=1, required=False, default=['+0000'], help='Timezone offset. Enter "-0500" for EST.')
    opts = parser.parse_args()
    
    #string agruments
    x_plex_token = quote_remover(opts.token[0])
    x_plex_language = quote_remover(opts.language[0])
    offset = quote_remover(opts.offset[0])
    xml_destination = quote_remover(opts.file[0])
    
    #integer arguments
    days_future = opts.days[0]
    if days_future > 21:
        days_future = 21
    days_past = opts.pastdays[0]
    if days_past > 1:
        days_past = 1
    
    print('token: ' + x_plex_token)
    print('language: ' + x_plex_language)
    print('days: ' + str(days_future))
    print('pastdays: ' + str(days_past))
    print('offset: ' + offset)
    print('file: ' + xml_destination)

    #dictionary arrays to build
    channel_dict = {'data': []}
    program_dict = {'data': []}
    
    keyErrors_contentRating = []
    errorDetails_contentRating = []
    
    keyErrors_channelCategory = []
    errorDetails_chanelCategory = []

    #dictionary prebuild
    rating_system = { 'tv-y' : 'TV Parental Guidelines',
                    'tv-y7' : 'TV Parental Guidelines',
                    'tv-g' : 'TV Parental Guidelines',
                    'tv-pg' : 'TV Parental Guidelines',
                    'tv-14' : 'TV Parental Guidelines',
                    'tv-ma' : 'TV Parental Guidelines',
                    'g' : 'MPAA',
                    'pg' : 'MPAA',
                    'pg-13' : 'MPAA',
                    'r' : 'MPAA',
                    'nc-17' : 'MPAA',
                    'u' : 'BBFC',
                    #'pg' : 'BBFC',
                    '12' : 'BBFC',
                    '12a' : 'BBFC',
                    '15' : 'BBFC',
                    '18' : 'BBFC',
                    'r18' : 'BBFC',
                    '0+' : 'GIO',
                    '6+' : 'GIO',
                    '12+' : 'GIO',
                    '15+' : 'GIO',
                    '18+' : 'GIO',
                    'nr' : 'n/a',
                    'ur' : 'n/a'
                    }

    rating_logo = { 'tv-y' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/TV-Y_icon.svg/240px-TV-Y_icon.svg.png',
                    'tv-y7' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/TV-Y7_icon.svg/240px-TV-Y7_icon.svg.png',
                    'tv-g' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/TV-G_icon.svg/240px-TV-G_icon.svg.png',
                    'tv-pg' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/TV-PG_icon.svg/240px-TV-PG_icon.svg.png',
                    'tv-14' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/TV-14_icon.svg/240px-TV-14_icon.svg.png',
                    'tv-ma' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/TV-MA_icon.svg/240px-TV-MA_icon.svg.png',
                    'g' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/RATED_G.svg/276px-RATED_G.svg.png',
                    'pg' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/RATED_PG.svg/320px-RATED_PG.svg.png',
                    'pg-13' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/RATED_PG-13.svg/320px-RATED_PG-13.svg.png',
                    'r' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/RATED_R.svg/284px-RATED_R.svg.png',
                    'nc-17' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Nc-17.svg/320px-Nc-17.svg.png',
                    'u' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/BBFC_U_2019.svg/270px-BBFC_U_2019.svg.png',
                    #'pg' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/BBFC_PG_2019.svg/270px-BBFC_PG_2019.svg.png',
                    '12' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/BBFC_12_2019.svg/240px-BBFC_12_2019.svg.png',
                    '12a' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/BBFC_12A_2019.svg/240px-BBFC_12A_2019.svg.png',
                    '15' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/BBFC_15_2019.svg/240px-BBFC_15_2019.svg.png',
                    '18' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/BBFC_18_2019.svg/240px-BBFC_18_2019.svg.png',
                    'r18' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/BBFC_R18_2019.svg/240px-BBFC_R18_2019.svg.png',
                    '0+' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/GSRR_G_logo.svg/240px-GSRR_G_logo.svg.png',
                    '6+' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/GSRR_P_logo.svg/240px-GSRR_P_logo.svg.png',
                    '12+' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/GSRR_PG_12_logo.svg/240px-GSRR_PG_12_logo.svg.png',
                    '15+' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/GSRR_PG_15_logo.svg/240px-GSRR_PG_15_logo.svg.png',
                    '18+' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/GSRR_R_logo.svg/240px-GSRR_R_logo.svg.png',
                    'nr' : 'https://loyoladigitaladvertising.files.wordpress.com/2014/02/nr-logo.png',
                    'ur' : 'http://3.bp.blogspot.com/-eyIrE_lKiMg/Ufbis7lWLlI/AAAAAAAAAK4/4XTYHCU8Dx4/s1600/ur+logo.png'
                    }
    
    #(Family, Movie, News, Sports, Talk)
    channel_category = {    '001' : '', #n/a
                            '002' : '', #Skills + Thrills
                            '003' : '', #Crime 360
                            '004' : '', #Lively Place
                            '005' : '', #Journy
                            '006' : '', #Nosey
                            '007' : '', #Deal or No Deal
                            '008' : 'Family', #Eddie's Wonderland
                            '009' : '', #n/a
                            '010' : '', #n/a
                            '011' : 'Family', #Toon Goggles
                            '012' : 'Family', #KidsFlix
                            '013' : 'Family', #Kidoodle TV
                            '014' : '', #n/a
                            '015' : 'Family', #TG Junior
                            '016' : 'Family', #pocket.watch
                            '017' : 'Family', #Ryan and Friends
                            '018' : 'Family', #Monster Kids
                            '019' : 'Anime', #CONtv Anime
                            '020' : 'Anime', #RetroCrush
                            '021' : 'News', #Cheddar News
                            '022' : 'News', #Yahoo! Finance
                            '023' : 'News', #Newsy
                            '024' : 'News', #Reuters Now
                            '025' : '', #n/a
                            '026' : 'News', #Newsmax
                            '027' : 'News', #Hollywire
                            '028' : 'Family', #The Bob Ross Channel
                            '029' : 'Sports', #Wipeout Xtra
                            '030' : '', #Judge Faith
                            '031' : 'Family', #AFV Family
                            '032' : '', #The Pet Collective
                            '033' : '', #n/a
                            '034' : '', #Comedy Dynamics
                            '035' : '', #n/a
                            '036' : '', #FailArmy
                            '037' : '', #n/a
                            '038' : '', #Gusto TV
                            '039' : '', #Tastemade
                            '040' : '', #DrinkTV
                            '041' : '', #Cooking Panda
                            '042' : '', #The Design Network
                            '043' : '', #n/a
                            '044' : '', #n/a
                            '045' : '', #The Boat Show
                            '046' : '', #Choppertown
                            '047' : '', #Electric Now
                            '048' : '', #Real Nosey
                            '049' : '', #Made In Hollywood
                            '050' : '', #Law & Crime
                            '051' : '', #Game Show Central
                            '052' : '', #PopStar! TV
                            '053' : '', #So...Real
                            '054' : '', #Revry
                            '055' : '', #Revry2
                            '056' : '', #RevryNews
                            '057' : '', #n/a
                            '058' : '', #Love Destination
                            '059' : '', #Dove Channel
                            '060' : '', #Whistle TV
                            '061' : '', #Glewed.TV
                            '062' : '', #PlayWorks
                            '063' : '', #People are Awesome
                            '064' : '', #n/a
                            '065' : '', #MOVIESPHERE
                            '066' : '', #n/a
                            '067' : 'Movie', #Hi-YAH!
                            '068' : 'Movie', #Wu Tang Collection
                            '069' : '', #Midnight Pulp
                            '070' : '', #Filmstream
                            '071' : 'Movie', #Hollywood Classics
                            '072' : 'Movie', #Maverick Black Cinema
                            '073' : 'Movie', #The Film Detective
                            '074' : '', #DarkMatter TV
                            '075' : 'Movie', #Gravitas Movies
                            '076' : '', #The Archive
                            '077' : '', #Runtime
                            '078' : 'Documentary', #Real Stories
                            '079' : '', #Wonder
                            '080' : '', #Timeline
                            '081' : 'Documentary', #MagellanTV NOW
                            '082' : 'Documentary', #Docurama
                            '083' : 'Sports', #fubo Sports Network
                            '084' : 'Sports', #ACCDN
                            '085' : 'Sports', #MAV TV Select
                            '086' : '', #n/a
                            '087' : 'Sports', #SurfNow TV
                            '088' : 'Sports', #EDGEsport
                            '089' : 'Sports', #SportsGrid
                            '090' : 'Sports', #Stadium
                            '091' : '', #n/a
                            '092' : 'Sports', #Channel Fight
                            '093' : 'Sports', #Ring of Honor
                            '094' : 'Sports', #WPT
                            '095' : 'Sports', #PlayersTV
                            '096' : 'Video Games', #IGN TV
                            '097' : 'Video Games', #VENN
                            '098' : 'Video Games', #Tankee
                            '099' : '', #n/a
                            '100' : '', #SKWAD
                            '101' : '', #CONtv
                            '102' : '', #Xplore
                            '103' : 'News', #WeatherSpy
                            '104' : '', #n/a
                            '105' : '', #Unidentified
                            '106' : '', #Sony Canal Comedias
                            '107' : '', #Sony Canam Competencias
                            '108' : '', #Sony Canal Novelas
                            '109' : '', #Runtime Español
                            '110' : '', #Canela TV
                            '111' : 'Music', #Latido Music
                            '112' : 'Family', #AFV Español
                            '113' : '', #BAMBU
                            '114' : '', #KMTV
                            '115' : '', #YUYU TV
                            '116' : '', #AsianCrush
                            '117' : 'Music', #Party Tyme Karaoke
                            '118' : '', #n/a
                            '119' : 'Music', #Loop Trending
                            '120' : 'Music', #Loop TGIF
                            '121' : 'Music', #Loop Hottest
                            '122' : 'Music', #Loop Flashback
                            '123' : 'Music', #Loop That's Hot
                            '124' : 'Music', #Loop 90's
                            '125' : 'Music', #Loop 80's
                            '126' : 'Music', #Loop Far Out
                            '127' : 'Music', #Party
                            '128' : 'Music', #Loop Beast
                            '129' : 'Music', #Loop Hip Hop
                            '130' : 'Music', #Loop R&B
                            '131' : 'Music', #Latin x Loop
                            '132' : 'Music', #Loop Texas Tunes
                            '133' : 'Music', #Loop Electronica
                            '134' : 'Music', #Loop Synapse
                            '135' : 'Music', #Loop Unwind
                            '136' : 'Music', #Loop Bedroom
                            '137' : 'Music' #Loop Yacht Rock
                            }

    #constants
    day = 24 * 60 * 60
    half_hour = 60 * 60 / 2
    
    days_total = days_future + days_past #define the total number of days

    now = time.time()
    now = int(now)
    now_30 = now - (now % half_hour) #go back to nearest 30 minutes
    epg_begin = now_30 - (days_past * day) #now - 30 minutes - past days

    epg_end = (days_future * day) + now_30 + half_hour

    x = 0
    while x < days_total: #do this for each day
        print('Loading Grid for PlexTV, day: ' + str(x+1) + '/' + str(days_total))
        if x == 0:
            interval_a = int(epg_begin)
        else:
            interval_a = int(interval_b)
        interval_b = int(interval_a + day)
        
        #url = 'https://epg.provider.plex.tv/grid?type=' + type + '&sort=beginsAt&endsAt%3E=' + str(interval_a) + '&beginsAt%3C=' + str(interval_b) + '&X-Plex-Product=' + x_plex_product + '&X-Plex-Version=' + x_plex_version + '&X-Plex-Client-Identifier=' + x_plex_client_identifer + '&X-Plex-Platform=' + x_plex_platform + '&X-Plex-Platform-Version=' + x_plex_platform_version + '&X-Plex-Sync-Version=' + x_plex_sync_version + '&X-Plex-Features=' + x_plex_features + '&X-Plex-Model=' + x_plex_model + '&X-Plex-Device=' + x_plex_device + '&X-Plex-Device-Screen-Resolution=' + x_plex_device_screen_resolution + '&X-Plex-Token=' + x_plex_token + '&X-Plex-Language=' + x_plex_language + '&X-Plex-Drm=' + x_plex_drm + '&X-Plex-Text-Format=' + x_plex_text_format + '&X-Plex-Provider-Version=' + x_plex_provider_version
        url = 'https://epg.provider.plex.tv/grid?type=' + type + '&sort=beginsAt&endsAt%3E=' + str(interval_a) + '&beginsAt%3C=' + str(interval_b) + '&X-Plex-Token=' + x_plex_token + '&X-Plex-Language=' + x_plex_language

        print('url[' + str(x+1) + ']: ' + url)
        grid = load_json(url)
        
        #with open('plex_xml_' + str(x) + '.json', 'w') as write_file:
        #    json.dump(grid, write_file, indent=4)
        
        y = 0
        for key in grid['MediaContainer']['Metadata']:
            type = fix(grid['MediaContainer']['Metadata'][y]['type'])
            if type == 'movie':
                try:
                    thumb = fix(grid['MediaContainer']['Metadata'][y]['thumb'])
                except KeyError as e:
                    thumb = ''
                title = fix(grid['MediaContainer']['Metadata'][y]['title'])
                subTitle = ''
                grandparentKey = ''
                grandparentType = ''
                grandparentGuid = ''
                parentIndex = ''
                index = ''
                grandparentRatingKey = ''
            elif type == 'episode':
                try:
                    thumb = fix(grid['MediaContainer']['Metadata'][y]['grandparentThumb'])
                except KeyError as e:
                    try:
                        thumb = fix(grid['MediaContainer']['Metadata'][y]['thumb'])
                    except KeyError as e:
                        thumb = ''
                title = fix(grid['MediaContainer']['Metadata'][y]['grandparentTitle'])
                subTitle = fix(grid['MediaContainer']['Metadata'][y]['title'])
                grandparentKey = fix(grid['MediaContainer']['Metadata'][y]['grandparentKey'])
                grandparentType = fix(grid['MediaContainer']['Metadata'][y]['grandparentType'])
                grandparentGuid = fix(grid['MediaContainer']['Metadata'][y]['grandparentGuid'])
                parentIndex = grid['MediaContainer']['Metadata'][y]['parentIndex']
                try:
                    index = grid['MediaContainer']['Metadata'][y]['index']
                except KeyError as e:
                    index = ''
                grandparentRatingKey = fix(grid['MediaContainer']['Metadata'][y]['grandparentRatingKey'])
            addedAt = grid['MediaContainer']['Metadata'][y]['addedAt']
            skipParent = grid['MediaContainer']['Metadata'][y]['skipParent']
            year = grid['MediaContainer']['Metadata'][y]['year']
            ratingKey = fix(grid['MediaContainer']['Metadata'][y]['ratingKey'])
            try:
                summary = fix(grid['MediaContainer']['Metadata'][y]['summary'])
            except KeyError as e:
                summary = ''
            key = fix(grid['MediaContainer']['Metadata'][y]['key'])
            originallyAvailableAt = fix(grid['MediaContainer']['Metadata'][y]['originallyAvailableAt'])
            #duration = grid['MediaContainer']['Metadata'][y]['duration']
            guid = fix(grid['MediaContainer']['Metadata'][y]['guid'])
            userState = grid['MediaContainer']['Metadata'][y]['userState']
            try:
                contentRating = fix(grid['MediaContainer']['Metadata'][y]['contentRating'])
            except KeyError as e:
                contentRating = 'NR'
        
            z = 0
            for key in grid['MediaContainer']['Metadata'][y]['Media']:
                origin = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['origin'])
                onAir = grid['MediaContainer']['Metadata'][y]['Media'][z]['onAir']
                beginsAt = grid['MediaContainer']['Metadata'][y]['Media'][z]['beginsAt']
                protocol = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['protocol'])
                premiere = grid['MediaContainer']['Metadata'][y]['Media'][z]['premiere']
                endsAt = grid['MediaContainer']['Metadata'][y]['Media'][z]['endsAt']
                channelVcn = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['channelVcn'])
                channelIdentifier = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['channelIdentifier'])
                channelTitle = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['channelTitle'])
                channelThumb = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['channelThumb'])
                duration = grid['MediaContainer']['Metadata'][y]['Media'][z]['duration']
                channelArt = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['channelArt'])
                videoResolution =  fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['videoResolution'])
                id = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['id'])
                channelShortTitle = fix(grid['MediaContainer']['Metadata'][y]['Media'][z]['channelShortTitle'])
        
                if duration > 0: #only add programs with a defined duration
                    program_dict['data'].append({
                    'ratingKey': ratingKey,
                    'title': title,
                    'subTitle': subTitle,
                    'summary': summary,
                    'addedAt': addedAt,
                    'originallyAvailableAt': originallyAvailableAt, #previously shown start time... need to format as YYYYMMDDHHMMSS -HHMM ... can omit unknowns
                    'thumb': thumb,
                    'type': type,
                    'grandparentType': grandparentType,
                    'parentIndex': parentIndex, #season number
                    'index': index, #episode number
                    'contentRating': contentRating, #content rating of the program... TV-PG for example
                    'year': year, #content rating of the program... TV-PG for example
                    'beginsAt': beginsAt, #start time in unix
                    'duration': duration, #duration
                    'endsAt': endsAt, #end time in unix
                    'premiere': premiere, #1 for new airings
                    'videoResolution': videoResolution, #video quality
                    'channelShortTitle': channelShortTitle, #short title
                    'channelVcn': channelVcn }) #vcn
            
                channel_dict['data'].append({
                'channelTitle': channelTitle, #vcn + short title
                'channelIdentifier': channelIdentifier, #key
                'channelShortTitle': channelShortTitle, #friendly name
                'channelVcn': channelVcn, #number
                'channelArt': channelArt, #number
                'channelThumb': channelThumb}) #icon
                
                z += 1
            y += 1
        x += 1

    # remove duplicates
    channel_list = [i for n, i in enumerate(channel_dict['data']) if i not in channel_dict['data'][n + 1:]]
    print('Channels Found: ' + str(len(channel_list)+1))
    program_list = [i for n, i in enumerate(program_dict['data']) if i not in program_dict['data'][n + 1:]]
    print('Programs Found: ' + str(len(program_list)+1))

    #start the xml file
    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
    xml += '\n<tv source-info-url=' + source_info_url + ' source-info-name=' + source_info_name + ' generator-info-name=' + generator_info_name + ' generator-info-url=' + generator_info_url + '>'

    x = 0
    while x < len(channel_list): #do this for each channel
        xml += '\n\t<channel id="' + 'PLEX.TV.' + channel_list[x]['channelShortTitle'].replace(' ', '.') + '">'
        xml += '\n\t\t<display-name>' + channel_list[x]['channelShortTitle'] + '</display-name>'
        xml += '\n\t\t<display-name>' + channel_list[x]['channelTitle'] + '</display-name>'
        xml += '\n\t\t<display-name>' + channel_list[x]['channelVcn'] + '</display-name>'
        xml += '\n\t\t<display-name>' + channel_list[x]['channelIdentifier'] + '</display-name>'
        xml += '\n\t\t<icon src="' + channel_list[x]['channelThumb'] + '" />'
        xml += '\n\t</channel>'
        print(channel_list[x]['channelTitle'] + ' will be added to the xml.' + str(x+1) + '/' + str(len(channel_list)))
        x += 1

    x = 0
    while x < len(program_list): #do this for each program
        timeStart = str(datetime.fromtimestamp(int(program_list[x]['beginsAt']))).replace('-', '').replace(':', '').replace(' ', '')
        timeEnd = str(datetime.fromtimestamp(int(program_list[x]['endsAt']))).replace('-', '').replace(':', '').replace(' ', '')
        timeAdded = str(datetime.fromtimestamp(int(program_list[x]['addedAt']))).replace('-', '').replace(':', '').replace(' ', '')
        timeOriginal = program_list[x]['originallyAvailableAt'].replace('-', '').replace(':', '').replace('T', '').replace('Z', '')
        
        xml += '\n\t<programme start="' + timeStart + ' ' + offset + '" stop="' + timeEnd + ' ' + offset + '" channel="PLEX.TV.' + program_list[x]['channelShortTitle'].replace(' ', '.') + '">' #program,, start, and end time
        
        xml += '\n\t\t<title lang="' + x_plex_language + '">' + program_list[x]['title'] + '</title>' #title
        print(program_list[x]['title'] + ',ratingKey: ' + program_list[x]['ratingKey'] + ' will be added to the xml.' + str(x+1) + '/' + str(len(program_list)))
        
        xml += '\n\t\t<desc lang="' + x_plex_language + '">' + program_list[x]['summary'] + '</desc>' #description/summary
        xml += '\n\t\t<length units="seconds">' + str(program_list[x]['duration']) + '</length>' #duration/length
        if timeOriginal != "": #if timeOriginal is not blank
            xml += '\n\t\t<date>' + timeOriginal + ' ' + offset + '</date>' #date
        elif str(program_list[x]['year']) != "": #else if year is not blank
            xml += '\n\t\t<date>' + str(program_list[x]['year']) + '</date>' #year

        if program_list[x]['type'] == 'episode':
            
            if program_list[x]['title'] != program_list[x]['subTitle'] and program_list[x]['subTitle'] != '': #if not equal
                xml += '\n\t\t<sub-title lang="' + x_plex_language + '">' + program_list[x]['subTitle'] + '</sub-title>' #sub-title/tagline
            xml += '\n\t\t<icon src="' + program_list[x]['thumb'] + '" />' #thumb/icon
            
            #episode numbering
            if program_list[x]['parentIndex'] != '' and program_list[x]['index'] != '':
                if int(program_list[x]['parentIndex']) < 10:
                    num_season = '0' + str(program_list[x]['parentIndex'])
                else:
                    num_season = str(program_list[x]['parentIndex'])
                if int(program_list[x]['index']) < 10:
                    num_episode = '0' + str(program_list[x]['index'])
                else:
                    num_episode = str(program_list[x]['index'])
                xml += '\n\t\t<episode-num system="onscreen">' + 'S' + num_season + 'E' + num_episode + '</episode-num>' #episode number
                xml += '\n\t\t<episode-num system="common">' + 'S' + num_season + 'E' + num_episode + '</episode-num>' #episode number
                indexSeason = int(program_list[x]['parentIndex'])
                indexSeason -= 1
                indexEpisode = int(program_list[x]['index'])
                indexEpisode -= 1
                xml += '\n\t\t<episode-num system="xmltv_ns">' + str(indexSeason) + '.' + str(indexEpisode) + '.</episode-num>' #episode number
            xml += '\n\t\t<episode-num system="plex">' + program_list[x]['ratingKey'] + '</episode-num>' #episode number
        
        try:
            xml += '\n\t\t<category lang="' + x_plex_language + '">' + channel_category[program_list[x]['channelVcn']] + '</category>' #music category
        except KeyError:
            keyErrors_channelCategory.append(program_list[x]['channelVcn'])
            errorDetails_chanelCategory.append('Vcn: ' + program_list[x]['channelVcn'] + ', channelShortTitle: ' + program_list[x]['channelShortTitle'])
        
        #content rating key
        #print(program_list[x]['contentRating'])
        if program_list[x]['contentRating'] != '': #if not blank
            try:
                xml += '\n\t\t<rating system="' + rating_system[program_list[x]['contentRating'].lower()] + '">' #rating system
                xml += '\n\t\t\t<value>' + program_list[x]['contentRating'] + '</value>' #rating
                xml += '\n\t\t\t<icon src="' + rating_logo[program_list[x]['contentRating'].lower()] + '" />' #rating logo from dictionary
                xml += '\n\t\t</rating>' #end rating key
            except KeyError:
                keyErrors_contentRating.append(program_list[x]['contentRating'])
                errorDetails_contentRating.append('Title: ' + program_list[x]['title'] + ', GrandparentTitle: ' + program_list[x]['grandparentTitle'])
        
        if program_list[x]['premiere'] == False: #if not premiere add the previously shown tag
            if timeOriginal != "": #if we have the originallyAvailableAt add it to the tag
                xml += '\n\t\t<previously-shown start="' + timeOriginal + ' ' + offset + '" />'
            else: #else don't add start time to the tag
                xml += '\n\t\t<previously-shown />'
        elif program_list[x]['premiere'] == True: #if program is premiere add the tag
            xml += '\n\t\t<premiere />'
        
        #add the video quality
        xml += '\n\t\t<video>'
        xml += '\n\t\t\t<quality>' + program_list[x]['videoResolution'] + 'p</quality>'
        xml += '\n\t\t</video>'
        
        #finish
        xml += '\n\t</programme>'
        
        x += 1

    xml += '\n</tv>\n'
    print('xml is ready to write')
    #print(xml)

    #write the file
    file_handle = open(xml_destination, "w")
    print('xml is being created')
    file_handle.write(xml)
    print('xml is being written')
    file_handle.close()
    print('xml is being closed')
    
    if keyErrors_contentRating != []:
        print('...')
        print('The following content rating key_errors were found. :' +str(keyErrors_contentRating))
        print(errorDetails_contentRating)
        print('Submit an issue on github so they can be added.')
    
    if keyErrors_channelCategory != []:
        print('...')
        print('The following channel key_errors were found. :' +str(keyErrors_channelCategory))
        print(errorDetails_chanelCategory)
        print('Submit an issue on github so they can be added.')

