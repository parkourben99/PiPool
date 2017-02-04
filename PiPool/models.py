from django.db import models
import RPIO


class Pin(models.Model):
    name = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=200, null=False)
    pin_number = models.IntegerField(null=False)
    is_thermometer = models.BooleanField(default=False, null=False)

    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    def get_direction(self):
        return RPIO.OUT if self.is_thermometer is False else RPIO.IN

    def get_temp(self):
        return 5

    def get_state(self):
        try:
            return RPIO.input(self.pin_number)
        except:
            return None

    def set_state(self, state):
        if state == 1:
            output = RPIO.HIGH
        else:
            output = RPIO.LOW

        print("setting pin_number:{number} to {state}".format(number=self.pin_number, state=output))

        return RPIO.output(self.pin_number, output)
