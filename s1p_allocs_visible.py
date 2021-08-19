#!/usr/bin/env python3

import os
import sys
import argparse
import pytricia
import sqlite3
import ipaddr
import logging
import petl as etl

# global config vars (set from command line parameters)
DATE = "20190101"
DPATH = "var/"

# loading functions

def etl_delegated_fromnetdata(pdate, prir='lacnic', limit=5 ):

    # CREATE TABLE numres 
    # (id INTEGER PRIMARY KEY, rir text, cc text, type text, block text, 
    # length integer, date integer, status text, orgid integer, 
    # istart INTEGER, iend INTEGER, prefix VARCHAR(80), equiv INTEGER);

    #
    fname = f"{DPATH}/netdata-{pdate}.db"
    if os.path.isfile(fname):
        co = sqlite3.connect(fname)
    else:
        print("Database not found!: ", fname)
        raise(FileNotFoundError)
    # print(fname)

    t1 = ( etl
            .fromdb(co, f"select * from numres where rir='{prir}' and type='ipv4' and (status='assigned' or status='allocated') limit {limit}")
            .convert('length', int)
            .convert('date', int)
            .convert('istart', int)
            .convert('iend', int)
            .convert('equiv', int)
    )

    # co.close()
    return t1
# end def

def etl_roadata_fromnetdata(pdate):
    pass
# end def

def etl_riswhois_fromnetdata(pdate, ptype='ipv4', pviewed_by=20):

    #
    fname = f"{DPATH}/netdata-{pdate}.db"
    if os.path.isfile(fname):
        co = sqlite3.connect(fname)
    else:
        print("Database not found!: ", fname)
        raise(FileNotFoundError)
    # print(fname)

    # CREATE TABLE riswhois 
    # (id INTEGER PRIMARY KEY, origin_as text, prefix text, viewed_by integer, 
    # istart UNSIGNED BIG INT, iend UNSIGNED BIG INT, type VARCHAR(5), pfxlen INTEGER);
    t1 = ( etl
            .fromdb(co, f"select * from riswhois where type='{ptype}' and viewed_by>={pviewed_by}")
            .convert('istart', int)
            .convert('iend', int)
            .convert('pfxlen', int)
    )
    return t1
# end def

def pytricia_riswhois(proute_table):
    pyt = pytricia.PyTricia()

    for r in proute_table.dicts():
        pyt[ r['prefix'] ] = {'prefix': r['prefix'] }
 
    return pyt
# end def


if __name__ == "__main__":
    print("ASIGNACIONES VISIBLES Y OSCURAS \n (c) carlos@lacnic.net\n v2 20210318\n--")
    #
    ap = argparse.ArgumentParser()
    ap.add_argument("-d","--date", required=True)
    ap.add_argument("--debug", default=logging.INFO, required=False)
    ap.add_argument("--limit", default=100, required=False)
    args = ap.parse_args()
    #
    logging.basicConfig(level=args.debug, stream=sys.stderr)
    #
    DATE = args.date
    print("Processing date: ", DATE)
    #
    t_allocs = etl_delegated_fromnetdata(DATE, 'lacnic', args.limit)
    print(t_allocs.look(), t_allocs.nrows() )
    #
    t2 = etl_riswhois_fromnetdata(DATE)
    print( t2.look() )
    #
    pyt = pytricia_riswhois(t2)

    # empiezo a contaaar !
    # itero sobre las asignaciones
    results_d = []
    count_allocs = 0
    for a in t_allocs.dicts():
        count_allocs = count_allocs+1
        if count_allocs % 100 == 0:
            logging.warning(f"Processed {count_allocs} allocations")
        # lo parto en /24s
        n = ipaddr.IPv4Network(a['prefix'])
        logging.debug(f"allocation:  {a['prefix']} :: ")
        a24s = n.subnet(new_prefix=24)
        c = 0
        for p in a24s:
            # print("%%", p)
            cov_route = pyt.get(str(p), None)
            if cov_route:
                c = c + 1
                logging.debug(f"\t{p} : {cov_route['prefix']}")
            # end if
        # end for
        visible = c*256
        total = len(a24s)*256
        dark = total-visible
        coverage = float(visible/total)*100
        result_row = {
            'date': DATE,
            'prefix': a['prefix'],
            'visible': visible,
            'dark': dark,
            'total': total,
            'coverage': coverage,
            'orgid': a['orgid']
        }
        results_d.append(result_row)
        logging.info(result_row)
    # end for
    t_results = etl.fromdicts(results_d)
    sum_total = sum( [x[4] for x in list(t_results) ][1:] )
    sum_dark = sum( [x[3] for x in list(t_results) ][1:] )
    sum_visible = sum( [x[2] for x in list(t_results) ][1:] )
    print("%% TOTAL espacio: ", sum_total)
    print("%% TOTAL dark: ", sum_dark)
    print("%% TOTAL visible: ", sum_visible)
    
    t_results_sorted = etl.sort(t_results, 'total', reverse=True)
    etl.tocsv(t_results_sorted, f"{DPATH}/s1p-allcs-visible-{DATE}.csv")
    #

    # etl.select(t1, lambda r: r[])
# end main

# end file

