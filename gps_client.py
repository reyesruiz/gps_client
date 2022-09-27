'''
Python gps client
Copyright 2022 Reyes Ruiz

https://github.com/reyesruiz/gps_client
'''

import time
import re
from datetime import datetime, timezone
from pathlib import Path
import serial
import gpxpy

SERIAL_DEVICE = "/dev/ttyACM0"
timestr = time.strftime("%Y%m%d-%H%M%S")
gpx_file_name = timestr
gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

def get_position(gps):
    '''
    Parsing gps data from device and outputing it to dictionary
    '''
    gps_data = gps.read_all().decode("utf-8").split('\r\n')
    gps_parsed_data = {'date': "",
                'time': "",
                'latitude': "",
                'latitude_orientation': "",
                'longitude': "",
                'longitude_orientation': "",
                'speed_knots': "",
                'true_course': "",
                'elevation_msl': "",
                'number_of_satellites_in_use': ""
                }
    gprmc = False
    gpgga = False
    for message in gps_data[::-1]:
        parts = message.split(',')
        #I want GPRMC and GPGGA
        if parts[0] == '$GPRMC' and not gprmc:
            receiver_warning = parts[2]
            if receiver_warning == 'A':
                gps_parsed_data['latitude'] = parts[3]
                gps_parsed_data['latitude_orientation'] = parts[4]
                gps_parsed_data['longitude'] = parts[5]
                gps_parsed_data['longitude_orientation'] = parts[6]
                gps_parsed_data['speed_knots'] = parts[7]
                gps_parsed_data['true_course'] = parts[8]
                gps_parsed_data['date'] = parts[9]
                gps_parsed_data['time'] = parts[1]
                gprmc = True

        elif parts[0] == '$GPGGA' and not gpgga:
            gps_parsed_data['number_of_satellites_in_use'] = parts[7]
            gps_parsed_data['elevation_msl'] = parts[9]
            gpgga = True
        if gprmc and gpgga:
            break
    return gps_parsed_data

def human_readable(data):
    '''
    Returning a human readable output, with gps information parsed and formatted
    for better reading, so far it is in degree, minute, second, miles, and feet.
    '''
    pattern = re.compile("(\\d{2})")
    match_results = pattern.findall(data['date'])
    #GPS Date Time as YYYY/MM/DD hh:mm:ss
    gps_date_time =  '20' + str(match_results[2]) + '/' \
            +  str(match_results[1]) + '/' \
            +  str(match_results[0])
    match_results = pattern.findall(data['time'].split('.')[0])
    gps_date_time = gps_date_time + " " \
            + match_results[0] + ':' \
            + match_results[1] + ':' \
            + match_results[2]
    latitude_parts = data['latitude'].split('.')
    match_results = pattern.findall(latitude_parts[0])
    # latitude degrees minutes seconds orientation
    latitude = match_results[0] + chr(176) \
            + match_results[1] + chr(39) \
            + str(round((float('0.' + latitude_parts[1]) * 60), 4)) + chr(34) \
            + data['latitude_orientation']
    longitude_parts = data['longitude'].split('.')
    pattern = re.compile("(\\d{3})(\\d{2})")
    match_results = pattern.findall(longitude_parts[0])
    # longitude degrees minutes seconds orientation
    longitude = str(match_results[0][0]) + chr(176) \
            + str(match_results[0][1]) + chr(39) \
            + str(round((float('0.' + longitude_parts[1]) * 60), 4)) + chr(34) \
            + data['longitude_orientation']
    elevation = str(round((float(data['elevation_msl']) * 3.280840), 2))
    speed = str(round((float(data['speed_knots']) * 1.15078), 2))
    true_course = data['true_course']
    compass_orientation = str()
    if true_course == "":
        true_course = '-'
        compass_orientation = '-'
    else:
        course = float(true_course)
        if course >= 0 <= 22.5:
            compass_orientation = 'N'
        elif course >= 22.5 <= 67.5:
            compass_orientation = 'NE'
        elif course >= 67.5 <= 112.5:
            compass_orientation = 'E'
        elif course >= 112.5 <= 157.5:
            compass_orientation = 'SE'
        elif course >= 157.5 <= 202.5:
            compass_orientation = 'S'
        elif course >= 202.5 <= 247.5:
            compass_orientation = 'SW'
        elif course >= 247.5 <= 292.5:
            compass_orientation = 'W'
        elif course >= 292.5 <= 337.5:
            compass_orientation = 'NW'
        elif course >= 337.5 <= 360:
            compass_orientation = 'N'
    satellites = data['number_of_satellites_in_use']

    human_readable_text = gps_date_time + ' '\
            + latitude + " " \
            + longitude + " " \
            + elevation + "ft MSL " \
            + speed + " Mph " \
            + true_course + chr(176) + " " \
            + compass_orientation \
            + " satellites in use: " + satellites
    return human_readable_text

