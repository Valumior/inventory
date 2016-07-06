import django_tables2 as tables
from django_tables2.utils import A
from manager.models import *
from manager.util import URLify_entry_signing

class AddressTable(tables.Table):
	details = tables.LinkColumn('addressDetails', kwargs={ 'pk' : A('pk') }, orderable=False, empty_values=(), attrs = { 'class' : 'btn btn-default' })
	edit = tables.LinkColumn('editAddress', kwargs={ 'pk' : A('pk') }, orderable=False, empty_values=(), attrs = { 'class' : 'btn btn-default' })
	
	class Meta:
		model = Address
		fields = ('city', 'street', 'street_number', 'details', 'edit')
		attrs = { 'class' : 'table table-bordered table-condensed' }
		
	def render_details(self):
		return 'Szczegoly'
		
	def render_edit(self):
		return 'Edytuj'

class AddressTableNoEdit(AddressTable):
	class Meta:
		exclude = ('edit',)

class EntryTable(tables.Table):
	signing = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('getURL') }, attrs = { 'class' : 'btn btn-default' })
	room = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('room.id') }, attrs = { 'class' : 'btn btn-default' })
	
	class Meta:
		model = Entry
		fields = ('signing', 'name', 'date_added', 'date_removed', 'room', 'short_description', 'last_modified')
		attrs = { 'class' : 'table table-bordered table-condensed' }

class RoomTable(tables.Table):
	room_id = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('pk') }, attrs = { 'class' : 'btn btn-default' })
	edit = tables.LinkColumn('editRoom', kwargs={ 'pk' : A('pk') }, orderable=False, empty_values=(), attrs = { 'class' : 'btn btn-default' })
	
	class Meta:
		model = Room
		fields = ('room_id', 'address', 'edit')
		attrs = { 'class' : 'table table-bordered table-condensed' }
		
	def render_edit(self):
		return 'Edytuj'

class RoomTableNoEdit(RoomTable):
	class Meta:
		exclude = ('edit',)

class UserPermissionsTable(tables.Table):
	user = tables.LinkColumn('userDetails', kwargs={ 'pk' : A('user.id') }, attrs = { 'class' : 'btn btn-default' })
	
	class Meta:
		model = UserPermissions
		fields = ('user', 'is_admin', 'is_user_manager', 'is_add_allowed', 'is_edit_allowed', 'is_session_controller', 'is_inventory')
		attrs = { 'class' : 'table table-bordered table-condensed' }

class InventoryOrderTable(tables.Table):
	details = tables.LinkColumn('inventoryOrderReports', kwargs={ 'pk' : A('pk') }, orderable=False, empty_values=(), attrs = { 'class' : 'btn btn-default' })
	
	class Meta:
		model = InventoryOrder
		fields = ('completed', 'date_ordered', 'date_completed', 'details')
		attrs = { 'class' : 'table table-bordered table-condensed' }
	
	def render_details(self):
		return 'Szczegoly'

class InventoryRoomReportTable(tables.Table):
	details = tables.LinkColumn('inventoryReportDetails', kwargs={ 'pk' : A('pk') }, orderable=False, empty_values=(), attrs = { 'class' : 'btn btn-default' })
	
	class Meta:
		model = InventoryRoomReport
		fields = ('room', 'date_posted', 'author', 'details')
		attrs = { 'class' : 'table table-bordered table-condensed' }
	
	def render_details(self):
		return 'Szczegoly'

class InventoryEntryNoteTable(tables.Table):
	entry = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('entry.getURL') }, attrs = { 'class' : 'btn btn-default' })
	
	class Meta:
		model = InventoryEntryNote
		fields = ('entry', 'status')
		attrs = { 'class' : 'table table-bordered table-condensed' }
