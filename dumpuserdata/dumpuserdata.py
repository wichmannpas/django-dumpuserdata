from collections import defaultdict

from django.apps import apps
from django.db import models


def dump_data(obj) -> dict:
    """Dump all data that is associated to obj. """
    data = defaultdict(list)

    processed = set()
    new = set()
    new.add(obj)

    while new:
        current = new.pop()
        processed.add(current)
        data['.'.join((
            current._meta.model.__module__,
            current._meta.model.__name__
        ))].append(current)


        for obj in related_objects(current):
            if obj in processed:
                continue
            new.add(obj)

    return dict(data)


def related_objects(obj) -> set:
    """
    Get all objects that directly (i.e., without transitivity) reference obj.
    """
    objects = set()

    obj_model = obj._meta.model

    for model in apps.get_models():
        for field in model._meta.fields:
            if not isinstance(field, models.fields.related.RelatedField):
                continue

            model = field.model

            target_field = field.target_field
            target_model = target_field.model

            if obj_model != target_model:
                continue

            objects |= set(
                model.objects.filter(**{
                    field.name: obj,
                }))

    return objects
