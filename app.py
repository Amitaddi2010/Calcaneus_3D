import streamlit as st
import numpy as np
import zipfile
import io
import os
import tempfile
from typing import List, Dict, Tuple, Optional

from utils import validate_stl_file, validate_zip_file
from processing import process_screw_placement
from visualization import plot_3d_results, plot_distance_graph

# Set page config
st.set_page_config(
    page_title="Calcaneus Screw Placement Analysis",
    page_icon="🦶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title and description
st.title("Calcaneus Screw Placement Analysis")
st.markdown("""
This application analyzes and visualizes screw placements in calcaneus (heel bone) surfaces using STL files.
Upload your medial and lateral bone surface STL files along with a ZIP containing screw STL files 
to receive comprehensive analysis of potential breaches and optimal placement.
""")

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This tool helps orthopedic surgeons analyze screw placement in the calcaneus (heel bone).
    
    ### Features:
    - Automatic detection of left/right foot
    - Breach detection for medial and lateral walls
    - Distance measurements between screws and bone surfaces
    - Interactive 3D visualization
    - Batch processing for multiple screws
    
    ### Instructions:
    1. Upload medial and lateral STL files
    2. Upload a ZIP file containing screw STL files
    3. Click 'Process Files' to analyze
    """)
    
    # Display calcaneus anatomy image
    st.subheader("Calcaneus Anatomy")
    st.image("https://pixabay.com/get/ge0620f777aa4d4de1820d0019138b9d9aa85b890281e831f4a1ac962001208a93843c0d25ba41787b09af9c55cd9d5d7eb18c33f3ae3c9edc06278705be8faaf_1280.jpg")
    
    # Display orthopedic visualization image
    st.subheader("Orthopedic Visualization")
    st.image("https://pixabay.com/get/gcafd3319db3a0cff55b7497ab36a732cd4c01ecbfd1c66941cb80fe81687f1c4909ca8c24a6d8f4560ce4452c553fda579f7ebe14e8fece5b7838a1f8da9f50b_1280.jpg")

# Main content area with file uploads
st.header("File Upload")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Medial Surface (STL)")
    medial_file = st.file_uploader("Upload a file or drag and drop", type=["stl"], key="medial_uploader", 
                                   help="Upload the STL file for the medial surface of the calcaneus.")
    
    if medial_file:
        is_valid = validate_stl_file(medial_file)
        if is_valid:
            st.success("Medial surface file uploaded successfully.")
        else:
            st.error("Invalid STL file. Please check the file and try again.")
            medial_file = None

with col2:
    st.subheader("Lateral Surface (STL)")
    lateral_file = st.file_uploader("Upload a file or drag and drop", type=["stl"], key="lateral_uploader",
                                   help="Upload the STL file for the lateral surface of the calcaneus.")
    
    if lateral_file:
        is_valid = validate_stl_file(lateral_file)
        if is_valid:
            st.success("Lateral surface file uploaded successfully.")
        else:
            st.error("Invalid STL file. Please check the file and try again.")
            lateral_file = None

st.subheader("Screws (ZIP file containing STL files)")
screws_zip = st.file_uploader("Upload a file or drag and drop", type=["zip"], key="screws_uploader",
                             help="Upload a ZIP file containing STL files for screws (maximum 48 files).")

screw_files = []
if screws_zip:
    is_valid, message, extracted_files = validate_zip_file(screws_zip)
    if is_valid:
        st.success(f"ZIP file uploaded successfully. Found {len(extracted_files)} screw STL files.")
        screw_files = extracted_files
    else:
        st.error(message)
        screws_zip = None

# Process button
if st.button("Process Files", disabled=not (medial_file and lateral_file and screw_files)):
    if not (medial_file and lateral_file and screw_files):
        st.error("Please upload all required files before processing.")
    else:
        with st.spinner("Processing files..."):
            # Create temporary files to store the uploaded content
            with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_medial, \
                 tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_lateral:
                
                # Write uploaded content to temp files
                temp_medial.write(medial_file.getvalue())
                temp_lateral.write(lateral_file.getvalue())
                
                # Create temporary files for each screw
                temp_screw_files = []
                for i, screw_data in enumerate(screw_files):
                    with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as temp_screw:
                        temp_screw.write(screw_data)
                        temp_screw_files.append(temp_screw.name)
                
                results = []
                for i, screw_file in enumerate(temp_screw_files):
                    # Process each screw
                    progress_text = f"Processing screw {i+1}/{len(temp_screw_files)}"
                    progress_bar = st.progress(0)
                    
                    try:
                        result = process_screw_placement(temp_medial.name, temp_lateral.name, screw_file)
                        results.append(result)
                        progress_bar.progress((i+1)/len(temp_screw_files))
                    except Exception as e:
                        st.error(f"Error processing screw {i+1}: {str(e)}")
                        
                # Delete temporary files
                os.unlink(temp_medial.name)
                os.unlink(temp_lateral.name)
                for temp_file in temp_screw_files:
                    os.unlink(temp_file)
            
            # Display results
            if results:
                st.subheader("Analysis Results")
                
                # Show foot side
                foot_side = results[0]['foot_side']
                st.info(f"🦶 Detected Foot Side: {foot_side}")
                
                # Create tabs for each screw
                tabs = st.tabs([f"Screw {i+1}" for i in range(len(results))])
                
                for i, tab in enumerate(tabs):
                    with tab:
                        result = results[i]
                        col1, col2 = st.columns([3, 2])
                        
                        with col1:
                            st.subheader("3D Visualization")
                            fig = plot_3d_results(result)
                            st.pyplot(fig)
                            
                        with col2:
                            st.subheader("Distance Measurements")
                            med_shortest = result['medial_shortest_positive']
                            med_longest_breach = result['medial_longest_negative']
                            lat_shortest = result['lateral_shortest_positive']
                            lat_longest_breach = result['lateral_longest_negative']
                            
                            dist_fig = plot_distance_graph(
                                result['axis_points'], 
                                result['signed_medial'], 
                                result['signed_lateral']
                            )
                            st.pyplot(dist_fig)
                            
                            # Summary statistics
                            st.subheader("Summary Statistics")
                            
                            # Medial wall info
                            st.markdown("**Medial Wall:**")
                            st.markdown(f"- Shortest Positive Distance: {med_shortest:.2f} mm")
                            
                            if np.isnan(med_longest_breach):
                                st.markdown("- ✅ No Medial Breach Detected")
                            else:
                                st.markdown(f"- ⚠️ Medial Breach Detected: {med_longest_breach:.2f} mm")
                            
                            # Lateral wall info
                            st.markdown("**Lateral Wall:**")
                            st.markdown(f"- Shortest Positive Distance: {lat_shortest:.2f} mm")
                            
                            if np.isnan(lat_longest_breach):
                                st.markdown("- ✅ No Lateral Breach Detected")
                            else:
                                st.markdown(f"- ⚠️ Lateral Breach Detected: {lat_longest_breach:.2f} mm")
                
                # Overall summary for all screws
                st.subheader("Overall Summary")
                
                # Count breaches
                medial_breaches = sum(1 for r in results if not np.isnan(r['medial_longest_negative']))
                lateral_breaches = sum(1 for r in results if not np.isnan(r['lateral_longest_negative']))
                
                st.markdown(f"- Total Screws Analyzed: {len(results)}")
                st.markdown(f"- Screws with Medial Breaches: {medial_breaches}")
                st.markdown(f"- Screws with Lateral Breaches: {lateral_breaches}")
                
                if medial_breaches == 0 and lateral_breaches == 0:
                    st.success("✅ All screws are properly placed with no breaches detected.")
                else:
                    st.warning(f"⚠️ {medial_breaches + lateral_breaches} screws have potential breaches. Please review the individual screw tabs for details.")
                    
                    # Recommendations
                    if medial_breaches > 0 or lateral_breaches > 0:
                        st.subheader("Recommendations")
                        st.markdown("""
                        - Review screws with breaches and consider repositioning
                        - For medial breaches, adjust the screw entry point laterally
                        - For lateral breaches, adjust the screw entry point medially
                        - Consider using shorter screws for cases with minimal clearance
                        """)
