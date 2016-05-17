from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import string, random
	
class Address(models.Model):
	city = models.CharField(max_length=100, blank=False)
	street = models.CharField(max_length=200, blank=False)
	street_number = models.CharField(max_length=20, blank=False)
	
	def __unicode__(self):
		return u'%s %s %s' % (self.city, self.street, self.street_number)
	
class Room(models.Model):
	room_id = models.CharField(max_length=20, blank=False)
	address = models.ForeignKey(Address, blank=False)

	def __unicode__(self):
		return u'%s, %s' % (self.address, self.room_id)

class Entry(models.Model):
	id_number = models.CharField(max_length=30, primary_key=True)
	date_added = models.DateTimeField(auto_now_add=True)
	last_modified = models.DateTimeField(auto_now=True)
	name = models.CharField(max_length=50, blank=False)
	description = models.TextField(max_length=500, null=True)
	room = models.ForeignKey(Room, null=True)

	def __unicode__(self):
		return u'%s' % (self.id_number)
		
	def save(self, *args, **kwargs):
		while not self.id_number:
			ret = []
			ret.extend('ITEM-')
			ret.extend(random.sample(string.letters, 2))
			ret.extend(random.sample(string.digits, 2))
			ret.extend(random.sample(string.letters, 2))
			ret.extend(random.sample(string.digits, 2))
			
			newid = ''.join(ret)
			
			if Entry.objects.filter(pk=newid).count() == 0:
				self.id_number = newid
		
		super(Entry, self).save(*args, **kwargs)

class LogEntry(models.Model):
	entry = models.ForeignKey(Entry, blank=False)
	log_date = models.DateTimeField(auto_now_add=True)
	old_location = models.ForeignKey(Room, blank=False, related_name='old_location')
	new_location = models.ForeignKey(Room, blank=False, related_name='new_location')
	user = models.ForeignKey(User, blank=False, related_name='change_author')
