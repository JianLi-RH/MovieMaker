import yaml

import utils

import config_reader
try:
    from libs import ImageHelper, SuCaiHelper
except ImportError:
    import ImageHelper
    import SuCaiHelper

class Character():
    def __init__(self, obj) -> None:
***REMOVED***
        示例：
          -
            名字: 小和尚 ***REMOVED*** Xiaoyou (F)
            素材: resources/SuCai/JueSe/和尚2.png
            位置: [0.4, 0.5]
            大小: [180, 260]
            发音人: x4_lingfeichen_emo
            显示: 
            图层: 0
            角度: 0
***REMOVED***
        self.name = obj.get("名字")
        self.image = obj.get("素材")
        self.tts_engine = obj.get("发音人引擎") if obj.get("发音人引擎") else config_reader.tts_engine
        self.speaker = obj.get("发音人", None)
        self.pos = utils.covert_pos(obj.get("位置", None)) ***REMOVED*** 位置
        self.size = obj.get("大小", None) ***REMOVED*** 位置    ***REMOVED***大小
        self.rotate = obj.get("角度") if obj.get("角度") else 0 ***REMOVED*** 显示角度
        self.display = True if obj.get("显示", None) == '是' else False ***REMOVED*** 默认不显示
        self.index = obj.get("图层", 0) ***REMOVED*** 角色显示的图层 （数值大的会覆盖数值小的）， 默认是0
        pass


***REMOVED***
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

    obj = script.get("场景")[0].get("角色")[0]
    char = Character(obj)
