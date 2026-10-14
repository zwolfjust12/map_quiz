"""Add explicit learning metadata and interior label anchors to prepared data."""
import json,re,collections
from shapely.geometry import shape
catalog=json.load(open('dist/data/catalog.json'))
settings={
 'TWN':('縣市',22,'zh'), 'GBR':('四個構成國',4,'en'), 'FRA':('大區',18,'fr'),
 'JPN':('都道府縣',47,'ja'),'USA':('州與哥倫比亞特區',51,'en'),'VNM':('舊制省市',63,'vi'),
 'ITA':('大區',20,'it'),'ESP':('自治區與自治市',19,'es'),'BEL':('大區',3,None),
 'DEU':('邦',16,'de'),'AUT':('邦',9,'de'),'AUS':('州與領地',None,'en'),'CAN':('省與領地',13,'en'),
 'BRA':('州與聯邦區',27,'pt'),'CHN':('省級分區',None,'zh'),'THA':('府及首都',77,'th'),
 'IDN':('省（資料快照）',None,'id'),'KOR':('道與廣域市等',None,'ko'),'RUS':('聯邦主體（資料快照）',None,'ru'),
 'NLD':('省與特別行政區',15,'nl'),'POL':('省',16,'pl'),'CHE':('邦',26,None),'PRT':('區與自治區',None,'pt')}
nonlatin=set('TWN CHN HKG MAC JPN KOR PRK RUS BLR UKR GRC CYP ISR IRN AFG BGD IND NPL PAK SAU IRQ SYR LBN JOR PSE EGY LBY TUN DZA MAR MRT SDN YEM OMN ARE QAT KWT BHR THA LAO KHM MMR LKA BTN ARM GEO ETH ERI BGR MKD MNG KAZ KGZ TJK'.split())
raw={f['properties']['adm1_code']:f['properties'] for f in json.load(open('admin1.json'))['features']}
for c in catalog:
 code=c['id'];level,expected,language=settings.get(code,('來源分區（層級待核對）',None,None))
 version='舊制 63 省市（2025 改制前）' if code=='VNM' else '資料快照・年代待確認'
 c.update(learning_level=level,expected_count=expected,available_count=c['count'],boundary_version=version,valid_period='2025 改制前' if code=='VNM' else None,primary_language=language,script='non-latin' if code in nonlatin else 'latin',source='Natural Earth 1:10m',license='Public domain',retrieved_at='2026-10-13',coverage_status='missing' if not c['count'] else 'partial' if expected and c['count']<expected else 'snapshot')
 if code=='VNM':c['note']='本題庫採街景學習用舊制 63 省市，不使用 2025 改制後區劃。'
 elif code=='TWN':c['note']='縣市層級：目前收錄 21 / 22 區，缺金門縣；本輪只測驗已收錄區域。'
 else:c['note']=('學習層級尚待逐國核對。' if code not in settings else '')+'區劃年代待確認；採來源快照，非現行官方完整名冊。'
 if not c['count']:continue
 p='dist/data/'+code+'.json';fc=json.load(open(p))
 for f in fc['features']:
  q=f['properties'];q.update(country_id=code,boundary_version=version,language=language,script='non-latin' if code in nonlatin or re.search('[\u0370-\u052f\u0590-\u109f\u3040-\u9fff\uac00-\ud7af]',q['local']) else 'latin')
  # Fallback flag is provenance, never infer native-language coverage from ASCII.
  r=raw.get(q['id'])
  if r and not (r.get('name_local') and not any(x in r['name_local'] for x in ['|','<','/'])):
   q['fallback']=not bool(language and r.get('name_'+language))
  if r and language and r.get('name_'+language) and any(x in q['local'] for x in ['|','/']):q['local']=r['name_'+language];q['fallback']=False
  q['name_status']='partial' if q['fallback'] or '待補' in q['zh'] else 'available'
  g=shape(f['geometry']);main=max(g.geoms,key=lambda x:x.area) if g.geom_type=='MultiPolygon' else g;pt=main.representative_point();q['label_point']=[round(pt.x,6),round(pt.y,6)]
 json.dump(fc,open(p,'w'),ensure_ascii=False,separators=(',',':'))
json.dump(catalog,open('dist/data/catalog.json','w'),ensure_ascii=False,separators=(',',':'))
print('Enriched',len(catalog),'country records')
