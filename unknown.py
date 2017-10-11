#!/usr/bin/env python

import sys, fileinput
import collections
import tree
from nltk.corpus import wordnet as wn

count = collections.defaultdict(int)

trees = []
for line in fileinput.input():
    t = tree.Tree.from_str(line)
    for leaf in t.leaves():
        count[leaf.label] += 1
    trees.append(t)

for t in trees:
    for leaf in t.leaves():
        if count[leaf.label] < 2:
            stem = wn.morphy(leaf.label)
            new_val = leaf.label
            if stem is not None:
                new_val = stem
            leaf.label = leaf.label.replace(new_val,"<unk>")
    sys.stdout.write("{0}\n".format(t))