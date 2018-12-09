import zmqhelpers
from sklearn.cluster import KMeans
import numpy as np
from datetime import timedelta
from datetime import datetime
import click
import zmq
import pandas as pd


"""
Preprocess.py
This node recieves data and trains a K-Means learner on a regular interval,
sending out the serialized model to a server.
"""


@click.command()
@click.option('--subscriber_port', type=int, help="Subscribing port.")
@click.option('--publisher_port', type=int, help="Publishing port.")
@click.option('--host', type=str, default='localhost', help="Host to use for communication.")
@click.option('--sending_interval', type=float, help="Training interval in seconds.")
@click.option('--max_buffer_size', type=int, default = 8192, help="Max buffer size of data buffer")
@click.option('--features', type=int, default=2, help='Number of recieved features')
@click.option('--use_fresh_data', type = bool, default = True, help='Use only fresh data in new training interval.')
def main(subscriber_port: int, publisher_port: int, host: str, sending_interval: float, max_buffer_size: int, features: int, use_fresh_data: bool):
    context = zmq.Context()

    subscriber = context.socket(zmq.SUB)
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
    subscriber.connect(f"tcp://{host}:{subscriber_port}")

    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{publisher_port}")

    data_buffer = np.zeros((max_buffer_size, features))
    data_index = 0

    interval = timedelta(seconds = sending_interval)
    next_timestamp = datetime.now() + interval

    running = True
    data = []
    iteration = []
    iter = 0
    processes = []

    while running:
        message_type = subscriber.recv()
        if message_type == zmqhelpers.ARRAY:
            array = zmqhelpers.recv_array(subscriber)
            try:
                data_buffer[data_index % max_buffer_size, :] = array
                data_index += 1
            except Exception as e:
                print(e)

        if message_type == zmqhelpers.TERMINATE:
            walker_data = pd.DataFrame(np.concatenate(data), columns=['x', 'y'])
            walker_data['iteration'] = iteration
            walker_data.to_csv('walkers.csv')
            publisher.send(zmqhelpers.TERMINATE)
            for process in processes:
                process.join()
            running = False

        if datetime.now() >= next_timestamp and data_index > 0:
            next_timestamp = datetime.now() + interval
            training_data = np.array(data_buffer[:data_index], dtype='float')
            if data_index > max_buffer_size:
                training_data = data_buffer
            if use_fresh_data:
                data_index = 0
            publisher.send(zmqhelpers.ARRAY)
            zmqhelpers.send_array(publisher, training_data)
            iteration.extend([iter] * training_data.shape[0])
            iter += 1
            data.append(training_data)

    return


if __name__ == "__main__":
    main()


