#!/bin/bash
## Script to run the online clustering demo.

python Predictor.py --subscribing_port 5000 &
P1=$!
python Trainer.py --subscriber_port 4999 --publisher_port 5000 --training_interval 3 --features 2 --max_buffer_size 2000 --output_file centroids.csv &
P2=$!
sleep 1s
python Source.py --port 4999 --steps 10000 --duration 10 --output_file walkers.csv &
P3=$!
wait $P1 $P2 $P3
python plot_demo.py