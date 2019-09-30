from django.db import models
from django.utils.encoding import python_2_unicode_compatible


from forkit.models import ForkableModel


@python_2_unicode_compatible
class Tag(ForkableModel):
    name = models.CharField(max_length=30)

    def __str__(self):
        return u'{0}'.format(self.name)


@python_2_unicode_compatible
class Author(ForkableModel):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def __str__(self):
        return u'{0} {1}'.format(self.first_name, self.last_name)


@python_2_unicode_compatible
class Blog(ForkableModel):
    name = models.CharField(max_length=50)
    author = models.OneToOneField(Author, on_delete=models.CASCADE)

    def __str__(self):
        return u'{0}'.format(self.name)


@python_2_unicode_compatible
class Post(ForkableModel):
    title = models.CharField(max_length=50)
    # intentionally left off the related_name attr
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author, related_name='posts')
    # intentionally left off the related_name attr
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return u'{0}'.format(self.title)


@python_2_unicode_compatible
class A(ForkableModel):
    title = models.CharField(max_length=50)
    d = models.ForeignKey('D', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u'{0}'.format(self.title)


@python_2_unicode_compatible
class B(ForkableModel):
    title = models.CharField(max_length=50)

    def __str__(self):
        return u'{0}'.format(self.title)


@python_2_unicode_compatible
class C(ForkableModel):
    title = models.CharField(max_length=50)
    a = models.ForeignKey(A, null=True, on_delete=models.CASCADE)
    b = models.ForeignKey(B, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return u'{0}'.format(self.title)


@python_2_unicode_compatible
class D(ForkableModel):
    title = models.CharField(max_length=50)

    def __str__(self):
        return u'{0}'.format(self.title)


@python_2_unicode_compatible
class E(ForkableModel):
    eyedee = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return u'{0}'.format(self.title)
