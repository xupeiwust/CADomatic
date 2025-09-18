import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import subprocess
from ..main import (
    run_freecad_script, 
    main, 
    GEN_SCRIPT, 
    LOG_FILE, 
    BASE_INSTRUCTION,
    GUI_SNIPPET,
    MAX_RETRIES
)


class TestRunFreecadScript:
    """Test the run_freecad_script function"""
    
    @patch("main.subprocess.run")
    @patch("main.LOG_FILE")
    def test_run_freecad_script_success(self, mock_log_file, mock_subprocess_run):
        """Test successful FreeCAD script execution"""
        # Mock subprocess return
        mock_subprocess_run.return_value = Mock(returncode=0)
        
        # Mock log file with harmless message
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "Exception while processing file: generated/result_script.py [module 'FreeCADGui' has no attribute 'activeDocument']"
        
        result = run_freecad_script()
        
        assert result is True
        mock_subprocess_run.assert_called_once_with(
            ["python", str(Path("src/run_freecad.py"))],
            capture_output=True,
            text=True
        )
    
    @patch("main.subprocess.run")
    @patch("main.LOG_FILE")
    def test_run_freecad_script_failure(self, mock_log_file, mock_subprocess_run):
        """Test failed FreeCAD script execution"""
        # Mock subprocess return
        mock_subprocess_run.return_value = Mock(returncode=0)
        
        # Mock log file with real error
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "SyntaxError: invalid syntax"
        
        result = run_freecad_script()
        
        assert result is False
    
    @patch("main.subprocess.run")
    @patch("main.LOG_FILE")
    def test_run_freecad_script_no_log_file(self, mock_log_file, mock_subprocess_run):
        """Test when log file doesn't exist"""
        mock_subprocess_run.return_value = Mock(returncode=0)
        mock_log_file.exists.return_value = False
        
        result = run_freecad_script()
        
        assert result is False


class TestMainFunction:
    """Test the main function"""
    
    @patch("main.input")
    @patch("main.BASE_INSTRUCTION")
    @patch("main.prompt_llm")
    @patch("main.run_freecad_script")
    @patch("main.open_freecad")
    @patch("main.GEN_SCRIPT")
    def test_main_success_first_attempt(
        self, mock_gen_script, mock_open_freecad, mock_run_freecad_script, 
        mock_prompt_llm, mock_base_instruction, mock_input
    ):
        """Test main function succeeds on first attempt"""
        # Mock user input
        mock_input.return_value = "Create a cube"
        
        # Mock base instruction file
        mock_base_instruction.read_text.return_value = "Base instructions"
        
        # Mock LLM response
        mock_prompt_llm.return_value = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        
        # Mock successful FreeCAD run
        mock_run_freecad_script.return_value = True
        
        # Mock file operations
        mock_file = Mock()
        mock_gen_script.write_text = mock_file.write_text
        
        with patch("builtins.print") as mock_print:
            main()
        
        # Verify LLM was called with correct prompt
        mock_prompt_llm.assert_called_once_with("Base instructions\n\nUser instruction: Create a cube")
        
        # Verify FreeCAD was opened
        mock_open_freecad.assert_called_once()
        
        # Verify success message would be printed
        mock_print.assert_any_call("No errors in generated code!")
    
    @patch("main.input")
    @patch("main.BASE_INSTRUCTION")
    @patch("main.prompt_llm")
    @patch("main.run_freecad_script")
    @patch("main.open_freecad")
    @patch("main.LOG_FILE")
    @patch("main.GEN_SCRIPT")
    def test_main_with_retries(
        self, mock_gen_script, mock_log_file, mock_open_freecad, 
        mock_run_freecad_script, mock_prompt_llm, mock_base_instruction, mock_input
    ):
        """Test main function with retries"""
        # Mock user input
        mock_input.return_value = "Create a cube"
        
        # Mock base instruction file
        mock_base_instruction.read_text.return_value = "Base instructions"
        
        # Mock LLM responses - first fails, then succeeds
        mock_prompt_llm.side_effect = [
            "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')",  # Initial
            "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"   # Fixed
        ]
        
        # Mock FreeCAD runs - first fails, then succeeds
        mock_run_freecad_script.side_effect = [False, True]
        
        # Mock log file
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "Syntax error"
        
        # Mock file operations
        mock_file = Mock()
        mock_gen_script.write_text = mock_file.write_text
        
        with patch("builtins.print"):
            main()
        
        # Verify LLM was called twice (initial + fix)
        assert mock_prompt_llm.call_count == 2
        
        # Verify FreeCAD was opened after success
        mock_open_freecad.assert_called_once()
    
    @patch("main.input")
    @patch("main.BASE_INSTRUCTION")
    @patch("main.prompt_llm")
    @patch("main.run_freecad_script")
    @patch("main.open_freecad")
    @patch("main.LOG_FILE")
    @patch("main.GEN_SCRIPT")
    def test_main_max_retries_reached(
        self, mock_gen_script, mock_log_file, mock_open_freecad, 
        mock_run_freecad_script, mock_prompt_llm, mock_base_instruction, mock_input
    ):
        """Test main function when max retries are reached"""
        # Mock user input
        mock_input.return_value = "Create a cube"
        
        # Mock base instruction file
        mock_base_instruction.read_text.return_value = "Base instructions"
        
        # Mock LLM responses - always return same code
        mock_prompt_llm.return_value = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        
        # Mock FreeCAD runs - always fail
        mock_run_freecad_script.return_value = False
        
        # Mock log file
        mock_log_file.exists.return_value = True
        mock_log_file.read_text.return_value = "Syntax error"
        
        # Mock file operations
        mock_file = Mock()
        mock_gen_script.write_text = mock_file.write_text
        
        with patch("builtins.print") as mock_print:
            main()
        
        # Verify LLM was called MAX_RETRIES + 1 times (initial + each retry)
        assert mock_prompt_llm.call_count == MAX_RETRIES + 1
        
        # Verify FreeCAD was never opened
        mock_open_freecad.assert_not_called()
        
        # Verify max retries message was printed
        mock_print.assert_any_call(f"❌ Max retries ({MAX_RETRIES}) reached. Check {LOG_FILE} for details.")


