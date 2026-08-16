import numpy as np
import trimesh
import manifold3d


def shape_to_manifold(shape, tol=0.01):
    """Тесселлирует build123d Shape и возвращает manifold3d.Manifold.

    Args:
        shape: build123d Part/Solid для тесселляции.
        tol: Допуск тесселляции (меньше = точнее, но больше полигонов).
    """
    v, t = shape.tessellate(tol)
    v_np = np.array([[vert.X, vert.Y, vert.Z] for vert in v], dtype=np.float32)
    t_np = np.array(t, dtype=np.uint32)
    mesh = trimesh.Trimesh(vertices=v_np, faces=t_np, process=True)
    mesh.fix_normals()
    return manifold3d.Manifold(manifold3d.Mesh(
        vert_properties=np.array(mesh.vertices, dtype=np.float32),
        tri_verts=np.array(mesh.faces, dtype=np.uint32)
    ))
