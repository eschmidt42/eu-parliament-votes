# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_parsing_roll_call_votes.ipynb (unless otherwise specified).

__all__ = ['get_ix', 'useful_string', 'SummaryParser', 'VotesParser', 'get_all_issues']

# Cell
import PyPDF2 as pdf
from pathlib import Path
import typing
import re
import pandas as pd
import collections
import plotly.express as px
import plotly.graph_objects as go

# Cell
def get_ix(strings:typing.List[str], pattern_fun:typing.Callable): # , must_match:bool=True
    #print(strings)
    return [i for i, s in enumerate(strings) if pattern_fun(s)] # (must_match and s==pattern) or (not must_match and pattern in s)

def useful_string(s):  return ('docx' not in s) and (len(s)>0) \
            and (s != ' ')

# Cell
class SummaryParser:

    pattern = re.compile('(\.\.+)')
    is_toc = lambda self, text: 'SOMMAIRE' in text or 'CONTENTS' in text

    def __init__(self, all_texts:typing.List[str]):

        self.num_pages = len(all_texts)

        self.ix_start, summary_text = self.get_start(all_texts)

        self.vote_names, self.vote_page_numbers = self.parse_names_and_page_numbers(summary_text)

        self.ix_end, summary_text = self.get_end(all_texts, summary_text)

        if self.ix_end > self.ix_start:
            self.vote_names, self.vote_page_numbers = self.parse_names_and_page_numbers(summary_text)

    def get_start(self, all_texts:typing.List[str]):
        ix_start = get_ix(all_texts, self.is_toc)[0]
        return ix_start, all_texts[ix_start]

    def parse_names_and_page_numbers(self, all_texts:typing.List[str]):
        texts = re.split(r'(\d+\.)(\s*[a-zA-Z])', all_texts)

        ix_content = get_ix(texts, self.is_toc)[0]
        texts = texts[ix_content+1:]

        given_number = texts[::3]

        contents = [text0.strip()+text1.strip() for text0, text1 in zip(texts[1::3],
                                                                        texts[2::3])]
        page_numbers, vote_names = [], []

        for text in contents:
            if 'docx' in text:
                _text = text.split('\n')
                _ix = get_ix(_text, lambda x: 'docx' in x)[0]
                _text = '\n'.join(_text[:_ix])
            else:
                _text = text
            try:
                re.search(r'(\d+)$', _text).group()
            except:
                print('failed at parsing', [text], 'to', [_text])

            page_numbers.append(int(re.search(r'(\d+)$', _text).group()))
            vote_names.append(re.sub(r'\.*\d+$', '', _text).strip())

        assert len(vote_names) == len(page_numbers)
        assert len(set(page_numbers)) == len(page_numbers), collections.Counter(page_numbers).most_common()

        return vote_names, [nr-1 for nr in page_numbers]

    def get_end(self, all_texts:typing.List[str], summary_text:str):

        if self.ix_start + 1 == self.vote_page_numbers[0]:
            return self.ix_start, summary_text

        ix_end = self.vote_page_numbers[0]
        summary_text = '\n'.join(all_texts[self.ix_start:ix_end])

        return ix_end, summary_text

    @property
    def df(self):
        return pd.DataFrame({
            'vote name': self.vote_names,
            'start page': self.vote_page_numbers,
            'end page': [nr - 1 for nr in self.vote_page_numbers[1:]] + [self.num_pages]
        })



