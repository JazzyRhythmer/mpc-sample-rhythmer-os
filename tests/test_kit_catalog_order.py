"""Kit display order must not silently retarget the original eight GEN recipes."""
from pathlib import Path
import json,re,unittest
ROOT=Path(__file__).resolve().parents[1]
class KitCatalogOrder(unittest.TestCase):
 def test_gen_recipe_identity_and_default(self):
  c=json.loads((ROOT/'config/sound-catalog.json').read_text());names=[k['name']for k in c['kits']]
  self.assertEqual(names[0],'K-WASUB / 909');self.assertTrue(all(n.startswith('K-WASUB /')for n in names[:4]))
  words=[('trx','classic'),('909',),('808',),('click','electro'),('industrial',),('soft','acoustic'),('dub',),('break','jungle')]
  expected=[next((n for n in c['kit_order_legacy']if any(w in n.lower()for w in ws)),names[0])for ws in words]
  text=(ROOT/'extensions/model/gen_engine_map.h').read_text();indices=list(map(int,re.search(r'gen_kit_programs\[\]=\{([^}]+)',text)[1].split(',')))
  self.assertEqual([names[i]for i in indices],expected)
  self.assertEqual(len(c['kits']),36);self.assertTrue(all(len(k['routes'])==16 for k in c['kits']))
if __name__=='__main__':unittest.main()
