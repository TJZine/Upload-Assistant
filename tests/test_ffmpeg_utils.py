from src.utils import ffmpeg as ffmpeg_utils


def test_sanitize_stream_label_replaces_victory_hand():
    assert ffmpeg_utils.sanitize_stream_label('[0✌0]') == '[0:v:0]'


def test_prepare_ffmpeg_command_fills_missing_map():
    command = ['ffmpeg', '-i', 'input.mkv', '-map', '', '-frames:v', '1', 'out.png']
    prepared = ffmpeg_utils.prepare_ffmpeg_command(command)
    idx = prepared.index('-map')
    assert prepared[idx + 1] == '0:v:0'
    assert prepared[0] == ffmpeg_utils.FFMPEG_BINARY


def test_prepare_ffmpeg_object_uses_env_override(monkeypatch):
    monkeypatch.setenv('UA_FFMPEG_BIN', '/custom/ffmpeg')
    import importlib

    import src.utils.ffmpeg as mod

    importlib.reload(mod)
    prepared = mod.prepare_ffmpeg_command(['ffmpeg', '-i', 'input', 'out.png'])
    assert prepared[0] == '/custom/ffmpeg'
    monkeypatch.delenv('UA_FFMPEG_BIN', raising=False)
    importlib.reload(mod)
