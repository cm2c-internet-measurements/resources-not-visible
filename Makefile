# Pipeline makefile
#
#

.PHONY: 20200209

20200209.done: 20200209
	./s0_get_netdatadb.sh $<
	time pipenv run ./s1_alloc_and_routes.py --date $<
