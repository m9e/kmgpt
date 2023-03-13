#!/bin/bash

cd "$(dirname "$0")"
source bin/activate > log.txt
python src/gen.py >> log.txt

