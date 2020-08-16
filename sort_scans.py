import os
import re
import shutil
import signal
import sys
import textract
from tempfile import mkstemp
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.completion import WordCompleter

TestCompleter = WordCompleter(['aa', 'zz', 'hush little baby'])

srcpath = Path('/home/gbirke/SynologyDrive/scans')
dest_path = Path('/home/gbirke/SynologyDrive/Dokumente')
preview_link = Path('/tmp/sort_scan_preview.pdf')

destinations = [d.stem for d in dest_path.glob('*') if d.is_dir()]

def create_preview_copy(preview_file):
    _, tmp_name = mkstemp()
    shutil.copy(preview_file, tmp_name)
    os.rename(tmp_name, preview_link)

class DestinationValidator(Validator):
    def validate(self, document):
        text = document.text.strip()
        if text in destinations:
            return
        raise ValidationError(message='Destination not valid')

DestinationList = WordCompleter(destinations)

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

date_match = re.compile(r'^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})')
normalize_whitespace = re.compile(r'\s+')

for srcfile in srcpath.glob('*.pdf'):
    print('{0}'.format(srcfile))
    create_preview_copy(srcfile)
    text = textract.process(srcfile)
    raw_wordlist = normalize_whitespace.sub(' ', str(text, 'utf-8')).split(' ')
    unique_words=set([w for w in raw_wordlist if len(w) > 2])
    NameCompleter = WordCompleter(list(unique_words))
    newname = prompt('File name: ', completer=NameCompleter)

    newname = newname.strip()
    split_date_format = date_match.sub(r"\1_\2_\3_\4_\5_\6", srcfile.stem)
    full_name = "{0} {1}{2}".format(split_date_format, newname, srcfile.suffix)

    destination = prompt('Destination: ',
        validator=DestinationValidator(),
        completer=DestinationList)

    final_destination = dest_path.joinpath(destination, full_name)
    print('Moving {0} to {1}'.format(srcfile, final_destination))
    os.rename(srcfile, final_destination)

