#!/bin/sh
DIR=test
find $DIR/ -name '*.feed.json' | xargs rm -f
find $DIR/ -name '_list_.json' | xargs rm -f
git co $DIR/
