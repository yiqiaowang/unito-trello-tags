import sys
sys.path.append('ttags/')
import unittest
import app


class AppTest(unittest.TestCase):

    def setUp(self):
        self.App = app.TrelloApp()
        self.App.Cards = [{
            'name': 'card1',
            'id': 'id1',
            'labels': [
                {'name': 'label1',
                 'id': 'labelid1'},
                {'name': 'label2',
                 'id': 'labelid2'}
            ]
        }, {
            'name': 'card1',
            'id': 'id1',
            'labels': [
                {'name': 'labell1',
                 'id': 'labelid1'},
                {'name': 'labell2',
                 'id': 'labelid2'}
            ]
        }]

    def test_parse_boards_json(self):
        boards = [
            {
                'name': 'board1',
                'details': 'bla bla',
                'id': 'id1',
                'lists': [
                    {
                        'name': 'list1',
                        'id': 'id100',
                        'desc': 'asdf'
                    }
                ]
            }
        ]
        parsed = app.TrelloApp.parse_boards_json(boards)

        expected = [
            {
                'name': 'board1',
                'id': 'id1',
                'lists': [
                    {
                        'name': 'list1',
                        'id': 'id100'
                    }
                ]
            }
        ]

        self.assertTrue(parsed == expected)

    def test_extract_lists(self):
        board = {
            'name': 'board1',
            'lists': [
                {
                    'name': 'list1',
                    'id': 'id1'
                },
                {
                    'name': 'list2',
                    'id': 'id2'
                }
            ]
        }

        extracted = app.TrelloApp.extract_lists(board)

        expected = [
            {
                'name': 'list1',
                'id': 'id1'
            },
            {
                'name': 'list2',
                'id': 'id2'
            }
        ]

        self.assertTrue(expected == extracted)

    def test_extract_cards(self):
        arr_of_cards = [
            {'name': 'card1',
             'id': 'id1',
             'labels': [{
                 'name': 'label1',
                 'id': 'idlabel1'
             }],
             'details': 'bla bla'
             }
        ]

        extracted = app.TrelloApp.extract_cards(arr_of_cards)
        expected = [
            {'name': 'card1',
             'id': 'id1',
             'labels': [{
                 'name': 'label1',
                 'id': 'idlabel1'
             }]
             }
        ]

        self.assertTrue(extracted == expected)

    def test_prepare_labels(self):
        prep_cards = self.App.prepare_labels(self.App.Cards)

        label_card_map = prep_cards[0]
        name_label_map = prep_cards[1]

        label = ('label1', 'labelid1')
        self.assertTrue(label in label_card_map.keys())
        self.assertTrue('label1' in name_label_map.keys())

    def test_get_similar_simple(self):
        label_names = ['foo', 'foi', 'bar', 'bae']

        expected_label_groups = [['foo', 'foi'], ['bar', 'bae']]
        label_groups = self.App.get_similar_simple(label_names)

        for group in expected_label_groups:
            group.sort()
        expected_label_groups.sort()

        for group in label_groups:
            group.sort()
        label_groups.sort()

        self.assertTrue(expected_label_groups == label_groups)

    def test_get_similar_leven(self):
        label_names = ['foo', 'foi', 'bar', 'bae']

        expected_label_groups = [['foo', 'foi'], ['bar', 'bae']]
        label_groups = self.App.get_similar_leven(label_names)

        for group in expected_label_groups:
            group.sort()
        expected_label_groups.sort()

        for group in label_groups:
            group.sort()
        label_groups.sort()

        self.assertTrue(expected_label_groups == label_groups)


if __name__ == '__main__':
    unittest.main()
