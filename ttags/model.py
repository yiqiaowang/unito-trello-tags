"""
Main class for interfacing with trello api.
"""
import requests


class TrelloTool:
    TRELLO_ENDPOINTS = {
        'get_boards': 'https://api.trello.com/1/members/me/boards',
        'get_list': 'https://api.trello.com/1/lists/{}/cards',
        'post_label': 'https://api.trello.com/1/cards/{}/idLabels',
        'delete_label': 'https://api.trello.com/1/cards/{}/idLabels/{}'
    }

    def __init__(self, credentials):
        self.key = credentials.get('key')
        self.token = credentials.get('token')

    def get_boards(self):
        """ Get information on boards and their lists. """
        parameters = {
            'fields': 'name',
            'lists': 'all',
            'key': self.key,
            'token': self.token
        }

        req = requests.get(
            TrelloTool.TRELLO_ENDPOINTS.get('get_boards'),
            params=parameters)

        return req

    def get_list(self, list_id):
        """ Get detailed information on a list, including cards and their labels. """
        parameters = {
            'fields': 'name,desc,labels',
            'key': self.key,
            'token': self.token
        }

        req = requests.get(TrelloTool.TRELLO_ENDPOINTS.get(
            'get_list').format(list_id), params=parameters)

        return req

    def delete_card_label(self, card_id, label_id):
        """ Delete a label from a card. """

        parameters = {
            'key': self.key,
            'token': self.token
        }

        req = requests.delete(
            TrelloTool.TRELLO_ENDPOINTS.get('delete_label').format(
                card_id, label_id), params=parameters)

        return req

    def post_id_label(self, card_id, label_id):
        """ Add a label to a card. """

        parameters = {
            'key': self.key,
            'token': self.token
        }
        payload = {
            'value': label_id
        }

        req = requests.post(TrelloTool.TRELLO_ENDPOINTS.get(
            'post_label').format(card_id), params=parameters, data=payload)

        return req
