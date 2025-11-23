"""
UI Element Detector using Computer Vision

This module detects UI elements (buttons, windows, text fields) using 
computer vision techniques like contour detection, edge detection, and OCR.
"""

import cv2
import numpy as np
import logging
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
import pytesseract

logger = logging.getLogger(__name__)


@dataclass
class UIElement:
    """Detected UI element."""
    id: str
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    class_name: str
    confidence: float
    text: str = ""
    affordances: List[str] = None
    style_hints: Dict[str, Any] = None
    embedding: Any = None  # Add embedding to match vlm_detector schema
    
    def __post_init__(self):
        if self.affordances is None:
            self.affordances = ['clickable']
        if self.style_hints is None:
            self.style_hints = {}


class CVUIDetector:
    """Computer Vision-based UI element detector."""
    
    def __init__(self):
        """Initialize the CV UI detector."""
        self.min_button_area = 100  # minimum area for a button
        self.max_button_area = 50000  # maximum area for a button
        logger.info("CV UI Detector initialized")
    
    def detect(self, image: np.ndarray) -> List[UIElement]:
        """
        Detect UI elements using computer vision techniques.
        
        Args:
            image: Input image (BGR format from cv2)
            
        Returns:
            List of detected UI elements
        """
        elements = []
        
        # 1. Detect rectangular UI elements (buttons, text fields, windows)
        rect_elements = self._detect_rectangles(image)
        elements.extend(rect_elements)
        
        # 2. Detect text regions using OCR
        text_elements = self._detect_text_regions(image)
        elements.extend(text_elements)
        
        # 3. Detect circular buttons
        circle_elements = self._detect_circles(image)
        elements.extend(circle_elements)
        
        logger.info(f"CV detector found {len(elements)} UI elements")
        return elements
    
    def _detect_rectangles(self, image: np.ndarray) -> List[UIElement]:
        """Detect rectangular UI elements like buttons and windows."""
        elements = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Filter by area
            if area < self.min_button_area or area > self.max_button_area:
                continue
            
            # Approximate the contour to a polygon
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            
            # Look for rectangular shapes (4 vertices)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate aspect ratio
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Determine element type based on aspect ratio
                if 0.8 < aspect_ratio < 1.2:
                    class_name = "button"  # Square-ish
                elif aspect_ratio > 2:
                    class_name = "textfield"  # Wide
                else:
                    class_name = "button"
                
                element = UIElement(
                    id=f"rect_{i}",
                    bbox=(x, y, x+w, y+h),
                    class_name=class_name,
                    confidence=0.7,
                    affordances=['clickable', 'focusable']
                )
                elements.append(element)
        
        return elements
    
    def _detect_text_regions(self, image: np.ndarray) -> List[UIElement]:
        """Detect text regions using OCR."""
        elements = []
        
        try:
            # Use pytesseract to get bounding boxes
            data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT
            )
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if not text:
                    continue
                
                conf = int(data['conf'][i])
                if conf < 30:  # Low confidence
                    continue
                
                x, y, w, h = (
                    data['left'][i], data['top'][i], 
                    data['width'][i], data['height'][i]
                )
                
                element = UIElement(
                    id=f"text_{i}",
                    bbox=(x, y, x+w, y+h),
                    class_name="text_label",
                    confidence=conf / 100.0,
                    text=text,
                    affordances=['readable']
                )
                elements.append(element)
                
        except Exception as e:
            logger.warning(f"OCR text detection failed: {e}")
        
        return elements
    
    def _detect_circles(self, image: np.ndarray) -> List[UIElement]:
        """Detect circular buttons using Hough Circle Transform."""
        elements = []
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        gray = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
            param1=50, param2=30, minRadius=10, maxRadius=100
        )
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for i, (x, y, r) in enumerate(circles):
                element = UIElement(
                    id=f"circle_{i}",
                    bbox=(x-r, y-r, x+r, y+r),
                    class_name="button",
                    confidence=0.6,
                    affordances=['clickable']
                )
                elements.append(element)
        
        return elements


def create_cv_detector() -> CVUIDetector:
    """Factory function to create a CV UI detector."""
    return CVUIDetector()
