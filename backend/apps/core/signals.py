"""Borra del disco los archivos reemplazados o de registros eliminados."""
from django.apps import apps
from django.db import models
from django.db.models.signals import post_delete, pre_save

LOCAL_APP_PREFIX = "apps."


def _file_fields(model):
    return [field for field in model._meta.get_fields() if isinstance(field, models.FileField)]


def delete_files_on_delete(sender, instance, **kwargs):
    for field in _file_fields(sender):
        stored_file = getattr(instance, field.name)
        if stored_file:
            stored_file.delete(save=False)


def delete_replaced_files(sender, instance, **kwargs):
    if not instance.pk:
        return
    previous = sender.objects.filter(pk=instance.pk).first()
    if previous is None:
        return
    for field in _file_fields(sender):
        old_file = getattr(previous, field.name)
        new_file = getattr(instance, field.name)
        if old_file and old_file.name != (new_file.name if new_file else None):
            old_file.delete(save=False)


def connect_file_cleanup():
    for model in apps.get_models():
        if not model.__module__.startswith(LOCAL_APP_PREFIX) or not _file_fields(model):
            continue
        post_delete.connect(delete_files_on_delete, sender=model, dispatch_uid=f"file_delete_{model._meta.label}")
        pre_save.connect(delete_replaced_files, sender=model, dispatch_uid=f"file_replace_{model._meta.label}")
