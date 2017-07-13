import factory

from core.tests.factories import ExtendedFactory
from .. import models


class OrganizationFactory(ExtendedFactory):
    class Meta:
        model = models.Organization

    name = factory.Sequence(lambda n: "Organization #%s" % n)
    slug = factory.Sequence(lambda n: "organization-%s" % n)
    description = factory.Sequence(
        lambda n: "Organization #%s description" % n)
    urls = ['http://example.com']
    contacts = []

    @factory.post_generation
    def add_users(self, create, users, **kwargs):
        if not create:
            return

        if users:
            for u in users:
                models.OrganizationRole.objects.create(organization=self,
                                                       user=u)


class ProjectFactory(ExtendedFactory):
    class Meta:
        model = models.Project

    name = factory.Sequence(lambda n: "Project #%s" % n)
    slug = factory.Sequence(lambda n: "project-%s" % n)
    organization = factory.SubFactory(OrganizationFactory)
    description = factory.Sequence(
        lambda n: "Project #%s description" % n)
    urls = ['http://example.com']
    contacts = []
    access = "public"

    @factory.post_generation
    def add_users(self, create, users, **kwargs):
        if not create:
            return

        if users:
            for u in users:
                models.OrganizationRole.objects.get_or_create(
                    organization=self.organization, user=u)
                models.ProjectRole.objects.create(project=self, user=u)


def clause(effect, action, object=None):
    if object is None:
        return {'effect': effect, 'action': action}
    else:
        return {'effect': effect, 'action': action, 'object': object}


class LayerGroupFactory(ExtendedFactory):
    class Meta:
        model = models.LayerGroup

    name = factory.Sequence(lambda n: "Layer Group #%s" % n)
    type = 'wms'
    project = factory.SubFactory(ProjectFactory)


class LayerFactory(ExtendedFactory):
    class Meta:
        model = models.Layer

    name = factory.Sequence(lambda n: "layer-#%s" % n)
    title = factory.Sequence(lambda n: "Layer #%s" % n)
    type = 'wms'
    group = factory.SubFactory(LayerGroupFactory)
    url = 'http://example.com'
