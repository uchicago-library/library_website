#!/bin/bash

source /data/motacilla/venv3.6/bin/activate && /data/motacilla/sites/library_website/manage.py report_daily_news_stories eee@uchicago.edu lib-staff@lib.uchicago.edu 7 `date -v -1d "+%Y%m%d"`



