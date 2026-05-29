"""
Unit tests for Silent Deployment feature.

Tests verify silent deployment detection functionality including:
- Window visibility detection
- Hidden process detection
- Startup type classification
- Process information collection
- Error handling and graceful failures
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
import psutil

# Import the module to test
from silent_deployment import (
    run,
    _detect_silent_deployment,
    _detect_no_window,
    _detect_hidden_process,
    _detect_startup_type,
    get_detailed_process_info
)


class TestSilentDeploymentRun:
    """Tests for the main run() function."""
    
    def test_run_returns_dict(self):
        """Test that run() returns a dictionary."""
        result = run(None)
        assert isinstance(result, dict)
    
    def test_run_with_callback(self):
        """Test that run() calls the send_event callback."""
        callback = Mock()
        result = run(callback)
        
        # Verify callback was called
        callback.assert_called_once()
        
        # Verify callback received correct event structure
        call_args = callback.call_args[0][0]
        assert 'feature' in call_args
        assert call_args['feature'] == 'silent_deployment'
        assert 'status' in call_args
        assert 'data' in call_args
    
    def test_run_without_callback(self):
        """Test that run() works without a callback."""
        result = run(None)
        assert result is not None
        assert isinstance(result, dict)
    
    def test_run_has_required_fields(self):
        """Test that run() returns all required fields."""
        result = run(None)
        
        required_fields = [
            'no_window',
            'hidden',
            'startup_type',
            'process_id',
            'process_name',
            'parent_process',
            'is_silent'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
    
    def test_run_error_handling(self):
        """Test that run() handles errors gracefully."""
        callback = Mock()
        
        with patch('silent_deployment._detect_silent_deployment') as mock_detect:
            mock_detect.side_effect = Exception("Test error")
            result = run(callback)
            
            # Should not crash
            assert result is not None
            assert result['process_id'] == os.getpid()
            
            # Callback should receive error status
            callback.assert_called_once()
            call_args = callback.call_args[0][0]
            assert call_args['status'] == 'error'


class TestDetectNoWindow:
    """Tests for window visibility detection."""
    
    def test_detect_no_window_returns_bool(self):
        """Test that _detect_no_window returns a boolean."""
        result = _detect_no_window()
        assert isinstance(result, bool)
    
    def test_detect_no_window_no_crash(self):
        """Test that _detect_no_window handles errors gracefully."""
        # Should not raise exception even in edge cases
        result = _detect_no_window()
        assert isinstance(result, bool)
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-only test")
    def test_detect_no_window_windows(self):
        """Test window detection on Windows."""
        result = _detect_no_window()
        assert isinstance(result, bool)


class TestDetectHiddenProcess:
    """Tests for hidden process detection."""
    
    def test_detect_hidden_process_returns_bool(self):
        """Test that _detect_hidden_process returns a boolean."""
        result = _detect_hidden_process()
        assert isinstance(result, bool)
    
    def test_detect_hidden_process_no_crash(self):
        """Test that _detect_hidden_process handles errors gracefully."""
        # Should not raise exception
        result = _detect_hidden_process()
        assert isinstance(result, bool)
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-only test")
    def test_detect_hidden_process_windows(self):
        """Test hidden process detection on Windows."""
        result = _detect_hidden_process()
        assert isinstance(result, bool)


class TestDetectStartupType:
    """Tests for startup type detection."""
    
    def test_detect_startup_type_returns_string(self):
        """Test that _detect_startup_type returns a string."""
        result = _detect_startup_type()
        assert isinstance(result, str)
    
    def test_detect_startup_type_valid_values(self):
        """Test that startup type is a valid value."""
        result = _detect_startup_type()
        valid_types = ['user', 'system', 'background', 'unknown']
        assert result in valid_types, f"Invalid startup type: {result}"
    
    def test_detect_startup_type_no_crash(self):
        """Test that _detect_startup_type handles errors gracefully."""
        # Should not raise exception
        result = _detect_startup_type()
        assert isinstance(result, str)


class TestDetectSilentDeployment:
    """Tests for main detection function."""
    
    def test_detect_silent_deployment_returns_dict(self):
        """Test that _detect_silent_deployment returns a dictionary."""
        result = _detect_silent_deployment()
        assert isinstance(result, dict)
    
    def test_detect_silent_deployment_required_keys(self):
        """Test that detection returns all required keys."""
        result = _detect_silent_deployment()
        
        required_keys = [
            'no_window',
            'hidden',
            'startup_type',
            'process_id',
            'process_name',
            'parent_process',
            'is_silent'
        ]
        
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
    
    def test_detect_silent_deployment_types(self):
        """Test that detection returns correct data types."""
        result = _detect_silent_deployment()
        
        assert isinstance(result['no_window'], bool)
        assert isinstance(result['hidden'], bool)
        assert isinstance(result['startup_type'], str)
        assert isinstance(result['process_id'], int)
        assert isinstance(result['process_name'], str)
        assert isinstance(result['parent_process'], str)
        assert isinstance(result['is_silent'], bool)
    
    def test_detect_silent_deployment_valid_pid(self):
        """Test that process_id is the current process."""
        result = _detect_silent_deployment()
        assert result['process_id'] == os.getpid()
    
    def test_is_silent_logic(self):
        """Test that is_silent flag reflects the conditions."""
        result = _detect_silent_deployment()
        
        expected_silent = (
            result['no_window'] or 
            result['hidden'] or 
            result['startup_type'] in ['system', 'background']
        )
        
        assert result['is_silent'] == expected_silent


class TestGetDetailedProcessInfo:
    """Tests for detailed process information function."""
    
    def test_get_detailed_process_info_returns_dict(self):
        """Test that get_detailed_process_info returns a dictionary."""
        result = get_detailed_process_info()
        assert isinstance(result, dict)
    
    def test_get_detailed_process_info_has_pid(self):
        """Test that detailed info includes process ID."""
        result = get_detailed_process_info()
        assert 'pid' in result
        assert result['pid'] == os.getpid()
    
    def test_get_detailed_process_info_has_name(self):
        """Test that detailed info includes process name."""
        result = get_detailed_process_info()
        assert 'name' in result
        assert isinstance(result['name'], str)
    
    def test_get_detailed_process_info_error_handling(self):
        """Test that function handles errors gracefully."""
        with patch('psutil.Process') as mock_process:
            mock_process.side_effect = Exception("Test error")
            result = get_detailed_process_info()
            
            # Should return dict with error
            assert isinstance(result, dict)
            assert 'error' in result


class TestIntegration:
    """Integration tests for the entire feature."""
    
    def test_full_workflow(self):
        """Test complete workflow from run() to result."""
        events = []
        
        def capture_event(event):
            events.append(event)
        
        result = run(capture_event)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'no_window' in result
        assert 'hidden' in result
        assert 'startup_type' in result
        assert 'process_id' in result
        
        # Verify callback was called
        assert len(events) == 1
        event = events[0]
        assert event['feature'] == 'silent_deployment'
        assert event['status'] == 'success'
        assert event['data'] == result
    
    def test_multiple_runs_consistency(self):
        """Test that multiple runs return consistent results."""
        result1 = run(None)
        result2 = run(None)
        
        # Same process should have same characteristics
        assert result1['process_id'] == result2['process_id']
        assert result1['process_name'] == result2['process_name']
        assert result1['startup_type'] == result2['startup_type']
    
    def test_no_exceptions_raised(self):
        """Test that no exceptions are raised during normal operation."""
        try:
            result = run(None)
            detailed = get_detailed_process_info()
            assert result is not None
            assert detailed is not None
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {str(e)}")


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_callback_exception_handling(self):
        """Test that exceptions in callback don't crash the run() function."""
        def bad_callback(event):
            raise ValueError("Callback error")
        
        # Should not raise exception
        result = run(bad_callback)
        assert result is not None
    
    def test_psutil_nosuchprocess(self):
        """Test handling when process is not found."""
        with patch('psutil.Process') as mock_process:
            mock_instance = MagicMock()
            mock_process.return_value = mock_instance
            mock_instance.parent.side_effect = psutil.NoSuchProcess(9999)
            
            # Should handle gracefully
            result = _detect_silent_deployment()
            assert result is not None
    
    def test_missing_parent_process(self):
        """Test handling when parent process is not available."""
        with patch('psutil.Process') as mock_process:
            mock_instance = MagicMock()
            mock_process.return_value = mock_instance
            mock_instance.parent.side_effect = AttributeError("No parent")
            
            # Should handle gracefully
            result = _detect_silent_deployment()
            assert 'parent_process' in result


class TestDataValidation:
    """Tests to validate data correctness."""
    
    def test_process_id_is_positive_integer(self):
        """Test that process ID is a positive integer."""
        result = run(None)
        assert result['process_id'] > 0
        assert isinstance(result['process_id'], int)
    
    def test_process_name_not_empty(self):
        """Test that process name is not empty."""
        result = run(None)
        assert len(result['process_name']) > 0
    
    def test_parent_process_not_none(self):
        """Test that parent process name is provided."""
        result = run(None)
        assert result['parent_process'] is not None
        assert isinstance(result['parent_process'], str)
    
    def test_startup_type_valid(self):
        """Test that startup type is valid."""
        result = run(None)
        valid_types = ['user', 'system', 'background', 'unknown']
        assert result['startup_type'] in valid_types


# Pytest configuration
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
