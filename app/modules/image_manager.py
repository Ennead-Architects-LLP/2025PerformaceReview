"""
Image Manager for Employee Profile Images

Handles copying, matching, and managing employee profile images with fuzzy name matching.
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from fuzzywuzzy import fuzz, process
import json
from .config import Config


class ImageManager:
    """Manages employee profile images with smart matching."""
    
    def __init__(self, source_images_dir: str = None, target_images_dir: str = None):
        """
        Initialize the image manager.
        
        Args:
            source_images_dir: Directory containing source employee images
            target_images_dir: Directory to copy images to (relative to project root)
        """
        if source_images_dir is None:
            source_images_dir = Config.get_image_source_path()
        if target_images_dir is None:
            target_images_dir = Config.get_image_target_path()
            
        self.source_dir = Path(source_images_dir)
        self.target_dir = Path(target_images_dir)
        self.image_mappings: Dict[str, str] = {}
        self.available_images: List[str] = []
        
    def setup_directories(self) -> bool:
        """
        Create target directory structure if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created/verified directory: {self.target_dir}")
            return True
        except Exception as e:
            print(f"❌ Error creating directory {self.target_dir}: {e}")
            return False
    
    def scan_source_images(self) -> List[str]:
        """
        Scan the source directory for available image files.
        
        Returns:
            List of image filenames found
        """
        if not self.source_dir.exists():
            print(f"⚠️  Source image directory not found: {self.source_dir}")
            return []
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        images = []
        
        for file_path in self.source_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                images.append(file_path.name)
        
        self.available_images = images
        print(f"📸 Found {len(images)} images in source directory")
        return images
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize a name for better matching.
        
        Args:
            name: Employee name to normalize
            
        Returns:
            Normalized name
        """
        # Remove common prefixes/suffixes and normalize
        name = re.sub(r'^(mr|ms|mrs|dr)\.?\s+', '', name.lower())
        name = re.sub(r'\s+(jr|sr|iii|ii|iv)\.?$', '', name)
        name = re.sub(r'[^\w\s]', '', name)  # Remove punctuation
        name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace
        return name
    
    def extract_name_from_filename(self, filename: str) -> str:
        """
        Extract employee name from image filename.
        
        Args:
            filename: Image filename
            
        Returns:
            Extracted name
        """
        # Remove file extension
        name = Path(filename).stem
        
        # Remove common suffixes like _profile, _pic, _photo, etc.
        name = re.sub(r'_profile$|_pic$|_photo$|_img$', '', name, flags=re.IGNORECASE)
        
        # Common patterns: "John_Doe.jpg", "John-Doe.jpg", "JohnDoe.jpg", "John Doe.jpg"
        name = re.sub(r'[_-]', ' ', name)
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)  # Add space before capitals
        
        return self.normalize_name(name)
    
    def find_best_image_match(self, employee_name: str, threshold: int = 70) -> Tuple[Optional[str], Optional[float]]:
        """
        Find the best matching image for an employee using fuzzy matching.
        
        Args:
            employee_name: Name of the employee
            threshold: Minimum similarity score (0-100)
            
        Returns:
            Tuple of (best matching image filename or None, confidence score or None)
        """
        if not self.available_images:
            return None, None
        
        normalized_employee_name = self.normalize_name(employee_name)
        
        # Create list of (filename, normalized_name) tuples
        image_candidates = []
        for img_file in self.available_images:
            img_name = self.extract_name_from_filename(img_file)
            image_candidates.append((img_file, img_name))
        
        # Use fuzzy matching to find best match
        matches = process.extract(
            normalized_employee_name, 
            [candidate[1] for candidate in image_candidates], 
            limit=3, 
            scorer=fuzz.ratio
        )
        
        if matches and matches[0][1] >= threshold:
            best_match_name = matches[0][0]
            # Find the original filename for the best match
            for img_file, img_name in image_candidates:
                if img_name == best_match_name:
                    confidence = matches[0][1]
                    print(f"🎯 Matched '{employee_name}' to '{img_file}' (confidence: {confidence}%)")
                    return img_file, confidence
        
        print(f"⚠️  No good match found for '{employee_name}' (best match: {matches[0][1] if matches else 0}%)")
        return None, None
    
    def copy_employee_images(self, employees: List[Any]) -> Dict[str, Dict[str, Any]]:
        """
        Copy and match employee images, plus copy all available images to asset library.
        
        Args:
            employees: List of Employee objects or employee data dictionaries
            
        Returns:
            Dictionary mapping employee names to image info dictionaries
        """
        if not self.setup_directories():
            return {}
        
        available_images = self.scan_source_images()
        if not available_images:
            print("⚠️  No images available to copy")
            return {}
        
        # First, copy ALL images to the asset library
        print(f"📸 Copying all {len(available_images)} images to asset library...")
        all_images_copied = 0
        for image_file in available_images:
            source_path = self.source_dir / image_file
            target_path = self.target_dir / image_file
            
            try:
                # Only copy if not already exists
                if not target_path.exists():
                    shutil.copy2(source_path, target_path)
                    all_images_copied += 1
                    print(f"✅ Copied asset: {image_file}")
                else:
                    print(f"⏭️  Asset already exists: {image_file}")
            except Exception as e:
                print(f"❌ Error copying asset {image_file}: {e}")
        
        print(f"📦 Asset Library Summary: {all_images_copied} new images copied")
        
        # Now handle employee-specific matching
        copied_count = 0
        matched_count = 0
        
        for employee in employees:
            # Handle both Employee objects and dictionaries
            employee_name = None
            
            if hasattr(employee, 'get'):
                # Dictionary object
                employee_name = employee.get('name', '')
            else:
                # Employee object - look for name attributes
                for attr_name in dir(employee):
                    if not attr_name.startswith('_') and 'name' in attr_name.lower():
                        attr_value = getattr(employee, attr_name)
                        if attr_value and not callable(attr_value):
                            employee_name = str(attr_value)
                            break
            
            if not employee_name:
                continue
            
            # Find best matching image with confidence score
            best_match, confidence = self.find_best_image_match(employee_name)
            
            image_info = {
                'filename': best_match,
                'confidence': confidence,
                'copied': False,
                'error': None
            }
            
            if best_match:
                # Image is already copied to asset library, just mark as matched
                image_info['copied'] = True
                copied_count += 1
                matched_count += 1
                print(f"🎯 Matched {employee_name}: {best_match} (confidence: {confidence}%)")
            else:
                print(f"⚠️  No image match found for {employee_name}")
            
            self.image_mappings[employee_name] = image_info
        
        print(f"\n📊 Employee Image Matching Summary:")
        print(f"   Total employees: {len(employees)}")
        print(f"   Images matched: {matched_count}")
        print(f"   Match rate: {matched_count/len(employees)*100:.1f}%")
        print(f"   Total images in asset library: {len(available_images)}")
        
        return self.image_mappings
    
    def save_image_mappings(self, output_file: str = None) -> bool:
        """
        Save image mappings to a JSON file.
        
        Args:
            output_file: Path to save mappings file
            
        Returns:
            True if successful, False otherwise
        """
        if output_file is None:
            output_file = Config.get_image_mappings_path()
            
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.image_mappings, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved image mappings to {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving image mappings: {e}")
            return False
    
    def get_image_path(self, employee_name: str) -> Optional[str]:
        """
        Get the image path for an employee.
        
        Args:
            employee_name: Name of the employee
            
        Returns:
            Relative path to image or None if not found
        """
        if employee_name in self.image_mappings and self.image_mappings[employee_name]:
            image_info = self.image_mappings[employee_name]
            if image_info.get('filename'):
                return f"{Config.IMAGE_TARGET_DIR}/{image_info['filename']}"
        return None
    
    def get_all_asset_images(self) -> List[str]:
        """
        Get list of all images in the asset library.
        
        Returns:
            List of image filenames in the asset library
        """
        if not self.target_dir.exists():
            return []
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        images = []
        
        for file_path in self.target_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                images.append(file_path.name)
        
        return sorted(images)
    
    def get_asset_library_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the asset library.
        
        Returns:
            Dictionary with asset library statistics
        """
        all_images = self.get_all_asset_images()
        matched_images = [info['filename'] for info in self.image_mappings.values() 
                         if info.get('filename')]
        
        return {
            'total_images': len(all_images),
            'matched_images': len(matched_images),
            'unmatched_images': len(all_images) - len(matched_images),
            'all_image_files': all_images
        }


