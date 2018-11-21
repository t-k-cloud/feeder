#!/usr/bin/python3
import feedparser
import datetime
import socket
import time
import glob
import json
import uuid
import shutil
import os

# SRCH_PATH = "./test/**/**/_feed_.json"
# MAX_CACHE = 3

SRCH_PATH = "./feeds/**/**/_feed_.json"
MAX_CACHE = 1000

def fetch(url):
	socket.setdefaulttimeout(20)
	feeds = feedparser.parse(url)
	# failed to crawler data
	if not len(feeds.entries) > 0:
		raise Exception('failed')
	# update title and link
	title, link = "(no title)", url
	if hasattr(feeds['feed'], 'title'):
		title = feeds['feed']['title']
	if hasattr(feeds['feed'], 'link'):
		link = feeds['feed']['link']
	# update feed entries
	entries = []
	for ent in feeds.entries:
		entries.append({
			"title": ent.title if hasattr(ent, 'title') else "",
			"link": ent.link if hasattr(ent, 'link') else "",
			"desc": ent.description if hasattr(ent, 'description') else ""
		})
	return title, link, entries

def write_feeds(dirname, entries, recent):
	any_update = False
	# write JSON feeds to files
	for ent in entries:
		if (len(ent["title"]) == 0 or
		    len(ent["link"])  == 0 or
		    len(ent["desc"])  == 0):
			continue
		link = ent["link"]
		if link not in recent:
			print('[update] %s' % link)
			p = dirname + '/' + str(uuid.uuid1()) + '.feed.json'
			with open(p, 'w') as fh:
				json.dump(ent, fh)
				recent[link] = str(datetime.datetime.now())
			any_update = True
	# avoid recent records being oversized
	ordered_keys = sorted(recent, key=lambda x: x[1], reverse=True)
	for k in ordered_keys:
		#to_print = (recent[k], k)
		if len(recent) > MAX_CACHE:
			#print("[dele] ", end="")
			del recent[k]
		else:
			#print("[keep] ", end="")
			break
		#print(to_print)
	return any_update

def process_feed_file(path):
	with open(path) as fh:
		j = json.load(fh)
		if 'failed' not in j:
			j['failed'] = 0
		if 'recent' not in j:
			j['recent'] = {}
		if 'url' not in j:
			print("[no url]")
			return j
		try:
			title, link, entries = fetch(j['url'])
		except KeyboardInterrupt:
			print("Aborted by KeyboardInterrupt.")
			exit(1)
		except:
			j['failed'] += 1
			print("<* Failed *>")
			return j
		if write_feeds(dirname, entries, j['recent']):
			j['last-update'] = str(datetime.datetime.now())
		j['title'] = title
		j['link'] = link
		j['view-engine'] = 'feed-view' # support listify
		j['detailed'] = True # support listify
		print("[%s]" % title)
		return j

print('[search path]', SRCH_PATH)
paths = glob.glob(SRCH_PATH)

for path in paths:
	print(path, end=": ")
	dirname = os.path.dirname(path)
	# process _feed_.json file
	j = process_feed_file(path)
	# write back to the file
	with open(path, 'w') as fh:
		json.dump(j, fh, indent=4)
	# make _list_.json copy to support listify
	cur_dir = os.path.dirname(os.path.realpath(__file__))
	from_path = cur_dir + '/' + path
	link_path = cur_dir + '/' + dirname + '/_list_.json'
	shutil.copyfile(from_path, link_path)
