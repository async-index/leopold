# Leopold Museum, pass 3: real proportions (OSM 46 x 40 x 24 m) + facade relief as geometry.
# Visible-facade features are measured in the reference image, back-projected with the reference
# camera onto the facade plane, then scaled to the real facade length.
#
# Boolean rule: no two operands may share a face plane where they meet (coplanar overlap breaks the
# exact solver and every later operation cascades). Parts either push into what they attach to, or
# stop a few mm short. Every boolean is verified (vertex count, volume direction, open edges).
# Run: Blender -b --factory-startup --python build3.py -- <out.blend> <render.png>
import bpy, bmesh, math, sys
from mathutils import Vector

out_blend, out_png = sys.argv[sys.argv.index("--") + 1:][:2]
E = 0.002                                   # the few-mm offset that keeps faces off each other's plane

# ---------- reference camera (fits the image at its own proportions, 48.93 x 34.1) ----------
CAM = Vector((-33.15, -53.3, 17.6))
R, F, U = Vector((0.760, -0.649, 0)), Vector((0.649, 0.760, 0)), Vector((0, 0, 1))
FPX, CX, V0 = 2298.0, 1024.0, 757.8
def hit(u, v, axis, val):
    d = F + ((u - CX) / FPX) * R + ((V0 - v) / FPX) * U
    return CAM + d * ((val - CAM[axis]) / d[axis])

W, D, H = 46.0, 40.0, 24.0                 # real building
SX, SY = W / 48.93, D / 34.1               # reference -> real, along each facade
def front(tl, br):                         # courtyard facade (plane y=0): px rect -> x0,x1,z0,z1
    a, b = hit(*tl, 1, 0), hit(*br, 1, 0); return a.x * SX, b.x * SX, b.z, a.z
def left(tl, br):                          # left facade (plane x=0): px rect -> y0,y1,z0,z1
    a, b = hit(*tl, 0, 0), hit(*br, 0, 0); return b.y * SY, a.y * SY, b.z, a.z

# ---------- scene helpers ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
coll = {}
def group(name):
    if name not in coll:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); coll[name] = c
    return coll[name]
def link(o, grp):
    for c in o.users_collection: c.objects.unlink(o)
    group(grp).objects.link(o); return o
def box(name, x0, x1, y0, y1, z0, z1, grp):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
    o = bpy.context.object; o.name = name; o.scale = (abs(x1-x0), abs(y1-y0), abs(z1-z0))
    bpy.ops.object.transform_apply(scale=True); return link(o, grp)
def prism(name, pts, a0, a1, axis, grp):
    """Closed solid: 2D polygon extruded a0..a1 along 'y' (pts are x,z) or 'z' (pts are x,y)."""
    bm = bmesh.new()
    mk = (lambda p, a: (p[0], a, p[1])) if axis == 'y' else (lambda p, a: (p[0], p[1], a))
    r0 = [bm.verts.new(mk(p, a0)) for p in pts]; r1 = [bm.verts.new(mk(p, a1)) for p in pts]
    bm.faces.new(r0); bm.faces.new(r1[::-1])
    for i in range(len(pts)):
        j = (i + 1) % len(pts); bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); group(grp).objects.link(o); return o
def carve(target, cutter):
    """Difference on a loose part (before it becomes an operand); cutter is removed."""
    m = target.modifiers.new("c", 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.object = cutter; m.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target; bpy.ops.object.modifier_apply(modifier="c")
    bpy.data.objects.remove(cutter); return target
def rod(name, a, b, r, grp):
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=r, depth=d.length, location=(a+b)/2)
    o = bpy.context.object; o.name = name
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = d.to_track_quat('Z', 'Y')
    bpy.ops.object.transform_apply(rotation=True); return link(o, grp)

# facade-local boxes: (a = along facade, n = into the wall, z = up)
def fbox(face, name, a0, a1, n0, n1, z0, z1, grp):
    if face == "front": return box(name, a0, a1, n0, n1, z0, z1, grp)
    return box(name, n0, n1, a0, a1, z0, z1, grp)
def recess(face, name, a0, a1, z0, z1, depth, grp="Cut"):
    return fbox(face, name, a0, a1, -0.5, depth, z0, z1, grp)
