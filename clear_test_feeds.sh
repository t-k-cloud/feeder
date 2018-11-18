#!/bin/sh
find test/ -name '*.feed.json' | xargs rm -f
git co test/
