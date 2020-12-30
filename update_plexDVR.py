# -*- coding: utf-8 -*-

import argparse
import requests
from requests.exceptions import HTTPError #why is get_json failing if I remove this?
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

    def get_json(url, headers):
        result = requests.get(url, headers=headers).json() #https://stackoverflow.com/a/14804320/11214013
        return result
    
    def post_req(url, data):
        resp = requests.post(url, data=data)
        return resp
    
    #argparse
    parser = argparse.ArgumentParser(description="Python script to refresh Plex DVR guide(s).", formatter_class=argparse.RawTextHelpFormatter)
    #parser.add_argument('-x', '--xml', type=str, nargs=1, required=False, default=['epg.xml'], help='Full input filepath of xml that includes channels to include for Plex. Default is epg.xml. Full file path can be specified. If only file name is specified then file from the current working directory will be used if it exists.')
    parser.add_argument('-u', '--uri', type=str, nargs=1, required=False, default=['http://127.0.0.1:32400'], help='Uri to access plex.')
    parser.add_argument('-t', '--token', type=str, nargs=1, required=True, default=[''], help='Plex server token')
    opts = parser.parse_args()
    
    #string agruments
    #xml = quote_remover(opts.xml[0])
    uri = quote_remover(opts.uri[0])
    token = quote_remover(opts.token[0])
    
    #plex_headers
    headers = {
            'Accept': 'application/json',
            'X-Plex-Device': 'web2tv',
            'X-Plex-Device-Name': 'web2tv',
            'X-Plex-Product': 'web2tv',
            'X-Plex-Version': '0.1',
            'X-Plex-Client-Identifier': 'rg14zekk3pa5zp4safjwaa8z',
            'X-Plex-Platform': 'Chrome',
            'X-Plex-Platform-Version': '80.0',
            'X-Plex-Token': token
        }
        
    #initialize session
    url_suffix = '/livetv/dvrs'
    url = uri + url_suffix
    j = get_json(url, headers) #get dvrs (as json)
    #print(j)
    
    with open('plex_dvrs.json', 'w') as write_file:
        json.dump(j, write_file, indent=4)
        
    #reload guide for each dvr
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
        
        #print(url)
        r = post_req(url, headers)
        #print(r)
        print('DVR ' + str(x) + ' with key ' + str(dvr_dict['data'][x]['key']) + ' guide data is refreshing.')
        
        x += 1

    '''
    #convert this to python from js #https://github.com/vexorian/dizquetv/blob/f428dbecf0c4fd51f9fba1a91fa98eaaae7bbdb8/src/plex.js#L162
    async RefreshChannels(channels, _dvrs) {
        var dvrs = typeof _dvrs !== 'undefined' ? _dvrs : await this.GetDVRS()
        var _channels = []
        let qs = {}
        for (var i = 0; i < channels.length; i++) {
            _channels.push(channels[i].number)
        }
        qs.channelsEnabled = _channels.join(',')
        for (var i = 0; i < _channels.length; i++) {
            qs[`channelMapping[${_channels[i]}]`] = _channels[i]
            qs[`channelMappingByKey[${_channels[i]}]`] = _channels[i]
        }
        for (var i = 0; i < dvrs.length; i++) {
            for (var y = 0; y < dvrs[i].Device.length; y++) {
                await this.Put(`/media/grabbers/devices/${dvrs[i].Device[y].key}/channelmap`, qs);
            }
        }
    }
    '''    

