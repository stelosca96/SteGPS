import time
import serial
import re

from haversine import haversine
from threading import Thread


class Gps:

    def __init__(self, serial_port, timezone=0, serial_baudrate=9600):
        self.serial_ = serial.Serial(serial_port, serial_baudrate)
        # self.file = open("aaa.txt", "a+")

        self.quality_ = 0  # 0 not fixed / 1 standard GPS / 2 differential GPS / 3 estimated (DR) fix

        self.speed_ = 0  # speed over ground km/h
        self.altitude_ = 0  # altitude (m)
        self.latitude_ = 0
        self.longitude_ = 0
        self.satellites_ = 0  # number of satellites in use
        self.time_ = 0  # UTC time hhmmss.ss
        self.date_ = 0  # date in day, month, year format ddmmyy es. 091219

        self._worker = Thread(target=self._run, daemon=False)
        self._worker.start()

    @property
    def fixed(self):
        return self.quality_ != 0

    @property
    def position(self):
        position = (self.latitude, self.longitude)
        return position

    @property
    def altitude(self):
        return self.altitude_

    @property
    def latitude(self):
        return self.latitude_

    @property
    def longitude(self):
        return self.longitude_

    @property
    def speed(self):
        return self.speed_

    @property
    def satellites(self):
        return self.satellites_

    @property
    def time(self):
        # UTC time hhmmss.ss
        p_hours = str(self.time_)[0:2]
        p_minutes = str(self.time_)[2:4]
        p_seconds = str(self.time_)[4:6]
        return '{}:{}:{}'.format(p_hours, p_minutes, p_seconds)

    @property
    def date(self):
        # date in day, month, year format ddmmyy es. 091219
        self.date_ = "000000" if self.date_ == 0 else str(self.date_)
        p_day = self.date_[0:2]
        p_month = self.date_[2:4]
        p_year = self.date_[4:6]
        return '{}-{}-{}'.format(p_day, p_month, p_year)

    @property
    def timestamp(self):
        return '{} {}'.format(self.date, self.time)

    def distance(self, latitude: float, longitude: float):
        position_distance = (latitude, longitude)
        return haversine(self.position, position_distance)

    @property
    def travelled_distance(self):
        return 0

    def _run(self):
        last_print = time.monotonic()
        while True:
            try:
                # serial read line by line
                line = self.serial_.read_until('\n'.encode()).decode()
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
        self.time_ = line[1]
        self.latitude_ = line[2]
        self.longitude_ = line[4]
        self.quality_ = line[6]
        self.satellites_ = line[7]
        self.altitude_ = line[9]

    def parse_xxGLL(self, line):
        if line.__len__() < 8:
            return
        self.latitude_ = line[1]
        self.longitude_ = line[3]

    def parse_xxRMC(self, line):
        if line.__len__() < 13:
            return
        self.time_ = line[1]
        self.latitude_ = line[3]
        self.longitude_ = line[5]
        self.date_ = line[9]

    def parse_xxVTG(self, line):
        if line.__len__() < 10:
            return
        self.speed_ = line[7]
