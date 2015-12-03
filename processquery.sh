


query=$1

tmpdir=`mktemp -d temp/temp.XXXXXXX`
currdir=$PWD
cd $tmpdir
 wget $query -O 0.html
 for((i=1;i<=9;i++)); do 
	 wget $query"&page=$i" -O $i.html; 
 done

 cat *.html | iconv -f "utf8" -t "gb18030" | grep "共有" > home.list

 awk -vFS="><a " '{for(i=1;i<=NF;i++){print "<a "$i">"}}' home.list  > temp; mv temp home.list

 grep -v "共有" home.list > temp; mv temp home.list

 echo "set names gbk;" > mysql.list
 sh $currdir/getfromhome.sh >> mysql.list
 wc -l mysql.list

 /search/wangzhen/tools/mysql.sh local < mysql.list
cd -
