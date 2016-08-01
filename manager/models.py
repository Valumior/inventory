from __future__ import unicode_literals

from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from manager.util import URLify_entry_signing

import string, random

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
	name_tag = models.CharField(max_length=20, unique=True, verbose_name='Identyfikator instytucji')
	
	def __unicode__(self):
		return u'%s' % (self.name_tag)

class EntryGroup(models.Model):
	group_number = models.CharField(max_length=10, unique=True, verbose_name='Identyfikator grupy')
	group_count = models.PositiveIntegerField(default=0)
	description = models.TextField(max_length=500, null=True, blank=True, verbose_name='Opis')
	
	def __unicode__(self):
		return u'%s' % (self.group_number)

class Entry(models.Model):
	GROUP = 'GRP'
	KST = 'KST'
	GROUP_TYPES = (
		(GROUP, 'Grupy'),
		(KST, 'Klasyfikacja Srodkow Trwalych')
	)
	
	signing = models.CharField(max_length=50, unique=True, primary_key=True, verbose_name='Oznakowanie')
	institution = models.ForeignKey(Institution, null=False, verbose_name='Instytucja')
	grouping_type = models.CharField(max_length=3, choices=GROUP_TYPES, verbose_name='Typ grupowania',)
	group = models.ForeignKey(EntryGroup, null=True, verbose_name='Grupa', blank=True)
	kst = models.DecimalField(max_digits=3, decimal_places=0, verbose_name='KST')
	inventory_number = models.PositiveIntegerField()
	name = models.CharField(max_length=100, blank=False, verbose_name='Nazwa')
	date_added = models.DateTimeField(verbose_name='Data dodania')
	added_value = models.DecimalField(max_digits=10, decimal_places=2, blank=False, verbose_name='Wartosc poczatkowa')
	added_description = models.TextField(max_length=250, blank=True)
	date_removed = models.DateTimeField(null=True, blank=True, verbose_name='Data likwidacji')
	removed_description = models.TextField(max_length=250, null=True, blank=True)
	removed_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Wartosc likwidacji')
	room = models.ForeignKey(Room, null=True, verbose_name='Pomieszczenie')
	short_description = models.TextField(max_length=150, null=True, blank=True, verbose_name='Krotki opis')
	description = models.TextField(max_length=500, null=True, blank=True, verbose_name='Opis')
	last_modified = models.DateTimeField(auto_now=True, verbose_name='Ostatnia modyfikacja')
	caretaker = models.ForeignKey(User, null=True, blank=True, verbose_name='Opiekun')
		
	def __unicode__(self):
		return u'%s' % (self.signing)
		
	def save(self, *args, **kwargs):
		
		if not self.inventory_number:
			if self.grouping_type == self.GROUP:
				self.group.group_count = self.group.group_count + 1
				self.group.save()
				self.inventory_number = self.group.group_count
			elif self.grouping_type == self.KST:
				max_kst = Entry.objects.filter(grouping_type=self.KST).aggregate(Max('inventory_number'))['inventory_number__max']
				if not max_kst:
					max_kst = 0
				self.inventory_number = max_kst + 1
		
		if not self.signing:
			sign_sections = []
			sign_sections.extend(self.institution.name_tag)
			sign_sections.extend(', ')
			if self.grouping_type == self.GROUP:
				sign_sections.extend(self.group.group_number)
			elif self.grouping_type == self.KST:
				sign_sections.extend(str(self.kst))
			sign_sections.extend('/')
			sign_sections.extend(str(self.inventory_number))
			
			sign = ''.join(sign_sections)
			self.signing = sign
		
		super(Entry, self).save(*args, **kwargs)
		
	def getURL(self):
		return URLify_entry_signing(self.signing)
		
	def getDict(self):
		return { 'signing' : self.signing , 'name' : self.name , 'room' : self.room , 'short_description' : self.short_description , 'description' : self.description , 'caretaker' : self.caretaker }

class LogEntry(models.Model):
	entry = models.ForeignKey(Entry, blank=False, verbose_name='Wpis')
	log_date = models.DateTimeField(auto_now_add=True, verbose_name='Data')
	old_location = models.ForeignKey(Room, null=True, related_name='old_location', verbose_name='Stara lokalizacja')
	new_location = models.ForeignKey(Room, null=True, related_name='new_location', verbose_name='Nowa lokalizacja')
	notes = models.TextField(max_length=200, null=True, blank=True, verbose_name='Opis zmiany')
	user = models.ForeignKey(User, blank=False, related_name='change_author', verbose_name='Autor')

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

class Liquidation(models.Model):
	LIQUIDATION = 'LT'
	TRANSFERENCE = 'PT'
	TYPE_CHOICES = (
		(LIQUIDATION, 'Likwidacja'),
		(TRANSFERENCE, 'Przekazanie')
	)
	
	date_issued = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')
	submitted = models.BooleanField(default=False, verbose_name='Zlozone')
	completed = models.BooleanField(default=False, verbose_name='Wykonane')
	rejected = models.BooleanField(default=False, verbose_name='Odrzucone')
	date_closed = models.DateTimeField(null=True, verbose_name='Data zamkniecia')
	document_title = models.CharField(max_length=50, verbose_name='Tytul dokumentu')
	document_type = models.CharField(max_length=2, choices=TYPE_CHOICES, blank=False, default=LIQUIDATION, verbose_name='Typ Dokumentu')
	entries = models.ManyToManyField(Entry)

	def getMsg(self):
		if self.document_title:
			if self.document_type == LIQUIDATION:
				return 'Likwidacja na podstawie dokumentu ' + self.document_title
			elif self.document_type == TRANSFERENCE:
				return 'Przekazanie na podstawie dokumentu ' + self.document_title
		return ''
	
	def __unicode__(self):
		if self.document_title == '':
			return u'Wniosek %s' % (self.date_issued)
		else:
			return u'Wniosek %s' % (self.document_title)

class UserPermissions(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
	is_admin = models.BooleanField(default=False, verbose_name='Administrator')
	is_session_controller = models.BooleanField(default=False, verbose_name='Kontroler sesji inwentaryzayjnych')
	is_edit_allowed = models.BooleanField(default=False, verbose_name='Edycja wpisow')
	is_add_allowed = models.BooleanField(default=False, verbose_name='Dodawanie wpisow')
	is_user_manager = models.BooleanField(default=False, verbose_name='Zarzadzanie uzytkownikami')
	is_inventory = models.BooleanField(default=False, verbose_name='Inwentaryzacja')
	is_liquidation = models.BooleanField(default=False, verbose_name='Wnioskowanie likwidacji')
	is_liquidation_approver = models.BooleanField(default=False, verbose_name='Zatwierdzanie likwidacji')

class UserSettings(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False)
	default_institution = models.ForeignKey(Institution, null=True, on_delete=models.SET_NULL, blank=True)
	default_room = models.ForeignKey(Room, null=True, on_delete=models.SET_NULL, blank=True)
	default_group = models.ForeignKey(EntryGroup, null=True, on_delete=models.SET_NULL, blank=True)
	
	def getDefaultsDict(self):
		return { 'institution' : self.default_institution , 'group' : self.default_group , 'room' : self.default_room }
