from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, Http404
import datetime
from django.core.urlresolvers import reverse

from PiControl.models import Pin, TempControl, TimeBand
from PiControl.models import Git
from PiControl.pin_controller import PinController
from .forms import PinForm, TimeBandForm
import rollbar

# Create the pin controller instance
pin_controller = PinController()


def dashboard(request):
    return render(request, "dashboard.html", pin_controller.get_dashboard_data())


def pins(request):
    return render(request, "pins/pins.html", pin_controller.get_all_pins())


def pin_create(request):
    return render(request, "pins/pin-create-edit.html", {'form': PinForm()})


def pin_delete(request, id):
    try:
        pin = pin_controller.my_pins.get(id=id)
    except Pin.DoesNotExist:
        raise Http404("Could not find that pin!")

    result = list(pin.delete()[1].values())[0]
    pin_controller.set_all_pins()

    return JsonResponse({'success': result})


def pin_post(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/pins")

    id = request.POST.get('id')

    if id.isdigit():
        pin = pin_controller.my_pins.get(id=id)
    else:
        pin = Pin()

    form = PinForm(request.POST, instance=pin)

    if form.is_valid():
        form.save()
        pin_controller.set_all_pins()

        return HttpResponseRedirect("/pins")

    return render(request, "pins/pin-create-edit.html", {'form': form})


def pin_edit(request, id):
    try:
        pin = pin_controller.my_pins.get(id=id)
    except Pin.DoesNotExist:
        raise Http404("Could not find that pin!")

    form = PinForm(instance=pin)
    return render(request, "pins/pin-create-edit.html", {"form": form})


def pin_set(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/")

    pin_id = request.POST['pin']
    state = True if request.POST['state'] == '1' or request.POST['state'].lower() == 'true' else False
    result = False

    try:
        pin = pin_controller.my_pins.get(id=pin_id)
    except Pin.DoesNotExist:
        return JsonResponse({'success': False, 'state': state, 'message': 'Can not find pin'})

    pin.set_state(state)
    new_state = pin.get_state()

    if new_state == state:
        result = True

    return JsonResponse({'success': result, 'state': new_state})


def update(request):
    git = Git()

    if request.method == 'POST':
        result = git.update()

        return JsonResponse({'success': result})

    status = git.check()

    return render(request, "git/update.html", {"status": status})


def manuel_toggle(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/")

    temp_control = TempControl.objects.first()
    state = True if request.POST['state'] == '1' or request.POST['state'].lower() == 'true' else False
    result = True

    if state != temp_control.manuel:
        try:
            now = datetime.datetime.now() + datetime.timedelta(hours=12)

            temp_control.manuel = state
            temp_control.manuel_at = None if not state else now
            temp_control.save()

            if state:
                temp_control.outside_turn_on()
        except Exception:
            rollbar.report_message("Unable to manuel_toggle state: " + str(state))
            result = False

    return JsonResponse({'success': result})


def abcdef(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/")

    temp_control = TempControl.objects.first()
    state = True if request.POST['state'] == '1' or request.POST['state'].lower() == 'true' else False
    result = True

    rollbar.report_message('manuel_toggle_off state: ' + str(state))

    if state != temp_control.manuel_off:
        try:
            now = datetime.datetime.now() + datetime.timedelta(hours=12)

            temp_control.manuel_off = state
            temp_control.manuel_off_at = None if not state else now
            temp_control.save()

            if state:
                temp_control.outside_turn_off()
        except Exception:
            rollbar.report_message("Unable to manuel_toggle_off state: " + str(state))
            result = False

    return JsonResponse({'success': result})


def maintain_update(request):
    if request.method != 'POST':
        return HttpResponseRedirect("/")

    temp_control = TempControl.objects.first()

    temp = request.POST['temp']
    range = request.POST['range']

    try:
        temp = float(temp)
        range = float(range)

        try:
            temp_control.temp = temp
            temp_control.range = range
            temp_control.save()
            result = True
        except:
            rollbar.report_message("Unable to save update for temp control")
            result = False
    except:
        result = False

    return JsonResponse({'success': result})


def get_temp(request):
    if request.method == 'POST':
        pin_id = request.POST['id']
    else:
        pin_id = request.GET['id']

    try:
        pin = pin_controller.my_pins.get(id=pin_id)
    except Pin.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Pin not found'})

    return JsonResponse({'success': True, 'temp': pin.get_temp()})


def schedule(request):
    days = TimeBand.objects.all()

    return render(request, "schedule/index.html", {"days": days})


def schedule_edit(request, id):
    try:
        time_band = TimeBand.objects.get(id=id)
    except TimeBand.DoesNotExist:
        raise Http404("Could not find that pin!")

    form = TimeBandForm(instance=time_band)
    return render(request, "schedule/create-edit.html", {"form": form})


def schedule_create(request):
    return render(request, "schedule/create-edit.html", {"form": TimeBandForm()})


def schedule_post(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('schedule'))

    id = request.POST.get('id')

    if id.isdigit():
        time_band = TimeBand.objects.get(id=id)
    else:
        time_band = TimeBand()

    form = TimeBandForm(request.POST, instance=time_band)

    if form.is_valid():
        form.save()

        return HttpResponseRedirect(reverse('schedule'))

    return render(request, "schedule/create-edit.html", {'form': form})


def schedule_delete(request, id):
    try:
        time_band = TimeBand.objects.get(id=id)
    except TimeBand.DoesNotExist:
        raise Http404("Could not find that pin!")

    result = list(time_band.delete()[1].values())[0]

    return JsonResponse({'success': result})