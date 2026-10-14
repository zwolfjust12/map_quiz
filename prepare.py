import json,collections,re
from shapely.geometry import shape,mapping
from shapely import orient_polygons
from shapely.ops import unary_union
from opencc import OpenCC
cc=OpenCC('s2twp')
raw=json.load(open('admin1.json'))['features']; countries=json.load(open('world10.json'))['features']; groups=collections.defaultdict(list)
for f in raw:groups[f['properties']['adm0_a3']].append(f)
lang={}
for codes,l in [('USA GBR AUS NZL CAN IRL JAM BHS BRB TTO GUY BLZ NGA GHA KEN UGA ZMB ZWE BWA ZAF NAM LBR SLE GMB MWI FJI PNG SLB VUT','en'),('TWN CHN HKG MAC','zh'),('JPN','ja'),('KOR PRK','ko'),('RUS BLR','ru'),('UKR','uk'),('GRC CYP','el'),('ISR','he'),('IRN AFG','fa'),('BGD','bn'),('IND NPL','hi'),('PAK','ur'),('SAU IRQ SYR LBN JOR PSE EGY LBY TUN DZA MAR MRT SDN YEM OMN ARE QAT KWT BHR','ar'),('VNM','vi'),('FRA','fr'),('DEU AUT','de'),('ITA','it'),('ESP MEX ARG CHL PER COL ECU VEN URY PRY BOL CRI PAN GTM HND SLV NIC CUB DOM','es'),('BRA PRT AGO MOZ','pt'),('IDN','id'),('TUR','tr'),('POL','pl'),('HUN','hu'),('SWE','sv'),('NLD','nl')]:
 for c in codes.split():lang[c]=l
aggzh={
'FRA':'奧弗涅-隆-阿爾卑斯|勃艮第-法蘭琪-康堤|布列塔尼|中央-羅亞爾河谷|科西嘉|大東部|瓜地洛普|法屬圭亞那|上法蘭西|馬丁尼克|馬約特|諾曼第|新阿基坦|奧克西塔尼|羅亞爾河地區|普羅旺斯-阿爾卑斯-蔚藍海岸|留尼旺|法蘭西島',
'ITA':'阿布魯佐|普利亞|巴西利卡塔|卡拉布里亞|坎帕尼亞|艾米利亞-羅馬涅|弗留利-威尼斯朱利亞|拉齊奧|利古里亞|倫巴底|馬爾凱|莫利塞|皮埃蒙特|薩丁尼亞|西西里|托斯卡尼|特倫提諾-上阿迪傑|翁布里亞|奧斯塔谷|威尼托',
'ESP':'安達魯西亞|亞拉岡|阿斯圖里亞斯|加那利群島|坎塔布里亞|卡斯提亞-雷昂|卡斯提亞-拉曼查|加泰隆尼亞|休達|埃斯特雷馬杜拉|納瓦拉|加利西亞|巴利亞利群島|拉里奧哈|馬德里|梅利利亞|穆爾西亞|巴斯克|瓦倫西亞',
'BEL':'布魯塞爾首都大區|法蘭德斯大區|瓦隆大區'}
def geom(g,tol):
 g=mapping(orient_polygons(shape(g).simplify(tol,preserve_topology=True),exterior_cw=True))
 def rnd(v):return [rnd(a) for a in v] if isinstance(v,(list,tuple)) else round(v,6)
 g['coordinates']=rnd(g['coordinates'])
 # D3 uses clockwise exterior rings.
 if g['type']=='Polygon':pass
 elif g['type']=='MultiPolygon':pass
 return g
catalog=[];world=[]
for w in countries:
 p=w['properties'];c=p['ADM0_A3'];fs=groups.get(c,[]);note='Natural Earth 資料快照；區劃與譯名可能未反映近期改制。'
 if c in aggzh:
  regs=sorted(set(f['properties']['region'] for f in fs)); zs=dict(zip(regs,aggzh[c].split('|'))); out=[]
  for r in regs:
   merged=unary_union([shape(f['geometry']) for f in fs if f['properties']['region']==r]); local={'Apulia':'Puglia','Sicily':'Sicilia','Canary Is.':'Canarias','Flemish':'Vlaams Gewest','Walloon':'Région wallonne','Capital Region':'Région de Bruxelles-Capitale'}.get(r,r)
   out.append({'type':'Feature','properties':{'id':c+'-'+r,'local':local,'en':r,'zh':zs[r],'fallback':False},'geometry':mapping(merged)})
  fs=out;note='依一級區劃合併來源邊界；'+note
 elif c=='GBR':
  subsets=collections.defaultdict(list)
  for f in fs:
   pp=f['properties'];r=pp['region'];h=pp['code_hasc'] or '';n='Northern Ireland' if r=='Northern Ireland' else 'Scotland' if r in ['Highlands and Islands','Eastern','North Eastern','South Western'] else 'Wales' if r in ['East Wales','West Wales and the Valleys'] else 'England';subsets[n].append(f)
  fs=[{'type':'Feature','properties':{'id':'GBR-'+n,'local':n,'en':n,'zh':{'England':'英格蘭','Scotland':'蘇格蘭','Wales':'威爾斯','Northern Ireland':'北愛爾蘭'}[n],'fallback':False},'geometry':mapping(unary_union([shape(f['geometry']) for f in ff]))} for n,ff in subsets.items()]
  note='以四個構成國為測驗層級。'+note
 if c=='VNM':note='此題庫為越南舊制 63 省市，未套用 2025 年改制；請勿作為現行行政區查詢。'
 if c=='TWN':note='縣市層級資料快照；來源缺少金門縣，因此目前共 21 區。'
 feats=[]
 for f in fs:
  q=f['properties']
  if 'local' in q:props=q
  else:
   native=q.get('name_local')
   if native and ('|' in native or '<' in native):native=None
   native=native or q.get('name_'+lang.get(c,''))
   fallback=not bool(native)
   native=native or q.get('name') or q.get('name_en') or q['adm1_code']
   if c in ['TWN','HKG','MAC']:native=cc.convert(native)
   props={'id':q['adm1_code'],'local':native,'en':q.get('name_en') or q.get('name') or native,'zh':cc.convert(q.get('name_zht') or q.get('name_zh') or '') or '中文譯名待補','fallback':fallback and bool(re.search(r'[^\x00-\x7f]',native))==False}
  feats.append({'type':'Feature','properties':props,'geometry':geom(f['geometry'],.008)})
 if feats:json.dump({'type':'FeatureCollection','features':feats},open('dist/data/'+c+'.json','w'),ensure_ascii=False,separators=(',',':'))
 name=cc.convert(p.get('NAME_ZHT') or p.get('NAME_ZH') or p['NAME_EN'])
 if c=='TWN':name='臺灣'
 entry={'id':c,'name':name,'en':p['NAME_EN'],'count':len(feats),'note':note,'continent':p.get('CONTINENT'),'lon':p.get('LABEL_X',0),'lat':p.get('LABEL_Y',0)}
 catalog.append(entry);world.append({'type':'Feature','properties':{'id':c},'geometry':geom(w['geometry'],.07)})
json.dump(catalog,open('dist/data/catalog.json','w'),ensure_ascii=False,separators=(',',':'))
json.dump({'type':'FeatureCollection','features':world},open('dist/data/world.json','w'),separators=(',',':'))
print('Countries:',len(catalog),'with regions:',sum(x['count']>0 for x in catalog),'regions:',sum(x['count'] for x in catalog))
