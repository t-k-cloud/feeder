#!/usr/bin/python3
import feedparser
import datetime
import socket
import time
import glob
import json
import uuid
import os

SRCH_PATH = "./test/**/**/_feed_.json"
# MAX_CACHE = 3

# SRCH_PATH = "./feeds/**/**/_feed_.json"
MAX_CACHE = 1000

def fetch(url):
	socket.setdefaulttimeout(20)
	feeds = feedparser.parse(url)
	if feeds.bozo:
		print('badly-formed or unreachable.')
		# do not return, try our best
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
	# write JSON feeds to files
	for ent in entries:
		link = ent["link"]
		if link not in recent:
			p = dirname + '/' + str(uuid.uuid1()) + '.feed.json'
			with open(p, 'w') as fh:
				json.dump(ent, fh)
				recent[link] = str(datetime.datetime.now())
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

def cnt_json(dirname):
	jsons = glob.glob(dirname + '/*.feed.json')
	return len(jsons)

print('[search path]', SRCH_PATH)
paths = glob.glob(SRCH_PATH)

for path in paths:
	dirname = os.path.dirname(path)
	j = {}
	# read _feed_.json file
	with open(path) as fh:
		j = json.load(fh)
		try:
			title, link, entries = fetch(j['url'])
		except:
			j['failed'] += 1
			print("[failed] %s" % path)
			continue
		write_feeds(dirname, entries, j['recent'])
		unread = cnt_json(dirname)
		j['unread'] = unread
		print("[%d unread] %s" % (unread, path))
	# write back to the file
	with open(path, 'w') as fh:
		json.dump(j, fh, indent=4)
	# make symbolic link to support listify
	cur_dir = os.path.dirname(os.path.realpath(__file__))
	from_path = cur_dir + '/' + path
	link_path = cur_dir + '/' + dirname + '/_list_.json'
	os.system('ln -sf ' + from_path + ' ' + link_path)
