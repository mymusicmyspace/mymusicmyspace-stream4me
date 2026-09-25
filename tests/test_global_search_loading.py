from pathlib import Path
import xml.etree.ElementTree as ET


root = Path(__file__).resolve().parents[1]
window = ET.parse(root / 'resources/skins/Default/720p/GlobalSearch.xml').getroot()
loading_group = next(control for control in window.iter('control')
                     if control.get('type') == 'group' and control.get('id') == '5')
assert loading_group.findtext('visible', '').strip().lower() == 'false'
source = (root / 'specials/globalsearch.py').read_text(encoding='utf-8')
channel_search = source.split('    def search(self):', 1)[1].split('    def get_channel_results', 1)[0]
assert channel_search.index("self.LOADING.setVisibleCondition('true')") < channel_search.index('self.LOADING.setVisible(True)')
