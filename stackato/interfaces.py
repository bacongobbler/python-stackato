import json
import urllib
from urlparse import urljoin
import requests
from stackato.apps import StackatoApp
from stackato.services import StackatoService
from stackato.exceptions import StackatoException, StackatoAuthenticationException
import os

'''
Represents an interface to communicate with a
Stackato micro cloud or cluster (known as a Stackato instance).
'''
class StackatoInterface(object):
    
    TOKEN_FILE_LOCAL_PATH = '~/.stackato/client/token'

    def __init__(self, target, username=None, password=None, store_token=False):
        self.target = target                # the Stackato instance we are targeting
        self.username = username            # username used to log into the instance
        self.password = password            # password used for the username
        self.token = None                   # token that is required for authenticated calls to the API
        self.store_token = store_token      # flag to store the token locally on the computer
        self.token_file = os.path.expanduser(self.TOKEN_FILE_LOCAL_PATH)    # path to the file that contains the token

        # check if the token is currently within the file. if it is, extract it and set self.token
        if self.store_token:
            if os.path.exists(self.token_file):
                with open(self.token_file) as fobj:
                    try:
                        data = json.load(fobj)
                        if self.target in data:
                            self.token = data[self.target]
                    except ValueError: # Invalid JSON in file, probably empty (or modified)
                        pass

    def auth_args(self, authentication_required):
        if not authentication_required and not self.token:
            return {}
        elif not self.token and self.store_token: # Ignore, will request new token afterwards!
            return {}
        elif not self.token:
            raise StackatoAuthenticationException("Please login before using this function")
        return {'headers': {'Authorization': self.token}}

    def _request(self, url, request_type=requests.get, authentication_required=True, data=None):
        if data:
            data = json.dumps(data)
        request = request_type(urljoin(self.target, url), data=data, **self.auth_args(authentication_required))
        if request.status_code == 200:
            return request
        elif request.status_code == 403:
            if not authentication_required:
                raise StackatoAuthenticationException(request.text)
            else:
                self.login()
                return self._request(url, request_type, authentication_required=False, data=data)
        elif request.status_code == 404:
            raise StackatoException("HTTP %s - %s" % (request.status_code, request.text))
        else:
            raise StackatoException("HTTP %s - %s" % (request.status_code, request.text))

    def _get_json_or_exception(self, *args, **kwargs):
        return self._request(*args, **kwargs).json()

    def _get_true_or_exception(self, *args, **kwargs):
        self._request(*args, **kwargs)
        return True

    def login(self):
        self.token = self._get_json_or_exception(
            "users/%s/tokens" % urllib.quote_plus(self.username),
            request_type=requests.post,
            authentication_required=False,
            data={'password': self.password}
        )['token']
        if self.store_token:
            data = {self.target: self.token}
            if os.path.exists(self.token_file):
                try:
                    with open(self.token_file) as token_file:
                        data = json.loads(token_file.read())
                        data[self.target] = self.token
                except ValueError: # Invalid JSON in file, probably empty
                    pass
            with open(self.token_file, 'w') as token_file:
                json.dump(data, token_file)
        return True

    def get_apps(self):
        return [StackatoApp.from_dict(app, self) for app in self._get_json_or_exception("apps/")]

    def get_app(self, name):
        return StackatoApp.from_dict(self._get_json_or_exception("apps/%s" % name), self)

    def get_app_crashes(self, name):
        return self._get_json_or_exception("apps/%s/crashes" % name)

    def get_app_instances(self, name):
        return self._get_json_or_exception("apps/%s/instances" % name)

    def get_app_stats(self, name):
        return self._get_json_or_exception("apps/%s/stats" % name)

    def delete_app(self, name):
        return self._get_true_or_exception("apps/%s" % name, request_type=requests.delete)

    def get_services(self):
        return [StackatoService.from_dict(service, self) for service in self._get_json_or_exception("services/")]

    def get_service(self, name):
        return StackatoService.from_dict(self._get_json_or_exception("services/%s" % name), self)

    def delete_service(self, name):
        return self._get_true_or_exception("services/%s" % name, request_type=requests.delete)
