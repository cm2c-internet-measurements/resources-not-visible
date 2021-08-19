#!/usr/bin/env python3

# import click

## BEGIN

# @click.command()
# def cli():
#     pass

import petl as etl
import sys
import argparse

def Average(lst): 
    return sum(lst) / len(lst) 

if __name__ == "__main__":
	try:
		ap = argparse.ArgumentParser()
		ap.add_argument("-d","--date", required=True)
		# ap.add_argument("--debug", default=logging.INFO, required=False)
		# ap.add_argument("--limit", default=100, required=False)
		args = ap.parse_args()
		DATE = args.date
	except Exception:
		print("ERROR! Date not specified. ")
		print("Usage: ./s2_aggregate_results.py --date YYYYMMDD")
		sys.exit(1)
	#
	print("Algunos agregados de los resultados, para fecha: ", DATE)

	t1 = ( etl.fromcsv(f"var/s1_invisible_prefixes-{DATE}.csv", delimiter="|")
		.convert('visible', int)
		.convert('dark', int)
		.convert('total', int)
	)
	#print(t1.look())

	print("Algunos agregados de los resultados, para fecha: ", DATE)
	print("Total de espacio de todo el pool", sum( [ x[4] for x in list(t1) ][1:] ) ) 

	print(" - ")
	# numero de asignaciones completamente invisibles
	n1 = etl.select(t1, lambda r: r['dark']==r['total']).sort('total', reverse=True)
	print("numero de asignaciones completamente invisibles", n1.nrows()) 
	print("total de ips en asignaciones completamente invisibles", sum( [ x[4] for x in list(n1) ][1:] ) ) 
	print("tamano  promedio de asignaciones completamente invisibles", Average( [ x[4] for x in list(n1) ][1:] ) )
	print("Las 10 primeras:") 
	for x in range(0,10):
		print(n1[x])
	print(" ")

	print(" - ")
	# numero de asignaciones parcialmente invisibles
	n2 = etl.select(t1, lambda r: (r['dark'] > 0 and (r['dark'] < r['visible'])) ).sort('total', reverse=True)
	print("numero de asignaciones parcialmente invisibles", n2.nrows()) 
	print("total de ips en asignaciones parcialmente invisibles", sum( [ x[3] for x in list(n2) ][1:] ) ) 
	print("tamano  promedio de asignaciones parcialmente invisibles (total) ", Average( [ x[4] for x in list(n2) ][1:] ) ) 
	print("tamano  promedio de asignaciones parcialmente invisibles (dark) ", Average( [ x[3] for x in list(n2) ][1:] ) )
	print("Las 5 primeras:") 
	for x in range(0,10):
		print(n2[x])
	print(" ")


	# tamaño promedio de prefijo completamente invisible

## END
