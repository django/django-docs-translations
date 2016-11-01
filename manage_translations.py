#!/usr/bin/env python
#
# This python file contains utility scripts to manage Django docs translations.
# It has to be run inside the django-docs-translations git root directory.
#
# The following command is available:
#
# * fetch: fetch translations from transifex.com and strip source lines from the
#          files.
# * robots_txt: produce a robots.txt file excluding resources with less than 90%
#               of translated strings
from __future__ import division

import os
import re
from argparse import ArgumentParser
from subprocess import PIPE, Popen, call, check_output

# intro and index ressources must be fully translated for these languages
ACTIVE_LANGUAGES = ['el', 'es', 'fr', 'id', 'ja', 'pt_BR']
# See https://www.transifex.com/django/django-docs/content/
ALL_RESOURCES = [
    'contents', 'faq', 'glossary', 'howto', 'index', 'internals', 'intro', 'misc',
    'ref', 'releases', 'topics',
]


def _current_version():
    """
    Return the Django version of the current git branch: 'dev', '1.10, ...
    """
    branch_name = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
    if branch_name == 'master':
        return 'dev'
    else:
        return branch_name.split('/')[1].replace('.x', '')


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


def robots_txt(*args):
    """
    Output a robots.txt file excluding resources with less than 90% of translated strings.
    """
    robots_content = ['User-agent: *']
    env = os.environ.copy()
    env['LANG'] = 'C'
    version = _current_version()
    for lang in ACTIVE_LANGUAGES:
        lang_dir = 'translations/%(lang)s/LC_MESSAGES/' % {'lang': lang}
        for res in ALL_RESOURCES:
            po_path = os.path.join(lang_dir, '%s.po' % res)
            if not os.path.exists(po_path):
                perc = 0
            else:
                # Calculate po file statistics
                p = Popen(['msgfmt', '-cv', '-o', '/dev/null', po_path], env=env,
                          stdout=PIPE, stderr=PIPE)
                _, errors = p.communicate()
                errors = errors.decode()
                r_tr = re.search(r"([0-9]+) translated", errors)
                r_un = re.search(r"([0-9]+) untranslated", errors)
                r_fz = re.search(r"([0-9]+) fuzzy", errors)
                translated = int(r_tr.group(1)) if r_tr else 0
                untranslated = int(r_un.group(1)) if r_un else 0
                fuzzy = int(r_fz.group(1)) if r_fz else 0
                perc = int(translated / (translated + untranslated + fuzzy) * 100)
            if perc < 90:
                # Write a line in robots.txt
                robots_content.append('Disallow: /%(lang)s/%(version)s/%(res)s' % {
                    'lang': lang,
                    'version': version,
                    'res': res,
                })
    print("\n".join(robots_content))


if __name__ == "__main__":
    RUNABLE_SCRIPTS = ('fetch', 'robots_txt')

    parser = ArgumentParser()
    parser.add_argument('cmd', nargs=1, choices=RUNABLE_SCRIPTS)
    parser.add_argument("-r", "--resources", action='append', help="limit operation to the specified resources")
    parser.add_argument("-l", "--languages", action='append', help="limit operation to the specified languages")
    options = parser.parse_args()

    eval(options.cmd[0])(options.resources, options.languages)
