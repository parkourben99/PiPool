from PiControl.models import Pin
import RPIO
import rollbar
import sys


class PinController(object):
    def __init__(self):
        RPIO.setmode(RPIO.BCM)
        self.my_pins = None
        self.set_all_pins()

    def get_thermometers(self):
        return self.my_pins.filter(is_thermometer=True)

    def set_all_pins(self):
        RPIO.cleanup()

        self.my_pins = Pin.objects.all()

        for pin in self.my_pins:
            try:
                RPIO.setup(pin.pin_number, pin.get_direction())

            except:
                rollbar.report_exc_info(sys.exc_info())
                self.my_pins.exclude(id=pin.id)

    def get_dashboard_data(self):
        data = {'thermometers': self.get_thermometers(), 'pins': self.my_pins.filter(is_thermometer=False)}

        return data

    def get_all_pins(self):
        return {'pins': self.my_pins}