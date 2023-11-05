#!/usr/bin/env python3

import sys
import wordcounter

mapper = wordcounter.Mapper(2, int(wordcounter.mapperports[int(sys.argv[1])]))
mapper.start()
