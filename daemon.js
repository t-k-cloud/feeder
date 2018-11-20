var express = require('express');
var bodyParser = require('body-parser');
var normUrl = require('normalize-url')
var glob = require('glob')
var fs = require("fs");
var feedParser = require('feedparser');
var request = require('request');
var process = require('process')
var filenamify = require('filenamify');

var app = express();
app.use(express.static('.'));
app.use(bodyParser.json());

// FEED_ROOT = './test'
FEED_ROOT = './feeds'

/* load all existing feed links */
function read_feed_links() {
	let feeds = {}
	return new Promise((resolve) => {
		glob(FEED_ROOT + "/**/**/_feed_.json", {}, (err, files) => {
			files.forEach((path, idx) => {
				const json = JSON.parse(fs.readFileSync(path).toString())
				const url  = normUrl(json.url)
				feeds[url] = {
					'path': path,
					'title': json.title
				}
			})
			resolve(feeds)
		});
	})
}

/* fetch a feed title from URL */
function fetch_feed_title(url) {
	return new Promise((resolve) => {
		var feedparser = new feedParser();
		process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;
		var req = request(url)
		req.on('error', function (error) {
			resolve([null, 'Connection error'])
		});

		req.on('response', function (res) {
			if (res.statusCode !== 200) {
				resolve([null, 'Bad HTTP status: ' + res.statusCode])
			} else {
				this.pipe(feedparser);
			}
		});

		feedparser.on('error', function (error) {
			resolve([null, 'Not a feed'])
		});

		feedparser.on('readable', function () {
			var meta = this.meta;
			resolve([meta.title, 'Successful'])
		});
	})
}

/* actual store feeds onto disk */
function store_new_feed(path, url, callbk) {
	console.log(path)
	/* make directory */
	try {
		fs.mkdirSync(path)
	} catch (err) {
		callbk('mkdir error: ' + err.code)
		return
	}
	/* write _feed_.json file */
	j = JSON.stringify({ 'url': url })
	fs.writeFile(path + "/_feed_.json", j, function(err) {
		if(err) {
			callbk('write _feed_.json error: ' + err)
			return
		}
		callbk('successful!')
	})
}

read_feed_links().then((feeds) => {
	const port = 8821;
	app.listen(port);
	console.log('listening on port ' + port)

	app.get('/add-feed/', function (req, res) {
		const url = normUrl(req.query.url)
		const folder = req.query.folder

		if (feeds[url]) {
			console.log(`${url} exists already!`)
			console.log(feeds[url])
			res.json({
				'normalized-url': url,
				'result': 'exists already!',
				'path': feeds[url]['path'],
				'title': feeds[url]['title']
			});
		} else {
			console.log(`Adding feed: ${url} to "${folder}"...`)
			fetch_feed_title(url).then((_res) => {
				const title = _res[0]
				const key = filenamify(
					title + '-' + url,
					{replacement: '_'}
				)
				const err = _res[1]
				if (title) {
					const path = `${FEED_ROOT}/${folder}/${key}`
					store_new_feed(path, url, (__res) => {
						feeds[url] = {'path': path, 'title': title}
						res.json({
							'normalized-url': url,
							'result': __res,
							'path': path,
							'title': title
						});
					})
				} else {
					res.json({
						'normalized-url': url,
						'result': err
					});
				}
			})
		}
	})

	process.on('SIGINT', function() {
		console.log('');
		console.log('Bye bye.');
		process.exit( );
	})
})
