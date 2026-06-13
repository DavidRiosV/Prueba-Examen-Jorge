from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Usuario, Intervencion, Tratamiento, Animal


class RegistroVeterinarioForm(UserCreationForm):
    numero_colegiado = forms.CharField(max_length=50)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'numero_colegiado', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'veterinario'
        user.numero_colegiado = self.cleaned_data['numero_colegiado']
        if commit:
            user.save()
            grupo = Group.objects.get(name='Veterinarios')
            user.groups.add(grupo)
        return user


class RegistroDuenoForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'dueno'
        if commit:
            user.save()
            grupo = Group.objects.get(name='Duenos')
            user.groups.add(grupo)
        return user


class IntervencionForm(forms.ModelForm):
    class Meta:
        model = Intervencion
        fields = ['nombre', 'descripcion', 'tratamiento', 'animales',
                  'nivel_riesgo', 'fecha_programada', 'fecha_fin_recuperacion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tratamiento'].queryset = Tratamiento.objects.filter(
            apto_para_intervenciones=True
        )
        hace_seis_meses = date.today() - relativedelta(months=6)
        self.fields['animales'].queryset = Animal.objects.filter(
            fecha_nacimiento__lte=hace_seis_meses
        )

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        qs = Intervencion.objects.filter(nombre=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una intervención con ese nombre.')
        return nombre

    def clean_descripcion(self):
        desc = self.cleaned_data['descripcion']
        if len(desc) < 100:
            raise forms.ValidationError('La descripción debe tener mínimo 100 caracteres.')
        return desc

    def clean_nivel_riesgo(self):
        nivel = self.cleaned_data['nivel_riesgo']
        if not (0 <= nivel <= 10):
            raise forms.ValidationError('El nivel de riesgo debe estar entre 0 y 10.')
        return nivel

    def clean(self):
        cleaned = super().clean()
        fp = cleaned.get('fecha_programada')
        fr = cleaned.get('fecha_fin_recuperacion')
        hoy = date.today()

        if fp and fr:
            if fp >= fr:
                self.add_error('fecha_programada',
                    'La fecha programada debe ser anterior a la de fin de recuperación.')
            if fr < hoy:
                self.add_error('fecha_fin_recuperacion',
                    'La fecha de fin de recuperación no puede ser en el pasado.')
        return cleaned
    
class BusquedaForm(forms.Form):
        texto = forms.CharField(required=False, label='Texto en nombre o descripción')
        fecha_desde = forms.DateField(required=False,
            widget=forms.DateInput(attrs={'type': 'date'}))
        fecha_hasta = forms.DateField(required=False,
            widget=forms.DateInput(attrs={'type': 'date'}))
        nivel_min = forms.IntegerField(required=False, label='Nivel de riesgo mínimo')
        animales = forms.ModelMultipleChoiceField(
                queryset=Animal.objects.all(), required=False)
        solo_pendientes = forms.BooleanField(required=False, label='Solo pendientes')