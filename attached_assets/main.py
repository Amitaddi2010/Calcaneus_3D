import numpy as np
import trimesh
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt

print('--- Full-Length XY-Plane Signed Perpendicular Distances (with Breach Summary) ---')

# Load STL files
medial = trimesh.load_mesh(input("Enter the Medial Wall STL path: "))
lateral = trimesh.load_mesh(input("Enter the Lateral Wall STL path: "))
screw = trimesh.load_mesh(input("Enter the Screw STL path: "))

# Determine foot side
is_left = np.mean(medial.vertices[:, 0]) > np.mean(lateral.vertices[:, 0])
foot_side = 'Left Calcaneus' if is_left else 'Right Calcaneus'
print(f"🦶 Detected Foot Side: {foot_side}")

# Step 1: PCA to get screw axis
screw_points = screw.vertices
center = np.mean(screw_points, axis=0)
_, _, vh = np.linalg.svd(screw_points - center)
axis_dir = vh[0]
projections = np.dot(screw_points - center, axis_dir)
min_proj, max_proj = projections.min(), projections.max()
length_screw = max_proj - min_proj
n_points = int(np.ceil(length_screw))
t = np.linspace(min_proj, max_proj, n_points)
axis_pts = center + t[:, None] * axis_dir

# Step 2: Define XY-plane perpendicular direction
perp_xy = np.array([-axis_dir[1], axis_dir[0], 0])
perp_xy /= np.linalg.norm(perp_xy)

# Step 3: Sampling and distance settings
probe_span = 100
n_samples = 400
dist_tol = 3
signed_medial = np.full(n_points, np.nan)
signed_lateral = np.full(n_points, np.nan)
medial_hit = np.full((n_points, 3), np.nan)
lateral_hit = np.full((n_points, 3), np.nan)

# Step 4: Loop through screw axis points
for i in range(n_points):
    Pi = axis_pts[i]
    s = np.linspace(-probe_span, probe_span, n_samples)
    probe_pts = Pi + s[:, None] * perp_xy

    # MEDIAL wall check
    D_med = cdist(probe_pts, medial.vertices)
    min_d_med = np.min(D_med, axis=1)
    dval, idx = min_d_med.min(), min_d_med.argmin()
    if dval < dist_tol:
        medial_hit[i] = probe_pts[idx]
        wallX = medial_hit[i, 0]
        screwX = Pi[0]
        signed_medial[i] = wallX - screwX if is_left else screwX - wallX

    # LATERAL wall check
    D_lat = cdist(probe_pts, lateral.vertices)
    min_d_lat = np.min(D_lat, axis=1)
    dval, idx = min_d_lat.min(), min_d_lat.argmin()
    if dval < dist_tol:
        lateral_hit[i] = probe_pts[idx]
        wallX = lateral_hit[i, 0]
        screwX = Pi[0]
        signed_lateral[i] = screwX - wallX if is_left else wallX - screwX

# Step 5: Visualization
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(screw_points[:, 0], screw_points[:, 1], screw_points[:, 2], c='magenta', alpha=0.6, label='Screw')
ax.scatter(medial.vertices[:, 0], medial.vertices[:, 1], medial.vertices[:, 2], c='red', alpha=0.3, label='Medial Wall')
ax.scatter(lateral.vertices[:, 0], lateral.vertices[:, 1], lateral.vertices[:, 2], c='blue', alpha=0.3, label='Lateral Wall')
ax.scatter(axis_pts[:, 0], axis_pts[:, 1], axis_pts[:, 2], c='yellow', s=10, label='Screw Axis Points')
for i in range(n_points):
    if not np.isnan(signed_medial[i]):
        ax.plot([axis_pts[i, 0], medial_hit[i, 0]], 
                [axis_pts[i, 1], medial_hit[i, 1]], 
                [axis_pts[i, 2], medial_hit[i, 2]], 'r-', linewidth=1)
    if not np.isnan(signed_lateral[i]):
        ax.plot([axis_pts[i, 0], lateral_hit[i, 0]], 
                [axis_pts[i, 1], lateral_hit[i, 1]], 
                [axis_pts[i, 2], lateral_hit[i, 2]], 'b-', linewidth=1)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.title(f'XY-Plane Signed Distances with Breach Logic ({foot_side})')
plt.legend()
plt.show()

# Step 6: Summary statistics
valid_idx = np.arange(10, n_points)
medial_vals = signed_medial[valid_idx]
lateral_vals = signed_lateral[valid_idx]

medial_shortest_positive = np.min(medial_vals[medial_vals > 0])
medial_longest_negative = np.min(medial_vals[medial_vals < 0]) if np.any(medial_vals < 0) else np.nan
lateral_shortest_positive = np.min(lateral_vals[lateral_vals > 0])
lateral_longest_negative = np.min(lateral_vals[lateral_vals < 0]) if np.any(lateral_vals < 0) else np.nan

print("\nMedial Wall:")
print(f"→ Shortest Positive Distance: {medial_shortest_positive:.2f} mm")
print(f"→ Longest Negative Breach: {medial_longest_negative:.2f} mm" if not np.isnan(medial_longest_negative) else "→ No Medial Breach Detected.")

print("\nLateral Wall:")
print(f"→ Shortest Positive Distance: {lateral_shortest_positive:.2f} mm")
print(f"→ Longest Negative Breach: {lateral_longest_negative:.2f} mm" if not np.isnan(lateral_longest_negative) else "→ No Lateral Breach Detected.")
