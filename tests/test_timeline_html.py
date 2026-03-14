#!/usr/bin/env python3
"""
Test that the frame timeline HTML is valid and contains required elements.
"""

import sys
from pathlib import Path

def test_timeline_html_exists():
    """Test that the timeline HTML file exists."""
    html_path = Path(__file__).parent.parent / "deepseek_frame_timeline.html"
    assert html_path.exists(), "deepseek_frame_timeline.html not found"


def test_timeline_html_has_required_elements():
    """Test that the HTML contains required elements."""
    html_path = Path(__file__).parent.parent / "deepseek_frame_timeline.html"
    
    with open(html_path) as f:
        content = f.read()
    
    # Check for essential HTML structure
    assert "<!DOCTYPE html>" in content
    assert "<html" in content
    assert "</html>" in content
    
    # Check for title
    assert "DeepSeek Frame Timeline" in content
    
    # Check for Chart.js
    assert "chart.js" in content.lower() or "Chart" in content
    
    # Check for file input
    assert 'type="file"' in content
    assert 'accept=".json"' in content
    
    # Check for example load button
    assert "Load Example" in content or "loadExample" in content
    
    # Check for session info panel
    assert "session" in content.lower()
    assert "turn" in content.lower()
    assert "frame" in content.lower()
    
    # Check for chart containers
    assert "chart" in content.lower()
    assert "canvas" in content.lower()


def test_timeline_html_javascript_present():
    """Test that JavaScript code is present."""
    html_path = Path(__file__).parent.parent / "deepseek_frame_timeline.html"
    
    with open(html_path) as f:
        content = f.read()
    
    # Check for JavaScript
    assert "<script>" in content or "<script " in content
    assert "function" in content
    
    # Check for session loading functions
    assert "loadSession" in content or "load_session" in content
    
    # Check for chart generation
    assert "Chart" in content


def test_timeline_html_css_present():
    """Test that CSS styling is present."""
    html_path = Path(__file__).parent.parent / "deepseek_frame_timeline.html"
    
    with open(html_path) as f:
        content = f.read()
    
    # Check for CSS
    assert "<style>" in content
    assert "background" in content
    assert "color" in content
    
    # Check for responsive design
    assert "container" in content.lower()


def test_timeline_html_file_size_reasonable():
    """Test that the HTML file is a reasonable size."""
    html_path = Path(__file__).parent.parent / "deepseek_frame_timeline.html"
    
    file_size = html_path.stat().st_size
    
    # Should be between 10KB and 100KB
    assert 10_000 < file_size < 100_000, f"HTML file size {file_size} is unusual"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
