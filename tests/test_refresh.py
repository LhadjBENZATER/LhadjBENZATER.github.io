import copy,json,pathlib,tempfile,unittest
from unittest.mock import patch
import refresh

class ResearchUpdaterTests(unittest.TestCase):
 def test_crossref_is_not_google_scholar(self):
  p={'scholarCitations':17,'scholarAsOf':'2026-11-21'}
  refresh.apply_crossref_metrics(p,{'is-referenced-by-count':14},'2026-11-22')
  self.assertEqual(p['scholarCitations'],17);self.assertEqual(p['scholarAsOf'],'2026-11-21');self.assertEqual(p['crossrefCitations'],14)
 def test_invalid_count_does_not_erase_last_good_value(self):
  p={'crossrefCitations':14,'crossrefAsOf':'2026-11-21'}
  refresh.apply_crossref_metrics(p,{'is-referenced-by-count':None},'2026-11-22')
  self.assertEqual(p,{'crossrefCitations':14,'crossrefAsOf':'2026-11-21'})
 def test_orcid_deduplication_and_normalization(self):
  ids={'external-id':[{'external-id-type':'doi','external-id-value':'https://doi.org/10.1002/ETT.70000'}]}
  record={'group':[{'external-ids':ids,'work-summary':[{'external-ids':ids}]}]}
  self.assertEqual(refresh.orcid_dois(record),{'10.1002/ett.70000'})
 def test_reject_wrong_author(self):
  work={'author':[{'family':'Benzater','given':'Benali'}],'type':'journal-article','title':['Different researcher'], 'published':{'date-parts':[[2026]]}}
  self.assertIsNone(refresh.from_crossref(work,'10.1234/example',{'orcid':'0009-0006-2533-0315'},'2026-11-21'))
 def test_orcid_identity_and_full_name(self):
  self.assertTrue(refresh.author_is_benzater({'ORCID':'https://orcid.org/0009-0006-2533-0315'},'0009-0006-2533-0315'))
  self.assertTrue(refresh.author_is_benzater({'given':'Hadj Abdelkader','family':'Benzater'},'0009-0006-2533-0315'))
 def test_source_outage_retains_data(self):
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);(root/'dist').mkdir()
   pubs=[{'id':'existing','doi':'10.1002/ett.70000','scholarCitations':17,'crossrefCitations':14}]
   metrics={'asOf':'2026-11-21','scholar':{'citations':68},'peerReview':{'records':76,'manuscripts':43}}
   for name,value in [('site-config.json',{'orcid':'0009-0006-2533-0315'}),('metrics-overrides.json',{}),('dist/publications.json',pubs),('dist/research-metrics.json',metrics)]:refresh.save(root/name,value)
   with patch('refresh.get_json',side_effect=TimeoutError('source unavailable')):status=refresh.refresh(root,apply=True)
   self.assertEqual(refresh.read(root/'dist/publications.json'),pubs)
   self.assertEqual(refresh.read(root/'dist/research-metrics.json')['scholar']['citations'],68)
   self.assertEqual(status['result'],'sources-unavailable')
 def test_duplicate_doi_is_not_added(self):
  work={'DOI':'10.1002/ett.70000','is-referenced-by-count':14}
  record={'group':[{'external-ids':{'external-id':[{'external-id-type':'doi','external-id-value':'10.1002/ETT.70000'}]}}]}
  with tempfile.TemporaryDirectory() as td:
   root=pathlib.Path(td);(root/'dist').mkdir()
   for name,value in [('site-config.json',{'orcid':'0009-0006-2533-0315'}),('metrics-overrides.json',{}),('dist/publications.json',[{'id':'old','doi':'10.1002/ett.70000','scholarCitations':17}]),('dist/research-metrics.json',{'asOf':'2026-11-21','scholar':{},'peerReview':{}})]:refresh.save(root/name,value)
   with patch('refresh.get_json',side_effect=lambda url:record if 'orcid.org' in url else {'message':work}):refresh.refresh(root,apply=True)
   self.assertEqual(len(refresh.read(root/'dist/publications.json')),1)
 def test_invalid_manual_metric_is_rejected(self):
  with self.assertRaises(ValueError):refresh.apply_overrides({'scholar':{}},[],{'scholar':{'asOf':'2026-11-21','citations':-1}})

if __name__=='__main__':unittest.main()
