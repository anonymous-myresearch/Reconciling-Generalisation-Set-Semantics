"""Regenerate source fixtures only. Expected results are stored separately and never written here."""
from copy import deepcopy
from pathlib import Path
from fixture_helpers import baseline,brokerage,hybrid,find,render
ROOT=Path(__file__).resolve().parent

def build():
 b=baseline(); out={'00_baseline':deepcopy(b)}
 a=deepcopy(b);del find(a,'O1','AccountByProductKind')['props']['isComplete']
 out['14_abstract_control']=deepcopy(a)
 find(a,'O2','c1')['props']['hasDeclaredType']='O1.Account';out['01_abstract_direct_attempt']=a
 a=deepcopy(b);brokerage(a);out['02_uncovered_account']=deepcopy(a)
 del find(a,'O1','AccountByProductKind')['props']['isComplete'];out['03_coverage_not_required']=a
 a=deepcopy(b);hybrid(a,False);out['04_empty_shared_specialisation']=a
 a=deepcopy(b);hybrid(a,True);out['05_populated_shared_specialisation']=deepcopy(a)
 find(a,'O1','AccountByProductKind')['props']['isDisjoint']=False;out['06_overlap_asserted']=a
 a=deepcopy(b);find(a,'O2')['wards']=[find(a,'O2','c1')];out['07_only_checking_populated']=a
 a=deepcopy(b);find(a,'O2')['wards']=[];out['08_empty_population']=a
 out['09_partial_population']=deepcopy(b)
 a=deepcopy(b);brokerage(a)
 find(a,'O1')['wards']=[w for w in find(a,'O1')['wards'] if w['name'] not in ['CheckingBrokerageExclusion','SavingsBrokerageExclusion']]
 find(a,'O2')['wards']=[w for w in find(a,'O2')['wards'] if w['name']!='b1']
 out['10_invariant_before']=deepcopy(a)
 bb=deepcopy(a);find(bb,'O2')['wards'].append(deepcopy(find(out['02_uncovered_account'],'O2','b1')));out['11_invariant_after']=bb
 del find(a,'O1','AccountByProductKind')['props']['isComplete'];out['12_permissive_before']=deepcopy(a)
 bb=deepcopy(a);find(bb,'O2')['wards'].append(deepcopy(find(out['02_uncovered_account'],'O2','b1')));out['13_permissive_after']=bb
 for name,model in out.items():
  (ROOT/'models'/f'{name}.fhas').write_text('// Controlled Account fixture v0.6. Presence of a property is preserved.\n'+render(model)+'\n')
 return out
if __name__=='__main__':build()
