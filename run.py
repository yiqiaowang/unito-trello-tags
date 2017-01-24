import cmd
import sys
sys.path.append('./ttags/')
from app import TrelloApp
from pprint import pprint

class TrelloCLI(cmd.Cmd):
    intro = 'Welcome to TrelloTags. Type help or ? to list commands.\n'
    prompt = '(TrelloTags) > '

    def __init__(self):
        super(TrelloCLI, self).__init__()
        self.app = TrelloApp()

    def do_login(self, arg):
        """Start a TrelloTags session."""
        try:
            if self.app.login():
                print("Logged in.")
        except FileNotFoundError:
            print("Configuration file not found. Place in ttargs as client_credentials.json.")
    def do_logout(self, arg):
        """Logout of your current session."""
        if self.app.authenticated:
            self.app.logout()
            print("Logged out.")
        else:
            print("Not logged in. Doing nothing.")

    def do_suggest(self, arg):
        """
        Find similar labels and merge them. Only works if you are logged in.
        """
        if self.app.authenticated:
            self.app.suggest_similar()
        else:
            print("Sorry, you are not logged in. Log in with 'login'.")

    def do_reinit(self, arg):
        """
        Reinitialize the data. May solve some errors caused by old data.
        Must be logged in.
        """
        if self.app.authenticated:
            self.app.initialize()
        else:
            print("Sorry, you are not logged in. Log in with 'login'.")
    
    def do_show(self,arg):
        """Prints out all the data currently stored."""
        pprint("Boards: {}".format(self.app.Boards))
        pprint("Lists: {}".format(self.app.Lists))
        pprint("Cards: {}".format(self.app.Cards))

    def do_quit(self, arg):
        """Quit TrelloTags."""
        sys.exit()


# try it out
if __name__ == '__main__':
    TrelloCLI().cmdloop()
