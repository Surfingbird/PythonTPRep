class ElementWithIndex:
    def __init__(self, ListOfElements = [], ListOfIndex = [], MatchedElemIndexe = None):
        self.ListOfElements = ListOfElements
        self.ListOfIndex = ListOfIndex
        self.MatchedElemIndexe = MatchedElemIndexe

    def __del__(self):
        self.ListOfElements = []
        self.ListOfIndex = []
        self.MatchedElemIndexe = []

