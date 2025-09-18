#!/usr/bin/env python3
"""
Test file path constants
"""

import unittest
from main import GEN_SCRIPT, LOG_FILE, BASE_INSTRUCTION

class TestFilePaths(unittest.TestCase):
    """Test that file path constants are correct"""
    
    def test_file_paths(self):
        """Test all file path constants"""
        self.assertEqual(str(GEN_SCRIPT), "generated/result_script.py")
        self.assertEqual(str(LOG_FILE), "generated/last_run_log.txt")
        self.assertEqual(str(BASE_INSTRUCTION), "prompts/base_instruction.txt")

if __name__ == '__main__':
    unittest.main()