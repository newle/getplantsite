#
# for((i=1;i<=9;i++)); do wget "http://www.plant.csdb.cn/photo?page=$i&sname=&chname=&creator=&province=&loc=&habit=&year=" -O home$i.html; done
#
# cat home*.html | iconv -f "utf8" -t "gb18030" | grep "共有" > home.list
#
# awk -vFS="><a " '{for(i=1;i<=NF;i++){print "<a "$i">"}}' home.list  > temp; mv temp home.list
#
# grep -v "共有" home.list > temp; mv temp home.list
#
# sh getfromhome.sh > mysql.list
#
# ~/tools/mysql.sh local < mysql.list
#

1. test:
		sh -x processquery.sh "http://www.plant.csdb.cn/photo?sname=&chname=%E9%BE%99%E7%8F%A0&creator=&province=&loc=&habit=&year="
