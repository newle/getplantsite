#coding:gb18030
import urllib2
import MySQLdb

yearlist = [  "1980","1981","1982","1983","1984","1985","1986","1987","1988","1989",
			  "1990","1991","1992","1993","1994","1995","1996","1997","1998","1999",
			  "2000","2001","2002","2003","2004","2005","2006","2007","2008","2009",
			  "2010","2011","2012","2013","2014","2015" ]
provincelist = [ "����", "���", "�ӱ�", "ɽ��", "���ɹ�", "����", "����", "������", "�Ϻ�", "����", "�㽭", "����", "����", "����", "ɽ��", "����", "����", "����", "�㶫", "����", "����", "����", "�Ĵ�", "����", "����", "����", "����", "����", "�ຣ", "����", "�½�", "���", "����", "̨��" ]
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
	focusline = getstartend(html, "<br>����", "\n")
	#print focusline
	pictermlist = focusline.split("><a ")
	#for i in pictermlist:
	#	print i
	picnum = getstartend(pictermlist[0], "<b>", "</b>")
	
	for i in range(1,len(pictermlist)):
		termlist = pictermlist[i].split("<br>")

		#target="_blank" href="details?guid=photo:cfh@541b0ae6-b4dd-45f9-b176-38275bb5bcda"><img width="100" height="75" src="http://www.cfh.ac.cn/Data/2009/200908/20090813/Thumbnail/541b0ae6-b4dd-45f9-b176-38275bb5bcda.jpg" /></a>
		#Tubocapsicum anomalum
		#����
		#<i>helixcn</i> ����(<a href="details?guid=photo:cfh@541b0ae6-b4dd-45f9-b176-38275bb5bcda" target="_blank">����</a>)</td><td align="center"  width="180"
		if len(termlist) < 4:
			continue;
		pageurl = "http://www.plant.csdb.cn/" + getstartend(termlist[0], "href=\"", "\"")
		tnpicurl = getstartend(termlist[0], "src=\"", "\"")
		picurl = normpic(tnpicurl)
		sname = termlist[1]
		chname = termlist[2]
		publisher = getstartend(termlist[3], "<i>", "</i>")
 		print  "replace into plantimage(pageurl, thumbnailurl, picurl, sname, chname, publisher) values( \"" + pageurl + "\",\"" + tnpicurl + "\",\"" + picurl + "\",\"" + sname + "\",\"" + chname + "\",\"" + publisher + "\" );"

		#push to db
		cur.execute(addtodb, (pageurl, tnpicurl, picurl, sname, chname, publisher))
		conn.commit()
		#add all item to paralist
		paralist['sname'].add(sname)
		paralist['chname'].add(chname)
		paralist['creator'].add(publisher)

	return picnum




def fetchhtml(url, encoding="utf8"):
	try:
		print url
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		return response.read().decode(encoding).encode("gb18030")
	except:
		return ""


def geturlfromdic(dic):
	ret = dic['host'] + 'sname=' + dic['sname'] + '&chname=' + dic['chname'] + '&creator=' + dic['creator'] + '&province=' + dic['province'] + '&loc=' + dic['loc'] + '&habit=' + dic['habit'] + '&year=' + dic['year']
	return ret

import hashlib
def getmd5(str):
	print str
	m = hashlib.md5()
	m.update(str)
	print m.hexdigest()
	return m.hexdigest()
def getmd5fromdic(dic):
	return getmd5(geturlfromdic(dic))


#http://www.plant.csdb.cn/photo?sname=Commelina communis &chname=��Ҷ�ӻ�&creator=&province=&loc=&habit=&year=
home={'host': 'http://www.plant.csdb.cn/photo?', 'sname':'Commelina communis ', 'chname':'��Ҷ�ӻ�', 'creator':'', 'province':'', 'loc':'', 'habit':'', 'year':''}

#print getmd5fromdic(home)

print geturlfromdic(home)
html = fetchhtml(geturlfromdic(home))
print html
#print html.encode("gb18030")
#print getallpicfrompageandstore(html)
