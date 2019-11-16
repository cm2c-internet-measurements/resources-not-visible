# Pipeline makefile
#
#

.PHONY: 20191110

20191102.done: 20191110
	./s0_get_netdatadb.sh $<
	time pipenv run ./s1_alloc_and_routes.py --date $<
