#! /bin/bash

# Jiri Kvita (c) 2004-2005

file="index.html"
title=""
titlecolor="#0000FF"
text=""
sourcetext=source.txt

TNsize=200
nx=4

# use separate extensions to convert e.g. eps to a page of gif's etc.
extension=gif
orig_extension=gif

rm -rf ${file}

if ! [ -d small ] ; then
 mkdir small
fi


echo "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\""  >> ${file}


echo "<html>" >> ${file}

echo "<head>"                      >> ${file}
echo "  <title> ${title} </title>" >> ${file}
echo " <meta http-equiv=\"Content-Type\" content=\"text/html;charset=UTF-8\" > " >> ${file}
echo "</head>"                     >> ${file}

echo " <body>" >> ${file}
echo "  <center><h1><span style=\"color: ${titlecolor};\">${title}</span></h1></center>" >> ${file}
echo "<p>" >> ${file}
echo ${text} >> ${file}
if [ -f ${sourcetext} ] ; then
  echo "Including text from file ${sourcetext} to ${file}..."
  cat ${sourcetext} >> ${file}
else
  echo "Warning: ${sourcetext} not found, no text included to ${file}..."
fi
echo "</p>" >> ${file}

echo "  <table>" >> ${file}
echo "   <tr>" >> ${file}
i=0
j=0

# echo "Creating thumbnails..."
for orig_img in `ls *.${orig_extension}` ; do 

  img=${orig_img}

  # convert from eps/ps as in orig_extension:
  #if ! [ ${orig_extension} == ${extension} ] ; then
  #  base=`echo $img | sed "s/.${orig_extension}//"`
  #  img=${base}.${extension}
  #  convert ${base}.${orig_extension} ${img}
  #fi

  #creating scaled thumbnails
  #convert -scale ${TNsize} ${img} small/TN_${img}

  echo "    <td align="center"><a href=\"${img}\"> <img src=\"${img}\" alt=\"${img}\"/> </a> </td>  "  >> ${file}
  i=`expr $i + 1` 
  j=`expr ${i} % ${nx}`
  if [ $j -eq 0 ] ; then
   echo "   </tr><tr>" >> ${file}
  fi

done

echo "    </tr>" >> ${file}
echo "  </table>" >> ${file}
DATE=`date`
echo "  <br /><br />Created ${DATE} by (c) Jiri Kvita using <a href=\"CreateHTMLpage.sh\">CreateHTMLpage.sh</a> :)"  >> ${file}
echo " </body>" >> ${file}
echo "</html>" >> ${file}
