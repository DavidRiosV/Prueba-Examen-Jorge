from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .forms import RegistroVeterinarioForm, RegistroDuenoForm, IntervencionForm, BusquedaForm
from .models import Intervencion, Animal


def home(request):
    return render(request, 'examen/home.html')


def registro_veterinario(request):
    form = RegistroVeterinarioForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'examen/registro_vet.html', {'form': form})


def registro_dueno(request):
    form = RegistroDuenoForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'examen/registro_dueno.html', {'form': form})


def mi_logout(request):
    logout(request)
    return redirect('login')


@login_required
@permission_required('examen.add_intervencion', raise_exception=True)
def crear_intervencion(request):
    form = IntervencionForm(request.POST or None)
    if request.method == 'POST':
        print('POST recibido')
        print('form valid:', form.is_valid())
        print('errores:', form.errors)
    if form.is_valid():
        intervencion = form.save(commit=False)
        intervencion.veterinario_responsable = request.user
        intervencion.save()
        form.save_m2m()
        return redirect('listar_intervenciones')
    return render(request, 'examen/crear_intervencion.html', {'form': form})


@login_required
def listar_intervenciones(request):
    if request.user.rol == 'veterinario':
        intervenciones = Intervencion.objects.filter(
            veterinario_responsable=request.user
        )
    else:
        intervenciones = Intervencion.objects.filter(
            animales__dueno=request.user
        ).distinct()
    return render(request, 'examen/listar.html', {'intervenciones': intervenciones})


@login_required
def editar_intervencion(request, pk):
    intervencion = get_object_or_404(Intervencion, pk=pk)
    if intervencion.veterinario_responsable != request.user:
        return redirect('listar_intervenciones')
    form = IntervencionForm(request.POST or None, instance=intervencion)
    if form.is_valid():
        form.save()
        return redirect('listar_intervenciones')
    return render(request, 'examen/editar_intervencion.html', {'form': form})


@login_required
def eliminar_intervencion(request, pk):
    intervencion = get_object_or_404(Intervencion, pk=pk)
    if intervencion.veterinario_responsable != request.user:
        return redirect('listar_intervenciones')
    if request.method == 'POST':
        intervencion.delete()
        return redirect('listar_intervenciones')
    return render(request, 'examen/confirmar_eliminar.html', {'obj': intervencion})


@login_required
def mis_animales(request):
    animales = Animal.objects.filter(dueno=request.user)
    return render(request, 'examen/mis_animales.html', {'animales': animales})


@login_required
def buscar(request):
    form = BusquedaForm(request.GET or None)

    if request.user.rol == 'veterinario':
        qs = Intervencion.objects.filter(veterinario_responsable=request.user)
    else:
        qs = Intervencion.objects.filter(animales__dueno=request.user).distinct()

    if form.is_valid():
        d = form.cleaned_data

        if d['texto']:
            qs = qs.filter(
                Q(nombre__icontains=d['texto']) |
                Q(descripcion__icontains=d['texto'])
            )
        if d['fecha_desde']:
            qs = qs.filter(fecha_programada__gte=d['fecha_desde'])
        if d['fecha_hasta']:
            qs = qs.filter(fecha_programada__lte=d['fecha_hasta'])
        if d['nivel_min'] is not None:
            qs = qs.filter(nivel_riesgo__gt=d['nivel_min'])
        if d['animales']:
            qs = qs.filter(animales__in=d['animales']).distinct()
        if d['solo_pendientes']:
            qs = qs.filter(completada=False)

    return render(request, 'examen/buscar.html', {'form': form, 'resultados': qs})