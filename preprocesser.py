import os
import argparse
import re
import glob
import tqdm
from collections import OrderedDict 


def _get_patterns(clean_type):
    patterns = OrderedDict()
    if clean_type == "lm_s":
        if not args.newlines:
            patterns['newlines'] = (re.compile(r'[\n\r]+'), ' ')
        patterns['alphanum_word'] = (re.compile(r'\S*\d+\S*'), ' N ') # Anything with a number
        patterns['eos_puncts'] = (re.compile(r"[.!?]+"), ' | ') # End of Sentence Puctuations
        if args.newlines:
            patterns['not_alphanum_pipe'] = (re.compile(r"[^a-zN|\n]+"), ' ')
        else:
            patterns['not_alphanum_pipe'] = (re.compile(r"[^a-zN|]+"), ' ')
        patterns['multi_space'] = (re.compile('\s{2,}'), ' ')
    elif clean_type == "lm_q":
        if not args.newlines:
            patterns['newlines'] = (re.compile(r'[\n\r]+'), ' ')
        patterns['alphanum_word'] = (re.compile(r'\S*\d+\S*'), ' N ') # Anything with a number
        patterns['eos_puncts'] = (re.compile(r"[.!]+"), ' | ') # End of Sentence Puctuations without Question Mark
        patterns['q_mark'] = (re.compile(r"\?+"), ' ? ')
        if args.newlines:
            patterns['not_alphanum_pipe'] = (re.compile(r"[^a-zN|\n]+"), ' ')
        else:
            patterns['not_alphanum_pipe'] = (re.compile(r"[^a-zN|?]+"), ' ')
        patterns['multi_space'] = (re.compile(r'\s{2,}'), ' ')
    else:
        raise ValueError

    return patterns

def clean_file(input_file, output_file, clean_type):
    patterns = _get_patterns(clean_type)

    text = None
    with open(input_file, "r") as inp:
        if args.newlines:
            text = '\n'.join([line.strip().lower() for line in  inp.readlines()])
        else:
            text = inp.read().strip().lower()
        for k, v in patterns.items():
            text = v[0].sub(v[1], text)

    if text:
        with open(output_file, "w") as out:
            if args.newlines:
                text = ' |\n'.join([sent.strip() for sent in text.split('|')])
                text = ' ?\n'.join([sent.strip() for sent in text.split('?')])
            out.write(text)


if __name__ == "__main__":

    from multiprocessing import Pool
    global args
    parser = argparse.ArgumentParser(description='PreProcessing the raw files')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing files to be processed')
    parser.add_argument('--output_dir', type=str, required=True, help='Destination Directory')
    parser.add_argument('--clean_type', type=str, choices=['lm_s', 'lm_q'], required=True, help='What kind of processing do you want.')
    parser.add_argument('--keep_newlines', dest="newlines", default=False, action="store_true")

    args = parser.parse_args()

    try:
        os.makedirs(args.output_dir)
    except OSError:
        check = input("'output_dir' already exists. Are you sure you want to continue? (y/n)")
        if check.lower() in ['n', 'no', 'no.']:
            exit(1)
    
    input_files = glob.glob(os.path.join(args.input_dir, "**"), recursive=True)
    data_to_process = []
    for input_file in input_files:
        file_name = os.path.basename(input_file)
        output_file = os.path.join(args.output_dir, file_name)
        data_to_process.append((input_file, output_file, args.clean_type))

    with Pool() as pool:
        pool.starmap(clean_file, data_to_process)

#    for input_file in tqdm.tqdm(input_files, desc="Cleaning under progress", total=len(input_files)):
#        if not os.path.isdir(input_file):
#            file_name = os.path.basename(input_file)
#            output_file = os.path.join(args.output_dir, file_name)
#            clean_file(input_file, output_file, args.clean_type)