def ribbed_panel(face, name, a0, a1, z0, z1, sunk=0.12, pitch=0.3, width=0.06, proud=0.06):
    recess(face, name, a0, a1, z0, z1, sunk)
    n = int((a1 - a0) / pitch)
    for i in range(n):
        c = a0 + (i + 0.5) * (a1 - a0) / n        # ribs stop E short of the recess head/sill, push 1 cm into its back
        fbox(face, f"{name}_Rib{i:03d}", c - width/2, c + width/2, sunk - proud, sunk + 0.01, z0 + E, z1 - E, "Add")
def framed_window(face, name, a0, a1, z0, z1, b=0.3, proud=0.08, depth=0.4):
    ring = fbox(face, name + "_Frame", a0, a1, -proud, 0.14, z0, z1, "Add")   # reaches behind the 0.12 rib recess
    carve(ring, fbox(face, name + "_Hole", a0 + b - E, a1 - b + E, -1, 1, z0 + b - E, z1 - b + E, "Tmp"))
    recess(face, name + "_Open", a0 + b, a1 - b, z0 + b, z1 - b, depth, "Cut2")   # after the ribs are added
def cells(face, name, a0, a1, z0, z1, n, gap=0.15, sunk=0.08):
    w = (a1 - a0 - gap * (n + 1)) / n
    for i in range(n):
        s = a0 + gap + i * (w + gap); recess(face, f"{name}_{i}", s, s + w, z0 + gap, z1 - gap, sunk)

# ---------- main volume ----------
box("Main", 0, W, 0, D, 0, H, "Building")
box("Plinth", -0.08, W + 0.08, -0.08, D + 0.08, -0.3, 0.35, "Building")        # bottom below the main's bottom plane

# ---------- left facade (x=0), measured ----------
SLAB_Y, _, _, SLAB_Z = left((200, 611), (290, 1208))                  # end slab: lower, separated by a groove
SLAB_DEPTH = 3.0
box("Slab_Top_Cut", -0.5, SLAB_DEPTH, SLAB_Y, D + 0.5, SLAB_Z, H + 2, "Cut")
# roof parapet: one ring solid around the main roof outline (the slab corner stays lower)
outline = [(0, 0), (W, 0), (W, D), (SLAB_DEPTH, D), (SLAB_DEPTH, SLAB_Y), (0, SLAB_Y)]
def offset(poly, d):                        # axis-aligned polygon offset (outward for d > 0; ccw order)
    out = []
    n = len(poly)
    for i in range(n):
        p0, p1, p2 = Vector(poly[i-1]), Vector(poly[i]), Vector(poly[(i+1) % n])
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((e0.y, -e0.x)), Vector((e1.y, -e1.x))
        out.append(tuple(p1 + (n0 + n1) * d / (1 + n0.dot(n1))))
    return out
par = prism("Parapet", offset(outline, 0.1), H - 0.3, 25.1, 'z', "Building")
carve(par, prism("ParapetHole", offset(outline, -0.4), H - 1, 26, 'z', "Tmp"))
g = left((290, 600), (308, 1215)); recess("left", "Slab_Groove", g[0], g[1], 0.4, H + 0.01, 0.35)
w = left((230, 715), (265, 778)); recess("left", "Slab_Window", w[0], w[1], w[2], w[3], 0.4)
for i, (a, b) in enumerate((((340, 668), (432, 985)), ((440, 660), (542, 990)), ((548, 650), (672, 1005)))):
    ribbed_panel("left", f"L_UpRib{i}", *left(a, b))
for i, (a, b) in enumerate((((390, 835), (430, 975)), ((440, 835), (480, 980)), ((622, 835), (678, 1000)))):
    framed_window("left", f"L_UpWin{i}", *left(a, b))
cells("left", "L_Cells1", *left((342, 1003), (687, 1097)), n=9)
for i, (a, b) in enumerate((((342, 1050), (435, 1235)), ((440, 1060), (550, 1275)), ((555, 1070), (687, 1310)))):
    ribbed_panel("left", f"L_LowRib{i}", *left(a, b))
for i, (a, b) in enumerate((((403, 1110), (433, 1230)), ((510, 1135), (545, 1270)), ((635, 1162), (677, 1312)))):
    framed_window("left", f"L_LowWin{i}", *left(a, b))
cells("left", "L_Cells2", *left((350, 1245), (687, 1400)), n=9)

