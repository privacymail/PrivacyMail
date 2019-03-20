#!/bin/bash
./manage.py flush
./manage.py loaddata /media/sf_seemoo_master/databases_json/signup_27_01.json
#./manage.py loaddata transformed_maillist.json
