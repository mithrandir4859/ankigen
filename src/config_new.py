from utils_i import merge_recursively

base = '/home/mithrandir/'

__default_config = {
    'fcon': {
        'direction': '2anki',
        # 'direction': '2fwiki',
        'fwiki_paths': [
            f'{base}Mednition/wiki_mednition/wiki_fresh/',
            f'{base}Projects/constitution/zettelkasten/',
        ],
        'import_2_anki_paths': [
            f'{base}Projects/ankigen_files/import_to_anki.txt'
        ],
        'export_from_anki_path': f'{base}/Projects/ankigen_files/export_from_anki.txt',
    },
    'cbgen': {
        'output_path': f'{base}Documents/sensitive/cbgen/cbgen.md'
    },
    'keys': {
        "openai_key": "aa-aaaaaaaaaaaaaaaá"
    }
}

try:
    from config_new_gitignored import config_override

    config = merge_recursively(__default_config, config_override)
    print('config override was applied successfully')
except ImportError:
    config = __default_config

fcon_config = config['fcon']
