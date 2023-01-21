from django.db import models
from django.db.models.fields import related
from django.core.exceptions import FieldDoesNotExist


class DeferredCommit(object):
    """Differentiates a non-direct related object that should be deferred
    during the commit phase.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '<DeferredCommit: "{0}">'.format(repr(self.value))


class Commits(object):
    "Stores pending direct and related commits relative to the reference."
    def __init__(self, reference):
        self.reference = reference
        self.direct = {}
        self.related = {}

    def defer(self, accessor, obj, direct=False):
        "Add object in the deferred queue for the given accessor."
        if direct:
            self.direct[accessor] = obj
        else:
            self.related[accessor] = obj

    def get(self, accessor, direct=False):
        "Get a deferred fork by the given accessor."
        if direct:
            return self.direct.get(accessor, None)
        return self.related.get(accessor, None)


class Memo(object):
    "Memoizes reference objects and their instance equivalents."
    def __init__(self):
        self._memo = {}

    def _key(self, reference):
        if reference.pk:
            return id(reference.__class__), reference.pk
        return id(reference)

    def has(self, reference):
        key = self._key(reference)
        return key in self._memo

    def add(self, reference, instance):
        key = self._key(reference)
        self._memo[key] = instance

    def get(self, reference):
        key = self._key(reference)
        return self._memo.get(key)


def _get_field_by_accessor(instance, accessor):
    """Extends the model ``Options.get_field_by_name`` to look up reverse
    relationships by their accessor name. This gets memod on the first
    lookup.

    The memo will only be needed when the ``related_name`` attribute has
    not been set for reverse relationships.
    """
    try:
        field = instance._meta.get_field(accessor)
        model = field.model
        direct = not field.auto_created or field.concrete
        m2m = field.many_to_many

        if isinstance(field, related.ForeignObjectRel):
            field = field.field
    # if this occurs, try related object accessor
    except FieldDoesNotExist as e:
        # check to see if this memo has been set
        if not hasattr(instance._meta, 'related_objects_by_accessor'):
            memo = {}

            related_objects = [
                f for f in instance._meta.get_fields()
                if (f.one_to_many or f.one_to_one)
                and f.auto_created and not f.concrete
            ]
            related_many_to_many_objects = [
                f for f in instance._meta.get_fields(include_hidden=True)
                if f.many_to_many and f.auto_created
            ]

            # reverse foreign key and many-to-many rels
            related_objects = related_objects + related_many_to_many_objects

            for rel in iter(related_objects):
                memo[rel.get_accessor_name()] = rel

            instance._meta.related_objects_by_accessor = memo

        rel = instance._meta.related_objects_by_accessor.get(accessor, None)

        # if the related object still doesn't exist, raise the exception
        # that is present
        if rel is None:
            raise e

        field, model, direct, m2m = (
            rel.field,
            rel.model,
            False,
            isinstance(rel.field, models.ManyToManyField)
        )

    # ignoring ``model`` for now.. no use for it
    return field, direct, m2m


def _get_field_value(instance, accessor):
    """Simple helper that returns the model's data value and catches
    non-existent related object lookups.
    """
    field, direct, m2m = _get_field_by_accessor(instance, accessor)

    value = None
    # attempt to retrieve deferred values first, since they will be
    # the value once comitted. these will never contain non-relational
    # fields
    if hasattr(instance, '_commits'):
        if m2m:
            value = instance._commits.get(accessor, direct=False)
        else:
            value = instance._commits.get(accessor, direct=direct)
        if value and isinstance(value, DeferredCommit):
            value = value.value

    # deferred relations can never be a NoneType
    if value is None:
        try:
            value = getattr(instance, accessor)
        # catch foreign keys and one-to-one lookups
        except models.ObjectDoesNotExist:
            value = None
        # catch many-to-many or related foreign keys
        except ValueError:
            value = []

    # get the queryset associated with the m2m or reverse foreign key.
    # logic broken up for readability
    if value and m2m or not direct and not isinstance(field, models.OneToOneField):
        if type(value) is not list:
            value = value.all()

    # ignoring ``model`` for now.. no use for it
    return value, field, direct, m2m


def _default_model_fields(instance, exclude=('pk',), deep=False):
    "Aggregates the default set of fields for creating an object fork."
    if not exclude:
        exclude = []
    # handle this special case..
    else:
        exclude = list(exclude)
        if 'pk' in exclude:
            exclude.remove('pk')
            exclude.append(instance._meta.pk.name)

    related_many_to_many = [
        field.get_accessor_name()
        for field in instance._meta.get_fields(include_hidden=True)
        if field.many_to_many and field.auto_created
    ]
    fields = (
        [f.name for f in instance._meta.fields + instance._meta.many_to_many] +
        related_many_to_many
    )

    if deep:
        fields += [
            field.get_accessor_name()
            for field in instance._meta.get_fields()
            if (field.one_to_many or field.one_to_one)
            and field.auto_created
            and not field.concrete
        ]

    return set(fields) - set(exclude)
