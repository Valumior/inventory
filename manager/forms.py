from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from manager.models import *

class BootstrapModelFormBase(ModelForm):
	def __init__(self, *args, **kwargs):
		form = super(BootstrapModelFormBase, self):__init__(*args, **kwargs)
		for visible in form.visible_fields():
			visible.field.widget.attrs['class'] = 'form-control'

class UserPermissionsForm(BootstrapModelFormBase):
	class Meta:
		model = UserPermissions
		exclude = ('user',)

class UserPermissionsFormNoAdmin(BootstrapModelFormBase):
	class Meta:
		model = UserPermissions
		exclude = ('user', 'is_admin', 'is_user_manager')

class UserSettingsForm(BootstrapModelFormBase):
	class Meta:
		model = UserSettings
		exclude = ('user',)

class AddresForm(BootstrapModelFormBase):
	class Meta:
		model = Address
		fields = '__all__'

class RoomForm(BootstrapModelFormBase):
	class Meta:
		model = Room
		fields = '__all__'

class InstitutionForm(BootstrapModelFormBase):
	class Meta:
		model = Institution
		fields = '__all__'

class EntryGroupForm(BootstrapModelFormBase):
	class Meta:
		model = EntryGroup
		fields = ('group_number', 'description')

class EntryForm(BootstrapModelFormBase):
	class Meta:
		model = Entry
		fields = ('institution', 'grouping_type', 'group', 'kst', 'date_added', 'added_description', 'added_value', 'name', 'short_description', 'description', 'room', 'caretaker')

	def clean_group(self):
		data = self.cleaned_data
		if data['grouping_type'] == 'KST':
			data['group'] = None
		elif data['grouping_type'] == 'GRP':
			if data['group'] is None:
				raise ValidationError('Brak grupy')
		return data['group']

class EntryEditForm(BootstrapModelFormBase):
	class Meta:
		model = Entry
		fields = ('name', 'short_description', 'description', 'room', 'caretaker')

class EntryFormSimple(BootstrapModelFormBase):
	class Meta:
		model = Entry
		fields = ('room', 'short_description','description')

class LiquidationForm(BootstrapModelFormBase):
	class Meta:
		model = Liquidation
		fields = ('document_type', 'document_title')

class UserForm(BootstrapModelFormBase):
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput())
	
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password2')
		widgets = {
				'password'	: forms.PasswordInput(),
		}
	
	def clean(self):
		data = self.cleaned_data
		if data['password'] != data['password2']:
			self._errors['password'] = ['Passwords do not match']
			del data['password']
			del data['password2']
		return data

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', widget=forms.PasswordInput())
	
class SearchForm(forms.Form):
	search = forms.CharField(label='Search')
