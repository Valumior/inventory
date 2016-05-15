from rest_framework import serializers
from manager.models import Address, Room, Entry

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
		fields = ('id_number', 'name', 'description', 'room')
		depth = 2
