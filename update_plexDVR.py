# -*- coding: utf-8 -*-

import argparse
import urllib2
import json

if __name__ == '__main__':
    def quote_remover(string):
        if string.startswith('"') and string.endswith('"'):
            string = string[1:-1]
        elif string.startswith("'") and string.endswith("'"):
            string = string[1:-1]
        else:
            string = string
        return string
    
    def get_json(url, request_headers):
        req = urllib2.Request(url, headers = request_headers)
        req.add_header("Accept",'application/json')
        opener = urllib2.build_opener()
        f = opener.open(req)
        result = json.loads(f.read())
        return result
        
    def post_json(url):
        try:
            req = urllib2.Request(url)
            req.add_data("Content-Type",'application/json')
            print('req: ' + str(req))
            opener = urllib2.build_opener()
            f = opener.open(req)
            result = json.loads(f.read())
        except:
            result = 'error'
        return result
    
    #argparse
    parser = argparse.ArgumentParser(description="Python script to convert pluto tv channels into m3u format.", formatter_class=argparse.RawTextHelpFormatter)
    #parser.add_argument('-x', '--xml', type=str, nargs=1, required=False, default=['epg.xml'], help='Full input filepath of xml that includes channels to include for Plex. Default is epg.xml. Full file path can be specified. If only file name is specified then file from the current working directory will be used if it exists.')
    parser.add_argument('-u', '--uri', type=str, nargs=1, required=False, default=['http://127.0.0.1:32400'], help='Uri to access plex.')
    parser.add_argument('-t', '--token', type=str, nargs=1, required=True, default=[''], help='Plex server token')
    opts = parser.parse_args()
    
    #string agruments
    #xml = quote_remover(opts.xml[0])
    uri = quote_remover(opts.uri[0])
    token = quote_remover(opts.token[0])
    
    #plex_headers = {'X-Plex-Token' : token}
    #page = get_json(uri + '/web/livetv/dvrs', plex_headers)
    #print(page)
    
    #initialize session
    url_prefix = uri
    url_suffix = '/livetv/dvrs'
    url = url_prefix + url_suffix
    payload = {'X-Plex-Token' : token} #https://stackoverflow.com/a/28628514/11214013
    j = get_json(url, payload)
    #print(j)
    
    with open('plex_dvrs.json', 'w') as write_file:
        json.dump(j, write_file, indent=4)
        
    #/livetv/dvrs/${dvrs[i].key}/reloadGuide
    dvr_dict = {'data': []}
    x = 0
    for key in j['MediaContainer']['Dvr']:
        dvr_dict['data'].append({
            'uuid': j['MediaContainer']['Dvr'][x]['uuid'],
            'language': j['MediaContainer']['Dvr'][x]['language'],
            'country': j['MediaContainer']['Dvr'][x]['country'],
            'refreshedAt': j['MediaContainer']['Dvr'][x]['refreshedAt'],
            'key': j['MediaContainer']['Dvr'][x]['key'],
            'lineupTitle': j['MediaContainer']['Dvr'][x]['lineupTitle']
            })
         
        #url = uri + '/livetv/dvrs/' + dvr_dict[x]['uuid'] + '/reloadGuide'
        url = uri + '/livetv/dvrs/' + dvr_dict['data'][x]['key'] + '/reloadGuide'
        #url = 'http://127.0.0.1:32400/tv.plex.providers.epg.cloud'
        
        url += '?X-Plex-Token=' + token
        
        print(url)
        r = post_json(url)
        print(r)
        
        x += 1
    
    '''    
    #url = uri + '/tv.plex.providers.epg.xmltv:48' + '/reloadGuide'
    #url = uri + '/livetv/dvrs/xmltv:48' + '/reloadGuide'
    url = uri + '/livetv/dvrs/48/reloadGuide'
    print(url)
    print(cookie)
    t, gar = post_url(url, payload)
    #with open('plex_cloudkey.json', 'w') as write_file:
    #    json.dump(t, write_file, indent=4)
    print(t)
    '''

