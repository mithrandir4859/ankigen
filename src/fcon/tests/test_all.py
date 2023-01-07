import pytest

from fcon.fcon_new import FconDi, FManager
from utils_i import setup_logger


def create_di(direction):
    base = '/home/mithrandir/Projects/ankigen/src/fcon/tests/'

    return FconDi(config={
        'direction': direction,
        'fwiki_paths': [
            f'{base}fwikis/fwiki1',
            f'{base}fwikis/fwiki2',
        ],
        'import_2_anki_paths': [
            f'{base}import_to_anki.txt'
        ],
        'export_from_anki_path': f'{base}/export_from_anki.txt',
    })


@pytest.fixture(scope='module', autouse=True)
def setup():
    setup_logger()


@pytest.fixture(scope='module')
def di_2anki():
    return create_di('2anki')


@pytest.fixture(scope='module')
def di_2fwiki():
    return create_di('2fwiki')


def test_workflow_di_2anki(di_2anki: FconDi):
    di_2anki.workflow().run()


def test_fmanager_di_2anki(di_2anki: FconDi):
    fmanager: FManager = di_2anki.reader().read_cards()

    assert fmanager
    assert len(fmanager) == 3
    assert fmanager.keys() == {
        '/2022 Dec 24, 02:47 4543/',
        '/2022 Dec 21, 22:44 4158/',
        '/2023 Jan 05, 14:24 2622/'
    }

    assert fmanager[0].dict() == {
        'identifier': '/2022 Dec 21, 22:44 4158/',
        'question': 'why?\ntags: #ai, #bitcoin',
        'answer': 'Answer.\n\nMore answer.\n\nMore details.\n\ntags: #crypto', 'tags': [],
        'original_text': '\nq: why?\ntags: #ai, #bitcoin \n/2022 Dec 21, 22:44 4158/\n\nAnswer.\n\nMore answer.\n\nMore details.\n\ntags: #crypto\n',
        'original_file': '/home/mithrandir/Projects/ankigen/src/fcon/tests/fwikis/fwiki1/nested_dir/docs_4_test_2.md'
    }

    assert fmanager[1].dict() == {
        'identifier': '/2022 Dec 24, 02:47 4543/',
        'question': 'What are the ankigen related directories?',
        'answer': 'Temporary: `~/Projects/ankigen_files/`\nPersonal: `~/Projects/constitution/zettelkasten/`\nMednition: `~/Mednition/wiki_mednition/wiki_fresh/`',
        'tags': [],
        'original_text': '\nq: What are the ankigen related directories?\n/2022 Dec 24, 02:47 4543/\n\nTemporary: `~/Projects/ankigen_files/`\nPersonal: `~/Projects/constitution/zettelkasten/`\nMednition: `~/Mednition/wiki_mednition/wiki_fresh/`\n',
        'original_file': '/home/mithrandir/Projects/ankigen/src/fcon/tests/fwikis/fwiki1/docs_4_test_1.md'
    }
    assert fmanager[2].dict() == {
        'identifier': '/2023 Jan 05, 14:24 2622/',
        'question': 'Should we fetch reason for visit before other transformers like parser?',
        'answer': 'Yes, such order makes sense. This way all the parsing may still happen in the parsing class like `EpicCdshParser`.',
        'tags': [],
        'original_text': '\nq: Should we fetch reason for visit before other transformers like parser?\n\n/2023 Jan 05, 14:24 2622/\n\nYes, such order makes sense. This way all the parsing may still happen in the parsing class like `EpicCdshParser`.\n\n',
        'original_file': '/home/mithrandir/Projects/ankigen/src/fcon/tests/fwikis/fwiki2/docs_4_test_3.md'
    }


def test_fmanager_2fwiki(di_2fwiki: FconDi):
    reader = di_2fwiki.reader()
    fmanager: FManager = reader.read_cards()

    assert len(fmanager) == 3
    # assert fmanager[0].dict() == {
    #     'identifier': '/2022 Dec 21, 22:44 4158/',
    #     'question': 'How do we use FHIR currently in Kate in Cerner integrations?',
    #     'answer': 'We call FHIR to retrieve fhir patient id, fhir encounter id. We do that right after parsing, because it is the earliest moment when we have enough data to perform the necessary FHIR calls. We call FHIR in a separate thread and store results into mongo in order to not block further message processing (tagging, fx, etc). See this: if self.flag_manager.is_epic_env: self.fhir_ids_retriever = Singleton(EpicIdsRetriever, self.cerner_notification_service) else: self.fhir_ids_retriever = Singleton( CernerIdsRetriever, self.cerner_notification_service, hospitals_to_ignore=self.flag_manager.do_not_preretrieve_external_ids_for )Also this: @wrap_into_list def _get_transformers(self, pretagging, posttagging): yield from pretagging if self.ffm.use_fhir_ids_retriever: yield self.common_di.fhir_ids_retriever if self.ffm.post_kate_readiness_asap: yield Singleton( KateReadinessAsapPoster, self.common_di.cerner_notification_service )Also this: def _handle_mappings_in_another_thread_if_necessary(self, external_ids, hospital): external_ids_copy = ExternalIds(**dict(external_ids.to_mongo())) external_ids_copy.hospital = hospital thread = Thread(target=self.handle_mappings, args=(external_ids_copy,)) thread.start()',
    #     'tags': [], 'original_text': None, 'original_file': None
    # }
    assert fmanager[1].dict() == {
        'identifier': '/2022 Dec 22, 01:02 1153/',
        'question': 'Assuming we will make on average at least 3 data fhir calls per encounter, should we process each response individually or together?',
        'answer': 'The question may be rephrased as: should we parse, tag, fx each '
                  'response separately and then merge the data together or should we '
                  'merge the data before parsing?\n'
                  '\n'
                  'Different FHIR endpoints would return different data which will '
                  'require different parsing,\n'
                  'tagging, feature extraction, so it is only natural that processing '
                  'of various responses would be set up differently and will happen '
                  'individually.',
        'tags': [], 'original_text': None, 'original_file': None
    }
    assert fmanager[2].dict() == {
        'identifier': '/2022 Dec 24, 02:47 4543/',
        'question': 'What is the limit when it comes to processing each FHIR response '
                    'individually? What if we know for sure that data from a certain '
                    'FHIR endpoint alone will never be sufficient to trigger a '
                    'meaningful prediction?',
        'answer': '__TLDR__: allow arbitrary grouping of FHIR calls into so-called '
                  '`FhirCallsTrigger`s.\n'
                  '\n'
                  'Such a question may seriously arise in some later implementations. '
                  'Currently we expect that we will receive significant amount of '
                  'data in hl7 and adding the data from FHIR (most notably, reason '
                  'for visit) may easily trigger the prediction together with hl7 '
                  'data.\n'
                  '\n'
                  'Processing each FHIR response individually also makes great sense '
                  'if we will be forced to call FHIR each N seconds to check whether '
                  'some fresh data has become available.\n'
                  '\n'
                  'We are also not really forced to make each and every fhir call its '
                  'own decision. We may arbitrarily group fhir calls if the need '
                  'arises. Such a group may be called `FhirCallsTrigger`. Right now '
                  'each hl7 message is a decision trigger (talking conceptually now, '
                  'there is no such class in the code). Now we would introduce '
                  'decision triggers that fetch data from fhir. Second-order '
                  'notifications may also be conceptualized and/or refactored as '
                  'decision triggers.',
        'tags': [], 'original_text': None, 'original_file': None
    }


def test_workflow_di_2fwiki(di_2fwiki: FconDi):
    workflow = di_2fwiki.workflow()
    workflow.run()
