


 awk -vFS=">|<" '
 function subtrim(x, start, end)
 {
	if((s = index(x, start)) != 0) {
		x = substr(x, s+length(start));
		if((e = index(x, end)) != 0) {
			return substr(x, 1, e-1); 
		}
	}
	return x;
 }
 function normpic(tnpic)
 {
	 if(index(tnpic, "Thumbnail") != 0) {
		 sub(/Thumbnail/, "Normal", tnpic);
	 } else if(index(tnpic, "image_t") != 0) {
	 	sub(/image_t/, "images", tnpic);
 	}
 	return tnpic;
 }
 NF>=25{
 pageurl="http://www.plant.csdb.cn/"subtrim($2, "href=\"", "\"");
 tnpicurl=subtrim($4,"src=\"", "\"");
 picurl = normpic(tnpicurl);
 sname=$9;
 chname=$11;
 publisher=$15

 #print pageurl"\t"tnpicurl"\t"picurl"\t"sname"\t"chname"\t"publisher
 print  "replace into plantimage(pageurl, thumbnailurl, picurl, sname, chname, publisher) values( \""pageurl"\",\""tnpicurl"\",\""picurl"\",\""sname"\",\""chname"\",\""publisher"\" );"
}' home.list
