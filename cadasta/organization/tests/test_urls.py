from django.test import TestCase
from django.core.urlresolvers import reverse, resolve
from core.tests.url_utils import version_ns, version_url

from .. import views


class OrganizationUrlTest(TestCase):
    def test_organization_list(self):
        self.assertEqual(
            reverse(version_ns('organization:list')),
            version_url('/organizations/')
        )

        resolved = resolve(version_url('/organizations/'))
        self.assertEqual(
            resolved.func.__name__,
            views.OrganizationList.__name__)

    def test_organization_detail(self):
        self.assertEqual(
            reverse(
                version_ns('organization:detail'),
                kwargs={'slug': 'org-slug'}),
            version_url('/organizations/org-slug/')
        )

        resolved = resolve(version_url('/organizations/org-slug/'))
        self.assertEqual(
            resolved.func.__name__,
            views.OrganizationDetail.__name__)
        self.assertEqual(resolved.kwargs['slug'], 'org-slug')

    def test_organization_users(self):
        self.assertEqual(
            reverse(
                version_ns('organization:users'),
                kwargs={'slug': 'org-slug'}),
            version_url('/organizations/org-slug/users/')
        )

        resolved = resolve(version_url('/organizations/org-slug/users/'))
        self.assertEqual(
            resolved.func.__name__,
            views.OrganizationUsers.__name__)
        self.assertEqual(resolved.kwargs['slug'], 'org-slug')

    def test_organization_users_detail(self):
        self.assertEqual(
            reverse(version_ns('organization:users_detail'),
                    kwargs={
                        'slug': 'org-slug',
                        'username': 'n_smith'
                    }),
            version_url('/organizations/org-slug/users/n_smith/')
        )

        resolved = resolve(
            version_url('/organizations/org-slug/users/n_smith/'))

        self.assertEqual(
            resolved.func.__name__,
            views.OrganizationUsersDetail.__name__)
        self.assertEqual(resolved.kwargs['slug'], 'org-slug')
        self.assertEqual(resolved.kwargs['username'], 'n_smith')