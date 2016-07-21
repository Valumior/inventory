import string

def URLify_entry_signing(signing):
	return string.replace(string.replace(signing,'/','__'),' ','_')
	
def deURLify_entry_signing(signing):
	return string.replace(string.replace(signing,'__','/'),'_',' ')

