# -*- coding: utf-8 -*-

import argparse
import urllib2
import time
from datetime import datetime, date

#url variables
type = '1%2C4'
#x_plex_product = 'Plex%20Web'
#x_plex_version = '4.48.1'
#x_plex_client_identifer = ''
#x_plex_platform = 'Firefox'
#x_plex_platform_version = '83.0'
#x_plex_sync_version = '2'
#x_plex_features = 'external-media%2Cindirect-media'
#x_plex_model = 'hosted'
#x_plex_device = 'Windows'
#x_plex_device_screen_resolution = '1366x418%2C1366x768'
#x_plex_drm = 'widevine'
#x_plex_text_format = 'plain'
#x_plex_provider_version = '1.3'

#xml constants
source_info_url = '"https://epg.provider.plex.tv/"'
source_info_name = '"plex.tv"'
generator_info_name = '"plex2xml"'
generator_info_url = '"https://github.com/ReenigneArcher/plex2xml"'

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
    
    #argparse
    parser = argparse.ArgumentParser(description="Python script to convert plex livetv guide into xml format.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--token', type=str, nargs=1, required=True, help='Token is required. To obtain token open plex in a Firefox and login. Then right click the page and then click "Inspect Element". Go to the network tab of the inspector. Open the Live TV (From Plex) section. Now sort the inspector by domain and look for the domain that is "epg.provider.plex.tv". Double click the file that begins with grid?. The token is found in the url of this page.')
    parser.add_argument('-d', '--days', type=int, nargs=1, required=False, default=[7], help='Days of EPG to collect.')
    parser.add_argument('-p', '--pastdays', type=int, nargs=1, required=False, default=[0], help='Days in past of EPG to collect.')
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
    days_past = opts.pastdays[0]
    
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
        print('Loading Grid for Day: ' + str(x+1) + '/' + str(days_total))
        if x == 0:
            interval_a = int(epg_begin)
        else:
            interval_a = int(interval_b)
        interval_b = int(interval_a + day)
        
        #url = 'https://epg.provider.plex.tv/grid?type=' + type + '&sort=beginsAt&endsAt%3E=' + str(interval_a) + '&beginsAt%3C=' + str(interval_b) + '&X-Plex-Product=' + x_plex_product + '&X-Plex-Version=' + x_plex_version + '&X-Plex-Client-Identifier=' + x_plex_client_identifer + '&X-Plex-Platform=' + x_plex_platform + '&X-Plex-Platform-Version=' + x_plex_platform_version + '&X-Plex-Sync-Version=' + x_plex_sync_version + '&X-Plex-Features=' + x_plex_features + '&X-Plex-Model=' + x_plex_model + '&X-Plex-Device=' + x_plex_device + '&X-Plex-Device-Screen-Resolution=' + x_plex_device_screen_resolution + '&X-Plex-Token=' + x_plex_token + '&X-Plex-Language=' + x_plex_language + '&X-Plex-Drm=' + x_plex_drm + '&X-Plex-Text-Format=' + x_plex_text_format + '&X-Plex-Provider-Version=' + x_plex_provider_version
        url = 'https://epg.provider.plex.tv/grid?type=' + type + '&sort=beginsAt&endsAt%3E=' + str(interval_a) + '&beginsAt%3C=' + str(interval_b) + '&X-Plex-Token=' + x_plex_token + '&X-Plex-Language=' + x_plex_language

        #print('x[' + str(x) + ']: ' + url)
        grid_page = load_url(url)
        
        tmp_program = GetListOfSubstrings( grid_page,    '<Video guid="', '</Video>' )
        #print(tmp_program)
        if len(tmp_program) > 0:
            y = 0
            while y < len(tmp_program):
                #print('y: ' + str(y))
                tmp_airing = GetListOfSubstrings( tmp_program[y], '<Media ', '</Media>' )
                
                z = 0
                while z < len(tmp_airing):
                    #print('z: ' + str(z))
                    program_dict['data'].append({
                    'ratingKey': find_between_split( tmp_program[y], 'ratingKey="', '"' ), #type of episode number?
                    'title': find_between_split( tmp_program[y], 'title="', '"' ), #episode/movie title... if episode this is sub-title
                    'grandparentTitle': find_between_split( tmp_program[y], 'grandparentTitle="', '"' ), #episode/movie title... if episode this is sub-title
                    'summary': find_between_split( tmp_program[y], 'summary="', '"' ), #description
                    'addedAt': find_between_split( tmp_program[y], 'addedAt="', '"' ), #date... need to format as YYYYMMDDHHMMSS -HHMM ... can omit unknowns
                    'originallyAvailableAt': find_between_split( tmp_program[y], 'originallyAvailableAt="', '"' ), #previously shown start time... need to format as YYYYMMDDHHMMSS -HHMM ... can omit unknowns
                    'thumb': find_between_split( tmp_program[y], 'thumb="', '"' ), #poster
                    'grandparentThumb': find_between_split( tmp_program[y], 'grandparentThumb="', '"' ), #poster for episodes
                    'type': find_between_split( tmp_program[y], 'type="', '"' ), #episode or movie... if episode we'll build the episode number... if movie we'll add the Movie category
                    'grandparentType': find_between_split( tmp_program[y], 'grandparentType="', '"' ), #show...
                    'parentIndex': find_between_split( tmp_program[y], 'parentIndex="', '"' ), #season number
                    'index': find_between_split( tmp_program[y], 'index="', '"' ), #episode number
                    'contentRating': find_between_split( tmp_program[y], 'contentRating="', '"' ), #content rating of the program... TV-PG for example
                    'year': find_between_split( tmp_program[y], 'year="', '"' ), #content rating of the program... TV-PG for example
                
                    #use tmp_airing and Z index for the following
                    'beginsAt': find_between_split( tmp_airing[z], 'beginsAt="', '"' ), #start time in unix
                    'duration': find_between_split( tmp_airing[z], 'duration="', '"' ), #duration
                    'endsAt': find_between_split( tmp_airing[z], 'endsAt="', '"' ), #end time in unix
                    'premiere': find_between_split( tmp_airing[z], 'premiere="', '"' ), #1 for new airings
                    'videoResolution': find_between_split( tmp_airing[z], 'videoResolution="', '"' ), #video quality
                    'channelShortTitle': find_between_split( tmp_airing[z], 'channelShortTitle="', '"' ), #vcn + short title
                    'channelVcn': find_between_split( tmp_airing[z], 'channelVcn="', '"' )}) #vcn + short title
                
                    channel_dict['data'].append({
                    'channelTitle': find_between_split( tmp_airing[z], 'channelTitle="', '"' ), #vcn + short title
                    'channelIdentifier': find_between_split( tmp_airing[z], 'channelIdentifier="', '"' ), #key
                    'channelShortTitle': find_between_split( tmp_airing[z], 'channelShortTitle="', '"' ), #friendly name
                    'channelVcn': find_between_split( tmp_airing[z], 'channelVcn="', '"' ), #number
                    'channelThumb': find_between_split( tmp_airing[z], 'channelThumb="', '"' )}) #icon
                    
                    #channel_dict['data'] = [i for n, i in enumerate(channel_dict['data']) if i not in channel_dict['data'][n + 1:]]
                    #program_dict['data'] = [i for n, i in enumerate(program_dict['data']) if i not in program_dict['data'][n + 1:]]
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
        if program_list[x]['duration'] != '0': #skip programs which are 0 length
            timeStart = str(datetime.fromtimestamp(int(program_list[x]['beginsAt']))).replace('-', '').replace(':', '').replace(' ', '')
            timeEnd = str(datetime.fromtimestamp(int(program_list[x]['endsAt']))).replace('-', '').replace(':', '').replace(' ', '')
            timeAdded = str(datetime.fromtimestamp(int(program_list[x]['addedAt']))).replace('-', '').replace(':', '').replace(' ', '')
            timeOriginal = program_list[x]['originallyAvailableAt'].replace('-', '').replace(':', '').replace('T', '').replace('Z', '')
            
            xml += '\n\t<programme start="' + timeStart + ' ' + offset + '" stop="' + timeEnd + ' ' + offset + '" channel="PLEX.TV.' + program_list[x]['channelShortTitle'].replace(' ', '.') + '">' #program,, start, and end time
            
            xml += '\n\t\t<desc lang="' + x_plex_language + '">' + program_list[x]['summary'] + '</desc>' #description/summary
            xml += '\n\t\t<length units="seconds">' + program_list[x]['duration'] + '</length>' #duration/length
            if timeAdded != "": #if timeAdded is not blank
                xml += '\n\t\t<date>' + timeAdded + ' ' + offset + '</date>' #time added to guide
            elif program_list[x]['year'] != "": #else if year is not blank
                xml += '\n\t\t<date>' + program_list[x]['year'] + '</date>' #year added to guide

            if program_list[x]['type'] == 'episode':
                xml += '\n\t\t<title lang="' + x_plex_language + '">' + program_list[x]['grandparentTitle'] + '</title>' #title
                print(program_list[x]['grandparentTitle'] + ',ratingKey: ' + program_list[x]['ratingKey'] + ' will be added to the xml.' + str(x+1) + '/' + str(len(program_list)))
                if program_list[x]['title'] != program_list[x]['grandparentTitle']: #if not equal
                    xml += '\n\t\t<sub-title lang="' + x_plex_language + '">' + program_list[x]['title'] + '</sub-title>' #sub-title/tagline
                xml += '\n\t\t<icon src="' + program_list[x]['grandparentThumb'] + '" />' #thumb/icon
                
                #episode numbering
                if program_list[x]['parentIndex'] != '':
                    if program_list[x]['index'] != '':
                        if int(program_list[x]['parentIndex']) < 10:
                            num_season = '0' + program_list[x]['parentIndex']
                        else:
                            num_season = program_list[x]['parentIndex']
                        if int(program_list[x]['index']) < 10:
                            num_episode = '0' + program_list[x]['index']
                        else:
                            num_episode = program_list[x]['index']
                        xml += '\n\t\t<episode-num system="onscreen">' + 'S' + num_season + 'E' + num_episode + '</episode-num>' #episode number
                        xml += '\n\t\t<episode-num system="common">' + 'S' + num_season + 'E' + num_episode + '</episode-num>' #episode number
                        indexSeason = int(program_list[x]['parentIndex'])
                        indexSeason -= 1
                        indexEpisode = int(program_list[x]['index'])
                        indexEpisode -= 1
                        xml += '\n\t\t<episode-num system="xmltv_ns">' + str(indexSeason) + '.' + str(indexEpisode) + '</episode-num>' #episode number
                xml += '\n\t\t<episode-num system="plex">' + program_list[x]['ratingKey'] + '</episode-num>' #episode number
                
            elif program_list[x]['type'] == 'movie':
                xml += '\n\t\t<title lang="' + x_plex_language + '">' + program_list[x]['title'] + '</title>' #title
                print(program_list[x]['title'] + ',ratingKey: ' + program_list[x]['ratingKey'] + ' will be added to the xml.' + str(x+1) + '/' + str(len(program_list)))
                xml += '\n\t\t<icon src="' + program_list[x]['thumb'] + '" />' #thumb/icon
            
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
            
            if program_list[x]['premiere'] == '0': #if not premiere add the previously shown tag
                if timeOriginal != "": #if we have the originallyAvailableAt add it to the tag
                    xml += '\n\t\t<previously-shown start="' + timeOriginal + ' ' + offset + '" />'
                else: #else don't add start time to the tag
                    xml += '\n\t\t<previously-shown />'
            elif program_list[x]['premiere'] == '1': #if program is premiere add the tag
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

'''
info we need for each channel
-channel id (as number + text)
-display-name (as number + text)
-display-name (as number)
-display-name (as text)
-icon src (as url to a png file)

    <channel id="ch_id">
        <display-name>ch_d2</display-name>
        <display-name>ch_d0</display-name>
        <display-name>ch_d1</display-name>
        <icon src="ch_ico" />
    </channel>

'''

'''
info we need for each program
-start (YYYYMMDDHHMMSS + offset)
-stop (YYYYMMDDHHMMSS + offset)
-channel (channel id)
-title

    <programme start="YYYYMMDDHHMMSS + offset" stop="YYYYMMDDHHMMSS + offset" channel="ch_id">
        <title lang="en">pr_title</title>
        <sub-title lang="en">pr_subtitle</sub-title>
        <desc lang="en">pr_desc</desc>
        <date>pr_YYYY or pr_YYYYMMDD</date>
        <credits>
            <actor>pr_actor</actor>
            <director>pr_director</director>
            <producer>pr_producer</producer>
            <presenter>pr_presenter</presenter>
        </credits>
        <category lang="en">pr_cat</category>
        <length units="minutes">pr_length</length>
        <icon src="pr_ico" />
        <url>pr_url</url>
        <country>US</country>
        <episode-num system="common">S32E10</episode-num>
        <episode-num system="plex">ratingKey</episode-num>
        <episode-num system="onscreen">S32E10</episode-num>
        <episode-num system="xmltv_ns">31.9.</episode-num>
        <new /> #first episode of a show ever
        <premiere /> #plex shows as new episode?
        <previously-shown start="YYYYMMDDHHMMSS" />
        <live />
        <last-chance /> #never on air again after this
        <subtitles type="teletext" />
        <video>
            <quality>720p</quality>
        </video>
        <rating system="pr_rating_system">
            <value>pr_rating</value>
            <icon src="rating_symbol.png" />
        </rating>
    </programme>

pr_cat (Family, Movie, News, Sports, Talk)
pr_rating (TV-Y, TV-Y7, TV-G, TV-PG, TV-14, TV-MA)
pr_rating_system (VCHIP, MPAA)

https://github.com/XMLTV/xmltv/blob/master/xmltv.dtd
'''

'''
plex xml to tvg xml notes

-guid = plex url
-key = plex value
ratingKey = use as form of episode number
summary = description
type = type of program (episode, movie)
thumb = program icon
addedAt = added to guide at this unix time... date
-duration = duration in seconds?
-userState = 0 or 1... unknown?
title = show or movie title
grandparentTitle = show title (episodes only)
grandparentType = type (show) (episodes only)
grandparentThumb = show icon (episodes only)
-grandparentRatingKey = plex value (episodes only)
-grandparentGuid = plex url (episodes only)
-grandparentKey = plex value (episodes only)
index = episode number (episodes only)
parentIndex = season number (episodes only)
-skipParent = 0 or 1... unknown
contentRating = rating
originallyAvailableAt = release date
year = release year
beginsAt = unix time of program start
duration = duration in seconds
endsAt = unix time of program end
-id = unknown
-onAir = 0 or 1... playing now
premiere = 0 or 1... previous airing is 0, new airing is 1
videoResolution = video height in pixels
-origin = guide source (livetv...)
-channelArt = channel fanart
channelIdentifier = unknown
channelShortTitle = channel name
channelThumb = channel icon
channelTitle = channel id
channelVcn = channel number
-container = stream container
-protocol = stream protocol
'''
