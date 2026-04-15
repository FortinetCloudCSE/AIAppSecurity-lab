from tools import read_resume_text, run_command


def test_read_resume_text_reads_local_file(tmp_path):
    resume = tmp_path / "resume.txt"
    resume.write_text("Jane Doe\nPython Engineer")

    result = read_resume_text(str(resume))

    assert "Jane Doe" in result
    assert "Python Engineer" in result


def test_run_command_allows_safe_command():
    result = run_command("echo hello")
    assert "hello" in result["stdout"]
    assert result["returncode"] == 0


def test_run_command_blocks_dangerous_command():
    result = run_command("rm -rf /")
    assert result["blocked"] is True
    assert result["returncode"] == 1
