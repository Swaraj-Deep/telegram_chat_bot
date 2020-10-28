import os
import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import InvalidArgument
import random
import json
import packages.covid_endpoint

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './configfiles/private_key.json'


class DialogFlowWrapper:
    def __init__(self):
        self.DIALOGFLOW_PROJECT_ID = 'covid-19bot-sbsl'
        self.DIALOGFLOW_LANGUAGE_CODE = 'en'
        self.helplines = self.populate_helpline_numbers()
        self.covidwrapper = packages.covid_endpoint.CovidWrapper()

    def populate_helpline_numbers(self):
        folder_name = os.path.join(os.getcwd(), 'training')
        file_name = 'numbers.json'
        data = {}
        with open(os.path.join(folder_name, file_name), 'r') as file_pointer:
            data = json.load(file_pointer)
        helplines = {}
        for key, value in data.items():
            key = key.lower()
            if key not in helplines:
                helplines[key] = [value]
            else:
                helplines[key].append(value)
        return helplines

    def process_input(self, text_to_be_analyzed, chat_id, first_name):
        SESSION_ID = chat_id
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(
            self.DIALOGFLOW_PROJECT_ID, SESSION_ID)
        text_input = dialogflow.types.TextInput(
            text=text_to_be_analyzed, language_code=self.DIALOGFLOW_LANGUAGE_CODE)
        query_input = dialogflow.types.QueryInput(text=text_input)
        knowledge_base_path = dialogflow.knowledge_bases_client \
            .KnowledgeBasesClient \
            .knowledge_base_path(self.DIALOGFLOW_PROJECT_ID, 'MTY5NjYxNzQ3MDEwOTUyMjMyOTY')
        query_params = dialogflow.types.QueryParameters(
            knowledge_base_names=[knowledge_base_path])
        try:
            response = session_client.detect_intent(
                session=session, query_input=query_input)
        except InvalidArgument:
            pass
        detected_intent = response.query_result.intent.display_name
        reply = ""
        if detected_intent == 'city_handler':
            reply = self.response_city_handler(response)
        elif detected_intent == 'state_handler':
            reply = self.response_state_handler(response)
        elif detected_intent == 'Knowledge.KnowledgeBase.MTY5NjYxNzQ3MDEwOTUyMjMyOTY':
            reply = self.response_faq(response)
        elif detected_intent == 'Default Welcome Intent':
            reply = self.response_welcome(response, first_name)
        elif detected_intent == 'Default Fallback Intent':
            reply = self.response_fallback(response, first_name)
        elif detected_intent == 'country_handler':
            reply = self.response_country_handler(response)
        elif detected_intent == 'helpline':
            reply = self.response_helpline(response)
        return reply

    def response_helpline(self, response):
        state_name = response.query_result.parameters.fields['geo-state'].string_value
        if state_name == "":
            return response.query_result.fulfillment_text
        else:
            state_name = state_name.lower()
            num_lst = []
            if state_name in self.helplines:
                reply = ''
                for item in self.helplines[state_name]:
                    for numbers in item:
                        num_lst.append(numbers)
                if len(num_lst) == 1:
                    reply = num_lst[0]
                else:
                    reply = f'You can call on any of the below numbers\n'
                    for numbers in num_lst:
                        reply += f'{numbers}\n'
                return reply
            else:
                return "Cannot find State. Make sure that you spelled the name correctly"

    def response_city_handler(self, response):
        city_name = response.query_result.parameters.fields['geo-city'].string_value
        if city_name == "":
            return response.query_result.fulfillment_text
        reply = ""
        confirmed_cases, active_cases, recovered, deaths = self.covidwrapper.get_district_data(
            city_name)
        reply += f'The details for {city_name}\nConfirmed Cases: {confirmed_cases}\nActive Cases: {active_cases}\nRecovered: {recovered}\nDeaths: {deaths}\n'
        return reply

    def response_state_handler(self, response):
        state_name = response.query_result.parameters.fields['geo-state'].string_value
        if state_name == "":
            return response.query_result.fulfillment_text
        reply = ""
        confirmed_cases, active_cases, recovered, deaths = self.covidwrapper.get_state_data(
            state_name)
        reply += f'The details for {state_name}\nConfirmed Cases: {confirmed_cases}\nActive Cases: {active_cases}\nRecovered: {recovered}\nDeaths: {deaths}\n'
        return reply

    def response_country_handler(self, response):
        country_name = response.query_result.parameters.fields['geo-country'].string_value
        if country_name == "":
            return response.query_result.fulfillment_text
        reply = ""
        confirmed_cases, active_cases, recovered, deaths = self.covidwrapper.get_country_data()
        reply += f'The details for India\nConfirmed Cases: {confirmed_cases}\nActive Cases: {active_cases}\nRecovered: {recovered}\nDeaths: {deaths}\n'
        return reply

    def response_faq(self, response):
        return response.query_result.fulfillment_text

    def prefix_reply(self, responses):
        """Returns a random string from a given set of responses"""
        pos = random.randint(0, len(responses) - 1)
        return responses[pos]

    def response_welcome(self, response, first_name):
        emoticons = ['😌', '🙂']
        responses = ['Hi ', 'Hello ', 'Whats up ', 'How are you ']
        reply = self.prefix_reply(responses) + first_name
        return "\n".join([self.prefix_reply(emoticons), reply])

    def response_fallback(self, response, first_name):
        phrase = "Wait there!! I am still learning"
        responses = ['🙄', '🤔', '😬', '😐']
        reply = self.prefix_reply(responses) + "\n" + phrase
        return reply


if __name__ == "__main__":
    d = DialogFlowWrapper()
    ipt = input()
    d.process_input(ipt, 'ciah')
