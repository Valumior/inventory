from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django_tables2 import RequestConfig
from easy_pdf.rendering import render_to_pdf_response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from manager.models import *
from manager.forms import *
from manager.serializers import *
from manager.tables import *
from manager.util import deURLify_entry_signing

import StringIO
import qrcode
from datetime import datetime

# Create your views here.

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def logEntryChange(old_entry, new_entry, user):
	change = False
	changelog = ''
	room = None
	if new_entry.name != old_entry['name']:
		change = True
		changelog = changelog + 'Zmiana nazwy\n'
	if new_entry.short_description != old_entry['short_description']:
		change = True
		changelog = changelog + 'Zmiana zmiana krotkiego opisu\n'
	if new_entry.description != old_entry['description']:
		change = True
		changelog = changelog + 'Zmiana opisu\n'
	if new_entry.room != old_entry['room']:
		change = True
		changelog = changelog + 'Zmiana pokoju\n'
		room = new_entry.room
	if new_entry.caretaker != old_entry['caretaker']:
		change = True
		changelog = changelog + 'Zmiana opiekuna\n'
	if change:
		return LogEntry(entry=new_entry, old_location=old_entry['room'], new_location=room, user=user, notes=changelog)
	return None


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
	if 'login' in _next or 'register' in _next:
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
			perm = UserPermissions(user=user)
			perm.save()
			success = True
			formset = UserForm()
	return render(request, 'register.html', { 'formset' : formset.as_p(), 'success' : success })

@login_required(login_url='login')
def mainView(request):
	data = Entry.objects.all()
	search = None
	if request.POST:
		if '_liquidate' in request.POST:
			liquidation = Liquidation()
			selected_entries = request.POST.getlist('selected')
			for entry in selected_entries:
				liqudation.entries.add(entry)
			liquidation.save()
			return HttpResponseRedirect(reverse('liquidationDetails', kwargs={ 'pk' : liquidation.id }))
		else:
			search = SearchForm(request.POST)
			if search.is_valid():
				searchString = search.cleaned_data['search']
				data = Entry.objects.filter(Q(signing__icontains=searchString) | Q(name__icontains=searchString) | Q(description__icontains=searchString))
	else:
		search = SearchForm()
	entries = EntryTable(data)
	RequestConfig(request).configure(entries)
	return render(request, 'main.html', { 'entries' : entries , 'search' : search})

@login_required(login_url='login')
def roomView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if permissions.is_admin:
		rooms = RoomTable(Room.objects.all())
	else:
		rooms = RoomTableNoEdit(Room.objects.all())
	RequestConfig(request).configure(rooms)
	return render(request, 'room.html', { 'rooms' : rooms })
	
@login_required(login_url='login')
def roomDetailsView(request, pk=None):
	if pk:
		room = get_object_or_404(Room, id=pk)
		entries = EntryTable(Entry.objects.filter(room=room))
		RequestConfig(request).configure(entries)
		return render(request, 'roomDetails.html', { 'room' : room , 'entries' : entries })
	return HttpResponseRedirect(reverse('room'))
	
@login_required(login_url='login')
def addressView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if permissions.is_admin:
		addressess = AddressTable(Address.objects.all())
	else:
		addressess = AddressTableNoEdit(Address.objects.all())
	RequestConfig(request).configure(addressess)
	return render(request, 'address.html', { 'addressess' : addressess })
	
@login_required(login_url='login')
def addressDetailView(request, pk=None):
	if pk:
		address = get_object_or_404(Address, id=pk)
		permissions = get_object_or_404(UserPermissions, user=request.user)
		if permissions.is_admin:
			rooms = RoomTable(Room.objects.filter(address=address), prefix='r-')
		else:
			rooms = RoomTableNoEdit(Room.objects.filter(address=address), prefix='r-')
		entries = EntryTable(Entry.objects.filter(room__address=address), prefix='e-')
		config = RequestConfig(request)
		config.configure(rooms)
		config.configure(entries)
		return render(request, 'addressDetails.html', { 'address' : address , 'rooms' : rooms , 'entries' : entries })
	return HttpResponseRedirect(reverse('address'))
	
