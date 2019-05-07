import kenlm
import argparse


def _score(text, lm, bos=False, eos=False):
    scr = lm.score(text, bos=bos, eos=eos)
    if args.debug:
        print("Score: {}\t{}".format(text, scr))
    return scr

def _add_pipes(inp, lm):
    # A PIPE token is inserted between two words of the inp and it's score is checked. 
    # This way, PIPE is checked at all locations between two words, basically, checking
    # for all possible locations of a sentence break. The one with the highest LM score 
    # is finally returned. 

    scr_max = _score(inp, lm)
    out = inp
    inp = inp.split()
    for i in range(1, len(inp)+1):
        # Add PIPE at the i-th index in text_blob. Note using | as PIPE
        tmp = " ".join(inp[:i] + ['|'] + inp[i:]).strip()
        scr_tmp = _score(tmp, lm)
        # Store the best n-gram according to the LM
        if scr_tmp > scr_max:
            scr_max = scr_tmp
            out = tmp
    return out.strip()



def get_all_sentences(inp_text, lm):
    all_sents = []
    inp_to_check  = [inp_text]
    while inp_to_check:
        # The PIPE in means there are two smaller sentences besides it. 
        # But those smaller sentences again need to be checked for further smaller sentences, until no-more PIPEs are added
        sents = _add_pipes(inp_to_check[0], lm)
        sents = [s.strip() for s in sents.split('|') if s.strip()]
        if len(sents) > 1:
            # Implies the inp_to_check[0] string was broken down into smaller sentences
            inp_to_check.extend(sents)
            inp_to_check.pop(0) # Since this str is checked just now
        else:
            # The sentence could not be broken down further into more sentences.
            # Hence, add this one to all_sents
            all_sents.append(sents[0])
            inp_to_check.pop(0) # Since this str is checked just now

    return all_sents


def get_questions(all_sents, lm):
    all_ques = []
    for s in all_sents:
        if _score(s + " ?", lm, True, True) > _score(s + " |", lm, True, True):
            # It's a question!
            all_ques.append(s + " ?")

    return all_ques


if __name__ == "__main__":

    import re
    from collections import OrderedDict 
    patterns = OrderedDict()
    patterns['alphanum_word'] = (re.compile(r'\S*\d+\S*'), ' N ') # Anything with a number
    patterns['re_end_puncts'] = (re.compile(r'[?!.]+'), ' | ')
    patterns['not_alphanum_eos'] = (re.compile(r"[^a-zN|]+"), ' ')
    patterns['re_multi_space'] = (re.compile(r'\s{2,}'), ' ')

    global args
    parser = argparse.ArgumentParser(description='Finds questions in unpunctuated raw text')
    parser.add_argument('--text', type=str, help='Input text to be processed')
    parser.add_argument('--input_file', type=str, help='File with texts to be processed. One sample per line')
    parser.add_argument('--output_file', type=str, help='File to write outputs of processed samples. One output per line')
    parser.add_argument('--lm_s', type=str, required=True, help='Path for sentence tokenization LM')
    parser.add_argument('--lm_q', type=str, required=True, help='Path for Question Identification LM')
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()

    # Loading Models
    lm_s = kenlm.Model(args.lm_s)
    lm_q = kenlm.Model(args.lm_q)

    samples = []
    if args.text:
        samples.append(args.text)
    elif args.input_file:
        with open(args.input_file, 'r') as inps:
            for l in inps.readlines():
                l = l.strip().lower()
                for k, v in patterns.items():
                    l = v[0].sub(v[1], l)
                samples.append(l)

    if args.output_file:
        outs = open(args.output_file, 'a')
        outs.write("Sample, Detected sentences, Detected questions\n")

    for i, text in enumerate(samples):
        # Sentence Tokenization
        all_sents = get_all_sentences(text, lm_s)
        # Question Identification
        ques = get_questions(all_sents, lm_q)
        print("\n#{} Sample: {}\n\nSentences:\n{}\n\nQuestions:\n{}\n"\
                .format(i, text, '\n'.join(all_sents), '\n'.join(ques)))
        if args.output_file:
            outs.write("{},{},{}\n".format(text, ' | '.join(all_sents), ' | '.join(ques)))

    if args.output_file:
        outs.close()

