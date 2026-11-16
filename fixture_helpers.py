"""Construct the first CAiSE Account example. Fixture authoring, not PAMoLa execution."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import uuid

ROOT = Path(__file__).resolve().parent
NS = uuid.UUID('70eaa70b-2ad0-4461-a62e-dc1b14799f91')

def node(badge, name, **props):
    return dict(badge=badge, name=name, props=props, wards=[])

def add(parent, child):
    parent['wards'].append(child)
    return child

def category(parent, name, general, specials, **props):
    c = add(parent, node('CA', name, **props))
    add(c, node('IC', 'general', isGeneralisation=True, hasRelatum='O1.' + general))
    for s in specials:
        add(c, node('IC', s, hasRelatum='O1.' + s))
    return c

def find(model, *path):
    n = model
    for name in path:
        n = next(w for w in n['wards'] if w['name'] == name)
    return n

def baseline():
    m = node('EN', 'AccountCase')
    schema = add(m, node('EN', 'O1'))
    pop = add(m, node('EN', 'O2'))
    for name in ('Account', 'CheckingAccount', 'SavingsAccount',
                 'OnlineAccount', 'BranchAccount', 'DualAccessCheckingAccount'):
        add(schema, node('EN', name, hasPotency=0 if name == 'Account' else 1))
    category(schema, 'AccountByProductKind', 'Account', ['CheckingAccount', 'SavingsAccount'],
             isComplete=True, isDisjoint=True)
    category(schema, 'AccountByAccessKind', 'Account', ['OnlineAccount', 'BranchAccount'],
             isComplete=False, isDisjoint=False)
    for general in ('CheckingAccount', 'OnlineAccount', 'BranchAccount'):
        category(schema, 'DualAccessSpecialises' + general, general,
                 ['DualAccessCheckingAccount'])
    for name, typ in [('c1', 'CheckingAccount'), ('s1', 'SavingsAccount'),
                      ('d1', 'DualAccessCheckingAccount')]:
        add(pop, node('EN', name, hasPotency=0, hasDeclaredType='O1.' + typ))
    return m

def brokerage(model):
    s = find(model, 'O1')
    add(s, node('EN', 'BrokerageAccount', hasPotency=1))
    category(s, 'BrokerageSpecialisesAccount', 'Account', ['BrokerageAccount'])
    category(s, 'CheckingBrokerageExclusion', 'Account',
             ['CheckingAccount', 'BrokerageAccount'], isDisjoint=True)
    category(s, 'SavingsBrokerageExclusion', 'Account',
             ['SavingsAccount', 'BrokerageAccount'], isDisjoint=True)
    add(find(model, 'O2'), node('EN', 'b1', hasPotency=0,
                              hasDeclaredType='O1.BrokerageAccount'))

def hybrid(model, populated):
    s = find(model, 'O1')
    add(s, node('EN', 'HybridAccount', hasPotency=1))
    for general in ('CheckingAccount', 'SavingsAccount'):
        category(s, 'HybridSpecialises' + general, general, ['HybridAccount'])
    if populated:
        add(find(model, 'O2'), node('EN', 'x1', hasPotency=0,
                                  hasDeclaredType='O1.HybridAccount'))

def render(n, path=''):
    path = path + '.' + n['name'] if path else n['name']
    props = [('hasName', json.dumps(n['name'])),
             ('hasPID', 'pid:pamola:caise:' + str(uuid.uuid5(NS, path)))]
    for key, value in n['props'].items():
        text = ('true' if value else 'false') if isinstance(value, bool) else str(value)
        props.append((key, text))
    head = n['badge'] + ' {' + ', '.join(k + ' ' + v for k, v in props)
    if not n['wards']:
        return head + '}'
    return head + ',\n' + ',\n'.join('  ' + render(w, path).replace('\n', '\n  ')
                                    for w in n['wards']) + '\n}'

