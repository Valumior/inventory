import string

def URLify_entry_singing(signing):
	return string.replace(string.replace(signing,'/','-'),' ','_')
	
def deURLify_entry_signing(signing):
	return string.replace(string.replace(signing,'-','/'),'_',' ')
	
