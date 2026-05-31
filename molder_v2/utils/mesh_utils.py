"""Mesh utility functions used by conformity and analysis modules."""

from collections import defaultdict, deque
from mathutils import Vector


def evaluated_mesh_from_object(obj, depsgraph=None):
    if depsgraph is None:
        return obj.data
    evaluated = obj.evaluated_get(depsgraph)
    return evaluated.to_mesh()


def count_boundary_and_non_manifold_edges(mesh):
    boundary = 0
    non_manifold = 0
    for edge in mesh.edges:
        linked = 0
        for poly in mesh.polygons:
            if edge.key[0] in poly.vertices and edge.key[1] in poly.vertices:
                linked += 1
        if linked == 1:
            boundary += 1
        elif linked != 2:
            non_manifold += 1
    return boundary, non_manifold


def edge_face_counts(mesh):
    counts = defaultdict(int)
    for poly in mesh.polygons:
        vertices = list(poly.vertices)
        for index, start in enumerate(vertices):
            end = vertices[(index + 1) % len(vertices)]
            counts[tuple(sorted((start, end)))] += 1
    return counts


def boundary_non_manifold_from_polygons(mesh):
    counts = edge_face_counts(mesh)
    boundary = sum(1 for count in counts.values() if count == 1)
    non_manifold = sum(1 for count in counts.values() if count != 2)
    return boundary, non_manifold, counts


def loose_part_count(mesh):
    if not mesh.vertices:
        return 0
    adjacency = defaultdict(set)
    for poly in mesh.polygons:
        verts = list(poly.vertices)
        for index, current in enumerate(verts):
            nxt = verts[(index + 1) % len(verts)]
            adjacency[current].add(nxt)
            adjacency[nxt].add(current)
    visited = set()
    parts = 0
    for vertex in range(len(mesh.vertices)):
        if vertex in visited:
            continue
        parts += 1
        queue = deque([vertex])
        visited.add(vertex)
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return parts


def polygon_centers_world(obj):
    mesh = obj.data
    return [obj.matrix_world @ poly.center for poly in mesh.polygons]


def vertex_world_positions(obj):
    return [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]


def mean_vector(vectors):
    if not vectors:
        return Vector((0.0, 0.0, 0.0))
    result = Vector((0.0, 0.0, 0.0))
    for vector in vectors:
        result += vector
    return result / len(vectors)
