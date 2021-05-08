# -*- coding: utf-8 -*-

import argparse
import requests
import time
from datetime import datetime, date
import dateutil.parser
import html
import uuid

#xml constants
source_info_url = '"https://pluto.tv"'
source_info_name = '"pluto.tv"'
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
    
    def load_json(url):
        result = requests.get(url=url, headers=headers).json()
        return result
    
    def isotime_convert(iso_time):
        time = dateutil.parser.isoparse(iso_time) #https://stackoverflow.com/a/15228038/11214013
        result = time.strftime('%Y%m%d%H%M%S') #https://python.readthedocs.io/en/v2.7.2/library/datetime.html#datetime-objects
        return result
    
    def fix(text):
        text = str(html.escape(text, quote=False).encode('ascii', 'xmlcharrefreplace'))[2:-1] #https://stackoverflow.com/a/1061702/11214013
        return text.replace("\\'", "'")
    
    def fix2(text):
        return text
    
    def get_number(channel):
        return channel.get('channelNumber')
    
    #argparse
    parser = argparse.ArgumentParser(description="Python script to convert pluto tv guide into xml/m3u format.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-e', '--epgHours', type=int, nargs=1, required=False, default=[10], help='Hours of EPG to collect. Pluto.TV only provides a few hours of EPG. Max allowed is 12.')
    
    #xml arguments
    parser.add_argument('-x', '--xmlFile', type=str, nargs=1, required=False, default=['plutotv.xml'], help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    parser.add_argument('--xml', action='store_true', required=False, help='Generate the xml file.')
    
    #m3u arguments
    parser.add_argument('-m', '--m3uFile', type=str, nargs=1, required=False, default=['plutotv.m3u'], help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    parser.add_argument('-p', '--prefix', type=str, nargs=1, required=False, default=[''], help='Channel name prefix.')
    parser.add_argument('-s', '--startNumber', type=int, nargs=1, required=False, default=[1], help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.')
    parser.add_argument('-k', '--keepNumber', action='store_true', required=False, help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.')
    parser.add_argument('--m3u', action='store_true', required=False, help='Generate the m3u file.')
    parser.add_argument('--streamlink', action='store_true', required=False, help='Generate the stream urls for use with Streamlink.')
    
    opts = parser.parse_args()
    
    #string agruments
    xml_destination = quote_remover(opts.xmlFile[0])
    m3u_destination = quote_remover(opts.m3uFile[0])
    prefix = quote_remover(opts.prefix[0])
    
    #integer arguments
    epg_hours = opts.epgHours[0]
    if epg_hours > 12:
        epg_hours = 12
    startNumber = opts.startNumber[0]
    
    #bool arguments
    makeXML = opts.xml
    makeM3U = opts.m3u
    keepNumber = opts.keepNumber
    streamlink = opts.streamlink
    
    print('hours: ' + str(epg_hours))
    print('xmlFile: ' + xml_destination)
    print('m3uFile: ' + m3u_destination)
    print('prefix: ' + prefix)
    print('startNumber: ' + str(startNumber))
    print('keepNumber: ' + str(keepNumber))
    print('streamlink: ' + str(streamlink))
    print('xml: ' + str(makeXML))
    print('m3u: ' + str(makeM3U))

    headers = {
            'Accept': 'application/json'
        }

    #dictionary arrays to build
    channel_dict = {'data': []}
    program_dict = {'data': []}
    
    #arrays to build
    channel_numbers = []
    
    keyErrors_contentRating = []
    errorDetails_contentRating = []
    
    keyErrors_channelCategory = []
    errorDetails_chanelCategory = []
    
    keyErrors_full = []

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
                    'no rating' : 'n/a',
                    'not rated' : 'n/a',
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
                    'no rating' : 'https://loyoladigitaladvertising.files.wordpress.com/2014/02/nr-logo.png',
                    'not rated' : 'https://loyoladigitaladvertising.files.wordpress.com/2014/02/nr-logo.png',
                    'ur' : 'http://3.bp.blogspot.com/-eyIrE_lKiMg/Ufbis7lWLlI/AAAAAAAAAK4/4XTYHCU8Dx4/s1600/ur+logo.png'
                    }

    #constants
    day = 24 * 60 * 60
    hour = 60 * 60
    half_hour = 60 * 60 / 2
    timezone = '-0000'
    timezone = timezone[:-2] + ':' + timezone[-2:]

    now = time.time()
    now = int(now)
    now_30 = now - (now % half_hour) #go back to nearest 30 minutes
    epg_begin = str(datetime.utcfromtimestamp(now_30)).replace(' ', 'T') + timezone

    epg_end = (epg_hours * hour) + now_30 + half_hour
    epg_end = str(datetime.utcfromtimestamp(epg_end)).replace(' ', 'T') + timezone

    print('Loading Grid for PlutoTV')
    
    url = 'https://service-channels.clusters.pluto.tv/v1/guide?start=' + epg_begin + '&stop=' + epg_end
    print('url: ' + url)

    grid = load_json(url)
    
    x = 0
    for key in grid['channels']:
        if keepNumber == False:
            newNumber =+ x
        elif keepNumber == True:
            newNumber = startNumber + grid['channels'][x]['number']
            
            r = 0
            index = 0
            while r < len(channel_numbers):
                if str(newNumber) == str(channel_numbers[r][0]):
                    index = r
                    s = len(channel_numbers[r])
                    channel_numbers[r].append(str(newNumber) + '.' + str(s))
                    print('Added sub channel: ' + channel_numbers[r][-1])
                    newNumber = channel_numbers[r][-1]
                    break
                r += 1
            if index == 0:
                channel_numbers.append([str(newNumber)])
                print('Added channel: ' + str(channel_numbers[-1][0]))

        channel_dict['data'].append({
            'channelName': fix(grid['channels'][x]['name']), #name
            'channelName_2': fix2(grid['channels'][x]['name']), #name
            'channelSlug': fix(grid['channels'][x]['slug']), #slug
            'channelSlug_2': fix2(grid['channels'][x]['slug']), #slug
            'channelHash': fix(grid['channels'][x]['hash']), #hash
            'channelHash_2': fix2(grid['channels'][x]['hash']), #hash
            'channelNumber': grid['channels'][x]['number'], #number
            'channelId': fix(grid['channels'][x]['id']), #id
            'channelId_2': fix2(grid['channels'][x]['id']), #id
            'channelSummary': fix(grid['channels'][x]['summary']), #summary
            'channelSummary_2': fix2(grid['channels'][x]['summary']), #summary
            'channelImage': fix(grid['channels'][x]['images'][0]['url']), #logo
            'channelImage_2': fix2(grid['channels'][x]['images'][0]['url']), #logo
            'newNumber': newNumber })
        
        y = 0
        for key in grid['channels'][x]['timelines']:
            try:
                title = fix(grid['channels'][x]['timelines'][y]['title'])
            except KeyError as e:
                title = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                start = grid['channels'][x]['timelines'][y]['start']
            except KeyError as e:
                start = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                stop = grid['channels'][x]['timelines'][y]['stop']
            except KeyError as e:
                stop = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                _id = grid['channels'][x]['timelines'][y]['_id']
            except KeyError as e:
                _id = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_id = grid['channels'][x]['timelines'][y]['episode']['_id'] #episode id
            except KeyError as e:
                episode_id = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_number = grid['channels'][x]['timelines'][y]['episode']['number'] #episode number
            except KeyError as e:
                episode_number = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_description = fix(grid['channels'][x]['timelines'][y]['episode']['description']) #episode description
            except KeyError as e:
                episode_description = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_duration = grid['channels'][x]['timelines'][y]['episode']['duration'] #episode duration
            except KeyError as e:
                episode_duration = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_originalContentDuration = grid['channels'][x]['timelines'][y]['episode']['originalContentDuration'] #episode content duration
            except KeyError as e:
                episode_originalContentDuration = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_genre = fix(grid['channels'][x]['timelines'][y]['episode']['genre']) #episode genre
            except KeyError as e:
                episode_genre = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_subGenre = fix(grid['channels'][x]['timelines'][y]['episode']['subGenre']) #episode sub genre
            except KeyError as e:
                episode_subGenre = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_clip_originalReleaseDate = grid['channels'][x]['timelines'][y]['episode']['clip']['originalReleaseDate'] #episode sub genre
            except KeyError as e:
                episode_clip_originalReleaseDate = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_rating = grid['channels'][x]['timelines'][y]['episode']['rating'] #episode rating
            except KeyError as e:
                episode_rating = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_name = fix(grid['channels'][x]['timelines'][y]['episode']['name']) #episode name
            except KeyError as e:
                episode_name = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_slug = fix(grid['channels'][x]['timelines'][y]['episode']['slug']) #episode slug
            except KeyError as e:
                episode_slug = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_poster_path = fix(grid['channels'][x]['timelines'][y]['episode']['poster']['path']) #episode slug
            except KeyError as e:
                episode_poster_path = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_firstAired = grid['channels'][x]['timelines'][y]['episode']['firstAired'] #episode first aired
            except KeyError as e:
                episode_firstAired = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_thumbnail_path = fix(grid['channels'][x]['timelines'][y]['episode']['thumbnail']['path']) #episode thumbnail path
            except KeyError as e:
                episode_thumbnail_path = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_liveBroadcast = grid['channels'][x]['timelines'][y]['episode']['liveBroadcast'] #episode live broadcast
            except KeyError as e:
                episode_liveBroadcast = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_featuredImage_path = fix(grid['channels'][x]['timelines'][y]['episode']['featuredImage']['path']) #episode featured image path
            except KeyError as e:
                episode_featuredImage_path = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_id = grid['channels'][x]['timelines'][y]['episode']['series']['_id'] #episode series id
            except KeyError as e:
                episode_series_id = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_name = fix(grid['channels'][x]['timelines'][y]['episode']['series']['name']) #episode series name
            except KeyError as e:
                episode_series_name = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_slug = fix(grid['channels'][x]['timelines'][y]['episode']['series']['slug']) #episode series slug
            except KeyError as e:
                episode_series_slug = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_type = grid['channels'][x]['timelines'][y]['episode']['series']['type'] #episode series type (possible values: tv, film, web-original, music-video, live, No information available)
            except KeyError as e:
                episode_series_type = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_tile_path = fix(grid['channels'][x]['timelines'][y]['episode']['series']['tile']['path']) #episode series tile path
            except KeyError as e:
                episode_series_tile_path = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_description = fix(grid['channels'][x]['timelines'][y]['episode']['series']['description']) #episode series description
            except KeyError as e:
                episode_series_description = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_summary = fix(grid['channels'][x]['timelines'][y]['episode']['series']['summary']) #episode series summary
            except KeyError as e:
                episode_series_summary = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))
            try:
                episode_series_featuredImage_path = fix(grid['channels'][x]['timelines'][y]['episode']['series']['featuredImage']['path']) #episode series featured image path
            except KeyError as e:
                episode_series_featuredImage_path = ''
                keyErrors_full.append('program title: ' + grid['channels'][x]['timelines'][y]['title'] + ' channelName: ' + grid['channels'][x]['name'] + ' KeyError: ' + str(e))

            program_dict['data'].append({
                'title': title, #title
                'start': start, #start
                'stop': stop, #stop
                '_id': _id, #id
                'episode_id': episode_id, #episode id
                'episode_number': episode_number, #episode number
                'episode_description': episode_description, #episode description
                'episode_duration': episode_duration, #episode duration
                'episode_originalContentDuration': episode_originalContentDuration, #episode content duration
                'episode_genre': episode_genre, #episode genre
                'episode_subGenre': episode_subGenre, #episode sub genre
                'episode_clip_originalReleaseDate': episode_clip_originalReleaseDate, #episode sub genre
                'episode_rating': episode_rating, #episode rating
                'episode_name': episode_name, #episode name
                'episode_slug': episode_slug, #episode slug
                'episode_poster_path': episode_poster_path, #episode slug
                'episode_firstAired': episode_firstAired, #episode first aired
                'episode_thumbnail_path': episode_thumbnail_path, #episode thumbnail path
                'episode_liveBroadcast': episode_liveBroadcast, #episode live broadcast
                'episode_featuredImage_path': episode_featuredImage_path, #episode featured image path
                'episode_series_id': episode_series_id, #episode series id
                'episode_series_name': episode_series_name, #episode series name
                'episode_series_slug': episode_series_slug, #episode series slug
                'episode_series_type': episode_series_type, #episode series type
                'episode_series_tile_path': episode_series_tile_path, #episode series tile path
                'episode_series_description': episode_series_description, #episode series description
                'episode_series_summary': episode_series_summary, #episode series summary
                'episode_series_featuredImage_path': episode_series_featuredImage_path, #episode series featured image path
                'channelSlug': grid['channels'][x]['slug']}) #channelSlug
            y += 1
        
        x += 1
    
    # remove duplicates
    channel_list = [i for n, i in enumerate(channel_dict['data']) if i not in channel_dict['data'][n + 1:]]
    print('Channels Found: ' + str(len(channel_list)+1))
    # sort by channel number (Ascending order)
    channel_list.sort(key=get_number) #https://www.programiz.com/python-programming/methods/list/sort#:~:text=%20Python%20List%20sort%20%28%29%20%201%20sort,an%20optional%20argument.%20Setting%20reverse%20%3D...%20More%20
    #print(channel_list)
    
    if makeXML == True:
        program_list = [i for n, i in enumerate(program_dict['data']) if i not in program_dict['data'][n + 1:]]
        print('Programs Found: ' + str(len(program_list)+1))

        #start the xml file
        xml = '<?xml version="1.0" encoding="UTF-8"?>'
        xml += '\n<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'
        xml += '\n<tv source-info-url=' + source_info_url + ' source-info-name=' + source_info_name + ' generator-info-name=' + generator_info_name + ' generator-info-url=' + generator_info_url + '>'
    
    if makeM3U == True:
        #start the m3u file
        m3u = '#EXTM3U'

        did = str(uuid.uuid4()) #https://docs.python.org/2.7/library/uuid.html
        sid = str(uuid.uuid4()) #https://docs.python.org/2.7/library/uuid.html

    x = 0
    while x < len(channel_list): #do this for each channel
        if makeXML == True:
            xml += '\n\t<channel id="' + 'PLUTO.TV.' + channel_list[x]['channelSlug'] + '">'
            xml += '\n\t\t<display-name>' + channel_list[x]['channelName'] + '</display-name>'
            xml += '\n\t\t<display-name>' + channel_list[x]['channelSlug'] + '</display-name>'
            xml += '\n\t\t<display-name>' + str(channel_list[x]['channelNumber']) + '</display-name>'
            xml += '\n\t\t<display-name>' + channel_list[x]['channelId'] + '</display-name>'
            xml += '\n\t\t<display-name>' + channel_list[x]['channelHash'] + '</display-name>'
            if channel_list[x]['channelImage'] != '':
                xml += '\n\t\t<icon src="' + channel_list[x]['channelImage'] + '" />'
            xml += '\n\t</channel>'
            #print(channel_list[x]['channelSlug'] + ' will be added to the xml.' + str(x+1) + '/' + str(len(channel_list)))
            print(channel_list[x]['channelName'])
        if makeM3U == True:
            m3u += '\n#EXTINF:-1 tvg-ID="PLUTO.TV.' + channel_list[x]['channelSlug_2']
            m3u += '" CUID="' + str(channel_list[x]['channelId_2'])
            m3u += '" tvg-chno="' + str(channel_list[x]['newNumber'])
            m3u += '" tvg-name="' + prefix + channel_list[x]['channelName_2']
            if channel_list[x]['channelImage'] != '':
                m3u += '" tvg-logo="' + channel_list[x]['channelImage_2']
            m3u += '" group-title="PLUTO.TV",' + prefix + channel_list[x]['channelName_2']
            
            if streamlink == True:
                m3u += '\n' + 'https://pluto.tv/live-tv/' + channel_list[x]['channelSlug_2']
            else:
                cid = str(channel_list[x]['channelId_2'])
                #print(cid)
                
                m3u += '\n' + 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/' + cid + '/master.m3u8?terminate=false&deviceType=web&deviceMake=Chrome&deviceModel=web&sid=' + sid + '&deviceId=' + did + '&deviceVersion=unknown&appVersion=unknown&clientTime=0&deviceDNT=0&userId=&advertisingId=&appName=web&buildVersion=&appStoreUrl=&architecture=&includeExtendedEvents=false&marketingRegion=US&serverSideAds=true'

            #print(channel_list[x]['channelSlug'] + ' will be added to the m3u.' + str(x+1) + '/' + str(len(channel_list)))
        x += 1

    if makeXML == True:
        x = 0
        while x < len(program_list): #do this for each program
            if program_list[x]['episode_duration'] / 1000 > 0: #if duration is greater than 0
                timeStart = isotime_convert(program_list[x]['start'])
                timeEnd = isotime_convert(program_list[x]['stop'])
                timeAdded = isotime_convert(program_list[x]['episode_clip_originalReleaseDate'])
                timeOriginal = isotime_convert(program_list[x]['episode_firstAired'])
                
                offset = '+0000'
                
                xml += '\n\t<programme start="' + timeStart + ' ' + offset + '" stop="' + timeEnd + ' ' + offset + '" channel="PLUTO.TV.' + program_list[x]['channelSlug'] + '">' #program,, start, and end time
                
                xml += '\n\t\t<desc lang="' + 'en' + '">' + program_list[x]['episode_description'] + '</desc>' #description/summary
                xml += '\n\t\t<length units="seconds">' + str(int(program_list[x]['episode_duration'] / 1000)) + '</length>' #duration/length
                if timeAdded != "": #if timeAdded is not blank
                    xml += '\n\t\t<date>' + timeAdded + ' ' + offset + '</date>' #date
                
                xml += '\n\t\t<title lang="' + 'en' + '">' + program_list[x]['episode_series_name'] + '</title>' #title
                
                try:
                    print('   Airing: ' + str(x+1) + '/' + str(len(program_list)) + ' will be added to the xml... ' + program_list[x]['episode_series_name'] + ',_id: ' + program_list[x]['_id'])
                except SyntaxError as e:
                    print("---Cannot print this title due to SyntaxError: " + str(e))
                    #time.sleep(2)
                except UnicodeEncodeError as e:
                    print("---Cannot print this title due to UnicodeEncodeError: " + str(e))
                    #time.sleep(2)
                
                if program_list[x]['episode_name'] != program_list[x]['episode_series_name']: #if not equal
                    xml += '\n\t\t<sub-title lang="' + 'en' + '">' + program_list[x]['episode_name'] + '</sub-title>' #sub-title/tagline
                xml += '\n\t\t<icon src="' + program_list[x]['episode_poster_path'] + '" />' #thumb/icon
                
                #print(program_list[x]['episode_series_type'])
                if program_list[x]['episode_series_type'] == 'tv':
                    #episode numbering (how to improve this? ... slow)
                    temp = program_list[x]['episode_slug'].split('-')
                    se_tmp = str(program_list[x]['episode_number']).rsplit('0',1)
                    #print(temp)
                    if temp[-1] == 'embed':
                        del temp[-1]
                    if temp[-1][:3] == 'ptv':
                        part = temp[-1][3:]
                        del temp[-1]
                    else:
                        part = ''
                    try: #https://stackoverflow.com/a/3501408/11214013
                        season = temp[-2]
                        t = int(season) + 1
                    except:
                        season = ''
                    if season != '' and str(program_list[x]['episode_number']) == temp[-1] or se_tmp[-1] == temp[-1]: #example for or: tv: rule does not match... Episode: 405 Slug: [u'280', u'sq', u'ft', u'bohemian', u'tree', u'house', u'2017', u'4', u'5']
                        try: #https://stackoverflow.com/a/3501408/11214013
                            episode = temp[-1]
                            t = int(episode) + 1
                        except:
                            episode = ''
                        if season == episode[:len(season)]:
                            episode = temp[-1][len(season):]
                        #print('tv: rule1 matches')
                    elif str(program_list[x]['episode_number']) == temp[-1][len(season):]: #exmaple tv: rule does not match... Episode: 1 Slug: [u'whistle', u'blower', u'1996', u'2', u'21']
                        episode = temp[-1][len(season):]
                        try: #https://stackoverflow.com/a/3501408/11214013
                            t = int(episode) + 1
                        except:
                            episode = ''
                        #print('tv: rule2 matches')
                    else:
                        episode = ''
                        #print(se_tmp)
                        #print(temp[-1][len(season):])
                        #print('tv: rule does not match... Episode: ' + str(program_list[x]['episode_number']) + ' Slug: ' + str(temp))
                    #print(season)
                    #print(episode)
                    if season != ''and int(season) > 0:
                        if episode != '' and int(episode) > 0:
                            if int(season) < 10:
                                num_season = '0' + season
                            else:
                                num_season = season
                            if int(episode) < 10:
                                num_episode = '0' + episode
                            else:
                                num_episode = episode
                            xml += '\n\t\t<episode-num system="onscreen">' + 'S' + num_season + 'E' + num_episode + '</episode-num>' #episode number
                            xml += '\n\t\t<episode-num system="common">' + 'S' + num_season + 'E' + num_episode + '</episode-num>' #episode number
                            indexSeason = int(season)
                            indexSeason -= 1
                            indexEpisode = int(episode)
                            indexEpisode -= 1
                            xml += '\n\t\t<episode-num system="xmltv_ns">' + str(indexSeason) + '.' + str(indexEpisode) + '.</episode-num>' #episode number
                    xml += '\n\t\t<episode-num system="pluto.tv.number">' + str(program_list[x]['episode_number']) + '</episode-num>' #episode number
                    xml += '\n\t\t<episode-num system="pluto.tv.slug">' + program_list[x]['episode_slug'] + '</episode-num>' #episode number
                    xml += '\n\t\t<episode-num system="pluto.tv.id">' + program_list[x]['episode_id'] + '</episode-num>' #episode number
                
                    xml += '\n\t\t<category lang="' + 'en' + '">' + program_list[x]['episode_genre'] + '</category>' #category
                    xml += '\n\t\t<category lang="' + 'en' + '">' + program_list[x]['episode_series_type'] + '</category>' #category
                
                #content rating key
                #print(program_list[x]['contentRating'])
                if program_list[x]['episode_rating'] != '': #if not blank
                    try:
                        xml += '\n\t\t<rating system="' + rating_system[program_list[x]['episode_rating'].lower()] + '">' #rating system
                        xml += '\n\t\t\t<value>' + program_list[x]['episode_rating'] + '</value>' #rating
                        xml += '\n\t\t\t<icon src="' + rating_logo[program_list[x]['episode_rating'].lower()] + '" />' #rating logo from dictionary
                        xml += '\n\t\t</rating>' #end rating key
                    except KeyError:
                        keyErrors_contentRating.append(program_list[x]['episode_rating'])
                        errorDetails_contentRating.append('Title: ' + program_list[x]['episode_name'] + ', Channel: ' + program_list[x]['channelSlug'])
                
                if program_list[x]['episode_firstAired'] != '': #if first aired is not blank add the premier
                    if timeOriginal != "": #if we have the originallyAvailableAt add it to the tag
                        xml += '\n\t\t<previously-shown start="' + timeOriginal + ' ' + offset + '" />'
                    else: #else don't add start time to the tag
                        xml += '\n\t\t<previously-shown />'
                else: #if program is premiere add the tag
                    xml += '\n\t\t<premiere />'
                
                if program_list[x]['episode_liveBroadcast'] == True or program_list[x]['episode_series_type'] == 'live':
                    xml += '\n\t\t<live />'
                
                #finish
                xml += '\n\t</programme>'
                
            x += 1

    if makeXML == True:
        xml += '\n</tv>\n'

        print('xml is ready to write')
        #print(xml)
        
        #write the file
        print('xml is being created')
        with open(xml_destination, "w") as f: #https://stackoverflow.com/a/42495690/11214013
            f.write(xml)
        print('xml has being written')

    if makeM3U == True:
        print('m3u is ready to write')
        #print(m3u)

        #write the file
        print('m3u is being created')
        with open(m3u_destination, "w", encoding='utf-8') as f: #https://stackoverflow.com/a/42495690/11214013
            f.write(m3u)
        print('m3u has being written')
    
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
    
    if keyErrors_full != []:
        print('...')
        print('The following json key_errors were found. :' +str(keyErrors_full))

