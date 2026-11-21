"""Standalone public-data updater. Python standard library only; no AI services."""
import argparse, concurrent.futures, datetime as dt, hashlib, json, pathlib, re, time
import urllib.error, urllib.parse, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
UTC=dt.timezone.utc

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,value):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
def utcnow():return dt.datetime.now(UTC).isoformat(timespec='seconds')
def get_json(url):
 for attempt in range(3):
  try:
   req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'ResearchPortfolioUpdater/1.0'})
   with urllib.request.urlopen(req,timeout=25) as response:return json.load(response)
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==2:raise
   retry=e.headers.get('Retry-After','')
   time.sleep(min(float(retry),15) if retry.isdigit() else 2**attempt)
  except (urllib.error.URLError,TimeoutError):
   if attempt==2:raise
   time.sleep(2**attempt)

def clean_doi(value):
 s=urllib.parse.unquote(str(value)).strip()
 s=re.sub(r'^https?://(?:dx\.)?doi\.org/','',s,flags=re.I)
 s=re.sub(r'^doi:\s*','',s,flags=re.I).strip().lower()
 return s if re.fullmatch(r'10\.\d{4,9}/\S+',s) else ''

def orcid_dois(record):
 result=set()
 for group in record.get('group',[]):
  entities=[group]+group.get('work-summary',[])
  for entity in entities:
   for item in (entity.get('external-ids') or {}).get('external-id',[]):
    if item.get('external-id-type','').lower()=='doi':
     doi=clean_doi(item.get('external-id-value',''))
     if doi:result.add(doi)
 return result

def author_is_benzater(author,orcid):
 if author.get('ORCID','').rstrip('/').endswith('/'+orcid):return True
 family=re.sub(r'[^a-z]','',author.get('family','').lower())
 given=re.sub(r'[^a-z]','',author.get('given','').lower())
 return family=='benzater' and given in ('hadjabdelkader','abdelkaderhadj')

def topic(title):
 t=title.lower()
 if any(w in t for w in ('antenna','lna','amplifier','impedance')):return 'RF & antennas'
 if any(w in t for w in ('random demodulator','sub-nyquist','acquisition')):return 'Sub-Nyquist acquisition'
 if any(w in t for w in ('cfar','radar','interference rejection')):return 'Radar & interference'
 if any(w in t for w in ('fpga','neural','learning')):return 'FPGA & learning'
 if any(w in t for w in ('joint sparse','matching pursuit','recovery and detection')):return 'Sparse recovery'
 return 'Cooperative sensing' if 'sensing' in t or 'cooperative' in t else 'Other research'

def from_crossref(work,doi,config,today):
 if not any(author_is_benzater(a,config['orcid']) for a in work.get('author',[])):return None
 kind={'journal-article':'Journal article','proceedings-article':'Conference paper','book-chapter':'Book chapter'}.get(work.get('type'))
 title=(work.get('title') or [''])[0].strip()
 date=work.get('published-print') or work.get('published') or work.get('published-online') or {}
 parts=(date.get('date-parts') or [[]])[0]
 if not kind or not title or not parts:return None
 year=int(parts[0]);authors=[' '.join([a.get('given',''),a.get('family','')]).strip() for a in work.get('author',[])]
 return {'id':'doi-'+hashlib.sha256(doi.encode()).hexdigest()[:14],'title':title,'year':year,'kind':kind,'topic':topic(title),'venue':(work.get('container-title') or [''])[0],'registeredVenue':(work.get('container-title') or [''])[0],'doi':doi,'source':'https://doi.org/'+doi,'authors':authors,'summary':'','note':'','verified':today,'registry':'Crossref','registry_url':'https://api.crossref.org/works/'+doi,'pages':work.get('page',''),'volume':work.get('volume',''),'issue':work.get('issue','')}

def apply_crossref_metrics(publication,work,today):
 value=work.get('is-referenced-by-count')
 if isinstance(value,int) and not isinstance(value,bool) and value>=0:
  publication['crossrefCitations']=value;publication['crossrefAsOf']=today
 # Scholar counts are intentionally never inferred from Crossref.

