#!/usr/bin/env python
################################################################
# (c) CarlosM carlos@xt6labs.io
# 
# 2019-10-06
################################################################

import pytricia
import sqlite3
import logging
import fire
import collections
import pysnooper
import csv

dbfile = "./var/netdata-latest.db"
# cc = 'AR'
rir = 'lacnic'
type = 'ipv6'
maxLen = 24

class netdatadb:
	def __init__(self, wdb):
		try:
			self.con = sqlite3.connect(wdb)
			self.con.row_factory = sqlite3.Row
		except:
			self.conf = False
			raise
	# end init

	def runsql(self, wsql):
		self.cur = self.con.cursor()
		self.cur.execute(wsql)
		return self.cur
	# end runsql

    # def getOneValue(self, wsql):
    #     self.cur = self.con.cursor()
    #     self.cur.execute(wsql)
    #     for x in self.cur:
    #         val = x.pop(0)
    #     return val
    # # end getOneValue
# end netdatadb

class counters:
    def __init__(self):
        self.cnt = {}
    # end

    def set(self, wkey, wval):
        self.cnt[wkey] = wval
    # end

    def get(self, wkey):
        return self.cnt.get(wkey, 0)
    # end

    def inc(self, wkey, winc=1):
        self.cnt[wkey] = self.cnt[wkey] + winc
# end counters


if __name__ == "__main__":
    logging.basicConfig( level=logging.INFO )
    stats = counters()
    logging.debug("Finding Invisible Resources - 20191006")

    #
    ndb = netdatadb(dbfile)

    # load allocations into pytricia
    logging.info("Loading Allocations and Assignments into pytricia")
    pyt = pytricia.PyTricia(128)
    sql_alloc = "SELECT * FROM numres WHERE rir='{}' AND type='{}' AND (status='allocated' or status='assigned') " \
        .format(rir, type)
    stats.set('allocs', 0)
    for e in ndb.runsql(sql_alloc):
        pfx = str(e['prefix'])
        logging.debug("loading alloc for {} ".format(pfx))
        pyt[pfx] = 'NV'
        stats.inc('allocs')
    #
    logging.info("Loaded {} allocs into trie".format(stats.get('allocs')) )

    # read routes and look for covering roas, logi assumes that most if not all ROAs will
    # protect _more specific_ prefixes than the ones listed in roas

    stats.set('ninvalid', 0)
    stats.set('nvalid', 0)
    stats.set('invisible', 0)
    stats.set('nroutes', 0)

    # open file for csv export
    csvfile = open("var/s1_invisible_prefixes.csv", "w")
    csv_export = csv.writer(csvfile, dialect='excel', delimiter='|')
    csv_export.writerow(["Prefix", "VisibleOrNot"])

    for x in ndb.runsql("SELECT * FROM riswhois WHERE type='{}' ".format(type, rir)):
        stats.inc('nroutes')
        rpfx = str(x['prefix'])
        # (rov_status, roas) = assignValidityStatus(roadata_pyt, x, 4)

        try:
            k = pyt.get_key(rpfx)
            pyt[k] = "V"
        except:
            continue

    # END FOR X

    for y in pyt:
        if pyt[y] == "NV":
            stats.inc('invisible')
        csvrow = [y, pyt[y]]
        csv_export.writerow(csvrow)
    # END FOR y


    logging.info("Found {} TOTAL routes".format(stats.get('nroutes')) )
    logging.info("Found {} allocations for rir {}".format(stats.get('allocs'), rir) )
    logging.info("Found {} invisible allocs for type {}".format(stats.get('invisible'), type) )
    # logging.info("Found {} unknown routes".format(stats.get('nunknown')) )

    csvfile.close()

# end script
