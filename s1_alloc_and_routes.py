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
import ipaddress as ipaddr

dbfile = "./var/netdata-latest.db"
# cc = 'AR'
rir = 'lacnic'
type = 'ipv4'
maxLen = 24
minpeers = 1

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
        pyt[pfx] = {'pfx': pfx, 'rutas': [], 'nrutas': 0}
        stats.inc('allocs')
    #
    logging.info("Loaded {} allocs into trie".format(stats.get('allocs')) )

    # read routes and look for covering roas, logi assumes that most if not all ROAs will
    # protect _more specific_ prefixes than the ones listed in roas

    # stats.set('ninvalid', 0)
    stats.set('visible', 0)
    stats.set('invisible', 0)
    stats.set('nroutes', 0)
    stats.set('nrouteslacnic',0)

    # open file for csv export
    csvfile = open("var/s1_invisible_prefixes.csv", "w")
    csv_export = csv.writer(csvfile, dialect='excel', delimiter='|')
    csv_export.writerow(["Prefix", "visible", "total"])

    for x in ndb.runsql("SELECT * FROM riswhois WHERE type='{}' and viewed_by>{} ".format(type, minpeers)):
        stats.inc('nroutes')
        rpfx = str(x['prefix'])

        try:
            k = pyt.get_key(rpfx)
            pyt[k]['rutas'].append(rpfx)
            pyt[k]['nrutas'] = pyt[k]['nrutas']+1
        except:
            continue

    # END FOR X


    # process each entry, compact routes and calculate unassigned space
    for y in pyt:
        pfxlist = []
        pfxalloc = ipaddr.ip_network(pyt[y]['pfx'])
        visible_addrs = 0
        for r in pyt[y]['rutas']:
            pfxlist.append(ipaddr.ip_network(r))
        # end for r
        # compact list
        pfxlist2 = [ipa for ipa in ipaddr.collapse_addresses(pfxlist) ]
        for q in pfxlist2:
            visible_addrs = visible_addrs + q.num_addresses
        # set values
        pyt[y]['visible'] = visible_addrs
        pyt[y]['dark'] = pfxalloc.num_addresses - visible_addrs
        pyt[y]['total'] = pfxalloc.num_addresses
    # end for y


    # Write output
    for y in pyt:
        if pyt[y]['nrutas'] == 0:
            stats.inc('invisible')
            # csvrow = [y, pyt[y]]
            csvrow = [y, pyt[y]['visible'], pyt[y]['dark'] ]
            csv_export.writerow(csvrow)
        else:
            stats.inc('visible')
            stats.inc('nrouteslacnic', pyt[y]['nrutas'] )
            csvrow = [y, pyt[y]]
            # csv_export.writerow(csvrow)
            pass
    # END FOR y


    # Print results

    logging.info("Found {} TOTAL routes".format(stats.get('nroutes')) )
    logging.info("Found {} allocations for rir {}".format(stats.get('allocs'), rir) )
    logging.info("Found {} invisible allocs for type {}".format(stats.get('invisible'), type) )
    logging.info("Found {} visible allocs for type {}".format(stats.get('visible'), type) )
    logging.info("Found {} visible routes for type {}, rir={} ".format(stats.get('nrouteslacnic'), type, rir) )
    # logging.info("Found {} unknown routes".format(stats.get('nunknown')) )

    csvfile.close()

# end script
