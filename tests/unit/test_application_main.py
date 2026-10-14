from personal_ai.application import main as main_module


def test_main_starts_application(capsys, monkeypatch):
    called = []
    monkeypatch.setattr(main_module, "bootstrap", lambda: called.append(True))

    assert main_module.main([]) == 0
    assert called == [True]
    assert "Personal AI initialized." in capsys.readouterr().out


def test_main_help_does_not_bootstrap(capsys, monkeypatch):
    called = []
    monkeypatch.setattr(main_module, "bootstrap", lambda: called.append(True))

    try:
        main_module.main(["--help"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("--help should exit")

    output = capsys.readouterr().out
    assert "usage:" in output.lower()
    assert "--version" in output
    assert called == []


def test_main_version_does_not_bootstrap(capsys, monkeypatch):
    called = []
    monkeypatch.setattr(main_module, "bootstrap", lambda: called.append(True))

    try:
        main_module.main(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("--version should exit")

    assert capsys.readouterr().out.strip() == "personal-ai 0.2.0"
    assert called == []
