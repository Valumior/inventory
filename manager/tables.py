import django_tables2 as tables
from django_tables2.utils import A
from manager.models import *
from manager.util import URLify_entry_signing

button_attrs = { 'a' :  { 'class' : 'btn btn-default btn-block' }}

class BaseTable(tables.Table):
	class Meta:
		attrs = { 'class' : 'table table-bordered table-condensed' }

class AddressTable(BaseTable):
	details = tables.LinkColumn('addressDetails', kwargs={ 'pk' : A('pk') }, orderable=False, text='Szczegoly', empty_values=(), attrs=button_attrs)
	edit = tables.LinkColumn('editAddress', kwargs={ 'pk' : A('pk') }, orderable=False, text='Edytuj', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = Address
		fields = ('city', 'street', 'street_number', 'details', 'edit')
		
class AddressTableNoEdit(AddressTable):
	class Meta:
		exclude = ('edit',)

class EntryTable(BaseTable):
	signing = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('getURL') }, attrs=button_attrs)
	room = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('room.id') }, attrs=button_attrs)
	
	class Meta:
		model = Entry
		fields = ('signing', 'name', 'date_added', 'added_price', 'date_removed', 'removed_price', 'room', 'short_description', 'last_modified')

class LogEntryTable(BaseTable):
	old_location = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('old_location.id') }, attrs=button_attrs)
	new_location = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('new_location.id') }, attrs=button_attrs)
	
	class Meta:
		model = LogEntry
		fields = ('entry', 'log_date', 'old_location', 'new_location', 'notes', 'user')

class RoomTable(BaseTable):
	room_id = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('pk') }, attrs=button_attrs)
	edit = tables.LinkColumn('editRoom', kwargs={ 'pk' : A('pk') }, orderable=False, text='Edytuj', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = Room
		fields = ('room_id', 'address', 'edit')

class RoomTableNoEdit(RoomTable):
	class Meta:
		exclude = ('edit',)

class UserPermissionsTable(BaseTable):
	user = tables.LinkColumn('userDetails', kwargs={ 'pk' : A('user.id') }, attrs=button_attrs)
	
	class Meta:
		model = UserPermissions
		fields = ('user', 'is_admin', 'is_user_manager', 'is_add_allowed', 'is_edit_allowed', 'is_session_controller', 'is_inventory')

class InventoryOrderTable(BaseTable):
	details = tables.LinkColumn('inventoryOrderReports', kwargs={ 'pk' : A('pk') }, orderable=False, text='Szczegoly', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = InventoryOrder
		fields = ('completed', 'date_ordered', 'date_completed', 'details')

class InventoryRoomReportTable(BaseTable):
	details = tables.LinkColumn('inventoryReportDetails', kwargs={ 'pk' : A('pk') }, orderable=False, text='Szczegoly', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = InventoryRoomReport
		fields = ('room', 'date_posted', 'author', 'details')

class InventoryEntryNoteTable(BaseTable):
	entry = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('entry.getURL') }, attrs=button_attrs)
	
	class Meta:
		model = InventoryEntryNote
		fields = ('entry', 'status')
