import io
import zipfile
import numpy as np
import trimesh
from typing import Tuple, List, Dict, Optional, Union

def validate_stl_file(file_obj) -> bool:
    """
    Validate if the uploaded file is a valid STL file.
    
    Args:
        file_obj: The uploaded file object
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Try to load the mesh with trimesh to validate it
        buffer = io.BytesIO(file_obj.getvalue())
        mesh = trimesh.load(buffer, file_type='stl')
        
        # Verify the mesh has vertices
        if len(mesh.vertices) < 3:
            return False
            
        # Reset file pointer for future use
        file_obj.seek(0)
        return True
    except Exception:
        return False

def validate_zip_file(file_obj) -> Tuple[bool, str, List[bytes]]:
    """
    Validate if the uploaded ZIP file contains valid STL files.
    
    Args:
        file_obj: The uploaded ZIP file object
        
    Returns:
        Tuple[bool, str, List[bytes]]: 
            - success status
            - error message if any
            - list of valid STL file contents
    """
    try:
        valid_files = []
        
        # Open the zip file
        with zipfile.ZipFile(io.BytesIO(file_obj.getvalue()), 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            # Check if we have any STL files
            stl_files = [f for f in file_list if f.lower().endswith('.stl')]
            
            if not stl_files:
                return False, "No STL files found in the ZIP archive.", []
                
            if len(stl_files) > 48:
                return False, f"Too many STL files in ZIP archive ({len(stl_files)}/48 max).", []
                
            # Extract and validate each STL file
            for stl_file in stl_files:
                with zip_ref.open(stl_file) as f:
                    stl_data = f.read()
                    
                    # Validate STL content
                    try:
                        buffer = io.BytesIO(stl_data)
                        mesh = trimesh.load(buffer, file_type='stl')
                        
                        if len(mesh.vertices) >= 3:
                            valid_files.append(stl_data)
                    except Exception:
                        # Skip invalid files
                        continue
                        
            if not valid_files:
                return False, "No valid STL files found in the ZIP archive.", []
                
            return True, "", valid_files
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file format.", []
    except Exception as e:
        return False, f"Error processing ZIP file: {str(e)}", []
