import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from typing import Dict, List, Tuple, Any, Optional

matplotlib.use('Agg')  # Use a non-interactive backend for Streamlit compatibility

def plot_3d_results(result: Dict[str, Any]) -> plt.Figure:
    """
    Create a 3D visualization of the screw placement analysis.
    
    Args:
        result: Dict containing analysis results
        
    Returns:
        matplotlib Figure with the 3D visualization
    """
    screw_points = result['screw_points']
    medial_vertices = result['medial_vertices']
    lateral_vertices = result['lateral_vertices']
    axis_pts = result['axis_points']
    medial_hit = result['medial_hit']
    lateral_hit = result['lateral_hit']
    signed_medial = result['signed_medial']
    signed_lateral = result['signed_lateral']
    foot_side = result['foot_side']
    
    # Create figure
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot downsampled points for better performance
    downsample = lambda arr, factor: arr[::factor]
    
    # Sample rate depends on number of points
    medial_factor = max(1, len(medial_vertices) // 2000)
    lateral_factor = max(1, len(lateral_vertices) // 2000)
    screw_factor = max(1, len(screw_points) // 1000)
    
    # Plot surfaces and screw
    ax.scatter(
        downsample(medial_vertices[:, 0], medial_factor),
        downsample(medial_vertices[:, 1], medial_factor),
        downsample(medial_vertices[:, 2], medial_factor),
        c='red', alpha=0.3, label='Medial Wall', s=10
    )
    ax.scatter(
        downsample(lateral_vertices[:, 0], lateral_factor),
        downsample(lateral_vertices[:, 1], lateral_factor),
        downsample(lateral_vertices[:, 2], lateral_factor),
        c='blue', alpha=0.3, label='Lateral Wall', s=10
    )
    ax.scatter(
        downsample(screw_points[:, 0], screw_factor),
        downsample(screw_points[:, 1], screw_factor),
        downsample(screw_points[:, 2], screw_factor),
        c='magenta', alpha=0.6, label='Screw', s=15
    )
    
    # Plot screw axis points
    ax.scatter(axis_pts[:, 0], axis_pts[:, 1], axis_pts[:, 2], 
               c='yellow', s=10, label='Screw Axis')
    
    # Plot measurement lines
    n_points = len(axis_pts)
    for i in range(n_points):
        if not np.isnan(signed_medial[i]):
            if signed_medial[i] < 0:  # Breach
                line_style = 'r--'  # Dashed red for breach
                line_width = 2
            else:
                line_style = 'r-'
                line_width = 1
                
            ax.plot([axis_pts[i, 0], medial_hit[i, 0]], 
                    [axis_pts[i, 1], medial_hit[i, 1]], 
                    [axis_pts[i, 2], medial_hit[i, 2]], 
                    line_style, linewidth=line_width)
                    
        if not np.isnan(signed_lateral[i]):
            if signed_lateral[i] < 0:  # Breach
                line_style = 'b--'  # Dashed blue for breach
                line_width = 2
            else:
                line_style = 'b-'
                line_width = 1
                
            ax.plot([axis_pts[i, 0], lateral_hit[i, 0]], 
                    [axis_pts[i, 1], lateral_hit[i, 1]], 
                    [axis_pts[i, 2], lateral_hit[i, 2]], 
                    line_style, linewidth=line_width)
    
    # Add labels and legend
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title(f'XY-Plane Signed Distances with Breach Logic ({foot_side})')
    plt.legend(loc='upper right', fontsize=8)
    
    # Set equal aspect ratio
    max_range = np.array([
        ax.get_xlim()[1] - ax.get_xlim()[0],
        ax.get_ylim()[1] - ax.get_ylim()[0],
        ax.get_zlim()[1] - ax.get_zlim()[0]
    ]).max() / 2.0
    
    mid_x = (ax.get_xlim()[1] + ax.get_xlim()[0]) / 2
    mid_y = (ax.get_ylim()[1] + ax.get_ylim()[0]) / 2
    mid_z = (ax.get_zlim()[1] + ax.get_zlim()[0]) / 2
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.tight_layout()
    return fig

def plot_distance_graph(
    axis_pts: np.ndarray, 
    signed_medial: np.ndarray, 
    signed_lateral: np.ndarray
) -> plt.Figure:
    """
    Create a 2D graph showing the signed distances along the screw axis.
    
    Args:
        axis_pts: Array of points along the screw axis
        signed_medial: Array of signed distances to the medial wall
        signed_lateral: Array of signed distances to the lateral wall
        
    Returns:
        matplotlib Figure with the distance graph
    """
    # Calculate distance along screw axis
    axis_dist = np.zeros(len(axis_pts))
    for i in range(1, len(axis_pts)):
        axis_dist[i] = axis_dist[i-1] + np.linalg.norm(axis_pts[i] - axis_pts[i-1])
    
    # Create figure
    fig, ax = plt.figure(figsize=(8, 4)), plt.gca()
    
    # Plot distances
    medial_mask = ~np.isnan(signed_medial)
    lateral_mask = ~np.isnan(signed_lateral)
    
    # Plot breach threshold line
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.5)
    
    # Plot medial distances
    if np.any(medial_mask):
        ax.scatter(axis_dist[medial_mask], signed_medial[medial_mask], 
                   c='red', label='Medial Wall Distance', alpha=0.7, s=20)
        
        # Connect points with lines
        ax.plot(axis_dist[medial_mask], signed_medial[medial_mask], 
                'r-', alpha=0.4)
    
    # Plot lateral distances
    if np.any(lateral_mask):
        ax.scatter(axis_dist[lateral_mask], signed_lateral[lateral_mask], 
                   c='blue', label='Lateral Wall Distance', alpha=0.7, s=20)
        
        # Connect points with lines
        ax.plot(axis_dist[lateral_mask], signed_lateral[lateral_mask], 
                'b-', alpha=0.4)
    
    # Highlight negative values (breaches)
    medial_breach = np.logical_and(medial_mask, signed_medial < 0)
    lateral_breach = np.logical_and(lateral_mask, signed_lateral < 0)
    
    if np.any(medial_breach):
        ax.scatter(axis_dist[medial_breach], signed_medial[medial_breach],
                   c='darkred', marker='x', s=80, label='Medial Breach')
    
    if np.any(lateral_breach):
        ax.scatter(axis_dist[lateral_breach], signed_lateral[lateral_breach],
                   c='darkblue', marker='x', s=80, label='Lateral Breach')
    
    # Add labels and legend
    ax.set_xlabel('Distance Along Screw Axis (mm)')
    ax.set_ylabel('Wall Distance (mm)')
    ax.set_title('Bone Wall Distances Along Screw Axis')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add annotation for breach interpretation
    if np.any(medial_breach) or np.any(lateral_breach):
        plt.figtext(0.5, 0.01, 
                    "⚠️ Negative values indicate a breach through the bone surface", 
                    ha="center", fontsize=10, 
                    bbox={"facecolor":"yellow", "alpha":0.2, "pad":5})
    
    plt.tight_layout()
    return fig
