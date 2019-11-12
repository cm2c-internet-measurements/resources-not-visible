# Pipeline makefile
#
#

.PHONY: 20191102

20191102.done: 20191102
	./s0_get_netdatadb.sh $<
	time pipenv run ./s1_alloc_and_routes.py --date $<
