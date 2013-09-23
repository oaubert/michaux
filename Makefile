MANAGE=python ./manage.py

all:
	echo "Specify a target"

schema: schema.xml

schema.xml: base/search_indexes.py
	$(MANAGE) build_solr_schema > $@
	echo "Do not forget to restart jetty and rebuild index"

rebuild:
	$(MANAGE) rebuild_index --noinput --remove

sync:
	./synchronize

backup:
	$(MANAGE) dumpdata base taggit | gzip -c > michaux.json.gz

restore:
	$(MANAGE) loaddata michaux.json.gz
