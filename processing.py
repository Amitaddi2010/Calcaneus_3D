import numpy as np
import trimesh
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional

def process_screw_placement(
    medial_path: str, 
    lateral_path: str, 
    screw_path: str
) -> Dict[str, Any]:
    """
    Process and analyze screw placement relative to medial and lateral walls.
    
    Args:
        medial_path: Path to the medial wall STL file
        lateral_path: Path to the lateral wall STL file
        screw_path: Path to the screw STL file
        
    Returns:
        Dict containing analysis results
    """
    # Load STL files
    medial = trimesh.load_mesh(medial_path)
    lateral = trimesh.load_mesh(lateral_path)
    screw = trimesh.load_mesh(screw_path)
    
    # Determine foot side
    is_left = np.mean(medial.vertices[:, 0]) > np.mean(lateral.vertices[:, 0])
    foot_side = 'Left Calcaneus' if is_left else 'Right Calcaneus'
    
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
    
    # Calculate summary statistics
    valid_idx = np.arange(10, n_points)
    medial_vals = signed_medial[valid_idx]
    lateral_vals = signed_lateral[valid_idx]
    
    # Filter out NaN values
    medial_vals = medial_vals[~np.isnan(medial_vals)]
    lateral_vals = lateral_vals[~np.isnan(lateral_vals)]
    
    # Get medial measurements
    medial_shortest_positive = np.min(medial_vals[medial_vals > 0]) if np.any(medial_vals > 0) else np.nan
    medial_longest_negative = np.min(medial_vals[medial_vals < 0]) if np.any(medial_vals < 0) else np.nan
    
    # Get lateral measurements
    lateral_shortest_positive = np.min(lateral_vals[lateral_vals > 0]) if np.any(lateral_vals > 0) else np.nan
    lateral_longest_negative = np.min(lateral_vals[lateral_vals < 0]) if np.any(lateral_vals < 0) else np.nan
    
    # Create result dictionary
    result = {
        'foot_side': foot_side,
        'is_left': is_left,
        'screw_points': screw_points,
        'medial_vertices': medial.vertices,
        'lateral_vertices': lateral.vertices,
        'axis_points': axis_pts,
        'medial_hit': medial_hit,
        'lateral_hit': lateral_hit,
        'signed_medial': signed_medial,
        'signed_lateral': signed_lateral,
        'medial_shortest_positive': medial_shortest_positive,
        'medial_longest_negative': medial_longest_negative,
        'lateral_shortest_positive': lateral_shortest_positive,
        'lateral_longest_negative': lateral_longest_negative
    }
    
    return result
