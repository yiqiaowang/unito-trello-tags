import app


def test_run():
    a = app.TrelloApp()
    a.login()
    a.suggest_similar()
    return a

if __name__ == "__main__":
    test = test_run()
