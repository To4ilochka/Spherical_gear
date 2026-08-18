from build123d import *
import config
import trimesh
from utils import shape_to_manifold
import os

print("==========================================")
print(" GENERATING SINGLE HEXAGONAL PIN")
print("==========================================")

with BuildPart() as pin:
    with BuildSketch(Plane.XY):
        RegularPolygon(radius=config.PIN_DIAMETER / 2, side_count=6)
    extrude(amount=config.PIN_LENGTH)
    
    if getattr(config, 'ENABLE_THREADED_INSERTS', True):
        # Добавляем отверстие под резьбовую вставку (снизу)
        with BuildSketch(Plane.XY):
            Circle(radius=config.INSERT_HOLE_DIAMETER / 2)
        extrude(amount=config.INSERT_HOLE_DEPTH, mode=Mode.SUBTRACT)

        # Добавляем отверстие под резьбовую вставку (сверху)
        with BuildSketch(Plane.XY.offset(config.PIN_LENGTH)):
            Circle(radius=config.INSERT_HOLE_DIAMETER / 2)
        extrude(amount=-config.INSERT_HOLE_DEPTH, mode=Mode.SUBTRACT)
    
    # Добавляем фаски на торцах для легкой вставки и направления резьбовой вставки
    top_faces = pin.faces().filter_by(Axis.Z)
    bottom_faces = pin.faces().filter_by(Axis.Z, reverse=True)
    
    # Собираем все края (edges) торцов
    end_edges = []
    for face in top_faces:
        end_edges.extend(face.edges())
    for face in bottom_faces:
        end_edges.extend(face.edges())
        
    chamfer_len = 0.5 # 0.5мм фаска идеальна и для внешнего края, и для направления вставки
    try:
        chamfer(end_edges, length=chamfer_len)
    except Exception as e:
        print(f"Warning: Could not apply chamfer: {e}")

print("Tessellating to Manifold3D...")
m_pin = shape_to_manifold(pin.part)

print("Exporting results...")
out_mesh = m_pin.to_mesh()
result_mesh = trimesh.Trimesh(vertices=out_mesh.vert_properties[:, :3], faces=out_mesh.tri_verts)
result_mesh.export(config.OUTPUT_PIN_STL)
print(f"Success! Saved as {config.OUTPUT_PIN_STL}")

# Удаляем старый файл со всеми пинами, если он есть
if os.path.exists("hex_pins.stl"):
    os.remove("hex_pins.stl")
    print("Cleaned up old hex_pins.stl")
