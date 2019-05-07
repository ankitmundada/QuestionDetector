# QuestionDetector
This is small experiment of using Language Models for sentence tokenization and Question detection


# StringAi Assignment


# Objective 
****----------

Given a text blob ***T***, identify all the questions ***Q_i*** in it. 


# Approach
----------

The problem has to be broken into two sub-problems: 
***Sentence Tokenization***

    Instead of identifying all the questions in ***T*** directly, first we identify all the *sentences*, ***S_i***, in ***T***.

***Question Identification***
**
    For each sentence *S_i* obtained from above, check if it is a question or not.
****
****
# Methodologies
----------


## *Language Model based approach:*

*Basic Idea*
We can extend the training corpus of Language Model to not just include words or characters, but ‘Question Mark ( **?** )’ and ‘End-Of-The-Sentence ( **|** ) tokens as well. 
**
*Language Models*
For each sub-problem in [+StringAi Assignment: Approach](https://paper.dropbox.com/doc/StringAi-Assignment-Approach-SYGyKzf2dLdFv055dReDS#:uid=894719539795993548318257&amp;h2=Approach), a separate  LM is required.

    1. ***LM_s*** (LM for *Sentence Tokenization*): trained on a corpus in which all the Sentence-End-Punctuation Marks (Question Mark, Period, Exclamation Mark etc.) are replaced with a PIPE token
    2. ***LM_q*** (LM for Question Identification): trained on a corpus in which all the Sentence-End-Punctuation Marks except Question Mark are replaced with a PIPE token.  Question Mark is kept as it is.

*Steps for Sentence Tokenization*

1. Add PIPE token to the *text blob* by scoring against *LM_s*. Split the *text* at PIPE and add PIPEs to the splitted outputs, till no further splitting is possible. 
2. Collect all the final splitted outputs as they are the most probable sentences in the original input according the LM
**
 
Sample Code:

    .
    .
    .
    
    def add_pipes(inp):
        # A PIPE token is inserted between two words of the inp and it's score is checked. 
        # This way, PIPE is checked at all locations between two words, basically, checking
        # for all possible locations of a sentence break. The one with the highest LM score 
        # is finally returned. 
    
        scr_max = lm.score(inp)
        out = inp
        for i in range(1, len(inp)):
            # Add PIPE at the i-th index in text_blob. Note using | as PIPE
            tmp = inp.insert(i, '|')
            scr_tmp = lm.score(tmp)
            # Store the best n-gram according to the LM
            if scr_tmp > scr_max:
                scr_max = scr_tmp
                out = tmp
        return out
    
    .
    .
    .
    
    all_sents = []
    def get_all_sentences(inp_text):
        inp_to_check  = [inp_text]
        while inp_to_check:
            # The PIPE in means there are two smaller sentences besides it. 
            # But those smaller sentences again need to be checked for further smaller sentences, until no-more PIPEs are added
            sents = add_pipes(inp_to_check[0]).split('|')
            if len(sents) > 1:
                # Implies the inp_to_check[0] string was broken down into smaller sentences
                inp_to_check.extend(sents)
                inp_to_check.pop(0) # Since this str is checked just now
            else:
                # The sentence could not be broken down further into more sentences.
                # Hence, add this one to all_sents
                all_sents.append(sents[0])
        

`NOTE:  The` `***get_all_sentences***` `function above can also be run recursively. But because of Python``'``s recursion limits, I``'``ve not done so`

*Steps for Question Identification*

Steps:

1. Score each sentence above by Lm_q to see if it’s actually a question or not.

Sample Code

    .
    .
    .
    all_ques = []
    for s in all_sents: # NOTE: all_sents is obtained from above
        if lm_q.score(s + " ?") > lm_q.score(s + "|"):
            # It's a question!
            all_ques.add(s)
    .
    .
    .


*******Experiments***
******The code for this approach can be found at:**

https://github.com/ankitmundada/QuestionDetector




    Datasets used for training the LMs: 
    1. Gutenberg Books Dataset: https://web.eecs.umich.edu/~lahiri/gutenberg_dataset.html
    2. SimpliWiki English Dump: https://dumps.wikimedia.org/simplewiki/latest/
    
      Number of Lines in the dataset: ~25 Million
      Size of the dataset: 1.3 Gb


*Pros and Cons*

| Pros                                                               | Cons                                                         |
| ------------------------------------------------------------------ | ------------------------------------------------------------ |
| Language Models are generally faster and easier to experiment with | This is an unconventional use-case for a LM                  |
| Not many hyper-parameters to tune                                  | Need to be compared with Deep Learning and NLP based methods |
| -                                                                  | Data cleaning needs to be aggressive                         |


***Some sample results of this approach:***

https://github.com/ankitmundada/QuestionDetector/blob/master/sample_outputs1.csv


*Please Note: The results are very preliminary, since the models are trained on very small datasets.* 



