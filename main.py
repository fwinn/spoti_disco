import json
import logging
import os
import random
import time
import spotipy
import yeelight

with open("config.json") as config_json:
    config = json.load(config_json)
bulb = config['yeelight_bulb_ip']
scope = "user-read-playback-state user-read-playback-position"
sp = spotipy.Spotify(auth_manager=spotipy.SpotifyOAuth(
    scope=scope,
    client_id=config['spotify']['client_id'],
    client_secret=config['spotify']['client_secret'],
    redirect_uri=config['spotify']['redirect_uri'],
    open_browser=False
))
colors = [(0, 31, 63),
          (8, 51, 88),
          (13, 99, 165),
          (255, 215, 23)]
color_nr = 0
logging.basicConfig(level=logging.INFO)


def get_current_track():
    output = sp.current_playback()
    if not output:
        return None
    progress = output['progress_ms'] / 1000
    if not output['item']:
        return None
    result = {
        'id': output['item']['id'],
        'progress': progress,
        'name': output['item']['name'],
        'is_playing': output['is_playing']
    }
    return result


def new_color_nr(recent):
    r = random.randint(0, len(colors) - 1)
    if recent == r:
        if recent == len(colors) - 1:
            recent = 0
        else:
            recent += 1
    else:
        recent = r
    return recent


def get_sections(track_id):
    analysis = sp.audio_analysis(track_id)
    sections = analysis["sections"]
    return sections


def get_section(sections, progress):
    for i in range(0, len(sections) - 1):
        if sections[i]['start'] <= progress < (sections[i]['start'] + sections[i]['duration']):
            return i


def new_color(color_nr):
    bulb.set_rgb(colors[color_nr][0], colors[color_nr][1], colors[color_nr][2])


old_id = ''
old_section = 420000
sections = []
bulb_on = False
counter = 0
track = None
active = False
while 1:
    if counter % 60 == 0:
        if counter > 10000:
            logging.info('Resetting counter...')
            counter = 0
        try:
            bulb_on = bulb.get_properties(['power'])['power'] == 'on'
        except yeelight.BulbException as e:
            logging.error(e)
        logging.info('Bulb on check: ' + str(bulb_on))
        if not bulb_on:
            track = None
    if bulb_on:
        logging.debug('Checking for current Song...')
        track = get_current_track()
    if track:
        track_id = track['id']
        progress = track['progress']
        is_playing = track['is_playing']
        if is_playing:
            if not active:
                active = True
                logging.info('Music resumed')
                try:
                    bulb.set_brightness(100)
                except yeelight.BulbException as e:
                    logging.error(e)
            if old_id != track_id:
                sections = get_sections(track_id)
                old_id = track_id
            section = get_section(sections, progress)
            if section != old_section:
                logging.info('New section: ' + str(section))
                logging.info(track['name'])
                color_nr = new_color_nr(color_nr)
                old_section = section
                new_color(color_nr)
            time.sleep(0.5)
        else:
            time.sleep(5)
            if active:
                logging.info('Music paused')
                try:
                    bulb.set_brightness(80)
                    bulb.set_rgb(255, 255, 255)
                    bulb.set_color_temp(3100)
                except yeelight.BulbException as e:
                    logging.error('Error: e')

                active = False
        counter += 1
    else:
        logging.info('No music playing')
        time.sleep(8)
        counter += 60
