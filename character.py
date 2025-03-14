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
        """
        示例：
          -
            名字: 小和尚
            素材: resources/SuCai/JueSe/和尚2.png
            # 位置： 可以设置成二维数组，这样scenario就可以同时生成多个相同的角色了，只是位置不同
            # 当位置是二维数组的时候，角色名会自动追加一个数字， 以0开始
            位置: [0.4, 0.5]
            大小: [180, 260]
            发音人: x4_lingfeichen_emo
            发音人引擎: chat    # 默认是 xunfei
            显示: 
            透明度: 0.1 
            图层: 0
            角度: 0
        """
        self.obj = obj
        self.name = obj.get("名字")
        self.image = SuCaiHelper.get_material(obj.get("素材"))
        if self.image.lower().endswith(".gif"):
            self.gif_frames = ImageHelper.get_frames_from_gif(self.image)
        else:
            self.gif_frames = []
        self.tts_engine = obj.get("发音人引擎") if obj.get("发音人引擎") else config_reader.tts_engine
        self.speaker = obj.get("发音人", None)
        self.pos = utils.covert_pos(obj.get("位置", None)) # 位置
        self.size = obj.get("大小", None) # 位置    #大小
        self.rotate = obj.get("角度") if obj.get("角度") else 0 # 显示角度
        self.display = True if obj.get("显示", None) == '是' else False # 默认不显示
        self.transparency = obj.get("透明度", 1) # 透明度取值 0 ～ 1： 0，完全透明；1， 完全不透明
        self.index = int(obj.get("图层")) if obj.get("图层") else 0 # 角色显示的图层 （数值大的会覆盖数值小的）， 默认是0
        pass


if __name__ == "__main__":
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

    obj = script.get("场景")[0].get("角色")[0]
    char = Character(obj)
