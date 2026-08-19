from build123d import *
import config
import math
import trimesh
from utils import shape_to_manifold
import os

print("==========================================")
print(" GENERATING SINGLE HEXAGONAL PIN (WITH NUT CATCHES)")
print("==========================================")

if getattr(config, 'ENABLE_NUT_CATCHES', True):
    nut_w = config.NUT_SIZE + 0.2 # Снизили допуск до 0.2 мм для плотной посадки
    nut_t = config.NUT_THICKNESS + 0.2 # Снизили допуск до 0.2 мм
    
    with BuildPart() as nut_tool:
        with BuildSketch(Plane.XY):
            RegularPolygon(radius=(nut_w / 2) / 0.866025, side_count=6, rotation=30)
        extrude(amount=nut_t/2, both=True)
        with BuildSketch(Plane.XY):
            Rectangle(width=nut_w, height=config.PIN_DIAMETER, align=(Align.CENTER, Align.MIN))
        extrude(amount=nut_t/2, both=True)

with BuildPart() as pin:
    # 1. Основное тело шестигранника
    with BuildSketch(Plane.XY):
        RegularPolygon(radius=config.PIN_DIAMETER / 2, side_count=6)
    extrude(amount=config.PIN_LENGTH)
    
    # 2. Делаем скругления и фаски ДО вырезания отверстий!
    # Фаски на торцах (чтобы штифт сам центрировался при вставке)
    top_faces = pin.faces().filter_by(Axis.Z)
    bottom_faces = pin.faces().filter_by(Axis.Z, reverse=True)
    
    end_edges = []
    for face in top_faces:
        end_edges.extend(face.outer_wire().edges())
    for face in bottom_faces:
        end_edges.extend(face.outer_wire().edges())
    chamfer(end_edges, length=0.6)
    
    # Скругления (fillet) на 6 вертикальных гранях (чтобы не цеплялись за углы при печати)
    vertical_edges = pin.edges().filter_by(Axis.Z)
    fillet(vertical_edges, radius=0.5)
    
    # 3. Сквозное отверстие в виде капли (Teardrop) для печати без поддержек
    R = config.SCREW_CLEARANCE_HOLE / 2
    with BuildSketch(Plane.XY):
        with BuildLine():
            c1 = CenterArc((0,0), radius=R, start_angle=135, arc_size=270)
            Line(c1 @ 1, (0, R * 1.4142))
            Line((0, R * 1.4142), c1 @ 0)
        make_face()
    extrude(amount=config.PIN_LENGTH, mode=Mode.SUBTRACT)
    
    # 4. Пазы под гайки (Nut Catches)
    if getattr(config, 'ENABLE_NUT_CATCHES', True):
        # Вычитаем инструмент снизу
        with Locations((0, 0, config.NUT_DEPTH_FROM_END)):
            add(nut_tool.part, mode=Mode.SUBTRACT)
            
        # Вычитаем инструмент сверху
        with Locations((0, 0, config.PIN_LENGTH - config.NUT_DEPTH_FROM_END)):
            add(nut_tool.part, mode=Mode.SUBTRACT)

print("Tessellating to Manifold3D...")
m_pin = shape_to_manifold(pin.part)

print("Exporting results...")
out_mesh = m_pin.to_mesh()
result_mesh = trimesh.Trimesh(vertices=out_mesh.vert_properties[:, :3], faces=out_mesh.tri_verts)
result_mesh.export(config.OUTPUT_PIN_STL)
print(f"Success! Saved as {config.OUTPUT_PIN_STL}")

if os.path.exists("hex_pins.stl"):
    os.remove("hex_pins.stl")
