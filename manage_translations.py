#!/usr/bin/env python
#
# This python file contains utility scripts to manage Django docs translations.
# It has to be run inside the django-docs-translations git root directory.
#
# The following command is available:
#
# * fetch: fetch translations from transifex.com and strip source lines from the
#          files.

import os
from argparse import ArgumentParser
from subprocess import call

# intro and index ressources must be fully translated for these languages
ACTIVE_LANGUAGES = ['el', 'es', 'fr', 'id', 'ja', 'pt_BR']


def fetch(resources=None, languages=None):
    """
    Fetch translations from Transifex, remove source lines.
    """
    if languages is None:
        languages = ACTIVE_LANGUAGES
    for lang in languages:
        call('tx pull -l %(lang)s --minimum-perc=5' % {'lang': lang}, shell=True)
        lang_dir = 'translations/%(lang)s/LC_MESSAGES/' % {'lang': lang}
        for po_file in os.listdir(lang_dir):
            if not po_file.endswith(".po"):
                continue
            po_path = os.path.join(lang_dir, po_file)
            print(po_path)
            call('msgcat --no-location -o %s %s' % (po_path, po_path), shell=True)


if __name__ == "__main__":
    RUNABLE_SCRIPTS = ('fetch',)

    parser = ArgumentParser()
    parser.add_argument('cmd', nargs=1, choices=RUNABLE_SCRIPTS)
    parser.add_argument("-r", "--resources", action='append', help="limit operation to the specified resources")
    parser.add_argument("-l", "--languages", action='append', help="limit operation to the specified languages")
    options = parser.parse_args()

    eval(options.cmd[0])(options.resources, options.languages)
