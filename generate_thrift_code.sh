#!/bin/sh
rm -rf clients/python_client/gen_py/
rm -rf servers/python_server/gen_py/

thrift -r --gen py tutorial.thrift
mv gen-py/ gen_py/

cp -r gen_py/ clients/python_client/gen_py/
cp -r gen_py/ servers/python_server/gen_py/

rm -rf gen_py/