import json
import requests
import pickle
import os.path

from django.conf import settings
from django.utils.text import slugify

from pyquery import PyQuery

CRM_BASE_URL = settings.CDMS_BASE_URL

COOKIE_FILE = '/tmp/cdms_cookie_{slug}.tmp'.format(
    slug=slugify(CRM_BASE_URL)
)


class CDMSApi(object):
    CRM_BASE_URL = settings.CDMS_BASE_URL
    CRM_ADFS_URL = settings.CDMS_ADFS_URL
    CRM_REST_BASE_URL = '%s/XRMServices/2011/OrganizationData.svc' % CRM_BASE_URL

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = self._get_or_create_session()

    def _get_or_create_session(self):
        """
        So that we don't login every time during dev, we save the cookie
        in a file and load it afterwards.
        """
        if not os.path.exists(COOKIE_FILE):
            session = self.login()
            with open(COOKIE_FILE, 'wb') as f:
                pickle.dump(session.cookies._cookies, f)

        with open(COOKIE_FILE, 'rb') as f:
            cookies = pickle.load(f)
            session = requests.session()
            jar = requests.cookies.RequestsCookieJar()
            jar._cookies = cookies
            session.cookies = jar
        return session

    def login(self):
        session = requests.session()

        # login form
        login_form_response = session.get(
            '{base}/?whr={adfs}'.format(
                base=self.CRM_BASE_URL,
                adfs=self.CRM_ADFS_URL
            ),
            verify=False
        )

        html_parser = PyQuery(login_form_response.content)
        username_field_name = html_parser('input[name*=Username]')[0].name
        password_field_name = html_parser('input[name*=Password]')[0].name
        submit_field = html_parser('input[name*=Submit]')[0]
        login_data = {
            field.name: field.value for field in html_parser('[type=hidden]')
        }

        login_data.update({
            username_field_name: self.username,
            password_field_name: self.password,
            submit_field.name: submit_field.value
        })

        # first submit
        login_resp = session.post(login_form_response.url, login_data)

        # second submit
        html_parser = PyQuery(login_resp.content)
        confirm_url = html_parser('form').attr('action')

        resp = session.post(
            confirm_url, {
                field.get('name'): field.get('value') for field in html_parser('input')
            }
        )

        # third submit
        html_parser = PyQuery(resp.content)
        confirm_url = html_parser('form').attr('action')

        resp = session.post(
            confirm_url, {
                field.get('name'): field.get('value') for field in html_parser('input')
            },
            verify=False
        )
        return session

    def _make_request(self, verb, url, data={}):
        print('calling url %s' % url)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

        if data:
            data = json.dumps(data)
        resp = getattr(self.session, verb)(url, data=data, headers=headers, verify=False)

        if resp.status_code in (200, 201):
            return resp.json()
        return resp

    def list(self, service, top=50, skip=0, select=None, filters=None, orderby=None):
        params = {}
        if filters:
            params['$filter'] = ' and '.join(filters)

        if select:
            params['$select'] = ','.join(select)

        if orderby:
            params['$orderby'] = orderby

        url = "{base_url}/{service}Set?$top={top}&$skip={skip}&{params}".format(
            base_url=self.CRM_REST_BASE_URL,
            service=service,
            top=top,
            skip=skip,
            params='&'.join([u'%s=%s' % (k, v) for k, v in params])
        )
        return self._make_request('get', url)

    def get(self, service, guid):
        url = "{base_url}/{service}Set(guid'{guid}')".format(
            base_url=self.CRM_REST_BASE_URL,
            service=service,
            guid=guid
        )
        return self._make_request('get', url)

    def update(self, service, guid, data):
        url = "{base_url}/{service}Set(guid'{guid}')".format(
            base_url=self.CRM_REST_BASE_URL,
            service=service,
            guid=guid
        )
        return self._make_request('put', url, data=data)

    def create(self, service, data):
        url = "{base_url}/{service}Set".format(
            base_url=self.CRM_REST_BASE_URL,
            service=service
        )
        return self._make_request('post', url, data=data)
