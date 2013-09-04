from stackato import Session
from bs4 import BeautifulSoup
import requests
import yaml

# json dictionary of basic login credentials
CREDENTIALS = yaml.load(open('credentials.yml'))
# the app id on Stackato
APP_NAME = 'demo'
# your user id on new relic
NEW_RELIC_USER_ID = 12345
# the application id of the app on New relic you wish to monitor
NEW_RELIC_APPLICATION_ID = 67890
# what percentage (represented in floating-point numbers) is your application's threshold to spawn new instances?
CPU_THRESHOLD = 80.5

#########################################################################################
#                                                                                       #
# Get a specific new-relic threshold value.                                             #
# https://github.com/newrelic/newrelic_api#view-all-alert-thresholds-for-an-application #
#                                                                                       #
#########################################################################################
def get_newrelic_threshold_value(user, appid, name='CPU'):
    headers = {'x-api-key': CREDENTIALS['token']}

    # request the 
    r = requests.get('https://api.newrelic.com/api/v1/accounts/' + user + '/applications/' + appid + '/threshold_values.xml', headers=headers)

    # read from the response body as xml data
    soup = BeautifulSoup(r.text, 'xml')

    # return the value of the specified threshold_value's name from the response
    return soup.find_all(attrs={'name': name})[0]['metric_value']

if __name__ == "__main__":
    # create a new interface to stackato with your login credentials
    s = Session(CREDENTIALS['target'], CREDENTIALS['username'], CREDENTIALS['password'])

    # convert to float, since the CPU threshold value is returned as a string
    metric_value = float(get_newrelic_threshold_value())

    if metric_value < CPU_THRESHOLD:
        print('application running normally. no new instances spawned.')
    else:
        # log into Stackato
        if s.login():
            # making a GET request
            app = s.get_app(APP_NAME)
            # increase the number of instances
            app['instances'] += 1
            # making a PUT request to the application
            if s.put_app(APP_NAME, app):
                print('added one more instance to this application.')
