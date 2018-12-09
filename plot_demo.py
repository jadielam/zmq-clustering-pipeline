from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot():
    centroids = pd.read_csv('centroids.csv')
    walkers = pd.read_csv('walkers.csv')
    sns.relplot(x='x',y='y', hue = 'iteration', sizes = (10,200), marker = '+', palette = sns.color_palette("hls", walkers['iteration'].unique().shape[0]), data = walkers, s=0.8)
    sns.relplot(x='x',y='y', hue = 'iteration', sizes = (10,200), marker = 'o', palette = sns.color_palette("hls", centroids['iteration'].unique().shape[0]), data = centroids, s=100)
    plt.show()

if __name__ == "__main__":
    plot()