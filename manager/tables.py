import django_tables2 as tables
from django_tables2.utils import A
from manager.models import *
from manager.util import URLify_entry_signing

button_attrs = { 'a' :  { 'class' : 'btn btn-default btn-block' }}
table_attrs = { 'class' : 'table table-bordered table-condensed' }

class AddressTable(tables.Table):
	details = tables.LinkColumn('addressDetails', kwargs={ 'pk' : A('pk') }, orderable=False, text='Szczegoly', empty_values=(), attrs=button_attrs)
	edit = tables.LinkColumn('editAddress', kwargs={ 'pk' : A('pk') }, orderable=False, text='Edytuj', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = Address
		fields = ('city', 'street', 'street_number', 'details', 'edit')
		attrs = table_attrs
		
class AddressTableNoEdit(AddressTable):
	class Meta:
		exclude = ('edit',)
		attrs = table_attrs

class EntryTable(tables.Table):
	signing = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('getURL') }, attrs=button_attrs)
	room = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('room.id') }, attrs=button_attrs)
	
	class Meta:
		model = Entry
		fields = ('signing', 'name', 'date_added', 'added_value', 'date_removed', 'removed_value', 'room', 'short_description', 'last_modified')
		attrs = table_attrs

class LogEntryTable(tables.Table):
	old_location = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('old_location.id') }, attrs=button_attrs)
	new_location = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('new_location.id') }, attrs=button_attrs)
	
	class Meta:
		model = LogEntry
		fields = ('entry', 'log_date', 'old_location', 'new_location', 'notes', 'user')
		attrs = table_attrs

class RoomTable(tables.Table):
	room_id = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('pk') }, attrs=button_attrs)
	edit = tables.LinkColumn('editRoom', kwargs={ 'pk' : A('pk') }, orderable=False, text='Edytuj', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = Room
		fields = ('room_id', 'address', 'edit')
		attrs = table_attrs

class RoomTableNoEdit(RoomTable):
	class Meta:
		exclude = ('edit',)
		attrs = table_attrs

class UserPermissionsTable(tables.Table):
	user = tables.LinkColumn('userDetails', kwargs={ 'pk' : A('user.id') }, attrs=button_attrs)
	
	class Meta:
		model = UserPermissions
		fields = ('user', 'is_admin', 'is_user_manager', 'is_add_allowed', 'is_edit_allowed', 'is_session_controller', 'is_inventory')
		attrs = table_attrs

class InventoryOrderTable(tables.Table):
	details = tables.LinkColumn('inventoryOrderReports', kwargs={ 'pk' : A('pk') }, orderable=False, text='Szczegoly', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = InventoryOrder
		fields = ('completed', 'date_ordered', 'date_completed', 'details')
		attrs = table_attrs

class InventoryRoomReportTable(tables.Table):
	details = tables.LinkColumn('inventoryReportDetails', kwargs={ 'pk' : A('pk') }, orderable=False, text='Szczegoly', empty_values=(), attrs=button_attrs)
	
	class Meta:
		model = InventoryRoomReport
		fields = ('room', 'date_posted', 'author', 'details')
		attrs = table_attrs

class InventoryEntryNoteTable(tables.Table):
	entry = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('entry.getURL') }, attrs=button_attrs)
	
	class Meta:
		model = InventoryEntryNote
		fields = ('entry', 'status')
		attrs = table_attrs

class LiquidationEntryNoteTable(tables.Table):
	entry = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('entry.getURL') }, attrs=button_attrs)
	name = tables.Column(accessor=A('entry.name'))
	edit = tables.LinkColumn('liquidationNoteEdit', kwargs={ 'pk' : A('pk') }, attrs=button_attrs, orderable=False, verbose_name='Edytuj')
	remove = tables.LinkColumn('liquidationNoteRemove', kwargs={ 'pk' : A('pk') }, attrs=button_attrs, orderable=False, verbose_name='Usun')
	
	class Meta:
		model = LiquidationEntryNote
		fields = ('entry', 'name', 'note', 'edit', 'remove')
		attrs = table_attrs

class LiquidationEntryNoteTableNoInteraction(tables.Table):
	class Meta:
		exclude = ('edit', 'remove')
		attrs = table_attrs
