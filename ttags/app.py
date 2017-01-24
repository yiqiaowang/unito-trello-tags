"""
Class that contains the main application functionality. 
"""

import auth
import model
import json
from random import choice
from fuzzywuzzy import fuzz
from difflib import get_close_matches
from functools import reduce


class TrelloApp:

    def __init__(self):
        self.credentials = None
        self.authenticated = False
        self.tool = None
        self.dirty = False

        self.Boards = []
        self.Lists = []
        self.Cards = []

    @staticmethod
    def parse_boards_json(boards_json):
        """
        Take an array (parsed from json) of boards and return
        a more usable array of board items.
        """
        board_arr = []

        for board in boards_json:
            board_dict = dict()
            board_dict["name"] = board.get('name')
            board_dict["id"] = board.get('id')
            board_dict["lists"] = [
                {'name': l.get('name'), 'id': l.get('id')} for l in board.get(
                    'lists')
            ]

            board_arr.append(board_dict)

        return board_arr

    @staticmethod
    def extract_lists(board_dict):
        """
        Take a board and return the lists in that board in a useable format.
        Returns a list of list dicts.
        """
        list_arr = []
        for _list in board_dict.get('lists'):
            list_dict = dict()
            list_dict['name'] = _list.get('name')
            list_dict['id'] = _list.get('id')
            list_arr.append(list_dict)
        return list_arr

    @staticmethod
    def extract_cards(arr_of_cards):
        """
        Take a list of cards and return the cards in a useable format.
        Returns a list of card dicts with unused data removed.
        """
        card_arr = []
        for card in arr_of_cards:
            card_dict = dict()
            card_dict["name"] = card.get('name')
            card_dict["id"] = card.get('id')
            card_dict["labels"] = [
                {'name': l.get('name'), 'id': l.get('id')} for l in card.get(
                    'labels')
            ]
            card_arr.append(card_dict)

        return card_arr

    def prepare_labels(self, cards):
        """
        Process the cards into two dicts that keep track of:
        label_name -> (label_name, label_id) and
        (label_name, label_id) -> [{card dict}].
        These will be helpfull when replacing the tags.
        """
        # (label name, label id) -> [{card dict}]
        label_card_map = dict()

        # label name -> (label name, label id)
        name_label_map = dict()

        for card in cards:
            labels = card['labels']
            for label in labels:
                label_tuple = (label.get('name'), label.get('id'))
                if label_tuple not in label_card_map.keys():
                    label_card_map[label_tuple] = [card]
                else:
                    label_card_map[label_tuple].append(card)

                if label.get('name') not in name_label_map:
                    name_label_map[label.get('name')] = [label_tuple]
                else:
                    name_label_map[label.get('name')].append(label_tuple)

        return (label_card_map, name_label_map)

    def get_similar_simple(self, label_names):
        """
        Use python's builtin get_diff_lib function along with
        a bit of randomness to decide which words are similar
        """
        # array to hold groups of labels with similar names
        label_groups = []
        # randomly select seed and group the names
        while len(label_names) > 0:
            seed = choice(label_names)
            # get close matches, must be unique
            similar_names = list(
                set(get_close_matches(seed, label_names, cutoff=0.4)))
            # add the seed to the close matches, add to label groups
            label_groups.append(similar_names)
            # Remove those names from the pool
            label_names = [x for x in label_names if x not in similar_names]

        # keep only those groups that have more than 1 element in it
        label_groups = [group for group in label_groups if len(group) > 1]
        return label_groups

    def get_similar_leven(self, label_names):
        """
        Get similar labels using levenshtein distance. No randomness here.
        """
        # array to hold groups of labels with similar names
        label_groups = []
        # randomly select seed and group the names
        while len(label_names) > 0:
            label_names.sort()
            seed = label_names[0]
            # get close matches, make sure the list is unique
            similar_names = list(set([name for name in label_names if
                                      fuzz.ratio(seed, name.replace('_', ' ').
                                                 replace('-', ' ')) > 40]))
            # add the seed to the close matches, add to label groups
            label_groups.append(similar_names)
            # Remove those names from the pool
            label_names = [name for name in label_names if
                           name not in similar_names]

        # keep only those groups that have more than 1 element in it
        label_groups = [group for group in label_groups if len(group) > 1]

        return label_groups

    def suggest_similar(self):
        """
        Suggest sumilar labels and give the option to merge them.
        """
        # if data is dirty, reinitialize
        if self.dirty:
            self.initialize()

        # prepare the dicts that keep track card and label information
        prepared_labels = self.prepare_labels(self.Cards)
        label_names = list(prepared_labels[1].keys())
        label_groups = self.get_similar_leven(label_names)

        label_card_map = prepared_labels[0]
        label_list = label_card_map.keys()
        name_label_map = prepared_labels[1]

        # for each group of similar tags, ask if you would like to replace them
        for group in label_groups:
            print("The following groups of labels are similar", group,
                  "Would you like to merge them under one label?")
            replace = input('(y/n): ')
            while replace != 'y' and replace != 'n':
                print("Didn't understand {}.".format(replace),
                      "Merge {} under one label?".format(group))
                replace = input('(y/n): ')

            # replacing cards
            if replace == 'y':
                print("Which label should replace the others?")
                label_options = reduce(lambda x, y: "{}, {}".format(x, y),
                                       group)
                label_name = input("Choose from - {}:".format(label_options))

                while label_name not in group:
                    print("{} not in {}".format(label_name, group))
                    label_name = input(
                        "Choose from - {}:".format(label_options))

                # Now that we have the label name we wish to use, find an id
                # that matches
                label_tuple_candidates = [label for label in label_list
                                          if label[0] == label_name]

                # Multiple labels may have the same name
                # No way to deal with this without explicitly asking the user.
                # Just pick the first one for now.
                if len(label_tuple_candidates) > 1:
                    print("Multiple labels found. Picking the first one.")

                label_tuple_candidates = label_tuple_candidates[0]
                # Get the (name, id) tuple from the name -> tuple dict
                # This gives us the id of the Label that will do the replacing
                replacing_id = label_tuple_candidates[1]

                # Replace all other labels in the group with the chosen label
                # after removing the chosen label from the group.
                if label_name in group:
                    group.remove(label_name)
                for replaced_name in group:

                    # Find the label tuple that corresponds to the label being
                    # replaced. This is the key of the tuple -> card dict.
                    # there may be different labels with the same name
                    replaced_label_arr = name_label_map[replaced_name]
                    for replaced_label in replaced_label_arr:
                        replaced_id = replaced_label[1]

                        # Replace all the cards that have said label.
                        # That is, all the cards found in the tuple -> card
                        # dict.
                        for card in label_card_map[replaced_label]:
                            card_id = card.get('id')
                            self.dirty = True
                            self.tool.delete_card_label(card_id, replaced_id)
                            self.tool.post_id_label(card_id, replacing_id)
            else:
                print("Not replacing, moving on.")

    def initialize(self):
        """Pull user's data from trello and process them for later use."""
        if self.authenticated:
            # remove stale data
            self.Boards = list()
            self.Cards = list()
            self.Lists = list()

            # Retrive all the boards of the user
            self.Boards = json.loads(self.tool.get_boards().content.decode())

            # For each board, extract the information on their lists.
            for board in self.Boards:
                self.Lists += self.extract_lists(board)

            # for each list, extract the information on their cards
            for _list in self.Lists:
                _list_id = _list.get('id')
                list_json = json.loads(
                    self.tool.get_list(_list_id).content.decode())
                cards_list = self.extract_cards(list_json)
                self.Cards += cards_list

            # Data is now up to date
            self.dirty = False

    def login(self):
        """
        Login process. Authroizes a user, setup the trello
        connector then initializes their data.
        """
        print("Authorize application by loggin in at your browser.")
        self.credentials = auth.authorize(8080)
        if 'key' in self.credentials and 'token' in self.credentials:
            self.authenticated = True
            self.tool = model.TrelloTool(self.credentials)
            print("Connected with Trello")
            self.initialize()
            print("Retrieved data")
            return True
        return False

    def logout(self):
        """
        Logout process. Removes logged in user's credentials
        then sets authenticated status to false.
        """
        if self.authenticated:
            self.credentials.clear()
            self.authenticated = False
        else:
            print("You are not logged in.")
