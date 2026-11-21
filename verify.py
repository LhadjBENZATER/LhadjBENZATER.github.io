import json,pathlib,re
from html.parser import HTMLParser
r=pathlib.Path(__file__).resolve().parent;d=r/'dist';records=json.loads((d/'publications.json').read_text());metrics=json.loads((d/'research-metrics.json').read_text());page=(d/'index.html').read_text();config=json.loads((r/'site-config.json').read_text())
assert len({p['id'] for p in records})==len(records)
dois=[p['doi'].lower() for p in records if p.get('doi')];assert len(dois)==len(set(dois))
assert not re.search(r'__[A-Z_]+__',page)
assert config['origin'] in page and 'deepfig11.chatgpt.site' not in page
class Check(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if a.get('href','').startswith('#'):self.refs.append(a['href'][1:])
c=Check();c.feed(page);assert len(c.ids)==len(set(c.ids));assert set(c.refs)<=set(c.ids)
for p in records:
 for key in ('scholarCitations','crossrefCitations'):
  if key in p:assert isinstance(p[key],int) and p[key]>=0
for name in ('styles.css','app.js','contact.vcf','sitemap.xml','robots.txt'):assert (d/name).is_file()
print('Verified standalone origin, catalogue identity, source-specific citation counts, assets and anchors.')
