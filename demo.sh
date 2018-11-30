#!/bin/bash
## Script to run the online clustering demo.
python Preprocess.py --subscriber_port 5000 --publisher_port 5001 --sending_interval 2.5 --features 2 --max_buffer_size 2000 --use_fresh_data True &
P1=$!
python Trainer.py --subscriber_port 5001 --publisher_port 5002 &
P2=$!
python Predictor.py --subscribing_port 5002 &
P3=$!
sleep 0.2s
python Source.py --port 5000 --steps 10000 --duration 10 &
wait $P1 $P2 $P3
python plot_demo.py