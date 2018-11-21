#!/bin/sh
function request() {
	curl -G \
		"http://localhost:8821/add-feed/" \
		--data folder=blog \
		--data-urlencode url=$1
}

function parseJSON() {
	python -c "import sys, json; print(json.load(sys.stdin)['result'])"
}

while read line
do
	echo $line
	request "$line" 2> /dev/null | parseJSON
done < feed.list
