import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit
import tree
import math
import time
plot_y = []
plot_x = []
scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')
terminals = []
non_terminals = []
words_present = set()

def parser_func(words, grammar):
  table = dd(float)
  table = dd(lambda: -999.0, table)
  back = dd(tuple)

  for j in range(1, len(words)+1):
    for entry in terminals:
      if words[j-1] == entry[1]:
        rule = entry[0] + '->' + entry[1]
        table[(j-1, j, entry[0])] = grammar[rule]
        back[(j-1, j, entry[0])] = (-1, words[j-1], '')    

    for i in range(j-2,-1,-1):
      for k in range(i+1,j):
        for entry in non_terminals:
          rule_string = entry[0] + "->" + entry[1] + " " + entry[2]
          rule_prob = grammar.get(rule_string)
          A = entry[0]
          B = entry[1]
          C = entry[2]
          prob = rule_prob + table[(i,k,B)] + table[(k,j,C)]
          if table[(i,j,A)] <= prob:
            table[(i,j,A)] = prob 
            back[(i,j,A)] = (k,B,C)

  # print "back"
  # for ele in back:
  #   print ele, back[ele]
  # print "table"
  # for ele in table:
  #   if table[ele] > -999:
  #     print ele, table[ele]
  return build_tree(back, table, words)

def build_tree(back, table, words):
  q = []
  i = 0
  j = len(words)
  label = 'TOP'
  top = tree.Node(label, [])
  count = 0
  q.append((top,i,j))
  while len(q) > 0:
    tuple_pop = q.pop()
    node = tuple_pop[0]
    i = tuple_pop[1]
    j = tuple_pop[2]
    back_tuple = back[(i,j,node.label)]
    if back_tuple:
      count += 1
      k = back_tuple[0]
      left = tree.Node(back_tuple[1],[])
      node.append_child(left)
      q.append((left,i,k))
      if back_tuple[2] is not '':
        right = tree.Node(back_tuple[2],[])
        node.append_child(right)
        q.append((right,k,j))
  t = tree.Tree(top)
  # print t.__str__()
  # # Q2
  # print "Output for the first line:"
  # print t.__str__()
  # print "Probability; ", table[(0, len(words), 'TOP')]
  if count > 0:
    return t.__str__()  
  return '' 

def preprocess(words):
  for j in range(0, len(words)):
    if words[j] not in words_present:
      words[j] = "<unk>"
  return words

def main():
  infile = open(sys.argv[1], 'r')
  outfile = open("o.txt", 'w')

  for text in infile.read().splitlines():
    t = tree.Tree.from_str(text)
    t.generate_rules()

  grammar = {}
  for k,v in tree.trace.items():
    LHS = k.split("->")[0]
    probability = float(v) / tree.count.get(LHS)
    grammar[k] = math.log10(probability)
    # outfile.write(k + " # " + str(probability) + "\n")

  # print grammar
  for item in grammar:
    outfile.write(item)
    outfile.write("\n")
  # print len(grammar)

  for k,v in tree.trace.items():
    LHS = k.split("->")[0]
    RHS = k.split("->")[1].split(" ")
    if len(RHS) == 1:
      item = [LHS, RHS[0]]
      terminals.append(item)
      words_present.add(RHS[0])
    else:
      item = [LHS, RHS[0], RHS[1]]
      non_terminals.append(item)


  parseinput = open(sys.argv[2], 'r')
  # parseoutput = open(sys.argv[4], 'w')

  words = parseinput.read().splitlines()
  count = 0

  for line in words:
    words = line.split()
    plot_x.append(math.log10(len(line.split())))
    words = preprocess(words)

    start = time.clock()
    parser_val = parser_func(words,grammar)
    duration = time.clock() - start

    plot_y.append(math.log10(duration*1000))
    # parseoutput.write(parser_val)
    # parseoutput.write("\n")
    print parser_val
  # # plot.plotgraph(plot_x,plot_y)

  
  # print len(terminals)
  # print terminals
  # print non_terminals
  # print len(non_terminals)
  # # Q1
  # print "Number of rules in the grammar: ", len(tree.trace)
  # maximum = max(tree.trace, key=tree.trace.get)
  # print 'The most frequent rule: ', maximum
  # print 'Number of times the above rule occured: ', tree.trace[maximum]




if __name__ == '__main__':
  main()
