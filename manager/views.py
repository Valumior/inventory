from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from manager.models import *
from manager.forms import *
from manager.serializers import *

import StringIO
import qrcode

# Create your views here.

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def loginView(request):
	logout(request)
	login_error = ''
	_next = '/'
	formset = LoginForm(request.POST or None)
	if request.method == 'POST':
		if request.POST['next']:
			_next = request.POST['next']
		if formset.is_valid():
			username = formset.cleaned_data['username']
			password = formset.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
				return HttpResponseRedirect(_next)
			loginError = 'Login data incorrect'
	else:
		if request.method == 'GET':
			if request.GET['next']:
				_next = request.GET['next']
	if 'login' in _next:
		_next = '/'
	return render(request, 'login.html', { 'formset' : formset.as_p(), 'Next' : _next, 'login_error' : login_error })
	
def logoutView(request):
	logout(request)
	return HttpResponseRedirect(reverse('main'))

def registrationView(request):
	logout(request)
	formset = UserForm(request.POST or None)
	success = False
	if request.POST:
		if formset.is_valid():
			user = User.objects.create_user(formset.cleaned_data['username'], formset.cleaned_data['email'], formset.cleaned_data['password'])
			user.first_name = formset.cleaned_data['first_name']
			user.last_name = formset.cleaned_data['last_name']
			user.is_active = False
			user.save()
			success = True
			formset = UserForm()
	return render(request, 'register.html', { 'formset' : formset.as_p(), 'success' : success })

def mainView(request):
	entries = Entry.objects.all()
	return render(request, 'main.html', { 'entries' : entries })

def roomView(request):
	rooms = Room.objects.all()
	return render(request, 'room.html', { 'rooms' : rooms })
	
def roomDetailsView(request, pk=None):
	if pk:
		room = get_object_or_404(Room, id=pk)
		entries = Entry.objects.filter(room=room)
		return render(request, 'roomDetails.html', { 'room' : room , 'entries' : entries })
	return HttpResponseRedirect(reverse('room'))
	
def addressView(request):
	addressess = Address.objects.all()
	return render(request, 'address.html', { 'addressess' : addressess })
	
def addressDetailView(request, pk=None):
	if pk:
		address = get_object_or_404(Address, id=pk)
		rooms = Room.objects.filter(address=address)
		entries = Entry.objects.filter(room__address=address)
		return render(request, 'addressDetails.html', { 'address' : address , 'rooms' : rooms , 'entries' : entries })
	return HttpResponseRedirect(reverse('address'))
	
def addAddressView(request, pk=None):
	if pk:
		address = get_object_or_404(Address, pk=pk)
	else:
		address = Address()
	
	formset = AddresForm(request.POST or None, instance=address)
	
	if request.method == 'POST':
		if formset.is_valid():
			addr = formset.save(commit=False)
			addr.save()
			return HttpResponseRedirect(reverse('address'))
	
	return render(request, 'addAddress.html', { 'formset' : formset.as_p() })

def addRoomView(request, pk=None):
	if pk:
		room = get_object_or_404(Room, pk=pk)
	else:
		room = Room()
	
	formset = RoomForm(request.POST or None, instance=room)
	
	if request.method == 'POST':
		if formset.is_valid():
			room = formset.save(commit=False)
			room.save()
			return HttpResponseRedirect(reverse('room'))
	
	return render(request, 'addRoom.html', { 'formset' : formset.as_p() })
	
@login_required(login_url='login')
def addEntryView(request, pk=None):
	if pk:
		entry = get_object_or_404(Entry, id_number=pk)
		editing = True
		old_room = entry.room
	else:
		entry = Entry()
		editing = False
	
	formset = EntryForm(request.POST or None, instance=entry)
	
	if request.method == 'POST':
		if formset.is_valid():
			entry = formset.save(commit=False)
			if editing:
				if entry.room.id != old_room.id:
					log = LogEntry(entry=entry, old_location=old_room, new_location=entry.room, user=request.user)
					log.save()
			entry.save()
			return HttpResponseRedirect(reverse('main'))
	
	return render(request, 'addEntry.html', { 'formset' : formset.as_p() })

def generateQrImage(request, pk=None):
	if pk:
		entry = None
		try:
			entry = Entry.objects.get(id_number=pk)
		except ObjectDoesNotExist:
			return HttpResponseRedirect(reverse('main'))
		
		id_number = entry.id_number
		qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
		qr.add_data(id_number)
		qr.make(fit=True)
		
		img = qr.make_image()
		temp = StringIO.StringIO()
		img.save(temp, format='PNG')
		filename = id_number + '.png'
		img_file = InMemoryUploadedFile(temp, None, filename, 'image/png', temp.len, None)
		
		qr_image = QrImage()
		qr_image.qr_image.save(filename, img_file)
		qr_image.save()
		entry.qr = qr_image
		entry.save()
	return HttpResponseRedirect(request.GET['next'])

