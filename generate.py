import json,html,pathlib,collections
root=pathlib.Path(__file__).parent;dist=root/'dist';records=json.loads((dist/'publications.json').read_text());esc=lambda s:html.escape(str(s),quote=True)
config=json.loads((root/'site-config.json').read_text())
origin=config['origin'].rstrip('/')
metrics=json.loads((dist/'research-metrics.json').read_text())
scholar_url=metrics['scholar']['url']
wos_url=metrics['peerReview']['url']
status=json.loads((dist/'update-status.json').read_text()) if (dist/'update-status.json').exists() else {}
from datetime import date
def pretty(value):
 d=date.fromisoformat(value[:10]);return f'{d.day} {d.strftime("%B")} {d.year}'
scholar_date=metrics['scholar'].get('asOf',metrics['asOf'])
wos_date=metrics['peerReview'].get('asOf',metrics['asOf'])
icons={
'NETWORK':'<path d="M9 8L23 18L38 8M7 32L23 18L39 33"/><circle cx="23" cy="18" r="5"/><circle cx="7" cy="7" r="3"/><circle cx="39" cy="7" r="3"/><circle cx="6" cy="34" r="3"/><circle cx="40" cy="34" r="3"/>',
'SPARSE':'<path d="M3 34H43M8 34V24M16 34V10M24 34V29M32 34V5M40 34V26"/><circle cx="16" cy="10" r="2"/><circle cx="32" cy="5" r="2"/>',
'WAVE':'<path d="M1 21C5 0 9 0 13 21S21 42 25 21S33 0 37 21S43 35 47 21"/><circle cx="5" cy="8" r="2"/><circle cx="17" cy="34" r="2"/><circle cx="29" cy="8" r="2"/><circle cx="41" cy="34" r="2"/>',
'RF':'<path d="M3 10H16L33 21L16 32V10M33 21H45M24 13V4M24 29V38M3 21H12"/><path d="M37 8C43 12 43 14 43 17M37 34C43 30 43 28 43 25"/>',
'RADAR':'<circle cx="24" cy="22" r="17"/><circle cx="24" cy="22" r="9"/><path d="M24 22L37 9M24 3V7M3 22H7M24 37V41M41 22H45"/><circle cx="29" cy="15" r="2"/>',
'CHIP':'<rect x="11" y="8" width="27" height="27" rx="3"/><rect x="18" y="15" width="13" height="13" rx="1"/><path d="M17 1V8M25 1V8M33 1V8M17 35V42M25 35V42M33 35V42M4 14H11M4 22H11M4 30H11M38 14H45M38 22H45M38 30H45"/>'}
def author_html(names):
 return ', '.join('<strong>'+esc(n)+'</strong>' if 'Benzater' in n else esc(n) for n in names)
