import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Any, Optional

def plot_3d_results(result: Dict[str, Any]) -> go.Figure:
    """
    Create an interactive 3D visualization of the screw placement analysis using Plotly.
    
    Args:
        result: Dict containing analysis results
        
    Returns:
        plotly Figure with the interactive 3D visualization
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
    fig = go.Figure()
    
    # Plot downsampled points for better performance
    downsample = lambda arr, factor: arr[::factor]
    
    # Sample rate depends on number of points
    medial_factor = max(1, len(medial_vertices) // 2000)
    lateral_factor = max(1, len(lateral_vertices) // 2000)
    screw_factor = max(1, len(screw_points) // 1000)
    
    # Plot surfaces and screw
    fig.add_trace(go.Scatter3d(
        x=downsample(medial_vertices[:, 0], medial_factor),
        y=downsample(medial_vertices[:, 1], medial_factor),
        z=downsample(medial_vertices[:, 2], medial_factor),
        mode='markers',
        marker=dict(size=2, color='red', opacity=0.3),
        name='Medial Wall'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=downsample(lateral_vertices[:, 0], lateral_factor),
        y=downsample(lateral_vertices[:, 1], lateral_factor),
        z=downsample(lateral_vertices[:, 2], lateral_factor),
        mode='markers',
        marker=dict(size=2, color='blue', opacity=0.3),
        name='Lateral Wall'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=downsample(screw_points[:, 0], screw_factor),
        y=downsample(screw_points[:, 1], screw_factor),
        z=downsample(screw_points[:, 2], screw_factor),
        mode='markers',
        marker=dict(size=3, color='magenta', opacity=0.6),
        name='Screw'
    ))
    
    # Plot screw axis points
    fig.add_trace(go.Scatter3d(
        x=axis_pts[:, 0],
        y=axis_pts[:, 1],
        z=axis_pts[:, 2],
        mode='markers',
        marker=dict(size=2, color='yellow'),
        name='Screw Axis'
    ))
    
    # Plot measurement lines
    n_points = len(axis_pts)
    for i in range(n_points):
        if not np.isnan(signed_medial[i]):
            color = 'red' if signed_medial[i] < 0 else 'green'
            width = 3 if signed_medial[i] < 0 else 1
            fig.add_trace(go.Scatter3d(
                x=[axis_pts[i, 0], medial_hit[i, 0]],
                y=[axis_pts[i, 1], medial_hit[i, 1]],
                z=[axis_pts[i, 2], medial_hit[i, 2]],
                mode='lines',
                line=dict(color=color, width=width),
                showlegend=False
            ))
            
        if not np.isnan(signed_lateral[i]):
            color = 'blue' if signed_lateral[i] < 0 else 'green'
            width = 3 if signed_lateral[i] < 0 else 1
            fig.add_trace(go.Scatter3d(
                x=[axis_pts[i, 0], lateral_hit[i, 0]],
                y=[axis_pts[i, 1], lateral_hit[i, 1]],
                z=[axis_pts[i, 2], lateral_hit[i, 2]],
                mode='lines',
                line=dict(color=color, width=width),
                showlegend=False
            ))
    
    # Update layout
    fig.update_layout(
        title=f'3D Visualization of Screw Placement ({foot_side})',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def plot_distance_graph(
    axis_pts: np.ndarray, 
    signed_medial: np.ndarray, 
    signed_lateral: np.ndarray
) -> go.Figure:
    """
    Create an interactive 2D graph showing the signed distances along the screw axis using Plotly.
    
    Args:
        axis_pts: Array of points along the screw axis
        signed_medial: Array of signed distances to the medial wall
        signed_lateral: Array of signed distances to the lateral wall
        
    Returns:
        plotly Figure with the interactive distance graph
    """
    # Calculate distance along screw axis
    axis_dist = np.zeros(len(axis_pts))
    for i in range(1, len(axis_pts)):
        axis_dist[i] = axis_dist[i-1] + np.linalg.norm(axis_pts[i] - axis_pts[i-1])
    
    # Create figure
    fig = go.Figure()
    
    # Plot breach threshold line
    fig.add_hline(y=0, line=dict(color='black', width=1, dash='solid'))
    
    # Plot medial distances
    medial_mask = ~np.isnan(signed_medial)
    if np.any(medial_mask):
        fig.add_trace(go.Scatter(
            x=axis_dist[medial_mask],
            y=signed_medial[medial_mask],
            mode='lines+markers',
            name='Medial Wall Distance',
            line=dict(color='red', width=2),
            marker=dict(size=6, color='red')
        ))
    
    # Plot lateral distances
    lateral_mask = ~np.isnan(signed_lateral)
    if np.any(lateral_mask):
        fig.add_trace(go.Scatter(
            x=axis_dist[lateral_mask],
            y=signed_lateral[lateral_mask],
            mode='lines+markers',
            name='Lateral Wall Distance',
            line=dict(color='blue', width=2),
            marker=dict(size=6, color='blue')
        ))
    
    # Highlight breaches
    medial_breach = np.logical_and(medial_mask, signed_medial < 0)
    lateral_breach = np.logical_and(lateral_mask, signed_lateral < 0)
    
    if np.any(medial_breach):
        fig.add_trace(go.Scatter(
            x=axis_dist[medial_breach],
            y=signed_medial[medial_breach],
            mode='markers',
            name='Medial Breach',
            marker=dict(size=10, color='darkred', symbol='x')
        ))
    
    if np.any(lateral_breach):
        fig.add_trace(go.Scatter(
            x=axis_dist[lateral_breach],
            y=signed_lateral[lateral_breach],
            mode='markers',
            name='Lateral Breach',
            marker=dict(size=10, color='darkblue', symbol='x')
        ))
    
    # Update layout
    fig.update_layout(
        title='Bone Wall Distances Along Screw Axis',
        xaxis_title='Distance Along Screw Axis (mm)',
        yaxis_title='Wall Distance (mm)',
        showlegend=True,
        hovermode='x unified',
        annotations=[
            dict(
                text="⚠️ Negative values indicate a breach through the bone surface",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.01,
                showarrow=False,
                bgcolor="yellow",
                opacity=0.2
            )
        ] if np.any(medial_breach) or np.any(lateral_breach) else []
    )
    
    return fig
