import json
import requests


class CovidWrapper:
    def __init__(self):
        self.state_district_wise = "https://api.covid19india.org/v2/state_district_wise.json"
        self.resources = "https://api.covid19india.org/resources/resources.json"
        self.overall_data = "https://api.rootnet.in/covid19-in/stats/latest"
        self.testing = "https://api.rootnet.in/covid19-in/stats/testing/latest"
        self.hospital_beds = "https://api.rootnet.in/covid19-in/hospitals/beds"

    def check_error(self, response, api_url):
        if response.status_code >= 500:
            print('[!] [{0}] Server Error'.format(response.status_code))
            return None
        elif response.status_code == 404:
            print('[!] [{0}] URL not found: [{1}]'.format(
                response.status_code, api_url))
            return None
        elif response.status_code == 401:
            print('[!] [{0}] Authentication Failed'.format(
                response.status_code))
            return None
        elif response.status_code == 400:
            print('[!] [{0}] Bad Request'.format(response.status_code))
            return None
        elif response.status_code >= 300:
            print('[!] [{0}] Unexpected Redirect'.format(response.status_code))
            return None
        elif response.status_code == 200:
            data = json.loads(response.content.decode('utf-8'))
            return data
        else:
            print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(
                response.status_code, response.content))
        return None

    def get_state_data(self, state_name):
        response = requests.get(self.state_district_wise)
        data = self.check_error(response, self.state_district_wise)
        curr_state = ""
        active_cases = 0
        confirmed_cases = 0
        deaths = 0
        recovered = 0
        for states in data:
            curr_state = states['state']
            if curr_state.lower() == state_name.lower():
                for districts in states['districtData']:
                    active_cases += districts['active']
                    confirmed_cases += districts['confirmed']
                    deaths += districts['deceased']
                    recovered += districts['recovered']
                    confirmed_cases += districts['delta']['confirmed']
                    deaths += districts['delta']['deceased']
                    recovered += districts['delta']['recovered']
        return (f'{confirmed_cases:,}', f'{active_cases:,}', f'{recovered:,}', f'{deaths:,}')

    def get_district_data(self, district_name):
        response = requests.get(self.state_district_wise)
        data = self.check_error(response, self.state_district_wise)
        curr_state = ""
        active_cases = 0
        confirmed_cases = 0
        deaths = 0
        recovered = 0
        for states in data:
            for districts in states['districtData']:
                if districts['district'].lower() == district_name.lower():
                    active_cases += districts['active']
                    confirmed_cases += districts['confirmed']
                    deaths += districts['deceased']
                    recovered += districts['recovered']
                    confirmed_cases += districts['delta']['confirmed']
                    deaths += districts['delta']['deceased']
                    recovered += districts['delta']['recovered']
        return (f'{confirmed_cases:,}', f'{active_cases:,}', f'{recovered:,}', f'{deaths:,}')

    def get_data(self):
        response = requests.get(self.state_district_wise)


if __name__ == "__main__":
    c = CovidWrapper()
    print(c.get_state_data('maharashtra'))
