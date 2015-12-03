#coding:gb18030
import urllib2
import MySQLdb

def fetchhtml(url, encoding="utf8"):
	try:
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		print url
		return response.read().decode(encoding).encode("gb18030")
	except:
		return ""


def geturlfromdic(dic):
	ret = dic['host'] + 'sname=' + dic['sname'] + \
		'&chname=' + dic['chname'] + \
		'&creator=' + dic['creator'] + \
		'&province=' + dic['province'] + \
		'&loc=' + dic['loc'] + \
		'&habit=' + dic['habit'] + \
		'&year=' + dic['year']
	return ret

import hashlib
def getmd5(str):
	m = hashlib.md5()
	m.update(str)
	return m.hexdigest()
def getmd5fromdic(dic):
	return getmd5(geturlfromdic(dic))
	

yearlist = [  "1980","1981","1982","1983","1984","1985","1986","1987","1988","1989",
			  "1990","1991","1992","1993","1994","1995","1996","1997","1998","1999",
			  "2000","2001","2002","2003","2004","2005","2006","2007","2008","2009",
			  "2010","2011","2012","2013","2014","2015" ]
provincelist = [ "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆", "香港", "澳门", "台湾" ]
userlist = set([])
#snamelist = set([])
chnamelist = set([])
loclist = set([])
habitlist = set([])

paralist = {
		"year": yearlist, 
		"province": provincelist,
#		"sname": snamelist,
		"chname": chnamelist,
		"creator": userlist,
		"loc": loclist,
		"habit": habitlist
		}

def getstartend(str, start, end=""):
	s_pos = str.find(start)
	if s_pos != -1:
		s_pos += len(start)
		if end != "":
			e_pos = str.find(end, s_pos)
			if e_pos != -1:
				return str[s_pos:e_pos]
		else:
			return str[s_pos:]
	return str
def normpic(tnpic):
	spos = tnpic.find("Thumbnail")
	if spos != -1:
		return tnpic[:spos] + "Normal" + tnpic[spos+len("Thumbnail"):]

	spos = tnpic.find("image_t")
	if spos != -1:
		return tnpic[:spos] + "images" + tnpic[spos+len("image_t"):]

	return tnpic;
			
	
#mysql -h"10.134.71.142" -u lvpi -plvpi picURLlibSta 
conn = MySQLdb.connect("10.134.71.142", "lvpi","lvpi", "picURLlibSta", charset='gbk', use_unicode=False)
cur = conn.cursor()
addtodb = "replace into plantimage(pageurl, thumbnailurl, picurl, sname, chname, publisher) values(%s, %s, %s, %s, %s, %s)"

def getallpicfrompageandstore(html):
	global conn
	global cur
	global addtodb

	global paralist
	#get all pic and store to mysql
	focusline = getstartend(html, "<br>共有", "\n")
	pictermlist = focusline.split("><a ")
	picnum = getstartend(pictermlist[0], "<b>", "</b>")
	try:
		picnum = int(picnum)	
	except Exception, e:
		print e
		picnum = 0
	
	for i in range(1,len(pictermlist)):
		termlist = pictermlist[i].split("<br>")
		if len(termlist) < 4:
			continue;
		#get detail
		pageurl = "http://www.plant.csdb.cn/" + getstartend(termlist[0], "href=\"", "\"")
		tnpicurl = getstartend(termlist[0], "src=\"", "\"")
		picurl = normpic(tnpicurl)
		sname = termlist[1]
		chname = termlist[2]
		publisher = getstartend(termlist[3], "<i>", "</i>")

		#push to db
 		#print  "replace into plantimage(pageurl, thumbnailurl, picurl, sname, chname, publisher) values( \"" + pageurl + "\",\"" + tnpicurl + "\",\"" + picurl + "\",\"" + sname + "\",\"" + chname + "\",\"" + publisher + "\" );"
		try:
			cur.execute(addtodb, (pageurl, tnpicurl, picurl, sname, chname, publisher))
			conn.commit()
		except Exception, e:
			print e
 			print  "replace into plantimage(pageurl, thumbnailurl, picurl, sname, chname, publisher) values( \"" + pageurl + "\",\"" + tnpicurl + "\",\"" + picurl + "\",\"" + sname + "\",\"" + chname + "\",\"" + publisher + "\" );"

		#add all item to paralist
#		paralist['sname'].add(sname)
		paralist['chname'].add(chname)
		paralist['creator'].add(publisher)

	return picnum


def splitquery(query, nextqueue):
	global paralist
	global finishedquerymd5
	split = False
	for key in paralist.keys():
		if query[key] == "":
			for i in paralist[key]:
				q = dict(query)
				q[key] = i
				if getmd5fromdic(q) not in finishedquerymd5:
					nextqueue.append(q)
					split = True
	return split

LIMITPICNUM = 500
PICNUMPERPAGE = 50
def processquery(query, nextqueue):
	global finishedquerymd5_file
	global finishedquerymd5
	global finishedquery

	global LIMITPICNUM
	global PICNUMPERPAGE 

	if len(finishedquerymd5) % 1000 == 1:
		finishedquerymd5_file=open("finished_md5.txt", "w")
		for i in finishedquerymd5:
			print >> finishedquerymd5_file, i
		finishedquerymd5_file.close()

	#check split if processed before
	if getmd5fromdic(query) in finishedquerymd5:
		print "has process this query: " + geturlfromdic(query)
		#print "md5 = " + getmd5fromdic(query)
		#print finishedquerymd5
		split = splitquery(query, nextqueue)
		if split == False:
			print "query can't not split still, add to the end of queue for next generate: " + geturlfromdic(query)
			nextqueue.append(query)
		return -1

	#get query
	html = fetchhtml(geturlfromdic(query))
	picnum = getallpicfrompageandstore(html)
	#get picnum
	pagenum = picnum/PICNUMPERPAGE
	#get all next few pages
	for i in range(1, 10 if pagenum>10 else pagenum):
		page = fetchhtml(geturlfromdic(query) + "&page=" + str(i))
		getallpicfrompageandstore(page)

	split = False
	if picnum > LIMITPICNUM:
		#get split condition
		split = splitquery(query, nextqueue)
		if split == False:
			print "query can't not split and has pic over limit, add to the end of queue for next generate: " + geturlfromdic(query)
			nextqueue.append(query)

	#mark as finished
	finishedquerymd5.add(getmd5fromdic(query))	
	finishedquery.append(query)

home={'host': 'http://www.plant.csdb.cn/photo?', 'sname':'', 'chname':'', 'creator':'', 'province':'', 'loc':'', 'habit':'', 'year':''}
finishedquerymd5 = set(open("finished_md5.txt", "r").readlines())
finishedquery = []

querylist = [ home,  ];
querylist2 = []
while True:
	if len(querylist)==0 and len(querylist2)==0:
		break
	for i in querylist:
		#add some thing to querylist2
		processquery(i, querylist2)
		print i
	querylist=[]
	for i in querylist2:
		#add some thing to querylist
		processquery(i, querylist)
		print i
	querylist2=[]








