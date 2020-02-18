import time
import serial
import re

from .haversine import haversine
from threading import Thread
from datetime import datetime, timedelta


class Gps:

    def __init__(self, serial_port: str, timezone_hours: int = 0, serial_baudrate: int = 9600):
        self.__serial = serial.Serial(serial_port, serial_baudrate)
        # self.file = open("aaa.txt", "a+")
        self.__timezone_offset = timedelta(hours=timezone_hours)
        self.__quality = 0  # 0 not fixed / 1 standard GPS / 2 differential GPS / 3 estimated (DR) fix

        self.__speed = 0  # speed over ground km/h
        self.__altitude = 0  # altitude (m)
        self.__latitude = 0
        self.__travelled_distance = 0
        self.__longitude = 0
        self.__satellites = 0  # number of satellites in use
        self.__time = 0  # UTC time hhmmss.ss
        self.__date = 0  # date in day, month, year format ddmmyy es. 091219
        self.__pos_0 = ('', '')
        self._worker = Thread(target=self._run, daemon=False)
        self._worker.start()

    @property
    def fixed(self):
        return self.__quality != 0

    @property
    def position(self):
        position = (self.latitude, self.longitude)
        return position

    @property
    def altitude(self):
        return self.__altitude

    @property
    def latitude(self):
        return self.__latitude

    @property
    def longitude(self):
        return self.__longitude

    @property
    def speed(self):
        return self.__speed

    @property
    def satellites(self):
        return self.__satellites

    @property
    def time(self):
        # UTC time hhmmss.ss
        p_hours = str(self.__time)[0:2]
        p_minutes = str(self.__time)[2:4]
        p_seconds = str(self.__time)[4:6]
        return '{}:{}:{}'.format(p_hours, p_minutes, p_seconds)

    @property
    def date(self):
        # date in day, month, year format ddmmyy es. 091219
        self.__date = "010100" if self.__date == 0 else str(self.__date)
        p_day = self.__date[0:2]
        p_month = self.__date[2:4]
        p_year = self.__date[4:6]
        return '{}-{}-{}'.format(p_year, p_month, p_day)

    @property
    def timestamp(self):
        timestamp = '{} {}'.format(self.date, self.time)
        utc = datetime.strptime(timestamp, '%y-%m-%d %H:%M:%S')
        # timestamp_f = utc + self.timezone_offset
        return utc

    def distance(self, latitude: float, longitude: float):
        position_distance = (latitude, longitude)
        return haversine(self.position, position_distance)

    @property
    def travelled_distance(self):
        return self.__travelled_distance

    def _run(self):
        last_print = time.monotonic()
        while True:
            try:
                # serial read line by line
                line = self.__serial.read_until('\n'.encode()).decode()
                # print(line)
                self.parse_line(line)
            except UnicodeDecodeError:
                print("Invalid line format")
            time.sleep(0.1)

    def parse_line(self, line: str):
        splitted_line = line.split(',')
        name = splitted_line[0]
        if re.match("^\$..GGA$", name):
            self.parse_xxGGA(splitted_line)
        elif re.match("^\$..GLL$", name):
            self.parse_xxGLL(splitted_line)
        elif re.match("^\$..RMC$", name):
            self.parse_xxRMC(splitted_line)
        elif re.match("^\$..VTG$", name):
            self.parse_xxVTG(splitted_line)

    def parse_xxGGA(self, line: list):
        if line.__len__() < 15:
            return
        self.__time = line[1]
        if self.__latitude != '' and self.__longitude != '':
            self.nmea_cord_to_decimal(line[3], line[5])
            self.add_distance(self.latitude, self.longitude)
        self.__quality = int(line[6])
        self.__satellites = int(line[7])
        self.__altitude = float(line[9])

    def parse_xxGLL(self, line):
        if line.__len__() < 8:
            return
        if self.__latitude != '' and self.__longitude != '':
            self.nmea_cord_to_decimal(line[1], line[3])

    def parse_xxRMC(self, line):
        if line.__len__() < 13:
            return
        self.__time = line[1]
        if self.__latitude != '' and self.__longitude != '':
            self.nmea_cord_to_decimal(line[3], line[5])
        self.__date = line[9]

    def parse_xxVTG(self, line):
        if line.__len__() < 10:
            return
        self.__speed = line[7]

    @travelled_distance.setter
    def travelled_distance(self, value):
        self.__travelled_distance = value

    def add_distance(self, latitude, longitude):
        pos_1 = (latitude, longitude)
        if longitude != '' and latitude != '' and self.__pos_0[0] != '' and self.__pos_0[1] != '':
            d = haversine(self.__pos_0, pos_1)
            if d > 1:
                self.__travelled_distance += d
        self.__pos_0 = pos_1

    def nmea_cord_to_decimal(self, latitude, longitude):
        if not re.match("[0-9]{4}.[0-9]+", latitude) or not re.match("[0-9]{5}.[0-9]+", longitude):
            return
        self.__latitude = float(latitude[0:2]) + float(latitude[2:])/60
        self.__longitude = float(longitude[0:3]) + float(longitude[3:])/60
