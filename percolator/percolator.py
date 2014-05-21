'''

TODO:
* Make this file a script that accepts two files
    1) queries files: 1 query per line (utf8)
    2) data file: 1 text item per line (utf8)

    * The output will be similar to data file except
    that each line will be prefixed with line numbers
    of the matching queries from queries file.

* Document the methods of this file so someone can
understand some of the more intricate parts of the code.

* Make this installable with pip (whoosh dependency)
* Write a README and provide sample queries and data files
for testing. Also describe the limitations of the query. eg:
no NOT. phrases cannot be longer than N words etc.

* During installation, install a script called percolate
that has the functionality of a script as mentioned above

* Do performance testing
'''

import sys
import hashlib
import argparse
import unicodedata
from collections import defaultdict
from itertools import product

from whoosh.qparser import QueryParser
from whoosh.query import And, Or
from whoosh.query.terms import Term
from whoosh.query.positional import Phrase

def make_translation_table():
    T = {}
    T[ord(u'\n')] = u' '
    T[ord(u'\r')] = u' '

    for i in xrange(sys.maxunicode):
        ch = unichr(i)

        # punctuation -> space
        if unicodedata.category(ch).startswith('P'):
            T[i] = u' '
            continue

        # upper -> lower
        if ch != ch.lower():
            T[i] = ch.lower()

    return T

TRANS_TBL = make_translation_table()

def clean(t):
    # Lower case and remove punctuations, newlines.
    return t.translate(TRANS_TBL)

def ngrams(s, min=1, max=3):
    n = defaultdict(int)

    for nlen in xrange(min, max+1):
        for i in xrange(len(s) - nlen + 1):
            k = s[i:i+nlen]

            if isinstance(k, (list, tuple)):
                k = ' '.join(k)

            n[k] += 1

    return n

def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)

def get_keywords(node, preserve_phrases=False):
    keywords = []

    if isinstance(node, Term):
        keywords.append(node.text.lower())
        return keywords

    elif isinstance(node, And):
        _ksets = []

        for child in node.children():
            _keywords = get_keywords(child, preserve_phrases)
            _ksets.append(_keywords)

        keywords = tuple(product(*_ksets))
        keywords = [flatten(x) for x in keywords]

    elif isinstance(node, Phrase):
        words = [w.lower() for w in node.words]
        term = ' '.join(words) if preserve_phrases else tuple(words)
        return (term,)

    else:
        for child in node.children():
            _keywords = get_keywords(child, preserve_phrases)
            keywords.extend(_keywords)

    return keywords

class QFragment(set):
    def __init__(self, token, data=None, qids=None):
        super(QFragment, self).__init__(data or [])
        self.qids = qids or set()
        self.token = token

    def __repr__(self):
        return 'QFragment(%s, %s, qids=%s)' % \
            (repr(self.token), repr(set(self)), repr(self.qids))

    def __cmp__(self, other):
        return cmp(hash(self), hash(other))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.token, tuple(sorted(self))))

    __unicode__ = lambda: unicode(repr(self))
    __str__ = __repr__

def _update_fragments(qfragments, k, krequired):
    if k in qfragments: return
    qfragments.add(QFragment(k, krequired))

def get_qfragments(query, max_fragments):
    qfragments = set()

    parser = QueryParser('t', None)
    parse_tree = parser.parse(query)
    keywords = get_keywords(parse_tree, True)

    for k in keywords:

        if isinstance(k, (str, unicode)):
            k = clean(k)
            kparts = k.split(' ')
            if len(kparts) <= max_fragments:
                qfragments.add(QFragment(token=k))
            else:
                for n in ngrams(kparts, min=max_fragments, max=max_fragments):
                    _update_fragments(qfragments, n, kparts)

        else:
            k = [clean(x) for x in k]
            for _k in k:
                _update_fragments(qfragments, _k, k)

    return qfragments

class Percolator(object):
    def __init__(self):
        self.queries = {}
        self.q_to_qfrags = {}
        self.tok_to_qfrags = {}
        self.tokens = set()

    def add_query(self, query):
        assert(isinstance(query, unicode))

        qid = hashlib.md5(query.encode('utf8', 'ignore')).hexdigest()
        if qid in self.queries: return qid

        self.queries[qid] = query
        q_qfrags = self.q_to_qfrags[qid] = set()

        qfragments = self._get_qfragments(query)
        for qfrag in qfragments:
            tok_qfrags = self.tok_to_qfrags.get(qfrag.token, set())
            if qfrag in tok_qfrags:
                qfrag = [x for x in tok_qfrags if x == qfrag][0]
            qfrag.qids.add(qid)
            q_qfrags.add(qfrag)

            tok_qfrags.add(qfrag)
            self.tok_to_qfrags[qfrag.token] = tok_qfrags
            self.tokens.add(qfrag.token)

        return qid

    def del_query(self, qid):
        del self.queries[qid]

        remove = []

        for qfrag in self.q_to_qfrags[qid]:
            qfrag.qids.remove(qid)
            if qfrag.qids: continue

            tok_qfrags = self.tok_to_qfrags.get(qfrag.token)
            tok_qfrags.discard(qfrag)

            if not tok_qfrags:
                remove.append(qfrag.token)

        for token in remove:
            del self.tok_to_qfrags[token]
            self.tokens.remove(token)

        del self.q_to_qfrags[qid]

    def get_matches(self, text, max_fragments=3):
        assert(isinstance(text, unicode))
        matches = set()

        unigrams = clean(text).split(' ')
        if not set(unigrams).intersection(self.tokens):
            return matches

        tokens = set(ngrams(unigrams, min=1, max=max_fragments))

        for token in tokens.intersection(self.tokens):
            for qfragment in self.tok_to_qfrags[token]:
                # check if qfragment has to be matched at all
                if qfragment.qids.issubset(matches): continue

                # are all required tokens present in text?
                if qfragment.issubset(tokens):
                    matches.update(qfragment.qids)

        return matches

    def _get_qfragments(self, query, max_fragments=3):
        return get_qfragments(query, max_fragments)

def main():
    pass

if __name__ == '__main__':
    main()
