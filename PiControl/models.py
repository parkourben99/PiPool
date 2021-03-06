from decimal import Decimal
from django.db import models
import os
import glob
import time
import git
import datetime
import RPi.GPIO as RPIO
import rollbar


class Pin(models.Model):
    name = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=200, null=False)
    pin_number = models.IntegerField(null=False)
    is_thermometer = models.BooleanField(default=False, null=False)

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_thermometer:
            try:
                self.thermometer = Thermometer('28')  # todo update this one day
            except:
                # rollbar.report_exc_info()
                # rollbar.report_message('could not set thermometer')
                self.thermometer = None

    def get_direction(self):
        return RPIO.OUT if self.is_thermometer is False else RPIO.IN

    def get_temp(self):
        if self.thermometer:
            self.thermometer.refresh()
            return self.thermometer.celsius

        return '?'

    def get_state(self):
        try:
            return RPIO.input(self.pin_number)
        except:
            rollbar.report_message('could not get_state')
            return None

    def get_select_name(self):
        return "{name} ({id})".format(name=self.name, id=self.pin_number)

    def get_state_opposite(self):
        return not self.get_state()

    def set_state(self, state):
        return RPIO.output(self.pin_number, RPIO.HIGH if state else RPIO.LOW)


class Thermometer(object):
    def __init__(self, serial):
        self.celsius = 0
        self.fahrenheit = 0
        self.serial = serial

        self.refresh()

    def read_temp_raw(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '{serial}*'.format(serial=self.serial))[0]
        device_file = device_folder + '/w1_slave'

        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()

        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()

        equals_pos = lines[1].find('t=')

        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            self.celsius = round(temp_c, 1)
            self.fahrenheit = ((self.celsius * 9) / 5.0) + 32

    def refresh(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        self.read_temp()


class Git(object):
    def __init__(self):
        self.repo = git.Repo(os.getcwd())
        self.branch = 'origin/develop'

    def check(self):
        self.repo.remote().fetch()

        diff = self.repo.index.diff(self.branch)
        return bool(diff)

    def update(self):
        try:
            self.repo.remote().pull()
            return True
        except git.GitCommandError:
            rollbar.report_message('could not update git')
            return False


class Schedule(models.Model):
    start_at = models.TimeField(null=True)
    end_at = models.TimeField(null=True)
    day_of_week = models.IntegerField(null=False)
    active = models.BooleanField(default=True, null=False)
    pin_id = models.IntegerField(null=False)

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    def get_week_day(self):
        days = ((0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'))

        return days[self.day_of_week][1]

    def __allowed_to_run(self):
        date_now = datetime.datetime.now()
        time_now = date_now.time()
        result = False

        if date_now.weekday() == self.day_of_week:
            if time_now > self.start_at and time_now < self.end_at:
                result = True

        return result

    def activate(self):
        pin = Pin.objects.filter(id=self.pin_id).first()
        state = pin.get_state()

        # todo fix bug where if pin is set for more then one day then the first instance turns it off
        # maybe just comment out the else?

        if state is None:
            rollbar.report_message('Could not get state for pin {}'.format(self.pin_id))
            return

        if self.__allowed_to_run():
            if not state:
                pin.set_state(True)
                ScheduleHistory().create(self, True)
        else:
            if state:
                pin.set_state(False)
                ScheduleHistory().create(self, False)


class ScheduleHistory(models.Model):
    schedule_id = models.IntegerField(null=False)
    output = models.TextField(null=True)

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    def create(self, schedule, pin_state):
        self.schedule_id = schedule.id
        #self.output = "Setting pin {}".format(pin_state)
        self.save()