def apply_overrides(metrics,pubs,overrides):
 for key,fields in [('scholar',['citations','hIndex','i10Index','profileEntries']),('peerReview',['records','manuscripts'])]:
  values=overrides.get(key)
  if values is None:continue
  date=values.get('asOf','');dt.date.fromisoformat(date)
  if date>dt.datetime.now(UTC).date().isoformat():raise ValueError('Override date cannot be in the future')
  for field in fields:
   if field in values:
    v=values[field]
    if not isinstance(v,int) or isinstance(v,bool) or v<0:raise ValueError('Metric must be a non-negative integer')
    metrics[key][field]=v
  metrics[key]['asOf']=date
  if key=='peerReview' and 'journals' in values:
   journals=values['journals']
   if not isinstance(journals,list) or not all(isinstance(j,dict) and isinstance(j.get('name'),str) and isinstance(j.get('manuscripts'),int) and j['manuscripts']>=0 for j in journals):raise ValueError('Invalid journal summary')
   if sum(j['manuscripts'] for j in journals)!=metrics[key]['manuscripts']:raise ValueError('Journal manuscript counts must match the total')
   metrics[key]['journals']=journals
 if 'publicationCitations' in overrides:
  dt.date.fromisoformat(overrides['scholar']['asOf'])
  for p in pubs:
   doi=clean_doi(p.get('doi',''))
   if doi in overrides['publicationCitations']:
    v=overrides['publicationCitations'][doi]
    if not isinstance(v,int) or isinstance(v,bool) or v<0:raise ValueError('Invalid publication count')
    p['scholarCitations']=v;p['scholarAsOf']=overrides['scholar']['asOf']
 return metrics,pubs

def refresh(root=ROOT,apply=False):
 config=read(root/'site-config.json');pubs=read(root/'dist/publications.json');metrics=read(root/'dist/research-metrics.json')
 previous=read(root/'dist/update-status.json') if (root/'dist/update-status.json').exists() else {}
 now=utcnow();today=now[:10];status={'attemptedAt':now,'added':0,'orcid':{'ok':False},'crossref':{'ok':False},'scholar':'Dated source figures retained; no automated scraping.','webOfScience':'Dated source figures retained; no licensed API configured.'}
 known={clean_doi(p.get('doi','')):p for p in pubs if p.get('doi')}
 candidates=set()
 try:
  record=get_json('https://pub.orcid.org/v3.0/'+config['orcid']+'/works');candidates=orcid_dois(record)
  status['orcid']={'ok':True,'workGroups':len(record.get('group',[])),'doiCount':len(candidates),'checkedAt':now}
 except Exception as e:status['orcid']['error']=str(e)[:180]
 def fetch(doi):
  try:return doi,get_json('https://api.crossref.org/works/'+urllib.parse.quote(doi,safe='/'))['message'],None
  except Exception as e:return doi,None,str(e)[:180]
 failures=[];success=0
 repository_dois={doi for doi in set(known)|candidates if doi.startswith('10.5281/')}
 status['repositories']={'retainedDois':len(repository_dois),'note':'Zenodo repository DOIs and version/concept aliases are retained; they are not Crossref citation records.'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
  for doi,work,error in executor.map(fetch,sorted((set(known)|candidates)-repository_dois)):
   if work is None:failures.append({'doi':doi,'error':error});continue
   returned=clean_doi(work.get('DOI',''))
   if returned and returned!=doi:failures.append({'doi':doi,'error':'Returned DOI mismatch'});continue
   success+=1
   if doi in known:apply_crossref_metrics(known[doi],work,today)
   elif doi in candidates:
    p=from_crossref(work,doi,config,today)
    if p:apply_crossref_metrics(p,work,today);pubs.append(p);known[doi]=p;status['added']+=1
 status['crossref']={'ok':success>0,'checkedAt':now,'recordsRead':success,'failures':failures}
 if success==0 and not status['orcid']['ok']:
  # Neither source worked: retain last good source data, but record the failed check.
  status['result']='sources-unavailable'
 else:status['result']='updated' if not failures and status['orcid']['ok'] else 'partial'
 status['lastSuccessfulAt']=now if success>0 or status['orcid']['ok'] else previous.get('lastSuccessfulAt')
 metrics['scholar'].setdefault('asOf',metrics.get('asOf','2026-11-21'))
 metrics['peerReview'].setdefault('asOf',metrics.get('asOf','2026-11-21'))
 metrics,pubs=apply_overrides(metrics,pubs,read(root/'metrics-overrides.json'))
 if apply:
  save(root/'dist/publications.json',pubs);save(root/'dist/research-metrics.json',metrics);save(root/'dist/update-status.json',status)
 print(json.dumps({'result':status['result'],'added':status['added'],'orcid':status['orcid'],'crossrefRecords':success,'failedCrossrefRecords':len(failures),'written':apply},ensure_ascii=False))
 return status
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args();refresh(apply=args.apply)
