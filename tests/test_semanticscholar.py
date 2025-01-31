import json
import unittest
from datetime import datetime

import vcr
from requests.exceptions import Timeout

from semanticscholar.Author import Author
from semanticscholar.Journal import Journal
from semanticscholar.Paper import Paper
from semanticscholar.SemanticScholar import SemanticScholar
from semanticscholar.SemanticScholarException import (
    BadQueryParametersException, ObjectNotFoundExeception)
from semanticscholar.Tldr import Tldr

test_vcr = vcr.VCR(
    cassette_library_dir='tests/data',
    path_transformer=vcr.VCR.ensure_suffix('.yaml')
)


class SemanticScholarTest(unittest.TestCase):

    def setUp(self) -> None:
        self.sch = SemanticScholar()

    def test_author(self) -> None:
        file = open('tests/data/Author.json', encoding='utf-8')
        data = json.loads(file.read())
        item = Author(data)
        self.assertEqual(item.affiliations, data['affiliations'])
        self.assertEqual(item.aliases, data['aliases'])
        self.assertEqual(item.authorId, data['authorId'])
        self.assertEqual(item.citationCount, data['citationCount'])
        self.assertEqual(item.externalIds, data['externalIds'])
        self.assertEqual(item.hIndex, data['hIndex'])
        self.assertEqual(item.homepage, data['homepage'])
        self.assertEqual(item.name, data['name'])
        self.assertEqual(item.paperCount, data['paperCount'])
        self.assertEqual(str(item.papers), str(data['papers']))
        self.assertEqual(item.url, data['url'])
        self.assertEqual(item.raw_data, data)
        self.assertEqual(str(item), str(data))
        self.assertEqual(item['name'], data['name'])
        self.assertEqual(item.keys(), data.keys())
        file.close()

    def test_journal(self) -> None:
        file = open('tests/data/Paper.json', encoding='utf-8')
        data = json.loads(file.read())['journal']
        item = Journal(data)
        self.assertEqual(item.name, data['name'])
        self.assertEqual(item.pages, data['pages'])
        self.assertEqual(item.volume, data['volume'])
        self.assertEqual(item.raw_data, data)
        file.close()

    def test_paper(self) -> None:
        file = open('tests/data/Paper.json', encoding='utf-8')
        data = json.loads(file.read())
        item = Paper(data)
        self.assertEqual(item.abstract, data['abstract'])
        self.assertEqual(str(item.authors), str(data['authors']))
        self.assertEqual(item.citationCount, data['citationCount'])
        self.assertEqual(str(item.citations), str(data['citations']))
        self.assertEqual(item.corpusId, data['corpusId'])
        self.assertEqual(item.embedding, data['embedding'])
        self.assertEqual(item.externalIds, data['externalIds'])
        self.assertEqual(item.fieldsOfStudy, data['fieldsOfStudy'])
        self.assertEqual(item.influentialCitationCount,
                         data['influentialCitationCount'])
        self.assertEqual(item.isOpenAccess, data['isOpenAccess'])
        self.assertEqual(str(item.journal), str(data['journal']['name']))
        self.assertEqual(item.openAccessPdf, data['openAccessPdf'])
        self.assertEqual(item.paperId, data['paperId'])
        self.assertEqual(item.publicationDate, datetime.strptime(
            data['publicationDate'], '%Y-%m-%d'))
        self.assertEqual(item.publicationTypes, data['publicationTypes'])
        self.assertEqual(item.publicationVenue, data['publicationVenue'])
        self.assertEqual(item.referenceCount, data['referenceCount'])
        self.assertEqual(str(item.references), str(data['references']))
        self.assertEqual(item.s2FieldsOfStudy, data['s2FieldsOfStudy'])
        self.assertEqual(item.title, data['title'])
        self.assertEqual(str(item.tldr), data['tldr']['text'])
        self.assertEqual(item.url, data['url'])
        self.assertEqual(item.venue, data['venue'])
        self.assertEqual(item.year, data['year'])
        self.assertEqual(item.raw_data, data)
        self.assertEqual(str(item), str(data))
        self.assertEqual(item['title'], data['title'])
        self.assertEqual(item.keys(), data.keys())
        file.close()

    def test_tldr(self) -> None:
        file = open('tests/data/Paper.json', encoding='utf-8')
        data = json.loads(file.read())['tldr']
        item = Tldr(data)
        self.assertEqual(item.model, data['model'])
        self.assertEqual(item.text, data['text'])
        self.assertEqual(item.raw_data, data)
        self.assertEqual(str(item), data['text'])
        file.close()

    @test_vcr.use_cassette
    def test_get_paper(self):
        data = self.sch.get_paper('10.1093/mind/lix.236.433')
        self.assertEqual(data.title,
                         'Computing Machinery and Intelligence')
        self.assertEqual(data.raw_data['title'],
                         'Computing Machinery and Intelligence')

    @test_vcr.use_cassette
    def test_get_papers(self):
        list_of_paper_ids = [
            'CorpusId:470667',
            '10.2139/ssrn.2250500',
            '0f40b1f08821e22e859c6050916cec3667778613']
        data = self.sch.get_papers(list_of_paper_ids)
        for item in data:
            with self.subTest(subtest=item.paperId):
                self.assertIn(
                    'E. Duflo', [author.name for author in item.authors])

    @test_vcr.use_cassette
    def test_timeout(self):
        self.sch.timeout = 0.01
        self.assertEqual(self.sch.timeout, 0.01)
        self.assertRaises(Timeout,
                          self.sch.get_paper,
                          '10.1093/mind/lix.236.433')

    @test_vcr.use_cassette
    def test_get_author(self):
        data = self.sch.get_author(2262347)
        self.assertEqual(data.name, 'A. Turing')

    @test_vcr.use_cassette
    def test_get_authors(self):
        list_of_author_ids = ['3234559', '1726629', '1711844']
        data = self.sch.get_authors(list_of_author_ids)
        list_of_author_names = ['E. Dijkstra', 'D. Parnas', 'I. Sommerville']
        self.assertCountEqual(
            [item.name for item in data], list_of_author_names)

    @test_vcr.use_cassette
    def test_not_found(self):
        methods = [self.sch.get_paper, self.sch.get_author]
        for method in methods:
            with self.subTest(subtest=method.__name__):
                self.assertRaises(ObjectNotFoundExeception, method, 0)

    @test_vcr.use_cassette
    def test_bad_query_parameters(self):
        self.assertRaises(BadQueryParametersException,
                          self.sch.get_paper,
                          '10.1093/mind/lix.236.433',
                          fields=['unknown'])

    @test_vcr.use_cassette
    def test_search_paper(self):
        data = self.sch.search_paper('turing')
        self.assertGreater(data.total, 0)
        self.assertEqual(data.offset, 0)
        self.assertEqual(data.next, 100)
        self.assertEqual(len(data.items), 100)
        self.assertEqual(
            data.raw_data[0]['title'],
            'Quantum theory, the Church–Turing principle and the universal '
            'quantum computer')

    @test_vcr.use_cassette
    def test_search_paper_next_page(self):
        data = self.sch.search_paper('turing')
        data.next_page()
        self.assertGreater(len(data), 100)

    @test_vcr.use_cassette
    def test_search_paper_traversing_results(self):
        data = self.sch.search_paper('turing')
        all_results = [item.title for item in data]
        self.assertRaises(BadQueryParametersException, data.next_page)
        self.assertEqual(len(all_results), len(data.items))

    @test_vcr.use_cassette
    def test_search_paper_fields_of_study(self):
        data = self.sch.search_paper('turing', fields_of_study=['Mathematics'])
        self.assertEqual(data[0].s2FieldsOfStudy[0]['category'], 'Mathematics')

    @test_vcr.use_cassette
    def test_search_author(self):
        data = self.sch.search_author('turing')
        self.assertGreater(data.total, 0)
        self.assertEqual(data.next, 0)


if __name__ == '__main__':
    unittest.main()
