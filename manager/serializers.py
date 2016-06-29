from rest_framework import serializers
from manager.models import Address, Room, Entry, UserPermissions

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
	
