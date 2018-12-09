import zmq
import zmqhelpers
import click
import pandas as pd
import numpy as np


"""
Predictor.py
Running loop which performs inference and updates its model in real-time.
Writes predictions and data to SQLite Database.
"""

context = zmq.Context()


@click.command()
@click.option('--subscribing_port', type=int, help="Subscribing port.")
@click.option('--host', type=str, default='localhost', help="Host.")
def main(subscribing_port: int, host: str):
    subscriber = context.socket(zmq.SUB)
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
    subscriber.connect(f"tcp://{host}:{subscribing_port}")

    running = True
    model = None
    centroids = []
    clusters = None
    while running:
        message_type = subscriber.recv()
        if message_type == zmqhelpers.MODEL:
            model = zmqhelpers.recv_zipped_pickle(subscriber)
            centroids.append(model.cluster_centers_)
            clusters = model.cluster_centers_.shape[0]


        elif message_type == zmqhelpers.ARRAY:
            data = zmqhelpers.recv_array(subscriber)
            if model is not None:
                try:
                    print(model.predict(data))
                except Exception as e:
                    print(f"Failed to predict on data\n.{e}")

        elif message_type == zmqhelpers.TERMINATE:
            centroid_data = pd.DataFrame(np.concatenate(centroids), columns=['x', 'y'])
            centroid_data['iteration'] = [int(i/clusters) for i in range(centroid_data.shape[0])]
            centroid_data.to_csv('centroids.csv')
            running = False

    return

if __name__ == "__main__":
    main()
