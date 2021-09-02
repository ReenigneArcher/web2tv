import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys
import zipfile
import tarfile
import json
import xml.etree.ElementTree as ET

import re
from selenium.common.exceptions import (NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

xml_constants = {
    'source-info-url': 'https://ustvgo.tv',
    'source-info-name': 'ustvgo.tv',
    'generator-info-name': 'web2tv',
    'generator-info-url': 'https://github.com/ReenigneArcher/web2tv'
}

default_headers = {
    'Accept': 'application/json'
}

channel_logos = {
    'abc': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/ABC.svg',
    'acc network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/ACC%20Network.svg',
    'ae': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/AandE.svg',
    'amc': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/AMC.svg',
    'animal': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Animal%20Planet.svg',
    'bbcamerica': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/BBC%20America.svg',
    'big ten network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Big%20Ten%20Network.svg',
    'bet': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/BET.svg',
    'boomerang': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Boomerang.svg',
    'bravo': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Bravo.svg',
    'c-span': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/C-SPAN.svg',
    'cbs': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/CBS.svg',
    'cbs sports network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/CBS%20Sports%20Network.svg',
    'cinemax': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Cinemax.svg',
    'cmt': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/CMT.svg',
    'cartoon network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Cartoon%20Network.svg',
    'cnbc': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/CNBC.svg',
    'cnn': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/CNN.svg',
    'comedy': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Comedy%20Central.svg',
    'cw': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/The_CW.svg/800px-The_CW.svg.png',
    'destination america': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Destination%20America.svg',
    'discovery': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Discovery.svg',
    'disney': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Disney%20Channel.svg',
    'disneyjr': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Disney%20Junior.svg',
    'disneyxd': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Disney%20XD.svg',
    'do it yourself ( diy )': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/DIY%20Network.svg',
    'e!': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/E.svg',
    'espn': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/ESPN.svg',
    'espn2': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/ESPN%202.svg',
    'espnu': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/ESPN%20U.svg',
    'espnews': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/ESPNews.svg',
    'foodnetwork': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Food%20Network.svg',
    'fox': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Fox.svg',
    'foxbusiness': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Fox%20Business%20Network.svg',
    'foxnews': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Fox%20News%20Channel.svg',
    'freeform': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Freeform.svg',
    'fox sports 1 (fs1)': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/FS1.svg',
    'fox sports 2 (fs2)': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/FS2.svg',
    'fx': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/FX.svg',
    'fx movie channel': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/FX%20Movie%20Channel.svg',
    'fxx': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/FXX.svg',
    'golf channel': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Golf%20Channel.svg',
    'game show network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Game%20Show%20Network.svg',
    'hallmark channel': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Hallmark%20Channel.svg',
    'hbo': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/HBO.svg',
    'hgtv': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/HGTV.svg',
    'history': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/History.svg',
    'hln': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/HLN.svg',
    'hallmark movies & mysteries': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Hallmark%20Movies%20and%20Mysteries.svg',
    'investigation discovery': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Investigation%20Discovery.svg',
    'lifetime': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Lifetime.svg',
    'lifetime movie network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/LMN.svg',
    'mlb network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/MLB%20Network.svg',
    'motor trend': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Motor%20Trend.svg',
    'msnbc': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/MSNBC.svg',
    'mtv': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/MTV.svg',
    'national geographic': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/National%20Geographic.svg',
    'nat geo wild': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/National%20Geographic%20Wild.svg',
    'nba tv': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/NBA%20TV.svg',
    'nbc': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/NBC.svg',
    'nbc sports ( nbcsn )': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/NBCSN.svg',
    'nfl network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/NFL%20Network.svg',
    'nfl redzone': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/NFL%20RedZone.svg',
    'nickelodeon': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Nickelodeon.svg',
    'nicktoons': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Nicktoons.svg',
    'one america news network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/One%20America%20News%20Network.png',
    'oprah winfrey network (own)': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Oprah%20Winfrey%20Network.svg',
    'olympic channel': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Olympic%20Channel.svg',
    'oxygen': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Oxygen.svg',
    'paramount': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Paramount%20Network.svg',
    'pbs': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/PBS.svg',
    'pop': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Pop.svg',
    'science': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Science.svg',
    'sec network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/SEC%20Network.svg',
    'showtime': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Showtime.svg',
    'starz': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Starz.svg',
    'sundancetv': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/SundanceTV.svg',
    'syfy': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Syfy.svg',
    'tbs': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/TBS.svg',
    'turner classic movies (tcm)': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/TCM.svg',
    'telemnundo': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Telemundo.svg',
    'tennis channel': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Tennis%20Channel.svg',
    'tlc': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/TLC.svg',
    'tnt': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/TNT.svg',
    'travel channel': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Travel%20Channel.svg',
    'trutv': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/TruTV.svg',
    'tv land': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/TV%20Land.svg',
    'the weather channel': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/The%20Weather%20Channel.svg',
    'univision': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/Univision.svg',
    'usa network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/USA%20Network.svg',
    'vh1': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/VH1.svg',
    'we tv': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/We%20TV.svg',
    'wwe network': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/WWE_Network_logo.svg/556px-WWE_Network_logo.svg.png',
    'yes network': 'https://raw.githubusercontent.com/Jasmeet181/mediaportal-us-logos/master/TV/YES.png'
}


def check_gecko_driver():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(script_dir, 'bin')

    if sys.platform.startswith('linux'):
        platform = 'linux'
        url = 'https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver')
        var_separator = ':'
    elif sys.platform == 'darwin':
        platform = 'mac'
        url = 'https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-macos.tar.gz'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver')
        var_separator = ':'
    elif sys.platform.startswith('win'):
        platform = 'win'
        url = 'https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-win64.zip'
        local_platform_path = os.path.join(bin_dir, platform)
        local_driver_path = os.path.join(local_platform_path, 'geckodriver.exe')
        var_separator = ';'
    else:
        raise RuntimeError('Could not determine your OS')

    if not os.path.isdir(bin_dir):
        os.mkdir(bin_dir)

    if not os.path.isdir(local_platform_path):
        os.mkdir(local_platform_path)

    if not os.path.isfile(local_driver_path):
        print('Downloading gecko driver...', file=sys.stderr)
        data_resp = requests.get(url, stream=True)
        file_name = url.split('/')[-1]
        tgt_file = os.path.join(local_platform_path, file_name)
        with open(tgt_file, 'wb') as f:
            for chunk in data_resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(tgt_file, 'r') as f_zip:
                f_zip.extractall(local_platform_path)
        else:
            with tarfile.open(tgt_file, 'r') as f_gz:
                f_gz.extractall(local_platform_path)

        if not os.access(local_driver_path, os.X_OK):
            os.chmod(local_driver_path, 0o744)

        os.remove(tgt_file)

    if 'PATH' not in os.environ:
        os.environ['PATH'] = local_platform_path
    elif local_driver_path not in os.environ['PATH']:
        os.environ['PATH'] = local_platform_path + var_separator + os.environ['PATH']


