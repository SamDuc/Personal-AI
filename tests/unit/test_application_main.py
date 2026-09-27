from personal_ai.application.main import main


def test_main_starts_application(capsys):
    assert main() == 0
    assert "Personal AI initialized." in capsys.readouterr().out
