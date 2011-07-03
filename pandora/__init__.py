from pandora import Pandora

# setuptools helper
DATA_FILES = ['crypt_key_input.h', 'crypt_key_output.h']

def get_pkg_data_files():
    import pkg_resources
    for file in DATA_FILES:
        yield (file, pkg_resources.resource_filename('pandora', file))