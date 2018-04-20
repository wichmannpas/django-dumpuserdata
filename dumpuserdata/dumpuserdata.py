from collections import defaultdict
from typing import Tuple

from django.apps import apps
from django.db import models


def dump_data(obj) -> dict:
    """Dump all data that is associated to obj. """
    data = defaultdict(list)

    added = set()
    processed = set()
    new = set()
    new.add(obj)

    while new:
        current = new.pop()
        processed.add(current)
        added.add(current)
        data['.'.join((
            current._meta.model.__module__,
            current._meta.model.__name__
        ))].append(current)


        related, reverse_related = related_objects(current)
        # TODO: it can probably not generically be determined whether
        # transitive relations should be followed, some kind of
        # model/field annotations are required for this.
        for obj in related:
            """
            we want to add related objects, but not
            transitive relations.
            """
            if obj not in added:
                data['.'.join((
                    obj._meta.model.__module__,
                    obj._meta.model.__name__
                ))].append(obj)
                added.add(obj)
        for obj in reverse_related:
            """
            we want to follow reverse related objects
            transitively (i.e., following the directed edges)
            """
            if obj in processed:
                continue
            new.add(obj)

    return dict(data)


def related_objects(obj) -> Tuple[set, set]:
    """
    Get two sets containing

    * all objects that are directly (i.e., without
        transitivity) referenced by obj
    * all objects that directly (i.e., without transitivity)
        reference obj
    """
    related = set()
    reverse_related = set()

    obj_model = obj._meta.model

    for field in obj_model._meta.fields:
        if not isinstance(field, models.fields.related.RelatedField):
            continue

        # TODO: this probably results in undesired behaviour for ManyToMany fields
        related.add(getattr(obj, field.name))

    for model in apps.get_models():
        for field in model._meta.fields:
            if not isinstance(field, models.fields.related.RelatedField):
                continue

            model = field.model

            target_field = field.target_field
            target_model = target_field.model

            if obj_model != target_model:
                continue

            reverse_related |= set(
                model.objects.filter(**{
                    field.name: obj,
                }))

    return related, reverse_related