# ---------- courtyard facade (y=0), measured ----------
recess("front", "F_UpWin", *front((932, 678), (1042, 762)), 0.4)
gx = front((1125, 578), (1140, 1245)); recess("front", "F_Groove", gx[0], gx[1], 0.4, H + 0.01, 0.35)
fbox("front", "F_Sign", *front((730, 1128), (815, 1300))[:2], -0.08, 0.02, *front((730, 1128), (815, 1300))[2:], "Add")
ribbed_panel("front", "F_Rib0", *front((1238, 655), (1512, 980)))
ribbed_panel("front", "F_Rib1", *front((1518, 660), (1705, 965)))
framed_window("front", "F_Win0", *front((1442, 837), (1500, 965)))
framed_window("front", "F_Win1", *front((1638, 812), (1680, 955)))
gw = front((1298, 993), (1405, 1088)); recess("front", "F_Grille", *gw, 0.4)
for i in range(1, 4):                       # bars: 2 cm back from the face, run 5 cm into head/sill and back wall
    x = gw[0] + i * (gw[1] - gw[0]) / 4; box(f"F_Grille_Bar{i}", x - 0.06, x + 0.06, 0.02, 0.45, gw[2] - 0.05, gw[3] + 0.05, "Add")
dr = front((1298, 1108), (1405, 1230)); recess("front", "F_Door", *dr, 0.6)
for i in range(1, 4):
    x = dr[0] + i * (dr[1] - dr[0]) / 4; box(f"F_Door_Mull{i}", x - 0.04, x + 0.04, 0.45, 0.65, dr[2] - 0.05, dr[3] + 0.05, "Add")
# lettering, engraved 5 cm; cap height from the reference's width:height ratio (~15:1)
lt = front((875, 1120), (1088, 1155))
bpy.ops.object.text_add(location=(lt[0], -0.3, lt[2]))
t = bpy.context.object; t.data.body = "LEOPOLD MUSEUM"; t.data.extrude = 0.35
t.rotation_euler = (math.radians(90), 0, 0)
bpy.context.view_layer.update(); t.data.size = ((lt[1] - lt[0]) / 15) / t.dimensions.y
lo, hi = 1.0, 4.0
for _ in range(30):
    t.data.space_character = (lo + hi) / 2; bpy.context.view_layer.update()
    lo, hi = (t.data.space_character, hi) if t.dimensions.x < lt[1] - lt[0] else (lo, t.data.space_character)
print("RESULT lettering", round(t.dimensions.x, 2), "x", round(t.dimensions.y, 2), "m, spacing", round(t.data.space_character, 2))
bpy.ops.object.convert(target='MESH')
bm = bmesh.new(); bm.from_mesh(t.data)                               # font meshes come out open: merge to a closed solid
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(t.data); bm.free()
bpy.ops.object.transform_apply(rotation=True)
t.name = "F_Lettering"; link(t, "Letters")

# ---------- back facade (y=D), from Commons photo 67 (CC0, 2021): camera solved from its geotag + the OSM
# corner + the wall's vanishing point; x = distance from the east corner. Only the first 17.7 m is visible
# (the Libelle lift tower hides the rest), so the remainder stays plain.
for nm, x0, x1, z0, z1 in (("B_UpTall", 1.6, 3.5, 11.6, 16.9), ("B_UpNarrow", 13.5, 15.5, 12.6, 17.5),
                           ("B_LowA", 13.7, 15.6, 4.1, 8.3), ("B_LowB", 9.6, 11.6, 3.9, 8.1)):
    box(nm, x0, x1, D - 0.4, D + 0.5, z0, z1, "Cut")

# ---------- entrance (x scaled to the real facade); y > 0 parts push into the main at staggered depths ----------
T_Z, T_W = 3.0, 9.0
T_X0, T_X1 = 17.0 * SX, 34.0 * SX
prism("Terrace", [(T_X0, -T_W), (T_X1, -T_W), (T_X1, -6.0), (41.0 * SX, -6.0), (41.0 * SX, 0.30), (T_X0, 0.30)], -1.5, T_Z, 'z', "Entrance")
S_X0, S_Z0, N = 6.5 * SX, -0.9, 22
run, rise = (T_X0 - S_X0) / (N + 2), (T_Z - S_Z0) / N
xs, x = [], S_X0
for i in range(N):
    if i == N // 2: x += 2 * run                                        # landing
    xs.append(x); x += run
