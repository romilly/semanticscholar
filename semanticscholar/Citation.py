class Citation:
    def __init__(self, data):
        self.citing_paper_id = None
        self.is_influential = None
        self.title = None
        self._init_attributes(data)

    def _init_attributes(self, data):
        self.is_influential = data['isInfluential']
        citingPaper = data['citingPaper']
        self.citing_paper_id = citingPaper['paperId']
        self.title = citingPaper['title']

    def __str__(self) -> str:
        return f'Citation({self.citing_paper_id}:{self.title})'

    def __repr__(self) -> str:
        return self.__str__()



