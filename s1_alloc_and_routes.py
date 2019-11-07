#!/usr/bin/env python
################################################################
# (c) CarlosM carlos@xt6labs.io
# 
# 2019-10-06
################################################################

import pytricia
import sqlite3
import logging
import click
import collections
import pysnooper
import csv
import ipaddress as ipaddr

# dbfile = "./var/netdata-latest.db"
rir = 'lacnic'
type = 'ipv4'
minpeers = 1
# LIMIT = 10000

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

def loadAllocsTrie_naif(dbfile):
    """
    Cargamos asignaciones en el trie asumiendo que toda ruta es un prefijo igual o mas especifico a una asignacion.
    """
    ndb = netdatadb(dbfile)

    # load allocations into pytricia
    logging.info("Loading Allocations and Assignments into pytricia")
    pyt = pytricia.PyTricia(32)
    sql_alloc = "SELECT * FROM numres WHERE rir='{}' AND type='{}' AND (status='allocated' or status='assigned') " \
        .format(rir, type)
    stats.set('allocs', 0)
    for e in ndb.runsql(sql_alloc):
        pfx = str(e['prefix'])
        org = int(e['orgid'])
        logging.debug("loading alloc for {} ".format(pfx))
        # pyt[pfx] = {'pfx': pfx, 'rutas': [], 'nrutas': 0}
        pyt[pfx] = {'pfx': pfx, 'rutas': [], 'nrutas': 0, 'orgid': org}
        stats.inc('allocs')
    #
    logging.info("Loaded {} allocs into trie".format(stats.get('allocs')) )
    return pyt
# end def loadAllocsTrie_naif

def loadAllocsTrie_compact(dbfile, LIMIT):
    """
    Cargamos el trie viendo que una organizacion puede tener prefijos agregables, y que las rutas que publica
    en realidad son mas especificas que estas asignaciones agregadas.
    """
    ndb = netdatadb(dbfile)

    # load allocations into pytricia
    logging.info("Loading Allocations and Assignments into pytricia")
    pyt = pytricia.PyTricia(32)

    # first loop over orgids
    sql_orgs = "SELECT orgid FROM numres WHERE rir='{}' AND type='{}' AND (status='allocated' or status='assigned') LIMIT {}" \
        .format(rir, type, LIMIT)

    stats.set('allocs', 0)
    no = 0
    for o in ndb.runsql(sql_orgs):
        org = int(o['orgid'])
        logging.debug("processing orgid: {}".format(org))
        no = no + 1
        if no % 200 == 0:
            logging.info("Loaded prefixes for {} organizations".format(no))
        
        sql_alloc = "SELECT * FROM numres WHERE rir='{}' AND type='{}' and orgid={} AND (status='allocated' or status='assigned') " \
            .format(rir, type, org)
        pfxlist = []
        for e in ndb.runsql(sql_alloc):
            pfx = str(e['prefix'])
            pfxlist.append(ipaddr.ip_network(pfx))
            logging.debug("loading alloc for {} ".format(pfx))
            # pyt[pfx] = {'pfx': pfx, 'rutas': [], 'nrutas': 0, 'orgid': org}
            # stats.inc('allocs')
        # end for e
        # collapse pfxlist 
        pfxlist2 = [ipa for ipa in ipaddr.collapse_addresses(pfxlist) ]
        for p in pfxlist2:
            pyt[p] = {'pfx': p, 'rutas': [], 'nrutas': 0, 'orgid': org}
            stats.inc('allocs')

    # end for o

    #
    logging.info("Loaded {} compacted allocs into trie".format(stats.get('allocs')) )
    return pyt
# end def loadAllocsTrie_compact

@click.command()
@click.option("--date", required=True, help="Process data obtained on <<DATE>>.")
@click.option("--limit", default=10000, help="Process at most LIMIT orgs.")
def cli(date, limit):
    dbfile = "var/netdata-{}.db".format(date)
    logging.info("Opening netdata file {}".format(dbfile))
    LIMIT = limit
    #
    ndb = netdatadb(dbfile)

    # pyt = loadAllocsTrie_naif(dbfile)
    pyt = loadAllocsTrie_compact(dbfile, LIMIT)

    stats.set('visible', 0)
    stats.set('invisible', 0)
    stats.set('nroutes', 0)
    stats.set('nrouteslacnic',0)

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

    # open file for csv export
    csvfile = open("var/s1_invisible_prefixes-{}.csv".format(date), "w")
    csv_export = csv.writer(csvfile, dialect='excel', delimiter='|')
    csv_export.writerow(["orgid","prefix", "visible", "dark", "total"])

    # Write output
    for y in pyt:
        if pyt[y]['nrutas'] == 0:
            stats.inc('invisible')
            # csvrow = [y, pyt[y]]
            csvrow = [pyt[y]['orgid'], y, pyt[y]['visible'], pyt[y]['dark'], pyt[y]['total'] ]
            csv_export.writerow(csvrow)
        else:
            stats.inc('visible')
            stats.inc('nrouteslacnic', pyt[y]['nrutas'] )
            csvrow = [pyt[y]['orgid'], y, pyt[y]['visible'], pyt[y]['dark'], pyt[y]['total'] ]
            # csvrow = [y, pyt[y]]
            csv_export.writerow(csvrow)
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

# end def cli

if __name__ == "__main__":
    logging.basicConfig( level=logging.INFO )
    stats = counters()
    logging.debug("Finding Invisible Resources - 20191006")
    cli()

# end script
