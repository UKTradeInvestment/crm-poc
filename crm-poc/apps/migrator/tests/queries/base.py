from unittest import mock

from django.test.testcases import TransactionTestCase

from cdms_api.utils import mocked_cdms_create, mocked_cdms_get


class BaseMockedCDMSApiTestCase(TransactionTestCase):
    @mock.patch('migrator.query.cdms_conn')
    def __call__(self, result, mocked_cdms_api, *args, **kwargs):
        mocked_cdms_api.create.side_effect = mocked_cdms_create()
        mocked_cdms_api.get.side_effect = mocked_cdms_get()
        self.mocked_cdms_api = mocked_cdms_api
        super(BaseMockedCDMSApiTestCase, self).__call__(result, *args, **kwargs)

    def assertAPICalled(self, model, verb, kwargs, tot=1):
        if tot == 1:
            kwargs = [kwargs]

        for index, single_kwargs in enumerate(kwargs):
            mock_verb = getattr(self.mocked_cdms_api, verb)

            self.assertEqual(mock_verb.call_count, tot)

            _args, _kwargs = mock_verb.call_args_list[index]
            self.assertEqual(_args, (model.cdms_migrator.service,))
            self.assertDictEqual(_kwargs, single_kwargs)

    def assertAPINotCalled(self, verbs):
        if not isinstance(verbs, list):
            verbs = [verbs]

        for verb in verbs:
            mock_verb = getattr(self.mocked_cdms_api, verb)
            self.assertEqual(
                mock_verb.call_count, 0,
                '%s should not get called' % verb
            )

    def assertNoAPINotCalled(self):
        self.assertAPINotCalled(['create', 'list', 'update', 'delete', 'get'])

    def assertAPICreateCalled(self, model, kwargs, tot=1):
        self.assertAPICalled(model, 'create', kwargs=kwargs, tot=tot)

    def assertAPIUpdateCalled(self, model, kwargs, tot=1):
        self.assertAPICalled(model, 'update', kwargs=kwargs, tot=tot)

    def assertAPIGetCalled(self, model, kwargs, tot=1):
        self.assertAPICalled(model, 'get', kwargs=kwargs, tot=tot)