zs = [S_Z0 + (i + 1) * rise for i in range(N)]
zs[-1] = T_Z - E                                                         # top tread sits just under the terrace floor plane
base = S_Z0 - 0.3
prof = [(xs[0], base), (xs[0], zs[0])]
for i in range(1, N): prof += [(xs[i], zs[i-1]), (xs[i], zs[i])]
prof += [(T_X0 + 0.3, zs[-1]), (T_X0 + 0.3, base)]
prism("Stair", prof, -T_W + 0.3, 0.28, 'y', "Entrance")
top = lambda x: S_Z0 + 0.9 + (T_Z - S_Z0) * (x - S_X0) / (T_X0 - S_X0)
prism("StairWall", [(S_X0, base - 0.1), (T_X0 + 0.3, base - 0.1), (T_X0 + 0.3, top(T_X0)), (S_X0, top(S_X0))],
      -T_W - E, -T_W + 0.4, 'y', "Entrance")
nosing = list(zip(xs, zs))
for k, (fa, fb) in enumerate(((0, N // 2 - 1), (N // 2, N - 1))):      # handrails: facade side + middle, per flight
    (xa, za), (xb, zb) = nosing[fa], nosing[fb]
    for j, yy in enumerate((-0.3, -T_W / 2)):
        a, b = Vector((xa, yy, za + 0.9)), Vector((xb + run, yy, zb + 0.9))
        rod(f"Rail_{k}{j}", a, b, 0.03, "Rails")
        for q in (a, b): rod(f"RailPost_{k}{j}_{q.x:.0f}", q - Vector((0, 0, 0.9)), q, 0.025, "Rails")
UP_Y, UN, UP_TOP = -4.75, 18, 5.9                                        # stops 10 cm under the balcony soffit
ub_x, ut_x = 33.33 * SX, 43.28 * SX
ux = [ub_x + i * (ut_x - ub_x) / UN for i in range(UN)]
uz = [T_Z + (i + 1) * (UP_TOP - T_Z) / UN for i in range(UN)]
prof = [(ux[0], -1.52), (ux[0], uz[0])]
for i in range(1, UN): prof += [(ux[i], uz[i-1]), (ux[i], uz[i])]
prof += [(ut_x, uz[-1]), (ut_x, -1.52)]
prism("UpStair", prof, UP_Y - 0.8, UP_Y + 0.8, 'y', "Entrance")
BX0, BX1, BY = 34.39 * SX, 46.57 * SX, -11.7
box("Balcony", BX0, BX1, BY, 0.32, 6.0, 10.0, "Entrance")
box("Balcony_Pier", 43.5 * SX, 46.5 * SX, -11.0, 0.25, -1.5 - E, 6.3, "Entrance")
nf, ns = 5, 5                                                            # mullion grid; one shared corner mullion
for i in range(nf + 1):
    x = BX0 + i * (BX1 - BX0) / nf; box(f"BalMullF{i}", x - 0.07, x + 0.07, BY - 0.08, BY + 0.01, 6.0 + E, 10.0 - E, "Add")
for i in range(1, ns + 1):
    y = BY + i * (0 - BY) / ns; box(f"BalMullS{i}", BX0 - 0.08, BX0 + 0.01, y - 0.07, y + 0.07, 6.0 + E, 10.0 - E, "Add")
box("BalTransomF", BX0 + 0.07 - E, BX1 - 0.07 + E, BY - 0.06, BY + 0.01, 7.25, 7.4, "Add")
box("BalTransomS", BX0 - 0.06, BX0 + 0.01, BY + 0.07 - E, -0.07 + E, 7.25, 7.4, "Add")

# ---------- roof: Libelle (separate objects, positions from pass 1 scaled to the real footprint) ----------
def S(v): return Vector((v.x * SX, v.y * SY, v.z))
def cyl(name, c, r, z0, z1, verts=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1-z0, location=(c.x, c.y, (z0+z1)/2))
    o = bpy.context.object; o.name = name; return link(o, "Roof")
def ring(name, c, r, z):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.12, major_segments=96, minor_segments=8, location=(c.x, c.y, z))
    o = bpy.context.object; o.name = name; return link(o, "Rails")
def circle_at(u, v, width_px, z):
    p = hit(u, v, 2, z); return p, width_px / 2 * (p - CAM).dot(F) / FPX
pc, pr = circle_at(1080, 475, 540, 29.0); pc = S(pc)
cyl("Pavilion_Roof_Low", pc, pr, 27.6, 28.2)
cyl("Pavilion_Roof_High", pc + Vector((pr*0.35, pr*0.1, 0)), pr*0.7, 28.4, 29.0)
cyl("Pavilion_Body", pc, pr*0.8, H - 0.1, 27.6)
cc, cr = circle_at(1438, 505, 104, 28.5); cyl("Cylinder", S(cc), cr, H - 0.1, 28.5)
def railing(prefix, u, v, w_top, z_top, z_low, low_scale):
    c, r = circle_at(u, v, w_top, z_top); c = S(c)
    ring(prefix + "_Top", c, r, z_top); ring(prefix + "_Low", c, r * low_scale, z_low)
    for k in range(8):
        a = 2 * math.pi * k / 8 + 0.3
        rod(f"{prefix}_Post_{k}", Vector((c.x + r*low_scale*math.cos(a), c.y + r*low_scale*math.sin(a), H)),
            Vector((c.x + r*math.cos(a), c.y + r*math.sin(a), z_top)), 0.1, "Rails")
railing("RingLeft", 612, 452, 298, 28.0, 26.3, 0.65)
railing("RingCenter", 1185, 490, 406, 28.0, 26.3, 0.8)

# ---------- booleans, each verified ----------
main = bpy.data.objects["Main"]
def mesh_state():
    bm = bmesh.new(); bm.from_mesh(main.data)
    st = (len(bm.verts), bm.calc_volume(signed=True), sum(not e.is_manifold for e in bm.edges)); bm.free(); return st
BAD = []
def apply_bool(op, collection):
    bad, n = [], 0
    for o in sorted(collection.objects, key=lambda o: o.name):
        bpy.context.view_layer.objects.active = main
        v0, vol0, open0 = mesh_state()
        m = main.modifiers.new(op, 'BOOLEAN'); m.operation = op; m.object = o; m.solver = 'EXACT'
        bpy.ops.object.modifier_apply(modifier=m.name)
        v1, vol1, open1 = mesh_state()
        why = ("no effect" if v1 == v0 else
               "volume wrong way" if (vol1 < vol0 - 1e-3 if op == 'UNION' else vol1 > vol0 + 1e-3) else
               f"open edges {open0}->{open1}" if open1 > open0 else None)
        if why: bad.append(f"{o.name}: {why}")
        bpy.data.objects.remove(o); n += 1
    BAD.extend(bad)
    print(f"RESULT {op} {collection.name}: {n} operands, {len(bad)} bad: {bad[:12]}")
apply_bool('DIFFERENCE', coll["Cut"])
apply_bool('DIFFERENCE', coll["Letters"])
for o in [o for o in coll["Building"].objects if o is not main]: link(o, "Add")
for o in list(coll["Entrance"].objects): link(o, "Add")
apply_bool('UNION', coll["Add"])
def terrace_rect(tl, br):                   # terrace front wall (plane y=-T_W)
    a, b = hit(*tl, 1, -T_W), hit(*br, 1, -T_W); return a.x * SX, b.x * SX, b.z, a.z
for nm, (tl, br) in (("T_Window", ((1382, 1265), (1444, 1321))), ("T_Door", ((1395, 1330), (1425, 1398)))):
    x0, x1, z0, z1 = terrace_rect(tl, br); box(nm, x0, x1, -T_W - 0.5, -T_W + 0.4, z0, z1, "Cut2")
apply_bool('DIFFERENCE', coll["Cut2"])
main.name = "Building"
_, vol, opn = mesh_state()
print("RESULT building tris", sum(len(p.vertices) - 2 for p in main.data.polygons), "volume m3", round(vol), "open edges", opn,
      "| TOTAL BAD", len(BAD))

# ---------- camera refit to the real proportions + clay render ----------
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera")); bpy.context.scene.collection.objects.link(cam)
cam.location = (-29.94, -54.28, 16.71); cam.rotation_euler = (math.radians(90), 0, -math.radians(37.6))
cam.data.sensor_fit = 'HORIZONTAL'; cam.data.sensor_width = 36
cam.data.lens = 2269 * 36 / 2048; cam.data.shift_y = -(1024 - 790) / 2048
sc = bpy.context.scene; sc.camera = cam
sc.render.resolution_x = sc.render.resolution_y = 2048
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'AgX'
clay = bpy.data.materials.new("Clay"); clay.use_nodes = True
clay.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
clay.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
for o in bpy.data.objects:
    if o.type == 'MESH': o.data.materials.clear(); o.data.materials.append(clay)
sc.world = bpy.data.worlds.new("World"); sc.world.use_nodes = True
bg = sc.world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (1, 1, 1, 1); bg.inputs["Strength"].default_value = 0.8
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 2.0; sun.data.angle = math.radians(15); sun.rotation_euler = (math.radians(50), 0, math.radians(25))
sc.render.filepath = out_png
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
