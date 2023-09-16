import yaml

import utils

try:
    from libs import ImageHelper, SuCaiHelper
except ImportError:
    import ImageHelper
    import SuCaiHelper

class Character():
    def __init__(self, obj) -> None:
        self.name = obj.get("名字")
        self.image = SuCaiHelper.get_sucai(obj.get("素材"))
        self.pos = utils.covert_pos(obj.get("位置", None)) # 位置
        self.size = obj.get("大小", None) # 位置    #大小
        self.rotate = obj.get("角度", None) # 显示角度
        self.display = True if obj.get("显示", None) == '是' else False # 默认不显示
        pass


if __name__ == "__main__":
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

    obj = script.get("场景")[0].get("角色")[0]
    char = Character(obj)
