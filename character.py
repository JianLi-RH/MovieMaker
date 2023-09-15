import yaml

try:
    from libs import ImageHelper, SuCaiHelper
except ImportError:
    import ImageHelper
    import SuCaiHelper

class Character():
    def __init__(self, obj) -> None:
        self.name = obj.get("名字")
        self.image = SuCaiHelper.get_sucai(obj.get("素材"))
        self.pos = None # 位置
        self.size = None    #大小
        self.rotate = 0 # 显示角度
        self.display = False # 默认不显示
        pass


if __name__ == "__main__":
    with open('script.yaml', 'r') as file:
       script = yaml.safe_load(file)

    obj = script.get("场景")[0].get("角色")[0]
    char = Character(obj)
