'''
Python csv to gpx file conversion from gps client
Copyright 2022 Reyes Ruiz

https://github.com/reyesruiz/gps_client
'''


import sys

FILE_NAME = sys.argv[1]
GPX_FILE_NAME = FILE_NAME + '-10.gpx'

with open(GPX_FILE_NAME, "w",  encoding="utf8") as gpx_file:
    gpx_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    gpx_file.write('<gpx xmlns="http://www.topografix.com/GPX/1/0" \
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
            xsi:schemaLocation="http://www.topografix.com/GPX/1/0 \
            http://www.topografix.com/GPX/1/0/gpx.xsd" \
            version="1.0" \
            creator="gps_client.py -- https://github.com/reyesruiz/gps_client">\n')
    gpx_file.write('  <trk>\n')
    gpx_file.write('    <trkseg>\n')

with open(FILE_NAME, "r", encoding="utf8") as csv_file:
    while True:
        line = csv_file.readline()
        if not line:
            break
        parts = line.split(',')
        latitude = parts[0]
        longitude = parts[1]
        elevation = parts[2]
        speed = parts[3]
        course = parts[4]
        satellites = parts[5]
        gps_time_parts = (parts[6].split('+'))[0].split(' ')
        gps_time = gps_time_parts[0] + 'T' + gps_time_parts[1] + 'Z'
        with open(GPX_FILE_NAME, "a",  encoding="utf8") as gpx_file:
            gpx_file.write('      <trkpt lat="' + latitude + '" ' + 'lon="' + longitude + '">\n')
            gpx_file.write('        <time>' + gps_time + '</time>\n')
            gpx_file.write('        <ele>' + elevation + '</ele>\n')
            gpx_file.write('        <speed>' + speed + '</speed>\n')
            gpx_file.write('        <course>' + course + '</course>\n')
            gpx_file.write('        <sat>' + satellites + '</sat>\n')
            gpx_file.write('      </trkpt>\n')

with open(GPX_FILE_NAME, "a",  encoding="utf8") as gpx_file:
    gpx_file.write('    </trkseg>\n')
    gpx_file.write('  </trk>\n')
    gpx_file.write('</gpx>')
