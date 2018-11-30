import zmqhelpers
from sklearn.cluster import KMeans
import numpy as np
from datetime import timedelta
from datetime import datetime
import click
import zmq
import pandas as pd
from multiprocessing import Pool, Process
import sys, gc


"""
Trainer.py
This node recieves data and trains a K-Means learner on a regular interval,
sending out the serialed model to a server.
"""



@click.command()
@click.option('--subscriber_port', type=int, help="Subscribing port.")
@click.option('--publisher_port', type=int, help="Publishing port.")
@click.option('--host', type=str, default='localhost', help="Host to use for communication.")
@click.option('--clusters', type = int, default = 3, help='Number of clusters to learn.')
def main(subscriber_port: int, publisher_port: int, host: str, clusters: int):
    context = zmq.Context()

    subscriber = context.socket(zmq.SUB)
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
    subscriber.connect(f"tcp://{host}:{subscriber_port}")

    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{publisher_port}")

    centroids = []
    iteration = []
    iter = 0
    running = True
    while running:
        message_type = subscriber.recv()
        if message_type == zmqhelpers.ARRAY:
            array = zmqhelpers.recv_array(subscriber)
            clustering_model = KMeans(n_clusters=clusters).fit(array)
            # Send out the model
            publisher.send(zmqhelpers.MODEL)
            zmqhelpers.send_zipped_pickle(publisher, clustering_model)
            centroids.append(clustering_model.cluster_centers_)
            iteration.extend([iter] * clustering_model.cluster_centers_.shape[0])
            iter += 1

        if message_type == zmqhelpers.TERMINATE:
            centroid_data = pd.DataFrame(np.concatenate(centroids), columns=['x', 'y'])
            centroid_data['iteration'] = iteration
            centroid_data.to_csv('centroids.csv')
            publisher.send(zmqhelpers.TERMINATE)
            running = False

    return


if __name__ == "__main__":
    main()