def get_args():
    # argparse
    parser = argparse.ArgumentParser(description="Python script to convert ustvgo.tv guide into xml/m3u format.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--number_as_name', action='store_true', required=False,
                        help='Use the channel number as the name and id. Improves channel display in Plex Media Server.')


    # xml arguments
    parser.add_argument('-x', '--xml_file', type=str, required=False, default='ustvgo.xml',
                        help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    parser.add_argument('--xml', action='store_true', required=False, help='Generate the xml file.')
    parser.add_argument('--long_date', action='store_true', required=False,
                        help='Use longer date format. Do not use for Plex Media Server.')

    # m3u arguments
    parser.add_argument('-m', '--m3u_file', type=str, required=False, default='ustvgo.m3u',
                        help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    parser.add_argument('-p', '--prefix', type=str, required=False, default='', help='Channel name prefix.')
    parser.add_argument('-s', '--start_number', type=int, required=False, default=1,
                        help='Start numbering here. For example 9000.')
    parser.add_argument('--m3u', action='store_true', required=False, help='Generate the m3u file.')
    parser.add_argument('--streamlink', action='store_true', required=False,
                        help='Generate the stream urls for use with Streamlink.')
    parser.add_argument('-d', '--debug', action='store_true', required=False,
                        help='Turn of headless mode for Firefox.')
    parser.add_argument('-t', '--timeout', type=int, default=10,
                        help='Maximum number of seconds to wait for the response')
    parser.add_argument('--max_retries', type=int, default=3,
                        help='Maximum number of attempts to collect data')

    opts = parser.parse_args()

    opts.language = 'en'

    return opts


def load_json(url, headers=default_headers):
    result = requests.get(url=url, headers=headers).json()
    return result


def build_channel_list(args):
    url = 'https://ustvgo.tv/'

    try:
        response = requests.get(url)
    except requests.RequestException as e:
        return False

    soup = BeautifulSoup(response.content, "lxml")

    channels = {}

    x = 0
    for item in soup.find('ol').find_all('li'):
        number = x + args.start_number

        try:
            channels[number] = {
                'name': item.find('a').text.strip(),
                'url': item.find('a').get('href')
            }

            x += 1
        except:
            pass

    return channels


def get_channel_data(args, channels):
    for channel_number, channel_data in channels.items():
        response = requests.get(channel_data['url'])

        soup = BeautifulSoup(response.content, "lxml")

        if args.xml:
            json_url = False
            for item in soup.find_all('iframe'):
                if item['src'].startswith('/tvguide/index.html#'):
                    json_url = f"https://ustvgo.tv{item['src']}.json".replace('index.html#', 'JSON2/')
                    break

            if json_url:
                grid = load_json(json_url)

            channel_data['programs'] = []
            for day, programs in grid['items'].items():
                for program in programs:
                    channel_data['programs'].append(dict(program))

        if args.m3u:
            for item in soup.find_all('iframe'):
                if item['src'].startswith('/clappr.php?stream='):
                    stream = item['src'].rsplit('=', 1)[-1]
                    channel_data['stream'] = stream

    return channels


def update_authentication(args, channel):
    # https://github.com/interlark/ustvgo_downloader/blob/master/update.py
    ff_options = FirefoxOptions()
    if not args.debug:
        ff_options.headless = True

    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('permissions.default.image', 2)
    firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    firefox_profile.set_preference('dom.disable_beforeunload', True)
    firefox_profile.set_preference('browser.tabs.warnOnClose', False)
    firefox_profile.set_preference('media.volume_scale', '0.0')

    driver = webdriver.Firefox(options=ff_options, firefox_profile=firefox_profile)

    IFRAME_CSS_SELECTOR = '.iframe-container>iframe'
    POPUP_ACCEPT_XPATH_SELECTOR = '//button[contains(text(),"AGREE")]'

    retry = 1
    url_parts = False

    while retry < args.max_retries and not url_parts:
        try:
            driver.get(channel['url'])

            # Get iframe
            iframe = None
            try:
                iframe = driver.find_element_by_css_selector(IFRAME_CSS_SELECTOR)
            except NoSuchElementException:
                break

            # Detect VPN-required channels
            try:
                driver.switch_to.frame(iframe)
                driver.find_element_by_xpath("//*[text()='Please use our VPN to watch this channel!']")
                need_vpn = True
            except NoSuchElementException:
                need_vpn = False
            finally:
                driver.switch_to.default_content()

            if need_vpn:
                break

            # close popup if it shows up
            try:
                driver.find_element_by_xpath(POPUP_ACCEPT_XPATH_SELECTOR).click()
            except NoSuchElementException:
                pass

            # Autoplay
            iframe.click()

            try:
                playlist = driver.wait_for_request('/playlist.m3u8', timeout=args.timeout)
            except TimeoutException:
                playlist = None

            if playlist:
                video_link = str(playlist)

                url_parts = video_link.split(f"/{channel['stream']}/", 1)

                if len(url_parts) == 2:
                    break
            else:
                raise Exception()

        except Exception as e:
            print('Failed to get key, retry(%d) ...' % retry)
            retry += 1

        except KeyboardInterrupt:
            driver.close()
            driver.quit()
            sys.exit(1)

    driver.close()
    driver.quit()

    return url_parts

    try:
        return captured_key
    except NameError:
        return False


def main():
    args = get_args()

    if args.xml:
        xml_tv = ET.Element("tv", xml_constants)

    if args.m3u:
        check_gecko_driver()
        m3u_f = open(args.m3u_file, "w", encoding='utf-8')

        m3u_f.write('#EXTM3U\n')

    channels = build_channel_list(args)
    channels = get_channel_data(args, channels)

    authentication = False

    for channel_number, channel in channels.items():
        if args.number_as_name:
            channel_id = str(channel_number)

        else:
            channel_id = f"{args.prefix}{channel['name']}"

        if args.xml:
            xml_channel = ET.SubElement(xml_tv, "channel", {"id": channel_id})

            if args.prefix != '':
                ET.SubElement(xml_channel, "display-name").text = f"{args.prefix}{channel['name']}"
            print(channel['name'])

            display_names_types = ['name']
            display_names = []
            for display_name_type in display_names_types:
                try:
                    if channel[display_name_type] not in display_names:
                        display_names.append(channel[display_name_type])
                        ET.SubElement(xml_channel, "display-name").text = f'{channel[display_name_type]}'
                except KeyError:
                    pass

            for program in channel['programs']:
                time_start = datetime.utcfromtimestamp(int(program['start_timestamp'])).strftime('%Y%m%d%H%M%S')
                time_end = datetime.utcfromtimestamp(int(program['end_timestamp'])).strftime('%Y%m%d%H%M%S')

                offset = '+0000'

                program_header_dict = {
                    'start': f'{time_start} {offset}',
                    'stop': f'{time_end} {offset}',
                    'channel': channel_id
                }

                xml_program = ET.SubElement(xml_tv, "programme", program_header_dict)

                try:
                    ET.SubElement(xml_program, "title", {'lang': args.language}).text = program['name']
                    print(program['name'])
                except KeyError:
                    pass

                try:
                    ET.SubElement(xml_channel, "icon", {'src': channel_logos[channel['name'].lower()]})
                except KeyError:
                    pass

                try:
                    if program['description'] != "":
                        ET.SubElement(xml_program, "desc", {'lang': args.language}).text = program['description']
                except KeyError:
                    pass

                try:
                    ET.SubElement(xml_program, "length", {'units': 'seconds'}).text = str(program['end_timestamp'] - program['start_timestamp'])
                except KeyError:
                    pass

                try:
                    if program['image'] != "":
                        ET.SubElement(xml_program, "icon", {'src': program['image']})
                except KeyError:
                    pass

                try:
                    ET.SubElement(xml_program, "episode-num", {'system': 'ustvgo'}).text = str(program['id'])
                except KeyError:
                    pass

                xml_video = ET.SubElement(xml_program, "video")
                ET.SubElement(xml_video, "present").text = 'yes'

        if args.m3u:
            print(channel['url'])
            if not authentication:
                authentication = update_authentication(args, channel)
            if authentication:
                if args.number_as_name:
                    tvg_name = f"{channel_number}"
                    tvg_id = f"{channel_number}"
                    cuid = f"{channel_number}"
                else:
                    tvg_name = f"{args.prefix}{channel['name']}"
                    tvg_id = f"{args.prefix}{channel['name']}"
                    cuid = f"{args.prefix}{channel['name']}"

                tvg_chno = f"{channel_number}"
                group_title = f'"USTVGO.TV",{args.prefix}{channel["name"]}'

                try:
                    tvg_logo = channel_logos[channel['name'].lower()]
                    m3u_f.write(
                        f'#EXTINF:-1 tvg-ID="{tvg_id}" CUID="{cuid}" tvg-chno="{tvg_chno}" tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title={group_title}\n')
                except KeyError:
                    m3u_f.write(
                        f'#EXTINF:-1 tvg-ID="{tvg_id}" CUID="{cuid}" tvg-chno="{tvg_chno}" tvg-name="{tvg_name}" group-title={group_title}\n')

                if args.streamlink:
                    #m3u_f.write(f"hls://{channel['stream']}{authentication}\n")
                    m3u_f.write(f"hls://{authentication[0]}/{channel['stream']}/{authentication[1]}\n")

                else:
                    #m3u_f.write(f"{channel['stream']}{authentication}\n")
                    m3u_f.write(f"{authentication[0]}/{channel['stream']}/{authentication[1]}\n")

    if args.xml:
        # write the xml file
        print('xml is being created')
        with open(args.xml_file, "wb") as xml_f:  # https://stackoverflow.com/a/42495690/11214013
            xml_f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
            xml_f.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'.encode('utf-8'))

            new_xml = ET.ElementTree(xml_tv)

            try:
                ET.indent(new_xml, space="\t", level=0)
            except AttributeError:
                print('Warning: Upgrade to Python 3.9 to have indented xml')
            new_xml.write(xml_f, encoding='utf-8')

        print('xml has being written')

    if args.m3u:
        print('m3u is being closed')
        m3u_f.close()


if __name__ == '__main__':
    main()
