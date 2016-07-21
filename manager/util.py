import string
from manager.models import *

def URLify_entry_signing(signing):
	return string.replace(string.replace(signing,'/','__'),' ','_')
	
def deURLify_entry_signing(signing):
	return string.replace(string.replace(signing,'__','/'),'_',' ')
	
def logEntryChange(old_entry, new_entry, user):
	change = False
	changelog = ''
	room = None
	if new_entry.name != old_entry.name:
		change = True
		changelog = changelog + 'Zmiana nazwy\n'
	if new_entry.short_description != old_entry.short_description:
		change = True
		changelog = changelog + 'Zmiana zmiana krotkiego opisu\n'
	if new_entry.description != old_entry.description:
		change = True
		changelog = changelog + 'Zmiana opisu\n'
	if new_entry.room != old_entry.room:
		change = True
		changelog = changelog + 'Zmiana pokoju\n'
		room = new_entry.room
	if new_entry.caretaker != old_entry.caretaker:
		change = True
		changelog = changelog + 'Zmiana opiekuna\n'
	if change:
		return LogEntry(entry=old_entry, old_location=old_entry.room, new_location=room, user=user, notes=changelog)
	return None
