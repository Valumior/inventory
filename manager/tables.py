import django_tables2 as tables
from django_tables2.utils import A
from manager.models import *
from manager.util import URLify_entry_signing

class EntryTable(tables.Table):
	signing = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('getURL') })
	
	class Meta:
		model = Entry
		fields = ('signing', 'name', 'date_added', 'date_removed', 'room', 'short_description', 'last_modified')

class RoomTable(tables.Table):
	room_id = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('pk') })
	
	class Meta:
		model = Room
		fields = ('room_id', 'address')

class UserPermissionsTable(tables.Table):
	user = tables.LinkColumn('userDetails', kwargs={ 'pk' : A('user.id') })
	
	class Meta:
		model = UserPermissions
		fields = ('user', 'is_admin', 'is_user_manager', 'is_add_allowed', 'is_edit_allowed', 'is_session_controller', 'is_inventory')

class InventoryOrderTable(tables.Table):
	details = tables.LinkColumn('inventoryOrderReports', kwargs={ 'pk' : A('pk') }, orderable=False, empty_values=())
	
	class Meta:
		model = InventoryOrder
		fields = ('completed', 'date_ordered', 'date_completed', 'details')
	
	def render_edit(self):
		return 'Szczegoly'

class InventoryRoomReportTable(tables.Table):
	details = tables.LinkColumn('inventoryReportDetails', kwargs={ 'pk' : A('pk') }, orderable=False, empty_values=())
	
	class Meta:
		model = InventoryRoomReport
		fields = ('room', 'date_posted', 'author', 'details')
	
	def render_edit(self):
		return 'Szczegoly'

class InventoryEntryNoteTable(tables.Table):
	entry = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('entry.getURL') })
	
	class Meta:
		model = InventoryEntryNote
		fields = ('entry', 'status')
