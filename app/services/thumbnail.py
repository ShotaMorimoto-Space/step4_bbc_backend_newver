from typing import BinaryIO, Tuple
import tempfile
import subprocess
import os
from pathlib import Path
import logging
from io import BytesIO
from PIL import Image

# メインのロガーを使用
from app.utils.logger import logger

class ThumbnailService:
    """Video thumbnail generation service"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir())
    
    def generate_thumbnail(self, video_file: BinaryIO, video_filename: str) -> BytesIO:
        """
        Generate thumbnail from video file
        
        Args:
            video_file: Video file binary stream
            video_filename: Original video filename
            
        Returns:
            BytesIO: Thumbnail image as JPEG
        """
        try:
            # Create temporary files
            temp_video_path = None
            temp_thumbnail_path = None
            
            try:
                # Save video to temporary file
                video_extension = Path(video_filename).suffix.lower()
                temp_video_path = self.temp_dir / f"temp_video_{os.getpid()}{video_extension}"
                
                logger.info(f"Saving video to temporary file: {temp_video_path}")
                with open(temp_video_path, "wb") as temp_video:
                    video_file.seek(0)  # Reset file pointer
                    video_content = video_file.read()
                    temp_video.write(video_content)
                    logger.info(f"Video file saved, size: {len(video_content)} bytes")
                
                # Generate thumbnail path
                temp_thumbnail_path = self.temp_dir / f"temp_thumbnail_{os.getpid()}.jpg"
                logger.info(f"Attempting to generate thumbnail at: {temp_thumbnail_path}")
                
                # Use ffmpeg to generate thumbnail at 2 seconds
                success = self._extract_thumbnail_with_ffmpeg(
                    str(temp_video_path),
                    str(temp_thumbnail_path),
                    timestamp="00:00:02"
                )
                
                # If thumbnail generation failed, try at 0 seconds
                if not success or not temp_thumbnail_path.exists():
                    logger.info("Retrying thumbnail generation at 0 seconds")
                    success = self._extract_thumbnail_with_ffmpeg(
                        str(temp_video_path),
                        str(temp_thumbnail_path),
                        timestamp="00:00:00"
                    )
                
                # If still failed, try without seeking
                if not success or not temp_thumbnail_path.exists():
                    logger.info("Retrying thumbnail generation without seeking")
                    success = self._extract_thumbnail_with_ffmpeg(
                        str(temp_video_path),
                        str(temp_thumbnail_path),
                        timestamp=None
                    )
                
                # If still failed, create a default thumbnail
                if not success or not temp_thumbnail_path.exists():
                    logger.warning(f"Failed to extract thumbnail from {video_filename}, creating default")
                    return self._create_default_thumbnail()
                
                # Read and return thumbnail
                with open(temp_thumbnail_path, "rb") as thumb_file:
                    thumbnail_data = BytesIO(thumb_file.read())
                    thumbnail_data.seek(0)
                    return thumbnail_data
                
            finally:
                # Clean up temporary files
                if temp_video_path and temp_video_path.exists():
                    try:
                        temp_video_path.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete temp video file: {e}")
                
                if temp_thumbnail_path and temp_thumbnail_path.exists():
                    try:
                        temp_thumbnail_path.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete temp thumbnail file: {e}")
                        
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return self._create_default_thumbnail()
    
    def _extract_thumbnail_with_ffmpeg(self, video_path: str, output_path: str, timestamp: str = None) -> bool:
        """
        Extract thumbnail using ffmpeg
        
        Args:
            video_path: Path to input video file
            output_path: Path for output thumbnail
            timestamp: Timestamp to extract (e.g., "00:00:02")
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                "-y"  # Overwrite output file
            ]
            
            if timestamp:
                cmd.extend(["-ss", timestamp])
            
            cmd.append(output_path)
            
            logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Thumbnail generated successfully: {output_path}")
                return True
            else:
                logger.warning(f"ffmpeg failed with return code {result.returncode}")
                logger.warning(f"ffmpeg stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg command timed out")
            return False
        except Exception as e:
            logger.error(f"Error running ffmpeg: {e}")
            return False
    
    def _create_default_thumbnail(self) -> BytesIO:
        """Create a default thumbnail image"""
        try:
            # Create a simple 320x240 black image with white text
            img = Image.new('RGB', (320, 240), color='black')
            
            # Convert to JPEG and return as BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            logger.info("Default thumbnail created")
            return output
            
        except Exception as e:
            logger.error(f"Error creating default thumbnail: {e}")
            # Return empty BytesIO as fallback
            return BytesIO()

# Global thumbnail service instance
thumbnail_service = ThumbnailService()