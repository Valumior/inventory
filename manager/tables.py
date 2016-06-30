import django_tables2 as tables
from manager.models import *

class EntryTable(tables.Table):
	class Meta:
		model = Entry

class RoomTable(tables.Table):
	class Meta:
		model = Room

class AddressTable(tables.Table):
	class Meta:
		model = Address
