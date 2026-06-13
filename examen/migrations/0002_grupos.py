from django.db import migrations

def crear_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    duenos, _ = Group.objects.get_or_create(name='Duenos')
    vets, _ = Group.objects.get_or_create(name='Veterinarios')

    for codename in ['add_intervencion', 'change_intervencion',
                     'delete_intervencion', 'view_intervencion']:
        try:
            perm = Permission.objects.get(codename=codename)
            vets.permissions.add(perm)
        except Permission.DoesNotExist:
            pass

    try:
        perm_ver = Permission.objects.get(codename='view_intervencion')
        duenos.permissions.add(perm_ver)
    except Permission.DoesNotExist:
        pass

class Migration(migrations.Migration):
    dependencies = [('examen', '0001_initial')]
    operations = [migrations.RunPython(crear_grupos)]