def copy_employee_images_from_pipeline(employee_data: List[Dict], 
                                     source_dir: str = None,
                                     target_dir: str = None) -> Dict[str, str]:
    """
    Convenience function to copy employee images as part of the pipeline.
    
    Args:
        employee_data: List of employee data dictionaries
        source_dir: Source images directory (uses config default if None)
        target_dir: Target images directory (uses config default if None)
        
    Returns:
        Dictionary mapping employee names to image filenames
    """
    if source_dir is None:
        source_dir = Config.get_image_source_path()
    if target_dir is None:
        target_dir = Config.IMAGE_TARGET_DIR
    
    manager = ImageManager(source_dir, target_dir)
    mappings = manager.copy_employee_images(employee_data)
    manager.save_image_mappings(Config.get_image_mappings_path())
    return mappings


if __name__ == "__main__":
    # Test the image manager
    manager = ImageManager()
    
    # Test with sample employee data
    test_employees = [
        {"name": "Brett Fabrikant"},
        {"name": "Xinya Li"},
        {"name": "Leah Li"},
        {"name": "Vivian Zhan"},
        {"name": "Matthew Hitscherich"},
        {"name": "Clayton Kaul"},
        {"name": "Regina Jiang"},
        {"name": "R. Kevin Hamlett"}
    ]
    
    mappings = manager.copy_employee_images(test_employees)
    manager.save_image_mappings()
