import streamlit as st
import numpy as np
import zipfile
import io
import os
import tempfile
import pandas as pd
import time
import base64
import datetime
from typing import List, Dict, Tuple, Optional

from utils import validate_stl_file, validate_zip_file
from processing import process_screw_placement
from visualization import plot_3d_results, plot_distance_graph
from database import db

# Set page config
st.set_page_config(
    page_title="Calcaneus Screw Placement Analysis",
    page_icon="🦶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create a session state for navigation and data
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = []
if 'current_patient_id' not in st.session_state:
    st.session_state.current_patient_id = None
if 'patients' not in st.session_state:
    st.session_state.patients = []
if 'patient_analyses' not in st.session_state:
    st.session_state.patient_analyses = []
    
# Load patients from database initially
try:
    st.session_state.patients = db.get_all_patients()
except Exception as e:
    st.error(f"Failed to load patients from database: {str(e)}")
    
# Download functions
def create_excel_download_link(df, filename, link_text):
    """
    Creates a download link for a pandas DataFrame as an Excel file
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Analysis Results', index=False)
    output.seek(0)
    
    b64 = base64.b64encode(output.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# Sidebar with navigation and information
with st.sidebar:
    st.title("Navigation")
    
    # Navigation buttons
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = 'landing'
        st.rerun()
        
    if st.button("📊 Analysis Dashboard", use_container_width=True):
        st.session_state.page = 'dashboard'
        st.rerun()
        
    if st.button("🔬 New Analysis", use_container_width=True):
        st.session_state.page = 'analysis'
        st.rerun()
        
    if st.button("👥 Patient Records", use_container_width=True):
        st.session_state.page = 'patients'
        # Refresh the patient list
        st.session_state.patients = db.get_all_patients()
        st.rerun()
    
    st.markdown("---")
    
    st.header("About")
    st.markdown("""
    This tool helps orthopedic surgeons analyze screw placement in the calcaneus (heel bone).
    
    ### Features:
    - Automatic detection of left/right foot
    - Breach detection for medial and lateral walls
    - Distance measurements between screws and bone surfaces
    - Interactive 3D visualization
    - Batch processing for multiple screws
    - Excel export functionality
    
    ### Instructions:
    1. Upload medial and lateral STL files
    2. Upload a ZIP file containing screw STL files
    3. Click 'Process Files' to analyze
    4. Export results to Excel for reporting
    """)
    
    # Display calcaneus anatomy image
    st.subheader("Calcaneus Anatomy")
    st.image("https://pixabay.com/get/ge0620f777aa4d4de1820d0019138b9d9aa85b890281e831f4a1ac962001208a93843c0d25ba41787b09af9c55cd9d5d7eb18c33f3ae3c9edc06278705be8faaf_1280.jpg")
    
    # Display orthopedic visualization image
    st.subheader("Orthopedic Visualization")
    st.image("https://pixabay.com/get/gcafd3319db3a0cff55b7497ab36a732cd4c01ecbfd1c66941cb80fe81687f1c4909ca8c24a6d8f4560ce4452c553fda579f7ebe14e8fece5b7838a1f8da9f50b_1280.jpg")

# Content based on the current page
if st.session_state.page == 'landing':
    # Landing page
    st.markdown("<h1 style='text-align: center;'>Welcome to Calcaneus Screw Placement Analysis</h1>", unsafe_allow_html=True)
    
    # Hero section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("""
        ## Advanced Orthopedic Analysis Tool
        
        This state-of-the-art application is designed for orthopedic surgeons and researchers to analyze and 
        visualize screw placements in calcaneus (heel bone) surfaces using STL files.
        
        ### Key Benefits:
        
        - **Precision Analysis**: Automatic detection of breaches and measurements between screws and bone surfaces
        - **Real-time Visualization**: Interactive 3D models of the calcaneus and screw placements
        - **Comprehensive Reporting**: Detailed statistics and exportable Excel reports
        - **Batch Processing**: Analyze multiple screws simultaneously for complex cases
        - **Clinical Decision Support**: Get evidence-based recommendations for optimal screw placement
        
        Start your analysis today by clicking the "New Analysis" button in the sidebar or below.
        """)
        
        # CTA Button
        if st.button("Start New Analysis", type="primary", use_container_width=True):
            st.session_state.page = 'analysis'
            st.rerun()
    
    with col2:
        # Hero image
        st.image("https://pixabay.com/get/gb3c0b7eaf58e1ea30b91d52276d1ebed1fa583aa8a31f97a1a40ef1eb80c5ca24b78a9e71ec0b4bbb2c2c3a0267a8f9f10d6c1bcc6cbdf71b3c07c2bd64ed86a_1280.jpg", 
                 caption="Advanced 3D Analysis Technology")
    
    # Features section
    st.markdown("<h2 style='text-align: center; margin-top: 2rem;'>Features</h2>", unsafe_allow_html=True)
    
    # Three column layout for features
    feat1, feat2, feat3 = st.columns(3)
    
    with feat1:
        st.markdown("### 🔍 Precision Analysis")
        st.markdown("""
        - Sub-millimeter accuracy
        - Automatic left/right detection
        - Critical breach identification
        - Distance measurements
        """)
    
    with feat2:
        st.markdown("### 📊 Visualization")
        st.markdown("""
        - Interactive 3D models
        - Cross-sectional views
        - Color-coded breach detection
        - Measurement graphs
        """)
    
    with feat3:
        st.markdown("### 📋 Reporting")
        st.markdown("""
        - Comprehensive statistics
        - Excel export functionality
        - Clinical recommendations
        - Batch processing capability
        """)
    
    # How it works section
    st.markdown("<h2 style='text-align: center; margin-top: 2rem;'>How It Works</h2>", unsafe_allow_html=True)
    
    # Create a 4-step process
    step1, step2, step3, step4 = st.columns(4)
    
    with step1:
        st.markdown("### Step 1")
        st.markdown("Upload medial and lateral calcaneus STL files")
        
    with step2:
        st.markdown("### Step 2")
        st.markdown("Upload ZIP file with screw STL files")
        
    with step3:
        st.markdown("### Step 3")
        st.markdown("Process and analyze screw placements")
        
    with step4:
        st.markdown("### Step 4")
        st.markdown("Review results and export to Excel")

elif st.session_state.page == 'analysis':
    # Analysis page (file upload and processing)
    st.title("STL Analysis Tool")
    
    # Show patient information if analyzing for a specific patient
    if st.session_state.current_patient_id:
        patient = db.get_patient(st.session_state.current_patient_id)
        if patient:
            st.info(f"Analyzing for Patient: {patient.name or patient.patient_id}")
    
    st.markdown("Upload your files below to begin the analysis process.")
    
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
    
    # Analysis notes
    notes = st.text_area("Analysis Notes (optional)", 
                       placeholder="Enter any notes about this analysis...")
    
    # Process button
    if st.button("Process Files", disabled=not (medial_file and lateral_file and screw_files), type="primary"):
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
                
                # Store results and save to database if there's a patient
                if results:
                    st.session_state.results = results
                    st.session_state.analysis_complete = True
                    
                    # Save to database if we have a patient
                    if st.session_state.current_patient_id and results:
                        try:
                            foot_side = results[0]['foot_side']
                            db.add_analysis(
                                patient_id=st.session_state.current_patient_id,
                                foot_side=foot_side,
                                results=results,
                                notes=notes if notes else None
                            )
                            st.success(f"Analysis saved to patient record.")
                        except Exception as e:
                            st.error(f"Error saving to database: {str(e)}")
                    
                    st.session_state.page = 'dashboard'
                    st.rerun()

elif st.session_state.page == 'dashboard' and st.session_state.analysis_complete:
    # Dashboard page (results and export)
    st.title("Analysis Dashboard")
    
    results = st.session_state.results
    
    if not results:
        st.warning("No analysis results found. Please run an analysis first.")
        if st.button("Go to Analysis Page"):
            st.session_state.page = 'analysis'
            st.rerun()
    else:
        # Show foot side
        foot_side = results[0]['foot_side']
        st.info(f"🦶 Detected Foot Side: {foot_side}")
        
        # Export to Excel button
        st.subheader("Export Results")
        
        # Create pandas DataFrame for export
        data = []
        for i, result in enumerate(results):
            data.append({
                'Screw Number': i+1,
                'Medial Shortest Distance (mm)': f"{result['medial_shortest_positive']:.2f}",
                'Medial Breach (mm)': f"{result['medial_longest_negative']:.2f}" if not np.isnan(result['medial_longest_negative']) else "No Breach",
                'Lateral Shortest Distance (mm)': f"{result['lateral_shortest_positive']:.2f}",
                'Lateral Breach (mm)': f"{result['lateral_longest_negative']:.2f}" if not np.isnan(result['lateral_longest_negative']) else "No Breach",
                'Foot Side': foot_side
            })
        
        df = pd.DataFrame(data)
        
        # Create download link
        excel_link = create_excel_download_link(df, "calcaneus_analysis_results.xlsx", "📊 Download Analysis Results as Excel")
        st.markdown(excel_link, unsafe_allow_html=True)
        
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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Screws Analyzed", len(results))
        with col2:
            st.metric("Medial Breaches", medial_breaches)
        with col3:
            st.metric("Lateral Breaches", lateral_breaches)
        
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
elif st.session_state.page == 'patients':
    # Patient Records page
    st.title("Patient Records")
    
    # Add new patient form
    with st.expander("Add New Patient", expanded=False):
        with st.form("new_patient_form"):
            patient_id = st.text_input("Patient ID", placeholder="Enter unique patient identifier")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Patient Name", placeholder="Optional")
            with col2:
                age = st.number_input("Age", min_value=0, max_value=120, value=0, step=1)
            
            gender = st.selectbox("Gender", ["", "Male", "Female", "Other"])
            
            submit = st.form_submit_button("Add Patient")
            
            if submit and patient_id:
                try:
                    # Check if patient already exists
                    existing = db.get_patient(patient_id)
                    if existing:
                        st.error(f"Patient with ID {patient_id} already exists.")
                    else:
                        # Add new patient
                        db.add_patient(
                            patient_id=patient_id,
                            name=name if name else None,
                            age=age if age > 0 else None,
                            gender=gender if gender else None
                        )
                        st.success(f"Patient {patient_id} added successfully.")
                        
                        # Refresh patient list
                        st.session_state.patients = db.get_all_patients()
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding patient: {str(e)}")
    
    # Display patients
    patients = st.session_state.patients
    if not patients:
        st.info("No patients found in the database. Add your first patient above.")
    else:
        st.subheader(f"Patient List ({len(patients)} patients)")
        
        # Convert patients to DataFrame for display
        patient_data = []
        for p in patients:
            patient_data.append({
                "ID": p.id,
                "Patient ID": p.patient_id,
                "Name": p.name or "-",
                "Age": p.age or "-",
                "Gender": p.gender or "-",
                "Date Added": p.created_at.strftime("%Y-%m-%d") if p.created_at else "-",
                "Actions": p.patient_id
            })
        
        df = pd.DataFrame(patient_data)
        
        # Display table with action buttons
        for i, row in df.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 1.5, 1.5, 0.8, 1.2, 2])
            
            with col1:
                st.text(f"#{row['ID']}")
            with col2:
                st.text(row["Patient ID"])
            with col3:
                st.text(row["Name"])
            with col4:
                st.text(row["Age"])
            with col5:
                st.text(row["Gender"])
            with col6:
                view_col, analyze_col = st.columns(2)
                with view_col:
                    if st.button("View History", key=f"view_{row['Patient ID']}"):
                        st.session_state.current_patient_id = row["Patient ID"]
                        st.session_state.patient_analyses = db.get_analyses_for_patient(row["Patient ID"])
                        st.session_state.page = 'patient_history'
                        st.rerun()
                with analyze_col:
                    if st.button("New Analysis", key=f"analyze_{row['Patient ID']}"):
                        st.session_state.current_patient_id = row["Patient ID"]
                        st.session_state.page = 'analysis'
                        st.rerun()
            
            st.markdown("---")

elif st.session_state.page == 'patient_history':
    # Patient History page
    patient_id = st.session_state.current_patient_id
    patient = db.get_patient(patient_id)
    analyses = st.session_state.patient_analyses
    
    if not patient:
        st.error("Patient not found.")
        st.button("Back to Patient List", on_click=lambda: setattr(st.session_state, 'page', 'patients'))
    else:
        st.title(f"Patient History: {patient.name or patient_id}")
        st.subheader(f"Patient ID: {patient_id}")
        
        # Patient info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Age", patient.age or "Not recorded")
        with col2:
            st.metric("Gender", patient.gender or "Not recorded")
        with col3:
            st.metric("Total Analyses", len(analyses))
        
        # Analysis list
        if not analyses:
            st.info("No analysis history for this patient.")
            if st.button("Perform New Analysis"):
                st.session_state.page = 'analysis'
                st.rerun()
        else:
            st.subheader("Analysis History")
            
            for i, analysis in enumerate(analyses):
                with st.expander(f"Analysis #{i+1} - {analysis.analysis_date.strftime('%Y-%m-%d %H:%M')} - {analysis.foot_side}"):
                    # Get screws for this analysis
                    screws = db.get_screws_for_analysis(analysis.id)
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.metric("Foot Side", analysis.foot_side)
                        st.metric("Number of Screws", len(screws))
                        
                        # Count breaches
                        medial_breaches = sum(1 for s in screws if s.has_medial_breach)
                        lateral_breaches = sum(1 for s in screws if s.has_lateral_breach)
                        
                        if medial_breaches == 0 and lateral_breaches == 0:
                            st.success("No breaches detected")
                        else:
                            st.warning(f"{medial_breaches + lateral_breaches} breaches detected")
                            
                    with col2:
                        if screws:
                            # Create DataFrame for screws
                            screw_data = []
                            for s in screws:
                                screw_data.append({
                                    "Screw #": s.screw_number,
                                    "Medial Dist": f"{s.medial_shortest_positive:.2f} mm" if s.medial_shortest_positive else "-",
                                    "Medial Breach": f"{s.medial_longest_negative:.2f} mm" if s.has_medial_breach else "No",
                                    "Lateral Dist": f"{s.lateral_shortest_positive:.2f} mm" if s.lateral_shortest_positive else "-",
                                    "Lateral Breach": f"{s.lateral_longest_negative:.2f} mm" if s.has_lateral_breach else "No"
                                })
                            
                            # Display as table
                            screw_df = pd.DataFrame(screw_data)
                            st.table(screw_df)
                    
                    # Notes
                    if analysis.notes:
                        st.text("Notes:")
                        st.text(analysis.notes)
                    
                    # Export to Excel
                    if screws:
                        excel_link = create_excel_download_link(
                            screw_df,
                            f"patient_{patient_id}_analysis_{analysis.id}.xlsx",
                            "📊 Download as Excel"
                        )
                        st.markdown(excel_link, unsafe_allow_html=True)
            
            # New analysis button
            if st.button("Perform New Analysis"):
                st.session_state.page = 'analysis'
                st.rerun()

else:
    # Default to landing page if no valid state
    st.session_state.page = 'landing'
    st.rerun()
