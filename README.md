# Trello Tags

Identify similar Trello labels and optionally merge Trello labels across lists and boards.
___

### Features

 * OAuth
 * Command line interface
 * Label merge


### Documentation
___
#### How do I use this?
First, make sure you have the dependencies installed. Refer to requirements.txt.
Install with:
```
pip install -r /path/to/requirements.txt
```
It is worth noting that python-levenshtein is optional, but installing it does silence some warnings given by FuzzyWuzzy.

Once the dependecies are installed, start the CLI with.
```
python run.py
```
Once inside the program, all the available commands will be displayed.

To view similar labels, login with ``` login ``` and ask for similar labels with ```suggest```. At this point, you will be shown similar labels and given the option to merge them under one of the labels. This should work even if multiple cards share labels.


#### Issues to know about
1. If there are multiple labels with the same name, you are not able to pick which of the two you intend to use when merging similar labels. It is possible to differentiate by prompting the user to pick between the two different label IDs. When this case arrises, a warning is given.
2. I've included the client keys and secret for a throwaway Trello account. All testing was done on this account.
3. Performance could be improved. Merging took a few seconds when testing, however this may be my network's fault.
#### Running the tests
Be in the project root and test with:
```
python -m unittest
```

