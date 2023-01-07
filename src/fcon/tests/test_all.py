import pytest

from fcon.fcon_new import FconDi, FManager


@pytest.fixture(scope='module')
def di_2anki():
    base = '/home/mithrandir/Projects/ankigen/src/fcon/tests/'

    return FconDi(config={
        'direction': '2anki',
        'fwiki_paths': [
            f'{base}fwikis/fwiki1',
            f'{base}fwikis/fwiki2',
        ],
        'import_2_anki_paths': [
            f'{base}import_to_anki.txt'
        ],
        # 'export_from_anki_path': f'{base}/Projects/ankigen_files/export_from_anki.txt',
        'export_from_anki_path': 'not applicable',
    })


def test_workflow(di_2anki: FconDi):
    di_2anki.workflow().run()


def test_fmanager(di_2anki: FconDi):
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
        'identifier': '/2022 Dec 24, 02:47 4543/', 'question': 'What are the ankigen related directories?',
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
