import gps
import serial
import time
import re

Serial_Device = "/dev/ttyACM0"
def get_position(gps):
    gps_data = gps.read_all().decode("utf-8").split('\r\n')
    gps_parsed_data = dict()
    gps_parsed_data = {'date': "",
                'time': "",
                'latitude': "",
                'latitude_orientation': "",
                'longitude': "",
                'longitude_orientation': "",
                'speed_knots': "",
                'true_course': "",
                'altitude_msl': "",
                'number_of_satellites_in_use': ""
                }
    for message in gps_data:
        parts = message.split(',')
        #I want GPRMC and
        if parts[0] == '$GPRMC':
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

        elif parts[0] == '$GPGGA':
            gps_parsed_data['number_of_satellites_in_use'] = parts[7]
            gps_parsed_data['altitude_msl'] = parts[9]
    return gps_parsed_data

def human_readable(data):
    pattern = re.compile("(\d{2})")
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
    pattern = re.compile("(\d{3})(\d{2})")
    m = pattern.findall(longitude_parts[0])
    longitude_degrees = m[0][0]
    longitude_minutes = m[0][1]
    longitude_seconds = str(round((float('0.' + longitude_parts[1]) * 60), 2))
    longitude_orientation = data['longitude_orientation']
    altitude = str(round((float(data['altitude_msl']) * 3.280840), 2))
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
            compass_orientation = 'Sw'
        elif course >= 247.5 and course <= 292.5:
            compass_orientation = 'W'
        elif course >= 292.5 and course <= 337.5:
            compass_orientation = 'NW'
        elif course >= 337.5 and course <= 360:
            compass_orientation = 'N'
    satellites = data['number_of_satellites_in_use']

    human_readable_text = date + ' ' + time + " " + latitude_degrees + chr(176) + latitude_minutes + '\'' + latitude_seconds + '\"' + latitude_orientation + " " + longitude_degrees + chr(176) + longitude_minutes + '\'' + longitude_seconds + '\"' + longitude_orientation + " " + altitude + "ft MSL " + speed + " Mph " + true_course + chr(176) + " " + compass_orientation + " satellites in use: " + satellites
    return human_readable_text

def main():
    gps = serial.Serial(Serial_Device, baudrate = 9600, timeout = 0.5)
    running = True
    while running == True:
        try:
            text = str()
            time.sleep(1)
            data = get_position(gps)
            print(data)
            text = human_readable(data)
            print(text)
        except KeyboardInterrupt:
            running = False
            gps.close()
            print("Done")

if __name__ == '__main__':
    main()
