#!/bin/sh
find test/ -name '*.feed.json' | xargs rm -f
find test/ -name '_list_.json' | xargs rm -f
git co test/