class TestCodeCleaning:
    """Test code cleaning functionality"""
    
    @patch("main.prompt_llm")
    def test_code_cleaning_with_backticks(self, mock_prompt_llm):
        """Test cleaning code that starts with backticks"""
        mock_prompt_llm.return_value = "```python\nimport FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')\n```"
        
        # This would be called in main, but we test the logic directly
        generated_code = mock_prompt_llm.return_value
        if generated_code.startswith("```"):
            generated_code = generated_code.strip("`\n ")
            if generated_code.lower().startswith("python"):
                generated_code = generated_code[len("python"):].lstrip()
        
        expected = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        assert generated_code == expected
    
    @patch("main.prompt_llm")
    def test_code_cleaning_without_backticks(self, mock_prompt_llm):
        """Test cleaning code that doesn't need cleaning"""
        mock_prompt_llm.return_value = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        
        generated_code = mock_prompt_llm.return_value
        if generated_code.startswith("```"):
            generated_code = generated_code.strip("`\n ")
            if generated_code.lower().startswith("python"):
                generated_code = generated_code[len("python"):].lstrip()
        
        expected = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        assert generated_code == expected


class TestGUISnippetAppending:
    """Test GUI snippet appending functionality"""
    
    def test_gui_snippet_appending(self):
        """Test that GUI snippet is correctly appended"""
        generated_code = "import FreeCAD\nbox = FreeCAD.ActiveDocument.addObject('Part::Box', 'Box')"
        final_code = generated_code + "\n\n" + GUI_SNIPPET
        
        assert GUI_SNIPPET in final_code
        assert final_code.startswith(generated_code)
        assert final_code.endswith(GUI_SNIPPET.strip())


# Test fixtures for integration-style tests
@pytest.fixture
def setup_test_environment(tmp_path):
    """Set up a test environment with temporary files"""
    # Create temporary files
    base_instruction = tmp_path / "base_instruction.txt"
    base_instruction.write_text("Create FreeCAD objects based on user input")
    
    gen_script = tmp_path / "result_script.py"
    log_file = tmp_path / "last_run_log.txt"
    
    return {
        "base_instruction": base_instruction,
        "gen_script": gen_script,
        "log_file": log_file
    }


def test_file_path_constants():
    """Test that file path constants are correct"""
    assert str(GEN_SCRIPT) == "generated/result_script.py"
    assert str(LOG_FILE) == "generated/last_run_log.txt"
    assert str(BASE_INSTRUCTION) == "prompts/base_instruction.txt"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])