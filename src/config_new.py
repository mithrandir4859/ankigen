from utils_i import merge_recursively

__default_config = {
    'fcon': {
        'direction': '2anki',
        # 'direction': '2fwiki',
    }
}

try:
    from config_new_gitignored import config_override

    config = merge_recursively(__default_config, config_override)
    print('config override was applied successfully')
except ImportError:
    config = __default_config

fcon_config = config['fcon']
