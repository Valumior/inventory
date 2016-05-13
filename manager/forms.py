from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from manager.models import Address, Room, QrImage, Entry

class AddresForm(ModelForm):
	class Meta:
		model = Address
		fields = '__all__'

class RoomForm(ModelForm):
	class Meta:
		model = Room
		fields = '__all__'

class EntryForm(ModelForm):
	class Meta:
		model = Entry
		fields = ('name', 'description', 'room')

class UserForm(ModelForm):
	password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput())
	
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password2')
		widgets = {
				'password'	: forms.PasswordInput(),
		}
	"""	
	def clean_email(self):
		mail = self.cleaned_data['email']
		if User.objects.filter(email=mail).exists():
			raise ValidationError('Email already registered')
		return mail
	"""	
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
