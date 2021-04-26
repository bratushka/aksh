from django import forms

from .models import Act, Document


class ActAdminForm(forms.ModelForm):
    class Meta:
        model = Act
        widgets = {
            'act_id': forms.TextInput,
            'title': forms.TextInput,
        }
        fields = '__all__'


class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        widgets = {
            'link': forms.TextInput,
            'title': forms.TextInput,
            'url': forms.TextInput,
        }
        fields = '__all__'
