import django_tables2 as tables
import django_tables2.utils import A
from manager.models import *

class EntryTable(tables.Table):
	signing = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('signing') })
	
	class Meta:
		model = Entry
		fields = ('signing', 'name', 'date_added', 'date_removed', 'room', 'short_description', 'last_modified')

class RoomTable(tables.Table):
	room_id = tables.LinkColumn('roomDetails', kwargs={ 'pk' : A('pk') })
	
	class Meta:
		model = Room
		fields = ('room_id', 'address')

class InventoryOrderTable(tables.Table):
	class Meta:
		model = InventoryOrder
		fields = '__all__'

class InventoryRoomReportTable(tables.Table):
	class Meta:
		model = InventoryRoomReport
		fields = ('room', 'date_posted')

class InventoryEntryNoteTable(table.Table):
	entry = tables.LinkColumn('entryDetails', kwargs={ 'pk' : A('entry.signing') })
	
	class Meta:
		model = InventoryEntryNote
		fields = ('entry', 'status')
