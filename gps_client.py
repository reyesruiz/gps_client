import gps
import serial


Serial_Device = "/dev/ttyACM0"

def get_position(gps):
    gps_data = gps.readlines()
    gps_parsed_data = {'date': "",
                'time': "",
                'latitude': "",
                'latitude_orientation': "",
                'logitude': "",
                'longitude_orientation': "",
                'speed_knots': "",
                'true_course': "",
                'altitude_msl': "",
                'number_of_satellites_in_use': ""
                }

    for message in gps_data:
        message = message.decode("utf-8")
        parts = message.split(',')
        #I want GPRMC and
        if parts[0] == '$GPRMC':
            receiver_warning = parts[2]
            if receiver_warning == 'A':
                gps_parsed_data['latitude'] = parts[3]
                gps_parsed_data['latitude_orientation'] = parts[4]
                gps_parsed_data['logitude'] = parts[5]
                gps_parsed_data['longitude_orientation'] = parts[6]
                gps_parsed_data['speed_knots'] = parts[7]
                gps_parsed_data['true_course'] = parts[8]
                gps_parsed_data['date'] = parts[9]
                gps_parsed_data['time'] = parts[1]

        elif parts[0] == '$GPGGA':
            gps_parsed_data['number_of_satellites_in_use'] = parts[7]
            gps_parsed_data['altitude_msl'] = parts[9]
    return gps_parsed_data

gps = serial.Serial(Serial_Device, baudrate = 9600, timeout = 0.5)
print(get_position(gps))
