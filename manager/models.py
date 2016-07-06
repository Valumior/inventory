from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from manager.util import URLify_entry_signing

import string, random

class UserPermissions(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
	is_admin = models.BooleanField(default=False, verbose_name='Administrator')
	is_session_controller = models.BooleanField(default=False, verbose_name='Kontroler sesji')
	is_edit_allowed = models.BooleanField(default=False, verbose_name='Edycja wpisow')
	is_add_allowed = models.BooleanField(default=False, verbose_name='Dodawanie wpisow')
	is_user_manager = models.BooleanField(default=False, verbose_name='Zarzadzanie uzytkownikami')
	is_inventory = models.BooleanField(default=False, verbose_name='Inwentaryzacja')
	
class Address(models.Model):
	city = models.CharField(max_length=100, blank=False, verbose_name='Miasto')
	street = models.CharField(max_length=200, blank=False, verbose_name='Ulica')
	street_number = models.CharField(max_length=20, blank=False, verbose_name='Numer')
	
	def __unicode__(self):
		return u'%s %s %s' % (self.city, self.street, self.street_number)
	
class Room(models.Model):
	room_id = models.CharField(max_length=20, blank=False, verbose_name='Identyfikator pokoju')
	address = models.ForeignKey(Address, blank=False, verbose_name='Adres')

	def __unicode__(self):
		return u'%s, %s' % (self.address, self.room_id)

class Institution(models.Model):
	name_tag = models.CharField(max_length=20, unique=True)
	
	def __unicode__(self):
		return u'%s' % (self.name_tag)

class EntryGroup(models.Model):
	group_number = models.CharField(max_length=10, unique=True)
	group_count = models.PositiveIntegerField(default=0)
	
	def __unicode__(self):
		return u'%s' % (self.group_number)

class Entry(models.Model):
	signing = models.CharField(max_length=50, unique=True, primary_key=True, verbose_name='Oznakowanie')
	institution = models.ForeignKey(Institution, null=False)
	group = models.ForeignKey(EntryGroup, null=False)
	inventory_number = models.PositiveIntegerField()
	name = models.CharField(max_length=100, blank=False, verbose_name='Nazwa')
	date_added = models.DateTimeField(verbose_name='Data dodania')
	added_description = models.TextField(max_length=250, blank=True)
	date_removed = models.DateTimeField(null=True, blank=True, verbose_name='Data likwidacji')
	removed_description = models.TextField(max_length=250, null=True, blank=True)
	room = models.ForeignKey(Room, null=True, verbose_name='Pomieszczenie')
	short_description = models.TextField(max_length=150, null=True, blank=True, verbose_name='Krotki opis')
	description = models.TextField(max_length=500, null=True, blank=True)
	last_modified = models.DateTimeField(auto_now=True, verbose_name='Ostatnia modyfikacja')
	caretaker = models.ForeignKey(User, null=True, blank=True, verbose_name='Opiekun')
		
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
			self.signing = sign
		
		super(Entry, self).save(*args, **kwargs)
		
	def getURL(self):
		return URLify_entry_signing(self.signing)

class LogEntry(models.Model):
	entry = models.ForeignKey(Entry, blank=False)
	log_date = models.DateTimeField(auto_now_add=True)
	old_location = models.ForeignKey(Room, blank=False, related_name='old_location')
	new_location = models.ForeignKey(Room, blank=False, related_name='new_location')
	user = models.ForeignKey(User, blank=False, related_name='change_author')

class InventoryOrder(models.Model):
	date_ordered = models.DateTimeField(auto_now_add=True)
	completed = models.BooleanField(default=False)
	date_completed = models.DateTimeField(null=True, blank=True)
	
class InventoryRoomReport(models.Model):
	room = models.ForeignKey(Room, verbose_name='Pomieszczenie')
	date_posted = models.DateTimeField(auto_now_add=True, verbose_name='Data')
	entries = models.ManyToManyField(Entry, through='InventoryEntryNote')
	author = models.ForeignKey(User, null=True, blank=True, verbose_name='Autor')
	order = models.ForeignKey(InventoryOrder)
	
class InventoryEntryNote(models.Model):
	MISSING = 'M'
	PRESENT = 'P'
	EXTRA = 'E'
	STATUS_CHOICES = (
		(MISSING, 'Brak'),
		(PRESENT, 'Obecny'),
		(EXTRA, 'Dodatkowy'),
	)
	
	entry = models.ForeignKey(Entry, verbose_name='Przedmiot')
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name='Status')
	report = models.ForeignKey(InventoryRoomReport)
