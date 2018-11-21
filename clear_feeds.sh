#!/bin/bash
DIR=feeds
find $DIR/ -name '*.feed.json' -print0 | xargs -0 rm -f
find $DIR/ -name '_list_.json' -print0 | xargs -0 rm -f
git co $DIR/
