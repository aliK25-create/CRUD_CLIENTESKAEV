from django import forms
from .models import Cliente
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre','apellidos', 'telefono', 'fecha_nac', 'foto']

        foto = forms.ImageField(required=False)
        
class RegistroForm(UserCreationForm):
    email= forms.EmailField(required=True)
    class Meta:
        model= User
        fields=["username", "email", "password1","password2"]

        
       
