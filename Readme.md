
程序入口： run.py

Prerequests:
https://imagemagick.org/script/download.php
https://imagemagick.org/script/install-source.php
https://crotoc.github.io/2018/09/28/Install-customized-fonts-for-imagemagick/***REMOVED***Install-customized-fonts-for-imagemagick
dnf install perl-FindBin


imagemagick的bug:
/home/jianl/.local/lib/python3.10/site-packages/moviepy/video/io/ffmpeg_reader.py ***REMOVED*** 259
infos = error.decode("utf-8", errors="ignore")


查找已安装的字体：
***REMOVED*** 系统字体路径： /usr/share/fonts/truetype/'
***REMOVED*** https://github.com/fonttools/fonttools
***REMOVED*** pip install --user fonttools
>>> from moviepy.editor import *
>>> TextClip.list('font')
[]
>>> TextClip.list('color')

pip install fonts
pip install font-amatic-sc
pip install font-fredoka-one


convert -debug configure -list font 2>&1 | grep -E "Searching|Loading"

find fonts/Roboto -type f -name '*.ttf' | imagick_type_gen -f - > /home/jianl/.config/ImageMagick/type-myfonts.xml

免费字体： https://www.fonts.net.cn/fonts-zh-1.html

https://github.com/Zulko/moviepy/blob/master/Dockerfile


文字转语音： https://voicemaker.in/
合并图片： https://www.media.io/image-converter/merge-png.html


例子：
场景: ***REMOVED*** 每个场景共用一套角色和背景，不同的场景使用不同的角色和背景
  -
    背景: resources/JiChuSuCai/BeiJing/1.jpg
    角色:
      -
        名字: 摩托车
        素材: resources/JiChuSuCai/JiaoTongGongJu/MoTuoChe/1.png
      -
        名字: 沙雕
        素材: resources/SuCai/JueSe/人物24.png
    活动:
      -
        名字: "1"
        描述: 人物出场
        背景音乐: resources/ShengYin/a.mp3
        字幕: 
        持续时间: 3秒
        动作:
          -
            名称: 行进
            角色: 摩托车
            开始位置: [0.1, 0.6] ***REMOVED*** 左上角
            结束位置: [0.8, 0.4]
            比例: [0.1, 0.06]  ***REMOVED*** 比例变化，开始比例 - 结束比例
            方式: 自然 ***REMOVED***跳跃、旋转
      -
        名字: "2"
        描述: 镜头拉近
        背景音乐: resources/ShengYin/打招呼.mp3
        字幕: 
        持续时间: 2秒
        动作:
          -
            名称: 消失
            角色: 摩托车
          -
            名称: 转身
            角色: 沙雕
            度数: 左右 ***REMOVED*** 左右, 上下， 45(逆时针角度)
          -
            名称: 镜头
            焦点: ["中心", "底部"]
            变化: [1, 0.7]  ***REMOVED*** 画面从100%显示，到70%显示，即将镜头拉近到70%
          -
            名称: gif ***REMOVED*** 向视频中插入一个gif
            素材: resources/SuCai/watermark.gif
            位置: [0.48, 0]
            比例: 0.7
            度数: 左右 ***REMOVED*** 左右, 上下， 45(逆时针角度)