# Cell
class VotesParser:

    def __init__(self, start_page:int, end_page:int, all_texts:typing.List[str]):
        '`end_page` is inclusive'
        assert start_page <= end_page
        self.start_page = start_page
        self.end_page = end_page

        votes_texts = self.preprocess(all_texts)

        original_votes, vote_corrections = self.check_for_corrections(votes_texts)

        #print(original_votes, vote_corrections)

        self.vote_counts, self.votes = self.parse_votes(original_votes)

        if vote_corrections is not None:
            self.corrections = self.parse_vote_corrections(vote_corrections)

    @property
    def df_votes(self):
        df = []
        for outcome in self.votes:
            for party in self.votes[outcome]:
                df.extend([(mep, outcome, party) for mep in self.votes[outcome][party]])
        return pd.DataFrame(df, columns=['MEP', 'vote', 'Party'])

    @property
    def df_corrections(self):
        df = []
        for outcome in self.votes:
            df.extend([(mep, outcome) for mep in self.corrections[outcome]])
        return pd.DataFrame(df, columns=['MEP', 'vote'])

    def preprocess(self, all_texts:typing.List[str]):
        votes_texts = "\n".join(all_texts[self.start_page:self.end_page+1])

        s = slice(self.start_page, self.end_page+1)
        votes_texts = "\n".join(all_texts[s]).split("\n")

        votes_texts = [text for text in votes_texts if \
                       useful_string(text)]
        return votes_texts

    def parse_votes(self, votes_texts:typing.List[str]):
        #print(votes_texts)

        ix_yes, ix_no, ix_abstain = self.get_yes_no_abstain_indices(votes_texts)

        counts = {
            'yes': int(votes_texts[ix_yes-1]),
            'no': int(votes_texts[ix_no-1]),
            'abstain': int(votes_texts[ix_abstain-1]),
        }
        votes = {
            'yes': self.get_mep_and_party_vote_for_outcome(votes_texts[ix_yes:ix_no-1]),
            'no': self.get_mep_and_party_vote_for_outcome(votes_texts[ix_no:ix_abstain-1]),
            'abstain': self.get_mep_and_party_vote_for_outcome(votes_texts[ix_abstain:])
        }
        #print(counts)
        #print([(k, (x:=[len(val) for val in v.values()]), sum(x)) for k,v in votes.items()])
        return counts, votes

    def get_yes_no_abstain_indices(self, votes_texts):
        ix_yes = min(get_ix(votes_texts, lambda x: x == '+'))
        ix_no = get_ix(votes_texts, lambda x: x == '-')[0]
        ix_abstain = max(get_ix(votes_texts, lambda x: x == '0'))
        assert ix_yes > 0
        assert ix_yes < ix_no
        assert ix_no < ix_abstain
        return ix_yes, ix_no, ix_abstain

    def parse_vote_corrections(self, votes_corrections_texts:typing.List[str]):

        ix_yes, ix_no, ix_abstain = self.get_yes_no_abstain_indices(votes_corrections_texts)

        yes_meps = '\n'.join(votes_corrections_texts[ix_yes+1:ix_no]).split(',')
        no_meps = '\n'.join(votes_corrections_texts[ix_no+1:ix_abstain]).split(',')
        abstain_meps = '\n'.join(votes_corrections_texts[ix_abstain+1:]).split(',')

        return {
            'yes': [self.process_mep(mep) for mep in yes_meps if useful_string(mep.strip())],
            'no': [self.process_mep(mep) for mep in no_meps if useful_string(mep.strip())],
            'abstain': [self.process_mep(mep) for mep in abstain_meps if useful_string(mep.strip())]
        }

    def get_mep_and_party_vote_for_outcome(self, votes_texts:typing.List[str]):

        ix_party = [(i,text) for i, text in enumerate(votes_texts)\
                    if len(text)>0 and (':' == text[0] or ':' == text[-1])]

        ix_party = [i if (text[-1]==':' and len(text)>1) else i-1 for i, text in ix_party]
        parties = [votes_texts[ix] for ix in ix_party]
        meps = [','.join(votes_texts[ix0+1:ix1]).split(',') for ix0, ix1 in
                zip(ix_party, ix_party[1:]+[len(votes_texts)])]
        votes = {party: [self.process_mep(mep) for mep in _meps if useful_string(mep.strip())] for party, _meps in zip(parties, meps)}

        return votes

    def process_mep(self, mep:str, placeholder:str='unknown mep'):
        mep = mep.strip()
        if ':' in mep:
            if mep.startswith(':'):
                mep = mep[1:]
            if mep.endswith(':'):
                mep = mep[:-1]
        if mep == '':
            mep = placeholder
        return mep

    def check_for_corrections(self, votes_texts:typing.List[str]):

        ix = get_ix(votes_texts, lambda x: 'CORRECCIONES E INTENCIONES DE VOTO' in x)
        assert len(ix) <= 1
        no_corrections = len(ix) == 0
        if no_corrections:
            return votes_texts, None
        else:
            return votes_texts[:ix[0]], votes_texts[ix[0]:]

# Cell
def get_all_issues(df_summary:pd.DataFrame, all_texts:typing.List[str]):
    all_votes, all_corrections = [], []
    all_counts = []

    for i,row in df_summary.iterrows():
        votes = VotesParser(row['start page'], row['end page'], all_texts)

        df_votes = votes.df_votes
        df_votes['vote name'] = row['vote name']
        all_votes.append(df_votes)

        counts = votes.vote_counts
        counts['vote name'] = row['vote name']
        all_counts.append(counts)

        df_corrections = votes.df_corrections
        df_corrections['vote name'] = row['vote name']
        all_corrections.append(df_corrections)

    all_counts = pd.DataFrame(all_counts)
    all_votes = pd.concat(all_votes)
    all_corrections = pd.concat(all_corrections)
    return all_counts, all_votes, all_corrections