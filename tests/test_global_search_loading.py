from pathlib import Path
import ast
import sys
import types
from unittest.mock import patch
import xml.etree.ElementTree as ET


root = Path(__file__).resolve().parents[1]
window = ET.parse(root / 'resources/skins/Default/720p/GlobalSearch.xml').getroot()
loading_group = next(control for control in window.iter('control')
                     if control.get('type') == 'group' and control.get('id') == '5')
assert loading_group.findtext('visible', '').strip().lower() == 'false'
source = (root / 'specials/globalsearch.py').read_text(encoding='utf-8')
channel_search = source.split('    def search(self):', 1)[1].split('    def get_channel_results', 1)[0]
assert channel_search.index("self.LOADING.setVisibleCondition('true')") < channel_search.index('self.LOADING.setVisible(True)')

series_open = source.split('    def open_streamingcommunity(self, item):', 1)[1].split('    def show_episodes', 1)[0]
assert 'dialog_progress_bg' in series_open
assert 'get_localized_string(90007)' in series_open
assert 'finally:' in series_open

on_click = source.split('    def onClick(self, control_id):', 1)[1].split('    def Back(self):', 1)[0]
assert 'elif search and control_id == RESULTS:' in on_click

platformtools = (root / 'platformcode/platformtools.py').read_text(encoding='utf-8')
autoplay_failure = platformtools.split('elif puedes == False:', 1)[1].split('\n    else:', 1)[0]
assert "item.channel == 'streamingcommunity'" in autoplay_failure
assert "item.contentType == 'episode'" in autoplay_failure
assert 'get_localized_string(90008)' in autoplay_failure
assert 'dialog_notification' in autoplay_failure

tree = ast.parse(platformtools)
play_options = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'get_dialogo_opciones')
servertools = types.ModuleType('core.servertools')
servertools.resolve_video_urls_for_playing = lambda *args: ([], False, 'Prossimamente')
core = types.ModuleType('core')
core.__path__ = []
core.servertools = servertools
notifications = []
namespace = {
    'config': types.SimpleNamespace(get_setting=lambda key: 0,
                                    get_localized_string=lambda string_id: str(string_id)),
    'logger': types.SimpleNamespace(debug=lambda *args: None),
    'dialog_notification': lambda *args, **kwargs: notifications.append((args, kwargs)),
    'play_canceled': False,
}
with patch.dict(sys.modules, {'core': core, 'core.servertools': servertools}):
    exec(compile(ast.Module(body=[play_options], type_ignores=[]), 'platformtools.py', 'exec'), namespace)
    item = types.SimpleNamespace(server='streamingcommunityws', video_urls=[], password='',
                                 url='https://example.invalid/episode',
                                 channel='streamingcommunity', contentType='episode')
    namespace['get_dialogo_opciones'](item, 0, False, True)
    assert notifications == [(('20000', '90008'), {'icon': 1})]
