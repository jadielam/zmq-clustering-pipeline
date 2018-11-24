import numpy as np
import click
import zmq
import zmqhelpers
import time
import pandas as pd

class Walker:
    def __init__(self, direction: float, variance: float, dimensions: int=2):
        self.direction = np.array([1,direction])
        self.variance = variance
        self.dimensions = dimensions
        self.current_step = 0

    def walk(self, steps: int):
        result = np.random.randn(steps, self.dimensions)
        dir = self.direction/steps
        for step in range(steps):
            result[step] *= self.variance**2
            result[step] += step * dir
        self.current_step += steps
        return result

@click.command()
@click.option('--steps', type=int, default=10000, help='Number of steps.')
@click.option('--duration', type=int, default=10, help='Time duration of simulated source.')
@click.option('--host', type=str, default='localhost', help='Host of URL')
@click.option('--port', type=int, default=5000, help='Port of URL')
@click.option('--output_file', type=str, default=None, help='Output random walks to a CSV.')
def main(steps:int, duration:int, host:str, port:int, output_file:str):
    # Three walkers
    walker1 = Walker(1.2, 0.3)
    walker2 = Walker(0.05, 0.05)
    walker3 = Walker(-0.6, 0.15)

    walks = {i: walker.walk(steps) for i, walker in enumerate([walker1, walker2, walker3])}
    walk_selection = np.random.randint(3, size=steps)

    sleep_interval = float(duration)/steps

    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{port}")

    data = []
    walkers = []
    ts = []
    for step, selection in enumerate(walk_selection):
        array = walks[selection][step, :]
        data.append(array)
        walkers.append(selection)
        publisher.send(zmqhelpers.ARRAY)
        ts.append(step/steps)
        zmqhelpers.send_array(publisher, array)
        time.sleep(sleep_interval)
    publisher.send(zmqhelpers.TERMINATE)

    if output_file is not None:
        df = pd.DataFrame(np.array(data))
        df.columns = ['x', 'y']
        df['walkers'] = walkers
        df['iteration'] = [int(i/2000) for i in range(steps)]
        df['time'] = ts
        df.to_csv(output_file)

    return


if __name__ == "__main__":
    main()








