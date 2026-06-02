"""Specialized chart — starting template.

Pick ONE of the examples below to start from, then edit the data
and styling to match the source image.
See references/specialized.md for radar / parallel coords / network / PCA.
"""
import numpy as np
import matplotlib.pyplot as plt

# === RADAR CHART ===
def radar_chart():
    categories = ['Speed', 'Power', 'Accuracy', 'Endurance', 'Agility', 'Focus']
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()

    player_a = [8, 6, 9, 7, 8, 9]
    player_b = [6, 8, 7, 8, 7, 7]
    # Close the polygon
    player_a += player_a[:1]
    player_b += player_b[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True),
                           constrained_layout=True)
    ax.fill(angles, player_a, color='#4C72B0', alpha=0.25)
    ax.plot(angles, player_a, color='#4C72B0', lw=1.5, label='Player A')
    ax.fill(angles, player_b, color='#DD8452', alpha=0.25)
    ax.plot(angles, player_b, color='#DD8452', lw=1.5, label='Player B')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 10)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    plt.savefig('output.png', dpi=200, bbox_inches='tight')


# === NETWORK GRAPH ===
def network_graph():
    import networkx as nx
    G = nx.karate_club_graph()  # example: 34 nodes, 78 edges
    pos = nx.spring_layout(G, seed=0)  # seed=0 makes the layout reproducible

    fig, ax = plt.subplots(figsize=(7, 6), constrained_layout=True)
    nx.draw_networkx_nodes(G, pos, node_color='lightblue',
                           node_size=200, ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    ax.set_axis_off()
    plt.savefig('output.png', dpi=200, bbox_inches='tight')


# === PCA SCATTER ===
def pca_scatter():
    from sklearn.decomposition import PCA
    from sklearn.datasets import load_iris
    data = load_iris()
    X, y = data.data, data.target
    X_2d = PCA(n_components=2).fit_transform(X)

    fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
    for label in np.unique(y):
        mask = y == label
        ax.scatter(X_2d[mask, 0], X_2d[mask, 1],
                   label=data.target_names[label], alpha=0.7)
    ax.set_xlabel('PC1'); ax.set_ylabel('PC2')
    ax.legend()
    plt.savefig('output.png', dpi=200, bbox_inches='tight')


# Pick the one that matches the source image and call it.
if __name__ == '__main__':
    radar_chart()
    # network_graph()
    # pca_scatter()
