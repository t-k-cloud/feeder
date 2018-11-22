#!/bin/bash
function request() {
	curl -G \
		"http://localhost/feeder/add-feed/" \
		--data folder=$1 \
		--data-urlencode url=$2
}

function parseJSON() {
	python -c "import sys, json; print(json.load(sys.stdin)['result'])"
}

function ctrl_c() {
	exit 1
}

trap ctrl_c INT

while read line
do
	tag=`echo $line | awk '{print $1}'`
	url=`echo $line | awk '{print $2}'`
	echo "tag=$tag, url=$url"
	request "$tag" "$url" 2> /dev/null | parseJSON
done < feeds/feed.list

touch feeds/added.tmp # unlock flag for running fetch.py
