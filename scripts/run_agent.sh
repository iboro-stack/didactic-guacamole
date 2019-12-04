#!/bin/bash
kafkacat -C -b testleader.ml -t event-stream -u -o end | python3 main_agent.py
