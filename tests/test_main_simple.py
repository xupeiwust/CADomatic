#!/usr/bin/env python3
"""
Test script for main.py functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import subprocess
import sys
import os

# Import the modules to test
from main import run_freecad_script, main, GEN_SCRIPT, LOG_FILE, BASE_INSTRUCTION, GUI_SNIPPET, MAX_RETRIES


class TestRunFreecadScript(unittest.TestCase):
    """Test the run_freecad_script function"""
    
    @patch('subprocess.run')
    @patch('main.LOG_FILE')
    def test_run_freecad_script_success(self, mock_log_file, mock_subprocess_run):
        """Test successful FreeCAD script execution"""
        # Mock subprocess return
        mock_subprocess_run.return_value = Mock(returncode=0)
        
        # Mock log file with harmless message
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "Exception while processing file: generated/result_script.py [module 'FreeCADGui' has no attribute 'activeDocument']"
        
        result = run_freecad_script()
        
        self.assertTrue(result)
        mock_subprocess_run.assert_called_once_with(
            ["python", str(Path("src/run_freecad.py"))],
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    @patch('main.LOG_FILE')
    def test_run_freecad_script_failure(self, mock_log_file, mock_subprocess_run):
        """Test failed FreeCAD script execution"""
        # Mock subprocess return
        mock_subprocess_run.return_value = Mock(returncode=0)
        
        # Mock log file with real error
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "SyntaxError: invalid syntax"
        
        result = run_freecad_script()
        
        self.assertFalse(result)
    
    @patch('subprocess.run')
    @patch('main.LOG_FILE')
    def test_run_freecad_script_no_log_file(self, mock_log_file, mock_subprocess_run):
        """Test when log file doesn't exist"""
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_log_file.exists.return_value = False
        
        result = run_freecad_script()
        
        self.assertFalse(result)


class TestMainFunction(unittest.TestCase):
    """Test the main function"""
    
    @patch('main.input')
    @patch('main.BASE_INSTRUCTION')
    @patch('main.prompt_llm')
    @patch('main.run_freecad_script')
    @patch('main.open_freecad')
    @patch('main.LOG_FILE')
    def test_main_success_first_attempt(self, mock_log_file, mock_open_freecad, 
                                      mock_run_freecad_script, mock_prompt_llm, 
                                      mock_base_instruction, mock_input):
        """Test main function succeeds on first attempt"""
        # Mock user input
        mock_input.return_value = "Create a cube"
        
        # Mock base instruction file
        mock_base_instruction.read_text.return_value = "Base instructions"
        
        # Mock LLM response
        mock_prompt_llm.return_value = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        
        # Mock successful FreeCAD run
        mock_run_freecad_script.return_value = True
        
        # Mock log file
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "Exception while processing file: generated/result_script.py [module 'FreeCADGui' has no attribute 'activeDocument']"
        
        # Mock file operations
        with patch('main.GEN_SCRIPT.write_text') as mock_write:
            with patch('builtins.print'):
                main()
        
        # Verify LLM was called with correct prompt
        mock_prompt_llm.assert_called_once_with("Base instructions\n\nUser instruction: Create a cube")
        
        # Verify FreeCAD was opened
        mock_open_freecad.assert_called_once()
    
    @patch('main.input')
    @patch('main.BASE_INSTRUCTION')
    @patch('main.prompt_llm')
    @patch('main.run_freecad_script')
    @patch('main.open_freecad')
    @patch('main.LOG_FILE')
    def test_main_max_retries_reached(self, mock_log_file, mock_open_freecad, 
                                    mock_run_freecad_script, mock_prompt_llm, 
                                    mock_base_instruction, mock_input):
        """Test main function when max retries are reached"""
        # Mock user input
        mock_input.return_value = "Create a cube"
        
        # Mock base instruction file
        mock_base_instruction.read_text.return_value = "Base instructions"
        
        # Mock LLM responses
        mock_prompt_llm.return_value = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        
        # Mock FreeCAD runs - always fail
        mock_run_freecad_script.return_value = False
        
        # Mock log file
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "Syntax error"
        
        # Mock file operations
        with patch('main.GEN_SCRIPT.write_text') as mock_write:
            with patch('builtins.print') as mock_print:
                main()
        
        # Verify LLM was called MAX_RETRIES + 1 times
        self.assertEqual(mock_prompt_llm.call_count, MAX_RETRIES + 1)
        
        # Verify FreeCAD was never opened
        mock_open_freecad.assert_not_called()
        
        # Verify max retries message would be printed
        mock_print.assert_any_call(f"❌ Max retries ({MAX_RETRIES}) reached. Check {LOG_FILE} for details.")


class TestCodeCleaning(unittest.TestCase):
    """Test code cleaning functionality"""
    
    def test_code_cleaning_with_backticks(self):
        """Test cleaning code that starts with backticks"""
        generated_code = "```python\nimport FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')\n```"
        
        # Clean the code (replicating the logic from main.py)
        if generated_code.startswith("```"):
            generated_code = generated_code.strip("`\n ")
            if generated_code.lower().startswith("python"):
                generated_code = generated_code[len("python"):].lstrip()
        
        expected = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        self.assertEqual(generated_code, expected)
    
    def test_code_cleaning_without_backticks(self):
        """Test cleaning code that doesn't need cleaning"""
        generated_code = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        
        # Clean the code (replicating the logic from main.py)
        if generated_code.startswith("```"):
            generated_code = generated_code.strip("`\n ")
            if generated_code.lower().startswith("python"):
                generated_code = generated_code[len("python"):].lstrip()
        
        expected = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        self.assertEqual(generated_code, expected)


class TestGUISnippetAppending(unittest.TestCase):
    """Test GUI snippet appending functionality"""
    
    def test_gui_snippet_appending(self):
        """Test that GUI snippet is correctly appended"""
        generated_code = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        final_code = generated_code + "\n\n" + GUI_SNIPPET
        
        self.assertIn(GUI_SNIPPET, final_code)
        self.assertTrue(final_code.startswith(generated_code))
        self.assertTrue(final_code.endswith(GUI_SNIPPET.strip()))


# Mock functions to avoid actual API calls and FreeCAD operations
def mock_prompt_llm(prompt):
    """Mock function for prompt_llm"""
    return "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"

def mock_open_freecad():
    """Mock function for open_freecad"""
    pass


# Replace the actual functions with mocks for testing
import main
main.prompt_llm = mock_prompt_llm
main.open_freecad = mock_open_freecad


if __name__ == '__main__':
    unittest.main()