USER=guest
PASSWORD=guest
HOST=ted.europa.eu
REMOTE_DIR=daily-packages/2018/
LOCAL_DIR=~/TED/daily-packages/2018/

lftp  -u "$USER","$PASSWORD" $HOST <<EOF

mirror -c $REMOTE_DIR $LOCAL_DIR;
exit
EOF
echo
echo "Transfer finished"
date