@login_required(login_url='login')
def addAddressView(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		raise PermissionDenied
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

@login_required(login_url='login')
def addRoomView(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		raise PermissionDenied
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
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if pk:
		if not permissions.is_admin:
			if not permissions.is_add_allowed:
				raise PermissionDenied
		entry = get_object_or_404(Entry, signing=deURLify_entry_signing(pk))
		editing = True
		old_entry = entry.getDict()
	else:
		if not permissions.is_admin:
			if not permissions.is_add_allowed:
				if not permissions.is_edit_allowed:
					raise PermissionDenied
		entry = Entry()
		editing = False
	
	if permissions.is_admin and not editing:
		formset = EntryForm(request.POST or None, instance=entry)
	elif editing:
		if permissions.is_admin:
			formset = EntryEditForm(request.POST or None, instance=entry)
		else:
			formset = EntryFormSimple(request.POST or None, instance=entry)
	else:
		raise PermissionDenied
	
	if request.method == 'POST':
		if formset.is_valid():
			entry = formset.save(commit=False)
			if editing:
				log = logEntryChange(old_entry, entry, request.user)
				if log:
					log.save()
			entry.save()
			return HttpResponseRedirect(reverse('main'))
	
	return render(request, 'addEntry.html', { 'formset' : formset.as_p() })

@login_required(login_url='login')
def generateQrImage(request, pk=None):
	if pk:
		entry = None
		try:
			entry = Entry.objects.get(signing=deURLify_entry_signing(pk))
		except ObjectDoesNotExist:
			return HttpResponseRedirect(reverse('main'))
		
		signing = entry.signing
		qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
		qr.add_data(signing)
		qr.make(fit=True)
		
		img = qr.make_image()
		response = HttpResponse(content_type='image/png')
		response['Content-Disposition'] = 'attachment; filename="%s"' % (entry.signing + '.png')
		img.save(response, 'PNG')
		return response
	else:
		return Http404

@login_required(login_url='login')
def entryDetailsView(request, pk=None):
	if pk:
		entry = get_object_or_404(Entry, signing=deURLify_entry_signing(pk))
		permissions = get_object_or_404(UserPermissions, user=request.user)
		logs = LogEntryTable(LogEntry.objects.filter(entry=entry))
		if LiquidationEntryNote.objects.filter(entry=entry, liquidation__completed=False, liquidation__rejected=False).exists():
			liquidation = LiquidationEntryNote.objects.get(entry=entry, liquidation__completed=False, liquidation__rejected=False).liquidation
		else:
			liquidation = None
		possible_liquidations = Liquidation.objects.filter(submitted=False)
		RequestConfig(request).configure(logs)
		return render(request, 'entryDetails.html', { 'permissions' : permissions , 'entry' : entry , 'logs' : logs, 'image' : reverse('generateQr', kwargs={ 'pk' : pk }), 'liquidation' : liquidation , 'possible_liquidations' : possible_liquidations })
	return HttpResponseRedirect(reverse('main'))

@login_required(login_url='login')
def userView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_user_manager:
			raise PermissionDenied
	inactive = User.objects.filter(is_active=False)
	active = UserPermissionsTable(UserPermissions.objects.filter(user__is_active=True))
	RequestConfig(request).configure(active)
	return render(request, 'user.html', { 'inactiveUsers' : inactive, 'activeUsers' : active })
	
@login_required(login_url='login')
def userDetailsView(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_user_manager:
			raise PermissionDenied
	if pk is None:
		raise Http404
	user = get_object_or_404(User, id=pk)
	target_permissions = get_object_or_404(UserPermissions, user=user)
	return render(request, 'userDetails.html', { 'selectedUser' : user , 'permissions' : permissions , 'target_permissions' : target_permissions })

@login_required(login_url='login')
def changeUserActiveStatus(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_user_manager:
			raise PermissionDenied
	if pk is None:
		raise Http404
	user = get_object_or_404(User, id=pk)
	target_permissions = get_object_or_404(UserPermissions, user=user)
	if not target_permissions.is_admin:
		if not target_permissions.is_user_manager:
			user.is_active = not user.is_active
			user.save()
			#TODO send email?	
	return HttpResponseRedirect(reverse('userDetails',kwargs={ 'pk' : pk }))
	
@login_required(login_url='login')
def removeUser(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_user_manager:
			raise PermissionDenied
	if pk is None:
		raise Http404
	user = get_object_or_404(User, id=pk)
	target_permissions = get_object_or_404(UserPermissions, user=user)
	if not target_permissions.is_admin:
		if not target_permissions.is_user_manager:
			user.delete()
	return HttpResponseRedirect(reverse('userDetails',kwargs={ 'pk' : pk }))

@login_required(login_url='login')
def changeUserRank(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_user_manager:
			raise PermissionDenied
	if pk is None:
		raise Http404
	
	user = get_object_or_404(User, id=pk)
	target_permissions = get_object_or_404(UserPermissions, user=user)
	if target_permissions.is_admin:
		raise PermissionDenied
	
	if permissions.is_admin:
		formset = UserPermissionsForm(request.POST or None, instance=target_permissions)
	else:
		formset = UserPermissionsFormNoAdmin(request.POST or None, instance=target_permissions)
	
	if request.method == 'POST':
		if formset.is_valid():
			perm = formset.save(commit=False)
			perm.save()
			return HttpResponseRedirect(reverse('userDetails',kwargs={ 'pk' : pk }))
	return render(request, 'userPermissionsEdit.html', { 'formset' : formset , 'pk' : pk })

@login_required(login_url='login')
def inventoryOrderView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	orders = InventoryOrderTable(InventoryOrder.objects.all())
	RequestConfig(request).configure(orders)
	
	return render(request, 'inventoryOrder.html', { 'permissions' : permissions , 'orders' : orders })
	
@login_required(login_url='login')
def createInventoryOrder(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_session_controller:
			raise PermissionDenied
	order = InventoryOrder()
	order.save()
	return HttpResponseRedirect(reverse('inventoryOrder'))

@login_required(login_url='login')
def inventoryOrderReportsView(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	order = get_object_or_404(InventoryOrder, pk=pk)
	order_reports = InventoryRoomReportTable(InventoryRoomReport.objects.filter(order=order), prefix='rr-')
	done_rooms = InventoryRoomReport.objects.filter(order=order).values_list('room__id', flat=True)
	remaining_rooms = RoomTableNoEdit(Room.objects.exclude(id__in=done_rooms), prefix='r-')
	config = RequestConfig(request)
	config.configure(order_reports)
	config.configure(remaining_rooms)
	
	return render(request, 'inventoryOrderReports.html', { 'permissions' : permissions , 'order_reports' : order_reports , 'remaining_rooms' : remaining_rooms , 'order' : order , 'finish' : Room.objects.exclude(id__in=done_rooms).exists() })

@login_required(login_url='login')
def inventoryReportDetailsView(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	report = get_object_or_404(InventoryRoomReport, pk=pk)
	inventory_notes = InventoryEntryNoteTable(InventoryEntryNote.objects.filter(report=report))
	RequestConfig(request).configure(inventory_notes)
	
	return render(request, 'inventoryReportDetails.html', { 'permissions' : permissions , 'inventory_notes' : inventory_notes , 'report' : report })

@login_required(login_url='login')
def generateInventoryOrderReport(request, pk=None):
	order = get_object_or_404(InventoryOrder, pk=pk)
	reports = InventoryRoomReport.objects.filter(order=order)
	entries = InventoryEntryNote.objects.filter(report__in=reports)
	present_entries = entries.filter(status='P')
	misplaced_entries = entries.filter(status='E').exclude(entry__in=present_entries.values('entry'))
	duplicate_entries = entries.filter(status='E').filter(entry__in=present_entries.values('entry'))
	missing_entries = entries.filter(status='M').exclude(entry__in=misplaced_entries.values('entry'))
	return render_to_pdf_response(request, 'inventoryOrderReportPdf.html', { 'present_entries' : present_entries , 'misplaced_entries' : misplaced_entries , 'missing_entries' : missing_entries })

@login_required(login_url='login')
def finishInventoryOrder(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_session_controller:
			raise PermissionDenied
	order = get_object_or_404(InventoryOrder, pk=pk)
	done_rooms = InventoryRoomReport.objects.filter(order=order).values_list('room__id', flat=True)
	if Room.objects.exclude(id__in=done_rooms).exists():
		raise PermissionDenied
	order.completed = True
	order.date_completed = datetime.now()
	order.save()
	return HttpResponseRedirect(reverse('inventoryOrderReports', kwargs={ 'pk' : pk }))

@login_required(login_url='login')
def entryGroupView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	groups = EntryGroup.objects.all()
	return render(request, 'entryGroup.html', { 'groups' : groups , 'permissions' : permissions })

@login_required(login_url='login')
def entryGroupDetailsView(request, pk=None):
	if not pk:
		raise Http404
	group = get_object_or_404(EntryGroup, pk=pk)
	entries = EntryTable(Entry.objects.filter(group=group))
	RequestConfig(request).configure(entries)
	return render(request, 'entryGroupDetails.html', { 'group' : group , 'entries' : entries })
	
@login_required(login_url='login')
def addEntryGroupView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		raise PermissionDenied
	formset = EntryGroupForm(request.POST or None)
	if request.method == 'POST':
		if formset.is_valid():
			formset.save()
			return HttpResponseRedirect(reverse('entryGroup'))
	return render(request, 'form.html', { 'formset' : formset , 'form_title' : 'Dodaj Grupe', 'form_url' : reverse('addEntryGroup')})

@login_required(login_url='login')
def institutionView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	institutions = Institution.objects.all()
	return render(request, 'institution.html', { 'institutions' : institutions , 'permissions' : permissions })

@login_required(login_url='login')
def addInstitutionView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		raise PermissionDenied
	formset = InstitutionForm(request.POST or None)
	if request.method == 'POST':
		if formset.is_valid():
			formset.save()
			return HttpResponseRedirect(reverse('institution'))
	return render(request, 'form.html', { 'formset' : formset , 'form_title' : 'Dodaj Instytucje', 'form_url' : reverse('addInstitution')})

@login_required(login_url='login')
def liquidationView(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	incomplete_liquidations = Liquidation.objects.filter(submitted=False)
	pending_liquidations = Liquidation.objects.filter(submitted=True, completed=False, rejected=False)
	completed_liquidations = Liquidation.objects.filter(completed=True)
	rejected_liquidations = Liquidation.objects.filter(rejected=True)
	return render(request, 'liquidation.html', { 'permissions' : permissions, 'incomplete_liquidations' : incomplete_liquidations , 'pending_liquidations' : pending_liquidations , 'completed_liquidations' : completed_liquidations , 'rejected_liquidations' : rejected_liquidations })

@login_required(login_url='login')
def createLiquidation(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_liquidation:
			raise PermissionDenied
	Liquidation().save()
	return HttpResponseRedirect(reverse('liquidation'))

@login_required(login_url='login')
def liquidationDetailsView(request, pk=None):
	liquidation = get_object_or_404(Liquidation, pk=pk)
	permissions = get_object_or_404(UserPermissions, user=request.user)
	liquidation_notes = EntryTable(liquidation.entries)
	RequestConfig(request).configure(liquidation_notes)
	return render(request, 'liquidationDetails.html', { 'permissions' : permissions , 'liquidation' : liquidation, 'liquidation_notes' : liquidation_notes })

@login_required(login_url='login')
def submitLiquidation(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_liquidation:
			raise PermissionDenied
	liquidation = get_object_or_404(Liquidation, pk=pk)
	liquidation.submitted = True
	liquidation.save()
	return HttpResponseRedirect(reverse('liquidationDetails', kwargs={ 'pk' : pk }))

@login_required(login_url='login')
def completeLiquidation(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_liquidation_approver:
			raise PermissionDenied
	liquidation = get_object_or_404(Liquidation, pk=pk)
	liquidation.completed = True
	for entry in liquidation.entries:
		entry.removed_value = 0.0
		entry.removed_description = liquidation.getMsg()
		entry.save()
	liquidation.save()
	return HttpResponseRedirect(reverse('liquidationDetails', kwargs={ 'pk' : pk }))

@login_required(login_url='login')
def rejectLiquidation(request, pk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_liquidation_approver:
			raise PermissionDenied
	liquidation = get_object_or_404(Liquidation, pk=pk)
	liquidation.rejected = True
	liquidation.save()
	return HttpResponseRedirect(reverse('liquidationDetails', kwargs={ 'pk' : pk }))
	
@login_required(login_url='login')
def generateLiquidationApplication(request, pk=None):
	liquidation = get_object_or_404(Liquidation, pk=pk)
	liquidation_notes = LiquidationEntryNote.objects.filter(liquidation=liquidation)
	return render_to_pdf_response(request, 'liquidationApplicationPdf.html', { 'liquidation_notes' : liquidation_notes })

@login_required(login_url='login')
def liquidateEntry(request, epk=None, lpk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_liquidation_approver:
			raise PermissionDenied
	entry = get_object_or_404(Entry, signing=deURLify_entry_signing(epk))
	liquidation = get_object_or_404(Liquidation, pk=lpk)
	if liquidation.submitted:
		raise PermissionDenied
	liquidation.entries.add(entry)
	return HttpResponseRedirect(reverse('liquidationDetiails', kwargs={ 'pk' : liquidation.id }))

@login_required(login_url='login')
def liquidationEntryRemove(request, lpk=None, epk=None):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	if not permissions.is_admin:
		if not permissions.is_liquidation:
			raise PermissionDenied
	entry = get_object_or_404(Entry, signing=deURLify_entry_signing(epk))
	liquidation = get_object_or_404(Liquidation, pk=lpk)
	liquidation.entries.remove(entry)
	return HttpResponseRedirect(reverse('liquidationDetiails', kwargs={ 'pk' : liquidation.id }))


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
	entry = get_object_or_404(Entry, signing=deURLify_entry_signing(pk))
	
	if request.method == 'GET':
		serializer = EntrySerializer(entry, many=False)
		return JSONResponse(serializer.data)
	elif request.method == 'PUT':
		old_entry = entry.getDict()
		data = JSONParser().parse(request)
		serializer = EntrySerializerShallow(entry, data=data, partial=True)
		if serializer.is_valid():
			entry = serializer.save()
			log = logEntryChange(old_entry, entry, request.user)
			if log:
				log.save()
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiRoom(request, pk=None):
	room = get_object_or_404(Room, id=pk)
	
	if request.method == 'GET':
		serializer = RoomSerializer(room, many=False)
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

@api_view(['GET'])
def apiUserPermissions(request):
	permissions = get_object_or_404(UserPermissions, user=request.user)
	
	if request.method == 'GET':
		serializer = UserPermissionsSerializer(permissions, many=False)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiInventoryOrders(request):
	if request.method == 'GET':
		active_orders = InventoryOrder.objects.filter(completed=False)
		serializer = InventoryOrderSerializer(active_orders, many=True)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['GET'])
def apiOrderRooms(request, pk=None):
	order = get_object_or_404(InventoryOrder, id=pk)
	
	if request.method == 'GET':
		done_rooms = InventoryRoomReport.objects.filter(order=order).values_list('room__id', flat=True)
		remaining_rooms = Room.objects.exclude(id__in=done_rooms)
		serializer = RoomSerializer(remaining_rooms, many=True)
		return JSONResponse(serializer.data)
	else:
		raise Http404

@api_view(['POST'])
def apiRoomReport(request):
	if request.method == 'POST':
		serializer = InventoryRoomReportSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save(author=request.user)
			return JSONResponse(serializer.errors, status=201)
		return JSONResponse(serializer.errors, status=400)
	else:
		raise Http404
		