def entryDetailsView(request, pk=None):
	if pk:
		entry = get_object_or_404(Entry, id_number=pk)
		logs = LogEntry.objects.filter(entry=entry)
		return render(request, 'entryDetails.html', { 'entry' : entry , 'logs' : logs})
	return HttpResponseRedirect(reverse('main'))

def userView(request):
	if not request.user.is_staff:
		raise PermissionDenied
	inactive = User.objects.filter(is_active=False)
	active = User.objects.filter(is_active=True)
	return render(request, 'user.html', { 'inactiveUsers' : inactive, 'activeUsers' : active })
	
def userDetailsView(request, pk=None):
	if not request.user.is_staff:
		raise PermissionDenied
	if pk is None:
		raise Http404
	user = get_object_or_404(User, id=pk)
	return render(request, 'userDetails.html', { 'selectedUser' : user })

def changeUserActiveStatus(request, pk=None):
	if not request.user.is_staff:
		raise PermissionDenied
	if pk is None:
		raise Http404
	user = get_object_or_404(User, id=pk)
	if not user.is_staff:
		if not user.is_superuser:
			user.is_active = not user.is_active
			user.save()
			if user.is_active and not Token.objects.get(user=user).exists():
				Token.objects.create(user=user)
			elif not user.is_active and not Token.objects.get(user=user).exists():
				Token.objects.get(user=user).delete()
			#TODO send email?	
	return HttpResponseRedirect(reverse('userDetails',kwargs={ 'pk' : pk }))
	
def removeUser(request, pk=None):
	if not request.user.is_staff:
		raise PermissionDenied
	if pk is None:
		raise Http404
	user = get_object_or_404(User, id=pk)
	if not user.is_staff:
		if not user.is_superuser:
			user.delete()
	return HttpResponseRedirect(reverse('userDetails',kwargs={ 'pk' : pk }))

def changeUserRank(request, pk=None):
	if not request.user.is_superuser:
		raise PermissionDenied
	if pk is None:
		raise Http404
	user = get_object_or_404(User, id=pk)
	if not user.is_superuser:
		user.is_staff = not user.is_staff
		user.save()
	return HttpResponseRedirect(reverse('userDetails',kwargs={ 'pk' : pk }))

@api_view(['GET'])
def apiEntries(request):
	if request.method == 'GET':
		entries = Entry.objects.all()
		serializer = EntrySerializer(entries, many=True)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiRooms(request):
	if request.method == 'GET':
		rooms = Room.objects.all()
		serializer = RoomSerializer(rooms, many=True)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiAddresses(request):
	if request.method == 'GET':
		addresses = Address.objects.all()
		serializer = AddressSerializer(addresses, many=True)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET', 'PUT'])
def apiEntry(request, pk=None):
	entry = get_object_or_404(Entry, id_number=pk)
	
	if request.method == 'GET':
		serializer = EntrySerializer(entry, many=False)
		return JSONResponse(serializer.data)
	elif request.method == 'PUT':
		old_room = entry.room
		data = JSONParser().parse(request)
		serializer = EntrySerializer(entry, data=data)
		if serializer.is_valid():
			entry = serializer.save()
			if old_room.id != entry.room.id:
				log = LogEntry(entry=entry, old_location=old_room, new_location=entry.room, user=request.user)
				log.save()
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiRoom(request, pk=None):
	room = get_object_or_404(Room, id=pk)
	
	if request.method == 'GET':
		serializer - RoomSerializer(room, many=False)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiAddress(request, pk=None):
	address = get_object_or_404(Address, id=pk)
	
	if request.method == 'GET':
		serializer = AddressSerializer(address, many=False)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiRoomEntries(request, pk=None):
	room = get_object_or_404(Room, id=pk)
	
	if request.method == 'GET':
		entries = Entry.objects.filter(room=room)
		serializer = EntrySerializer(entries, many=True)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiAddressRooms(request, pk=None):
	address = get_object_or_404(Address, id=pk)
	
	if request.method == 'GET':
		rooms = Room.objects.filter(address=address)
		serializer = RoomSerializer(rooms, many=True)
		return JSONResponse(serializer.data)
	else:
		raise Http404