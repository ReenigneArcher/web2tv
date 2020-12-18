# -*- coding: utf-8 -*-

import argparse
import urllib2
import time
from datetime import datetime, date
import json
import dateutil.parser

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
        opener = urllib2.build_opener()
        f = opener.open(req)
        result = json.loads(f.read())
        return result
    
    def isotime_convert(iso_time):
        time = dateutil.parser.isoparse(iso_time) #https://stackoverflow.com/a/15228038/11214013
        result = time.strftime('%Y%m%d%H%M%S') #https://python.readthedocs.io/en/v2.7.2/library/datetime.html#datetime-objects
        return result
    
    def change_text(text): #https://stackoverflow.com/a/30320137/11214013
        return text.encode('utf-8')  # assuming the encoding is UTF-8

    def get_number(channel):
        return channel.get('channelNumber')
    
    #argparse
    parser = argparse.ArgumentParser(description="Python script to convert pluto tv channels into m3u format.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-f', '--file', type=str, nargs=1, required=False, default=['plutotv.m3u'], help='Full destination filepath. Default is plutotv.m3u. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    opts = parser.parse_args()
    
    #string agruments
    destination = quote_remover(opts.file[0])
    print('file: ' + destination)

    #dictionary arrays to build
    channel_dict = {'data': []}

    #constants
    day = 24 * 60 * 60
    half_hour = 60 * 60 / 2

    now = time.time()
    now = int(now)
    now_30 = now - (now % half_hour) #go back to nearest 30 minutes
    epg_begin = str(datetime.fromtimestamp(now_30)).replace(' ', 'T') + '-00:00'

    epg_end = (2 * 60 * 60) + now_30 + half_hour
    epg_end = str(datetime.fromtimestamp(epg_end)).replace(' ', 'T') + '-00:00'

    print('Loading Grid for PlutoTV')
    
    url = 'https://service-channels.clusters.pluto.tv/v1/guide?start=' + epg_begin + '&stop=' + epg_end
    print(url)
    grid = load_json(url)
    
    x = 0
    for key in grid['channels']:
        channel_dict['data'].append({
            'channelName': grid['channels'][x]['name'], #name
            'channelSlug': grid['channels'][x]['slug'], #slug
            'channelHash': grid['channels'][x]['hash'], #hash
            'channelNumber': grid['channels'][x]['number'], #number
            'channelId': grid['channels'][x]['id'], #id
            'channelSummary': grid['channels'][x]['summary'], #summary
            'channelImage': grid['channels'][x]['images'][0]['url'] }) #logo
        
        x += 1
    
    # remove duplicates
    channel_list = [i for n, i in enumerate(channel_dict['data']) if i not in channel_dict['data'][n + 1:]]
    print('Channels Found: ' + str(len(channel_list)+1))
    
    # sort by Age (Ascending order)
    channel_list.sort(key=get_number) #https://www.programiz.com/python-programming/methods/list/sort#:~:text=%20Python%20List%20sort%20%28%29%20%201%20sort,an%20optional%20argument.%20Setting%20reverse%20%3D...%20More%20
    #print(channel_list)
    
    #start the m3u file
    m3u = '#EXTM3U'

    x = 0
    while x < len(channel_list): #do this for each channel
        m3u += '\n#EXTINF:-1 tvg-ID="PLUTO.TV.' + channel_list[x]['channelSlug']
        m3u += '" tvg-name="' + channel_list[x]['channelName']
        m3u += '" tvg-logo="' + channel_list[x]['channelImage']
        m3u += '" group-title="PLUTO USA",' + channel_list[x]['channelName']
        
        number = str(channel_list[x]['channelNumber'])
        cid = str(channel_list[x]['channelId'])
        #print(number)
        #print(cid)
        
        m3u += '\n' + 'https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/' + cid + '/master.m3u8?terminate=false&deviceType=web&deviceMake=web&deviceModel=web&sid=' + number + '&deviceId=' + cid + '&deviceVersion=DNT&appVersion=DNT&deviceDNT=0&userId=&advertisingId=&deviceLat=&deviceLon=&app_name=&appName=web&buildVersion=&appStoreUrl=&architecture=&includeExtendedEvents=false&marketingRegion=US&serverSideAds=false'

        print(channel_list[x]['channelSlug'] + ' will be added to the m3u.' + str(x+1) + '/' + str(len(channel_list)))

        x += 1

    print('m3u is ready to write')
    #print(m3u)

    #write the file
    file_handle = open(destination, "w")
    print('m3u is being created')
    m3u = change_text(m3u)
    file_handle.write(m3u)
    print('m3u is being written')
    file_handle.close()
    print('m3u is being closed')
