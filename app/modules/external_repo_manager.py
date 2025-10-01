"""
External Repository Manager

Handles copying images from external EmployeeData repository to local assets directory.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .config import Config
from .utils import log_info, log_error


class ExternalRepoManager:
    """Manages copying images from external EmployeeData repository."""
    
    def __init__(self, external_repo_path: str = None, external_image_dir: str = None):
        """
        Initialize the external repository manager.
        
        Args:
            external_repo_path: Path to the external EmployeeData repository
            external_image_dir: Subdirectory within the repo containing images
        """
        self.external_repo_path = external_repo_path or Config.get_external_employee_data_repo_path()
        self.external_image_dir = external_image_dir or Config.get_external_image_source_path()
        self.local_target_dir = Config.get_image_target_path()
        
    def is_external_repo_available(self) -> bool:
        """
        Check if the external repository is available and accessible.
        
        Returns:
            True if external repo is available, False otherwise
        """
        if not self.external_repo_path:
            log_info("⚠️  No external EmployeeData repository configured")
            return False
            
        if not os.path.exists(self.external_repo_path):
            log_error(f"❌ External repository not found: {self.external_repo_path}")
            return False
            
        if not os.path.exists(self.external_image_dir):
            log_error(f"❌ External image directory not found: {self.external_image_dir}")
            return False
            
        return True
    
    def scan_external_images(self) -> List[str]:
        """
        Scan the external repository for available images.
        
        Returns:
            List of image filenames found in external repo
        """
        if not self.is_external_repo_available():
            return []
            
        try:
            image_files = []
            for file in os.listdir(self.external_image_dir):
                if Config.is_supported_image_file(file):
                    image_files.append(file)
            
            log_info(f"[INFO] Found {len(image_files)} images in external repository: {self.external_image_dir}")
            return image_files
            
        except Exception as e:
            log_error(f"❌ Error scanning external images: {e}")
            return []
    
    def copy_images_from_external_repo(self, force_copy: bool = False) -> Dict[str, bool]:
        """
        Copy all images from external EmployeeData repository to local assets/images.
        
        Args:
            force_copy: If True, overwrite existing images. If False, skip existing images.
            
        Returns:
            Dictionary mapping image filenames to copy success status
        """
        if not self.is_external_repo_available():
            return {}
            
        # Ensure local target directory exists
        try:
            os.makedirs(self.local_target_dir, exist_ok=True)
            log_info(f"✅ Created/verified local directory: {self.local_target_dir}")
        except Exception as e:
            log_error(f"❌ Error creating local directory: {e}")
            return {}
        
        # Scan external images
        external_images = self.scan_external_images()
        if not external_images:
            log_info("⚠️  No images found in external repository")
            return {}
        
        # Copy images
        copy_results = {}
        copied_count = 0
        skipped_count = 0
        
        log_info(f"[INFO] Copying images from external repository...")
        log_info(f"   Source: {self.external_image_dir}")
        log_info(f"   Target: {self.local_target_dir}")
        
        for image_file in external_images:
            source_path = os.path.join(self.external_image_dir, image_file)
            target_path = os.path.join(self.local_target_dir, image_file)
            
            try:
                # Check if target already exists
                if os.path.exists(target_path) and not force_copy:
                    log_info(f"⏭️  Image already exists: {image_file}")
                    copy_results[image_file] = True
                    skipped_count += 1
                    continue
                
                # Copy the image
                shutil.copy2(source_path, target_path)
                log_info(f"✅ Copied: {image_file}")
                copy_results[image_file] = True
                copied_count += 1
                
            except Exception as e:
                log_error(f"❌ Error copying {image_file}: {e}")
                copy_results[image_file] = False
        
        # Summary
        log_info(f"📦 External Repository Copy Summary:")
        log_info(f"   Total images found: {len(external_images)}")
        log_info(f"   Successfully copied: {copied_count}")
        log_info(f"   Already existed: {skipped_count}")
        log_info(f"   Failed: {len(external_images) - copied_count - skipped_count}")
        
        return copy_results
    
    def get_external_repo_stats(self) -> Dict[str, any]:
        """
        Get statistics about the external repository.
        
        Returns:
            Dictionary with external repo statistics
        """
        if not self.is_external_repo_available():
            return {
                'available': False,
                'external_repo_path': self.external_repo_path,
                'external_image_dir': self.external_image_dir,
                'total_images': 0
            }
        
        external_images = self.scan_external_images()
        
        return {
            'available': True,
            'external_repo_path': self.external_repo_path,
            'external_image_dir': self.external_image_dir,
            'total_images': len(external_images),
            'image_files': external_images
        }


def copy_images_from_employee_data_repo(external_repo_path: str = None, 
                                       force_copy: bool = False) -> bool:
    """
    Convenience function to copy images from EmployeeData repository.
    
    Args:
        external_repo_path: Path to EmployeeData repository (uses config if None)
        force_copy: Whether to overwrite existing images
        
    Returns:
        True if copying was successful, False otherwise
    """
    try:
        manager = ExternalRepoManager(external_repo_path)
        
        if not manager.is_external_repo_available():
            log_error("❌ External EmployeeData repository not available")
            return False
        
        log_info("🔄 Starting image copy from EmployeeData repository...")
        copy_results = manager.copy_images_from_external_repo(force_copy)
        
        if not copy_results:
            log_error("❌ No images were copied from external repository")
            return False
        
        successful_copies = sum(1 for success in copy_results.values() if success)
        total_images = len(copy_results)
        
        if successful_copies == total_images:
            log_info("✅ Successfully copied all images from EmployeeData repository")
            return True
        else:
            log_error(f"⚠️  Partially successful: {successful_copies}/{total_images} images copied")
            return False
            
    except Exception as e:
        log_error(f"❌ Error copying images from EmployeeData repository: {e}")
        return False
