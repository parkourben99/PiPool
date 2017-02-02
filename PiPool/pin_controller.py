from PiPool.models import Pin
import RPIO


class PinController(object):
    def __init__(self):
        RPIO.setmode(RPIO.BCM)

        self.my_pins = set()
        self.set_all_pins()

    def get_thermometers(self):
        return self.my_pins.filter(is_thermometer=True)

    def set_all_pins(self):
        RPIO.cleanup()

        for pin in Pin.objects.all():
            try:
                RPIO.setup(pin.pin_number, pin.get_direction())
                RPIO.output(pin.pin_number, RPIO.HIGH)

                self.my_pins.add(pin)
            except: pass

    def get_dashboard_data(self):
        data = {'thermometers': self.get_thermometers(), 'pins': self.my_pins.filter(is_thermometer=False)}

        return data

    def get_all_pins(self):
        return {'pins': self.my_pins}