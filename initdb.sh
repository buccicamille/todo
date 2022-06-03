#!/bin/bash

rm -rf migrations todo.sqlite
flask db init
flask db migrate -m "changed database"
flask db upgrade
