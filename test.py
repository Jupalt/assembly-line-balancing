import matplotlib.pyplot as plt
import networkx as nx

# Beispiel-Daten
stations = {
    1: {'type': 'Manual', 'tasks': [1, 2]},
    2: {'type': 'Robot', 'tasks': [3, 4]},
    3: {'type': 'Robot', 'tasks': [5, 9, 10]}
}

# Graph erstellen
G = nx.Graph()

# Knoten (Stationen) hinzufügen
for station, data in stations.items():
    G.add_node(station, label=f"Station {station} ({data['type']})")

# Knoten (Aufgaben) hinzufügen
for station, data in stations.items():
    tasks = data['tasks']
    for task in tasks:
        G.add_node(task, label=f"Task {task}")  # Füge Aufgaben als Knoten hinzu
        G.add_edge(station, task, weight=1)

# Positionen der Knoten festlegen
# Stationen entlang der x-Achse
pos = {station: (station, 0) for station in stations}

# Positionen für Aufgaben hinzufügen, um sie zu vermeiden, dass sie sich mit den Stationen überschneiden
task_offset = 0.5
for task in range(1, 11):  # Aufgaben reichen von 1 bis 10 (kann angepasst werden)
    if task in G.nodes:
        pos[task] = (task, task_offset)  # Aufgaben an der y-Achse verschoben

# Visualisierung
plt.figure(figsize=(12, 6))
nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', font_size=10, font_weight='bold', edge_color='gray')

plt.title("Stationen und Aufgaben")
plt.show()