def save_gpx(data):
    '''
    Saving gps data in gpx format both gpx 1.0 and 1.1, 1.0 because it has speed data.
    '''
    pattern = re.compile("(\\d{2})")
    latitude_parts = data['latitude'].split('.')
    match_results = pattern.findall(latitude_parts[0])
    latitude = round((float(match_results[0]) \
            + (float(match_results[1])/60) \
            + (float(str(float('0.' + latitude_parts[1]) \
            * 60))/3000)), 8)
    if data['latitude_orientation'] == 'S':
        latitude = 0 - latitude
    longitude_parts = data['longitude'].split('.')
    pattern = re.compile("(\\d{3})(\\d{2})")
    match_results = pattern.findall(longitude_parts[0])
    longitude = round((float(match_results[0][0]) \
            + (float(match_results[0][1])/60) \
            + (float(str(float('0.' + longitude_parts[1]) \
            * 60))/3000)), 8)
    if  data['longitude_orientation'] == 'W':
        longitude = 0 - longitude
    elevation = data['elevation_msl']
    gps_timestamp = datetime.now(timezone.utc)
    pattern = re.compile("(\\d{2})")
    match_results = pattern.findall(data['date'])
    gps_timestamp = gps_timestamp.replace(year=int('20' + str(match_results[2])), \
            month=int(str(match_results[1])), \
            day=int(str(match_results[0])))
    time_parts = data['time'].split('.')
    match_results = pattern.findall(time_parts[0])
    gps_timestamp = gps_timestamp.replace(hour=int(match_results[0]), \
            minute=int(match_results[1]), \
            second=int(match_results[2]), \
            microsecond=0)
    #course = data['true_course']
    speed = data['speed_knots']
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(\
            latitude=latitude, \
            longitude=longitude, \
            elevation=elevation, \
            time=gps_timestamp, \
            speed=speed))
    gpx_file_name_10 = gpx_file_name + "-10.gpx"
    path = Path(gpx_file_name_10)
    if path.is_file():
        Path(gpx_file_name_10).rename(gpx_file_name_10 + ".shadow")
    with open(gpx_file_name_10, "w", encoding="utf8") as gpx_file:
        gpx_file.write(str(gpx.to_xml('1.0')))
    gpx_file_name_11 = gpx_file_name + "-11.gpx"
    path = Path(gpx_file_name_11)
    if path.is_file():
        Path(gpx_file_name_11).rename(gpx_file_name_11 + ".shadow")
    with open(gpx_file_name_11, "w", encoding="utf8") as gpx_file:
        gpx_file.write(str(gpx.to_xml('1.1')))

def main():
    '''
    Main Function to process gps data
    '''
    found_gps = False
    while not found_gps:
        try:
            gps = serial.Serial(SERIAL_DEVICE, baudrate = 9600, timeout = 0.5) # pylint: disable=no-member
            found_gps = True
        except: # pylint: disable=bare-except
            print("An exception occurred, GPS device might not be present")
            time.sleep(5)
    running = True
    while running:
        try:
            text = str()
            time.sleep(1)
            data = get_position(gps)
            #print(data)
            text = human_readable(data)
            print(text)
            with open("gps_info.log", "a", encoding="utf8") as info_file:
                info_file.write(text + "\n")
            save_gpx(data)
        except KeyboardInterrupt:
            running = False
            gps.close()
            print('Created GPX:', gpx.to_xml())
            print("Done")

if __name__ == '__main__':
    main()
