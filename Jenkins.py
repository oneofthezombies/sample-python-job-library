from typing import Optional, Tuple, Dict
import requests
import json
import os


class Jenkins:
    def __init__(self, username: str, token: str) -> None:
        self.username = username
        self.token = token

    def get_crumb(
        self,
        jenkins_url: str = os.environ['JENKINS_URL']
    ) -> Tuple[str, str]:
        jenkins_url = jenkins_url if jenkins_url.endswith('/') else f'{jenkins_url}/'
        url = f'{jenkins_url}crumbIssuer/api/json'
        method = 'get'
        auth = (self.username, self.token)
        response = requests.request(method, url, auth=auth)
        if (response.status_code != 200):
            raise Exception({
                'request': {
                    'url': url,
                    'method': method,
                    'auth': auth
                },
                'response': {
                    'status_code': response.status_code,
                    'text': response.text
                }
            })
        result = json.loads(response.text)
        return result['crumbRequestField'], result['crumb']

    def update_build_config(
        self,
        build_url: str = os.environ['BUILD_URL'],
        display_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> None:
        build_url = build_url if build_url.endswith('/') else f'{build_url}/'
        config: Dict[str, str] = {}
        if display_name:
            config['displayName'] = display_name
        if description:
            config['description'] = description
        if len(config) == 0:
            raise Exception(config)

        url = f'{build_url}configSubmit'
        method = 'post'
        auth = (self.username, self.token)
        crumb_key, crumb_value = self.get_crumb()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            crumb_key: crumb_value
        }
        data = {
            'json': json.dumps(config)
        }
        response = requests.request(method, url, auth=auth, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception({
                'request': {
                    'url': url,
                    'auth': auth,
                    'headers': headers,
                    'data': data
                },
                'response': {
                    'status_code': response.status_code,
                    'text': response.text
                }
            })


if __name__ == '__main__':
    username = 'hunhoekim'
    token = '11b4f02bdb99a3e19cdf8e6aca42072176'
    jenkins = Jenkins(username=username, token=token)
    jenkins.update_build_config(
        display_name='[MyProject][MyBranch][RepoA#12 RepoB#34]',
        description='REPO_A_REVISION=12\nREPO_B_REVISION=34')
