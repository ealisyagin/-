from .models import Unit
from django.forms import ModelForm, TextInput

class UnitForm(ModelForm):
	class Meta:
		model = Unit
		fields = ['user_id']
		
		widgets = {
			"user_id": TextInput(attrs={
				'class': 'form-control',
				'placeholder': 'user_id'
			}),		
		}
