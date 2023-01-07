import pytest

from fcon.fcon_new import FconDi


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

#
# def test_workflow(di_2anki: FconDi):
#     di_2anki.workflow().run()


def test_fmanager(di_2anki: FconDi):
    fmanager = di_2anki.reader().read_cards()

    assert fmanager
    assert len(fmanager) == 3
