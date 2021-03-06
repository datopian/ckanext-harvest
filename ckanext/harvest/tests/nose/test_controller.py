from ckan.lib.helpers import url_for

from ckantoolkit.tests import helpers, factories
from ckanext.harvest.tests.nose import factories as harvest_factories
from nose.tools import assert_in
import ckanext.harvest.model as harvest_model
from ckan.plugins import toolkit
from ckan import model


class TestController(helpers.FunctionalTestBase):

    @classmethod
    def setup_class(cls):

        helpers.reset_db()
        super(TestController, cls).setup_class()
        harvest_model.setup()
        sysadmin = factories.Sysadmin()
        cls.extra_environ = {'REMOTE_USER': sysadmin['name'].encode('ascii')}

    @classmethod
    def teardown_class(cls):
        super(TestController, cls).teardown_class()
        helpers.reset_db()

    def setup(self):
        super(TestController, self).setup()
        sysadmin = factories.Sysadmin()
        self.extra_environ = {'REMOTE_USER': sysadmin['name'].encode('ascii')}

    def test_index_page_is_rendered(self):

        source1 = harvest_factories.HarvestSource()
        source2 = harvest_factories.HarvestSource()

        app = self._get_test_app()

        response = app.get(u'/harvest')

        assert_in(source1['title'], response.unicode_body)
        assert_in(source2['title'], response.unicode_body)

    def test_new_form_is_rendered(self):

        app = self._get_test_app()
        url = url_for('harvest_new')

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in('<form id="source-new"', response.unicode_body)

    def test_edit_form_is_rendered(self):

        source = harvest_factories.HarvestSource()

        app = self._get_test_app()

        url = url_for('harvest_edit', id=source['id'])

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in('<form id="source-new"', response.unicode_body)

    def test_source_page_rendered(self):

        source = harvest_factories.HarvestSource()
        app = self._get_test_app()
        url = url_for('harvest_read', id=source['name'])

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in(source['name'], response.unicode_body)

    def test_admin_page_rendered(self):

        source_obj = harvest_factories.HarvestSourceObj()
        job = harvest_factories.HarvestJob(source=source_obj)

        app = self._get_test_app()
        url = url_for('harvest_admin', id=source_obj.id)

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in(source_obj.title, response.unicode_body)

        assert_in(job['id'], response.unicode_body)

    def test_about_page_rendered(self):

        source = harvest_factories.HarvestSource()
        app = self._get_test_app()
        url = url_for('harvest_about', id=source['name'])

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in(source['name'], response.unicode_body)

    def test_job_page_rendered(self):

        job = harvest_factories.HarvestJob()
        app = self._get_test_app()
        url = url_for('harvest_job_list', source=job['source_id'])

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in(job['id'], response.unicode_body)

    def test_job_show_last_page_rendered(self):

        job = harvest_factories.HarvestJob()
        app = self._get_test_app()
        url = url_for('harvest_job_show_last', source=job['source_id'])

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in(job['id'], response.unicode_body)

    def test_job_show_page_rendered(self):

        job = harvest_factories.HarvestJob()
        app = self._get_test_app()
        url = url_for(
            'harvest_job_show', source=job['source_id'], id=job['id'])

        response = app.get(url, extra_environ=self.extra_environ)

        assert_in(job['id'], response.unicode_body)

    def test_job_show_object(self):
        source_obj = harvest_factories.HarvestSourceObj()
        job = harvest_factories.HarvestJob(source=source_obj)

        context = {
            'model': model,
            'session': model.Session,
            'ignore_auth': True,
        }
        data_dict = {
            'guid': 'guid',
            'content': 'test content',
            'job_id': job['id'],
            'source_id': source_obj.id,
            'extras': {'a key': 'a value'},
        }
        harvest_object = toolkit.get_action('harvest_object_create')(
            context, data_dict)

        app = self._get_test_app()
        url = url_for('harvest_object_show', id=harvest_object['id'])

        response = app.get(url)

        assert_in(data_dict['content'], response.unicode_body)
