#!/bin/bash

cat <<EOF
How about reading the source code instead of
running the entire pipeline?

Please think twice whether you really need
to download over 5000 files from sejm.gov.pl.

Thanks.
EOF

exit

mkdir data

for (( session=1; session <= 95 ; session++ ))
do
  num_downloaded=0
  num_failures=0
  for (( voting=1; ; voting++ ))
  do
    >&2 echo "Session ${session}, voting ${voting}"
    url="http://orka.sejm.gov.pl/Glos7.nsf/nazwa/${session}_${voting}/\$file/glos_${session}_${voting}.pdf"
    /usr/bin/wget --directory-prefix=data "${url}" 2>> wget.log
    failure=$(( !! $? ))
    if (( failure ))
    then
      num_failures=$(( ${num_failures} + 1 ))
    else
      num_failures=0
      num_downloaded=$(( ${num_downloaded} + 1 ))
    fi
    if (( num_failures > 5 && num_downloaded > 0 ))
    then
      break
    fi
    if (( num_failures > 100 ))
    then
      break
    fi
  done
  >&2 echo "Done session ${session} with ${num_downloaded} votings"
done

for file in ./data/*.pdf
do
  >&2 echo "${file}"
  pdftohtml -q -nodrm -noframes -wbt 20 "${file}"
done

./scrape.py
./svd.py
./plot3d.py
./plot2d.py
./axes.py
