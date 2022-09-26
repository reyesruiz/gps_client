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
        if parts[0] == '$GPRMC' and gprmc == False:
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

        elif parts[0] == '$GPGGA' and gpgga == False:
            gps_parsed_data['number_of_satellites_in_use'] = parts[7]
            gps_parsed_data['elevation_msl'] = parts[9]
            gpgga = True
        if gprmc == True and gpgga == True:
            break
    return gps_parsed_data

def human_readable(data):
    pattern = re.compile("(\\d{2})")
    m = pattern.findall(data['date'])
    year = '20' + str(m[2])
    month = str(m[1])
    day = str(m[0])
    date = year + '/' + month + '/' + day
    time_parts = data['time'].split('.')
    m = pattern.findall(time_parts[0])
    hour = m[0]
    minute = m[1]
    second = m[2]
    time = hour + ':' + minute + ':' + second
    latitude_parts = data['latitude'].split('.')
    m = pattern.findall(latitude_parts[0])
    latitude_degrees = m[0]
    latitude_minutes = m[1]
    latitude_seconds = str(round((float('0.' + latitude_parts[1]) * 60), 2))
    latitude_orientation = data['latitude_orientation']
    longitude_parts = data['longitude'].split('.')
    pattern = re.compile("(\\d{3})(\\d{2})")
    m = pattern.findall(longitude_parts[0])
    longitude_degrees = m[0][0]
    longitude_minutes = m[0][1]
    longitude_seconds = str(round((float('0.' + longitude_parts[1]) * 60), 2))
    longitude_orientation = data['longitude_orientation']
    elevation = str(round((float(data['elevation_msl']) * 3.280840), 2))
    speed = str(round((float(data['speed_knots']) * 1.15078), 2))
    true_course = data['true_course']
    compass_orientation = str()
    if true_course == "":
        true_course = '-'
        compass_orientation = '-'
    else:
        course = float(true_course)
        if course >= 0 and course <= 22.5:
            compass_orientation = 'N'
        elif course >= 22.5 and course <= 67.5:
            compass_orientation = 'NE'
        elif course >= 67.5 and course <= 112.5:
            compass_orientation = 'E'
        elif course >= 112.5 and course <= 157.5:
            compass_orientation = 'SE'
        elif course >= 157.5 and course <= 202.5:
            compass_orientation = 'S'
        elif course >= 202.5 and course <= 247.5:
            compass_orientation = 'SW'
        elif course >= 247.5 and course <= 292.5:
            compass_orientation = 'W'
        elif course >= 292.5 and course <= 337.5:
            compass_orientation = 'NW'
        elif course >= 337.5 and course <= 360:
            compass_orientation = 'N'
    satellites = data['number_of_satellites_in_use']

    human_readable_text = date + ' ' + time + " " + latitude_degrees + chr(176) + latitude_minutes + '\'' + latitude_seconds + '\"' + latitude_orientation + " " + longitude_degrees + chr(176) + longitude_minutes + '\'' + longitude_seconds + '\"' + longitude_orientation + " " + elevation + "ft MSL " + speed + " Mph " + true_course + chr(176) + " " + compass_orientation + " satellites in use: " + satellites
    return human_readable_text

def save_gpx(data):
    pattern = re.compile("(\\d{2})")
    latitude_parts = data['latitude'].split('.')
    m = pattern.findall(latitude_parts[0])
    latitude_degrees = m[0]
    latitude_minutes = m[1]
    latitude_seconds = str(round((float('0.' + latitude_parts[1]) * 60), 2))
    latitude_orientation = data['latitude_orientation']
    longitude_parts = data['longitude'].split('.')
    pattern = re.compile("(\\d{3})(\\d{2})")
    m = pattern.findall(longitude_parts[0])
    longitude_degrees = m[0][0]
    longitude_minutes = m[0][1]
    longitude_seconds = str(round((float('0.' + longitude_parts[1]) * 60), 2))
    longitude_orientation = data['longitude_orientation']
    elevation = data['elevation_msl']
    latitude = float(latitude_degrees) + (float(latitude_minutes)/60)+(float(latitude_seconds)/3600)
    longitude = float(longitude_degrees) + (float(longitude_minutes)/60)+(float(longitude_seconds)/3600)
    if latitude_orientation == 'S':
        latitude = 0 - latitude
    if longitude_orientation == 'W':
        longitude = 0 - longitude
    pattern = re.compile("(\\d{2})")
    m = pattern.findall(data['date'])
    year = '20' + str(m[2])
    month = str(m[1])
    day = str(m[0])
    time_parts = data['time'].split('.')
    m = pattern.findall(time_parts[0])
    hour = m[0]
    minute = m[1]
    second = m[2]
    gps_timestamp = datetime.now(timezone.utc)
    gps_timestamp = gps_timestamp.replace(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second), microsecond=0)
    #course = data['true_course']
    speed = data['speed_knots']
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(latitude=latitude, longitude=longitude, elevation=elevation, time=gps_timestamp, speed=speed))
    gpx_file_name_10 = gpx_file_name + "-10.gpx"
    path = Path(gpx_file_name_10)
    if path.is_file():
        Path(gpx_file_name_10).rename(gpx_file_name_10 + ".shadow")
    gpx_file = open(gpx_file_name_10, 'w')
    gpx_file.write(str(gpx.to_xml('1.0')))
    gpx_file.close()
    gpx_file_name_11 = gpx_file_name + "-11.gpx"
    path = Path(gpx_file_name_11)
    if path.is_file():
         Path(gpx_file_name_11).rename(gpx_file_name_11 + ".shadow")
    gpx_file = open(gpx_file_name_11, 'w')
    gpx_file.write(str(gpx.to_xml('1.1')))
    gpx_file.close()

def main():
    found_gps = False
    while found_gps != True:
        try:
            gps = serial.Serial(SERIAL_DEVICE, baudrate = 9600, timeout = 0.5)
            found_gps = True
        except:
            print("An exception occurred, GPS device might not be present")
            time.sleep(5)
    running = True
    while running == True:
        try:
            text = str()
            time.sleep(1)
            data = get_position(gps)
            #print(data)
            text = human_readable(data)
            print(text)
            f = open("gps_info.log", "a")
            f.write(text + "\n")
            f.close()
            save_gpx(data)
        except KeyboardInterrupt:
            running = False
            gps.close()
            print('Created GPX:', gpx.to_xml())
            print("Done")

if __name__ == '__main__':
    main()
