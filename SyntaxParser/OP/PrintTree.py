# -*- coding: utf-8 -*-

def print_tree(tree):
    buff = ['S']
    _print_tree(tree, buff, '', 0)
    print('\n'.join(buff))
 
def _print_tree(tree, buff, prefix, level):
    count = len(tree)
    for k, v in tree.items():
        count -= 1
        if v:
            buff.append('%s -> %s' % (prefix, k))
            if count > 0:
                _print_tree(v, buff, prefix + ' |  ', level + 1)
            else:
                _print_tree(v, buff, prefix + '    ', level + 1)
        else:
            buff.append('%s -> %s' % (prefix, k))
 
def test():
    tree = {
        'bin': { 'bash': None, 'cat': None, 'cp': None, },
        'etc': {
            'init.d': { 'apache2':None, 'slapd':None, 'sshd':None, },
            'passwd': None,
            'hosts': None,
        },
        'var': {
            'log': {
                'apache2': { 'accesslog':None, 'errorlog': None, },
            },
        },
    }
    print_tree(tree)
 
if __name__ == '__main__':
    test()