#!/usr/bin/env python
# -*- coding: utf-8 -*-

from nfa_and_dfa import NFA, DFA, NFANode, DFANode


class LexicalAnalyze(object):
    def __init__(self):
        super(LexicalAnalyze, self).__init__()
        self.productions = []
        self.key_words = {}
        self.tool_set = {}
        self.NFA = None
        self.DFA = None

    def read_lex_grammar(self, file_name):
        cur_left = None
        cur_right = []
        line_num = 0
        for line in open(file_name, 'r'):
            line = line.split('\n')[0]
            index = line.find(':')
            cur_left = line[0:index]
            cur_right = line[index + 1:len(line)]
            line_num += 1
            if line_num < 4:
                self.tool_set[cur_left] = set(cur_right.split('|'))
                continue
            elif line_num == 4:
                for word in set(cur_right.split('|')):
                    self.key_words[word] = cur_left
                continue
            production = {}
            production['left'] = cur_left
            index = cur_right.find(' ')
            if index != -1:
                production['input'] = cur_right[0:index]
                production['right'] = cur_right[index + 1:len(cur_right)]
            else:
                production['input'] = cur_right
                production['right'] = None
            self.productions.append(production)

    def create_nfa(self):
        all_status = {}

        def get_create_nfa_node(name, _type):
            if name in all_status:
                node = all_status[name]
            else:
                node = NFANode(name=name, _type=_type)
            return node

        start_node = get_create_nfa_node('start', 0)
        end_node = get_create_nfa_node('end', 1)
        all_status['start'] = start_node
        all_status['end'] = end_node
        for produ in self.productions:
            name = produ['left']
            alpha = produ['input']
            right = produ['right']
            node = get_create_nfa_node(name, 0)
            if right is not None:
                target_node = get_create_nfa_node(right, 0)
            if alpha not in self.tool_set.keys():
                if right is None:
                    node.add_edge(alpha, 'end')
                else:
                    if right in self.tool_set:
                        for val in self.tool_set[right]:
                            node.add_edge(alpha, val)
                    else:
                        node.add_edge(alpha, right)
            else:
                for val in self.tool_set[alpha]:
                    if right is None:
                        node.add_edge(val, 'end')
                    else:
                        if right in self.tool_set:
                            for val in self.tool_set[right]:
                                node.add_edge(alpha, val)
                        else:
                            node.add_edge(alpha, right)
                            node.add_edge(val, right)
            all_status[name] = node
            if right is not None:
                all_status[right] = target_node

        alphabets = set()
        for i in range(ord(' '), ord('~') + 1):
            alphabets.add(chr(i))
        self.NFA = NFA(alphabets)
        self.NFA.status = all_status

    def nfa_to_dfa(self):
        all_status = {}

        def get_create_dfaNode(name, _type):
            if name in all_status:
                return all_status[name]
            else:
                node = DFANode(name, _type)
            return node
        for node_name in self.NFA.status['start'].edge['$']:
            start_node = get_create_dfaNode('start', 0)
            dfa_node = get_create_dfaNode(node_name, 0)
            start_node.add_edge('$', node_name)
            all_status['start'] = start_node
            all_status[node_name] = dfa_node
            is_visit = set()
            queue = list()
            nfa_node_set = set()
            nfa_node_set.add(node_name)
            queue.append((nfa_node_set, node_name))
            while queue:
                node_name = queue.pop(0)
                top_node_name = node_name[0]
                dfa_node_name = node_name[1]
                # print 'to =', top_node_name, ', df =', dfa_node_name
                dfa_node = get_create_dfaNode(dfa_node_name, 0)
                for alpha in self.NFA.alphabets:
                    target_set = set()
                    for nfa_node_name in top_node_name:
                        nfa_name = self.NFA.status[nfa_node_name]
                        if alpha in nfa_name.edge.keys():
                            for name in nfa_name.edge[alpha]:
                                target_set.add(name)
                    if not target_set:
                        continue
                    dfa_new_node_name = ''
                    _type = 0
                    tmp_list = list(target_set)
                    target_list = sorted(tmp_list)
                    for tar in target_list:
                        dfa_new_node_name = '%s$%s' % (dfa_new_node_name, tar)
                        _type += int(self.NFA.status[tar]._type)
                    if _type > 0:
                        _type = 1
                    dfa_new_node = get_create_dfaNode(dfa_new_node_name, _type)
                    dfa_node.add_edge(alpha, dfa_new_node_name)
                    all_status[dfa_node_name] = dfa_node
                    all_status[dfa_new_node_name] = dfa_new_node
                    if dfa_new_node_name in is_visit:
                        continue
                    else:
                        is_visit.add(dfa_new_node_name)
                        queue.append((target_set, dfa_new_node_name))
        alphabets = set()
        for i in range(ord(' '), ord('~') + 1):
            alphabets.add(chr(i))
        self.DFA = DFA(alphabets)
        self.DFA.status = all_status

    def run_on_dfa(self, line, pos):
        for dfa_name in self.DFA.status['start'].edge['$']:
            cur_pos = pos
            token = ''
            token_type = dfa_name
            c_node = self.DFA.status[dfa_name]
            while cur_pos < len(line) and line[cur_pos] in c_node.edge.keys():
                token += line[cur_pos]
                c_node = self.DFA.status[list(c_node.edge[line[cur_pos]])[0]]
                cur_pos += 1
            if c_node._type > 0:
                if token in self.key_words.keys():
                    token_type = token
                return cur_pos - 1, token_type, token
        return pos, None, ''

    def read_and_analyze(self, file_name):
        line_num = 0
        lex_error = False
        token_table = []
        for line in open(file_name, 'r'):
            pos = 0
            line_num += 1
            line = line.split('\n')[0]
            while pos < len(line) and not lex_error:
                while pos < len(line) and line[pos] in ['\t', '\n', ' ', '\r']:
                    pos += 1
                if pos < len(line):
                    pos, token_type, token = self.run_on_dfa(line, pos)
                    if token_type is None:
                        print 'Lexical error at line %s, column %s' % (
                            (str(line_num), str(pos)))
                        lex_error = True
                        break
                    else:
                        token_table.append((token_type, token))
                        print '(\'%s\'\t, \'%s\')' % (token_type, token)
                    pos += 1
        if not lex_error:
            output = open('token_table.data', 'w+')
            for token_type, token in token_table:
                type_of_token = token
                if token_type == 'identifier' or token_type == 'number':
                    type_of_token = token_type
                output.write('%s %s\n' % (type_of_token, token))
            output.close()
            return True
        return False


def main():
    lex_ana = LexicalAnalyze()
    lex_ana.read_lex_grammar('lex_grammar.txt')
    lex_ana.create_nfa()
    lex_ana.nfa_to_dfa()
    lex_ana.read_and_analyze('source.cc')

if __name__ == '__main__':
    main()
