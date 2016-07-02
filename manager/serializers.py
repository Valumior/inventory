from rest_framework import serializers
from manager.models import *

class AddressSerializer(serializers.ModelSerializer):
	class Meta:
		model = Address
		fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
	address = AddressSerializer(many=False, read_only=True)
	
	class Meta:
		model = Room
		fields = '__all__'
		
class EntrySerializer(serializers.ModelSerializer):
	class Meta:
		model = Entry
		fields = ('signing', 'name', 'description', 'room')
		depth = 2
		
class EntrySerializerShallow(serializers.ModelSerializer):
	class Meta:
		model = Entry
		fields = ('signing', 'name', 'description', 'room')

class UserPermissionsSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserPermissions
		exclude = ('user')

class InventoryOrderSerializer(serializers.ModelSerializer):
	class Meta:
		model = InventoryOrder
		exclude = ('date_completed')

class InventoryEntryNoteSerializer(serializers.ModelSerializer):
	class Meta:
		model = InventoryEntryNote
		fields = ('entry', 'status')

class InventoryRoomReportSerializer(serializers.ModelSerializer):
	entries = InventoryEntryNoteSerializer(many=True)
	
	class Meta:
		model = InventoryRoomReport
		fields = ('room', 'entries', 'order')
	
	def create(self, validated_data):
		entries_data = validated_data.pop('entries')
		inventoryRoomReport = InventoryRoomReport.objects.create(**validated_data)
		for entry_data in entries_data:
			InventoryEntryNote.objects.create(report=inventoryRoomReport, **entry_data)
		return inventoryRoomReport
