from configparser import ConfigParser

def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    if parser.has_section(section):
        return {k: v for k, v in parser.items(section)}
    else:
        raise Exception(f'Section {section} not found in {filename}')