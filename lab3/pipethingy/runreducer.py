#!/usr/bin/env python3

import sys
import wordcounter

reducer_id = sys.argv[1]  # get the reducer ID from the command line argument
reducer = wordcounter.Reducer(reducer_id)
reducer.start()