def pub(p):
 url='https://doi.org/'+p['doi'] if p['doi'] else p['source'];doi=p['doi'];links=[]
 if doi: links.append(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer" data-i18n="repository"'+('>Repository / DOI</a>' if doi.startswith('10.5281/') else ' data-publisher="true">Publisher / DOI</a>'))
 if p['source']!=url: links.append(f'<a href="{esc(p["source"])}" target="_blank" rel="noopener noreferrer" data-i18n="authorCopy">Author record</a>')
 if not links: links.append(f'<a href="{esc(p["source"])}" target="_blank" rel="noopener noreferrer" data-i18n="authorCopy">Author record</a>')
 for link in p.get('extra',[]): links.append(f'<a href="{esc(link["url"])}" target="_blank" rel="noopener noreferrer">{esc(link["label"])}</a>')
 links.append(f'<button class="cite-button" data-cite="{p["id"]}" data-i18n="cite">Cite</button>')
 citation=(f'<a class="scholar-count" href="{esc(scholar_url)}" target="_blank" rel="noopener noreferrer" title="Google Scholar snapshot: 21 November 2026"><strong>{p["scholarCitations"]}</strong> <span data-i18n="citationMetric">citations</span><span class="scholar-source">Google Scholar</span></a>' if 'scholarCitations' in p and p['kind']!='Correction' else '')
 crossref=(f'<span class="crossref-count" title="Crossref count checked {esc(p.get("crossrefAsOf",""))}">Crossref: <strong>{p["crossrefCitations"]}</strong></span>' if 'crossrefCitations' in p else '')
 citation+=crossref
 metadata=f'DOI: {esc(doi)}<br>' if doi else ''
 metadata+=f'<a href="{esc(p.get("registry_url",p["source"]))}" target="_blank" rel="noopener noreferrer">{esc(p.get("registry","Author record"))}</a> · Checked 20 November 2026'
 return f'''<article class="pub" data-id="{p['id']}" id="work-{p['id']}"><div class="pub-year">{p['year']}</div><div class="pub-content"><div class="pub-meta"><span class="kind" data-kind="{esc(p['kind'])}">{esc(p['kind'])}</span><span class="pub-topic" data-topic="{esc(p['topic'])}">{esc(p['topic'])}</span>{citation}</div><h3><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(p['title'])}</a></h3><p class="pub-authors">{author_html(p['authors'])}</p><p class="pub-venue">{esc(p['venue'])}</p><div class="pub-links">{''.join(links)}</div>{'<p class="pub-note">'+esc(p['note'])+'</p>' if p['note'] else ''}<details><summary data-i18n="sourceDetails">Metadata &amp; source</summary><p>{metadata}</p>{'<p>'+esc(p['scholarNote'])+'</p>' if p.get('scholarNote') else ''}</details></div></article>'''
feature_art=[
'<path d="M20 90H285M35 90V75M50 90V78M65 90V30M80 90V22M95 90V35M110 90V78M125 90V81M140 90V76M155 90V27M170 90V20M185 90V32M200 90V82M215 90V78M230 90V37M245 90V29M260 90V78M275 90V81"/><path d="M20 100H285" stroke-dasharray="3 5" opacity=".4"/>',
'<rect x="34" y="22" width="92" height="70" rx="4"/><path d="M47 35H112M47 48H112M47 61H112M47 74H112M60 28V86M75 28V86M90 28V86M105 28V86" opacity=".4"/><rect x="49" y="31" width="11" height="55" fill="currentColor" opacity=".12"/><rect x="93" y="31" width="11" height="55" fill="currentColor" opacity=".12"/><path d="M148 42H171M148 53H171M190 90H279M202 90V69M217 90V35M232 90V76M247 90V24M262 90V75"/>',
'<path d="M24 60H98L165 27V93L98 60M165 60H282M58 60V86H80M210 60V32H232M210 32V20M200 26H220M38 38C52 25 70 25 83 38M230 88C244 101 262 101 277 88"/><circle cx="48" cy="60" r="3"/><circle cx="210" cy="60" r="3"/>'
]
featured=[]
for i,id in enumerate(['blind','mrmp','lna']):
 p=next(p for p in records if p['id']==id);link='https://doi.org/'+p['doi'];tag=['Adaptive cooperative sensing','Joint sparse recovery','RF receiver design'][i]
 featured.append(f'<article class="feature-card"><div class="feature-art" aria-hidden="true"><svg viewBox="0 0 310 120">{feature_art[i]}</svg></div><div class="feature-body"><div class="feature-kicker" data-i18n="feature{i}Tag">{tag} · {p["year"]}</div><h3>{esc(p["title"])}</h3><p data-i18n="feature{i}Summary">{esc(p["summary"])}</p><a href="{esc(link)}" target="_blank" rel="noopener noreferrer" data-i18n="readPublication">Read publication</a></div></article>')
person={'@context':'https://schema.org','@type':'Person','@id':origin+'/#researcher','name':'Hadj Abdelkader Benzater','url':origin,'jobTitle':'Telecommunications researcher and PhD candidate','affiliation':{'@type':'CollegeOrUniversity','name':'École Militaire Polytechnique','address':{'@type':'PostalAddress','addressLocality':'Algiers','addressCountry':'DZ'}},'email':'mailto:benzater.hadj@gmail.com','sameAs':['https://github.com/LhadjBENZATER','https://orcid.org/0009-0006-2533-0315','https://www.researchgate.net/profile/Hadj-Benzater','https://enp-edu.academia.edu/BENZATERhadj',scholar_url,wos_url],'knowsAbout':['Cooperative compressed spectrum sensing','Joint sparse recovery','Software-defined radio','Sub-Nyquist acquisition','RF circuits']}
page={'@context':'https://schema.org','@type':'ProfilePage','name':'Hadj Abdelkader Benzater | EMP Research','url':origin,'mainEntity':person,'dateModified':status.get('attemptedAt',scholar_date)[:10]}
schema=[page]+[{'@context':'https://schema.org','@type':'ScholarlyArticle','name':p['title'],'datePublished':str(p['year']),'url':'https://doi.org/'+p['doi'] if p['doi'] else p['source'],'author':[{'@type':'Person','name':n} for n in p['authors']],'identifier':p['doi'] or p['source']} for p in records if p['kind'] not in ['Poster','Correction']]
template=(root/'index.template.html').read_text()
for k,v in {'__ORIGIN__':origin,'__WORK_COUNT__':str(sum(p['kind']!='Correction' for p in records)),'__SCHOLAR_TOTAL__':str(metrics['scholar']['citations']),'__H_INDEX__':str(metrics['scholar']['hIndex']),'__I10_INDEX__':str(metrics['scholar']['i10Index']),'__SCHOLAR_ENTRIES__':str(metrics['scholar']['profileEntries']),'__REVIEW_RECORDS__':str(metrics['peerReview']['records']),'__REVIEW_MANUSCRIPTS__':str(metrics['peerReview']['manuscripts']),'__REVIEW_JOURNALS__':str(len(metrics['peerReview']['journals'])),'__SCHOLAR_DATE__':pretty(scholar_date),'__WOS_DATE__':pretty(wos_date),'__CHECK_DATE__':pretty(status.get('attemptedAt',scholar_date)),'__METRICS__':json.dumps(metrics,ensure_ascii=False).replace('</','<\\/'),'__STATUS__':json.dumps(status,ensure_ascii=False).replace('</','<\\/'),'__JOURNALS__':''.join('<li>'+esc(j['name'])+'</li>' for j in metrics['peerReview']['journals']),'__PUBLICATIONS__':''.join(pub(p) for p in sorted(records,key=lambda x:-x['year'])),'__FEATURED__':''.join(featured),'__SCHEMA__':json.dumps(schema,ensure_ascii=False).replace('</','<\\/'),'__DATA__':json.dumps(records,ensure_ascii=False).replace('</','<\\/')}.items():template=template.replace(k,v)
for k,v in icons.items():template=template.replace('__ICON_'+k+'__','<svg viewBox="0 0 48 44">'+v+'</svg>')
template=template.replace('data-i18n="repository" data-publisher="true"','data-i18n="publisher"')
template=template.replace('<span class="external" aria-hidden="true">↗</span>','')
(dist/'index.html').write_text(template)
(dist/'.nojekyll').touch()
(dist/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+origin+'/sitemap.xml\n')
(dist/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>'+origin+'/</loc><lastmod>'+status.get('attemptedAt',scholar_date)[:10]+'</lastmod></url></urlset>')
(dist/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#102c36"/><text x="32" y="47" font-family="Georgia,serif" font-size="52" fill="#a5efce" text-anchor="middle">b</text></svg>')
(dist/'social.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630"><rect width="1200" height="630" fill="#102c36"/><circle cx="1040" cy="300" r="240" fill="none" stroke="#547f7e"/><circle cx="1040" cy="300" r="170" fill="none" stroke="#547f7e"/><text x="85" y="150" font-family="Arial" font-size="21" fill="#a5efce" letter-spacing="5">RESEARCH AT EMP · ALGIERS</text><text x="85" y="285" font-family="Arial" font-size="65" fill="white">Hadj Abdelkader</text><text x="85" y="375" font-family="Arial" font-size="90" fill="#a5efce">Benzater.</text><text x="85" y="490" font-family="Arial" font-size="26" fill="#b3ccce">Compressed sensing · Cooperative detection · SDR · RF</text></svg>')
(dist/'contact.vcf').write_text('BEGIN:VCARD\r\nVERSION:3.0\r\nN:Benzater;Hadj Abdelkader;;;\r\nFN:Hadj Abdelkader Benzater\r\nORG:École Militaire Polytechnique;Laboratoire Télécommunications\r\nTITLE:Telecommunications Researcher\r\nEMAIL;TYPE=WORK:benzater.hadj@gmail.com\r\nEMAIL;TYPE=WORK:d_BENZATER.HADJ_ABDELKADER@emp.mdn.dz\r\nURL:'+origin+'\r\nNOTE:ORCID 0009-0006-2533-0315\r\nEND:VCARD\r\n')
print('Generated site:',len(records),'catalogue records;',len(schema)-1,'structured publication records')

