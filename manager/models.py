from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import string, random

class UserPermissions(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
	is_admin = models.BooleanField(default=False)
	is_session_controller = models.BooleanField(default=False)
	is_edit_allowed = models.BooleanField(default=False)
	is_add_allowed = models.BooleanField(default=False)
	is_user_manager = models.BooleanField(default=False)
	is_inventory = models.BooleanField(default=False)
	
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

class Institution(models.model):
	name_tag = models.CharField(max_length=20)
	
	def __unicode__(self):
		return u'%s' % (self.name_tag)

class EntryGroup(models.model):
	group_number = models.CharField(max_length=10)
	group_count = models.PositiveIntegerField(default=0)
	
	def __unicode__(self):
		return u'%s' % (self.group_number)

class Entry(models.Model):
	institution = models.ForeignKey(Institution, null=False)
	group = models.ForeignKey(EntryGroup, null=False)
	inventory_number = models.PositiveIntegerField()
	name = models.CharField(max_length=100, blank=False)
	date_added = models.DateTimeField()
	added_description = models.TextField(max_length=250, blank=True)
	date_removed = models.DateTimeField(null=True, blank=True)
	removed_description = models.TextField(max_length=250, null=True, blank=True)
	room = models.ForeignKey(Room, null=True)
	description = models.TextField(max_length=500, null=True, blank=True)
	signing = models.CharField(max_length=50)
	last_modified = models.DateTimeField(auto_now=True)
		
	def __unicode__(self):
		return u'%s' % (self.signing)
		
	def save(self, *args, **kwargs):
		
		if not self.inventory_number:
			self.group.group_count = self.group.group_count + 1
			self.group.save()
			self.inventory_number = self.group.group_count
		
		if not self.signing:
			sign_sections = []
			sign_sections.extend(self.institution.name_tag)
			sign_sections.extend(', ')
			sign_sections.extend(self.group.group_number)
			sign_sections.extend('/')
			sign_sections.extend(str(self.inventory_number))
			
			sign = ''.join(sign_sections)
		
		super(Entry, self).save(*args, **kwargs)

class LogEntry(models.Model):
	entry = models.ForeignKey(Entry, blank=False)
	log_date = models.DateTimeField(auto_now_add=True)
	old_location = models.ForeignKey(Room, blank=False, related_name='old_location')
	new_location = models.ForeignKey(Room, blank=False, related_name='new_location')
	user = models.ForeignKey(User, blank=False, related_name='change_author')
