---
title: "PocketSphinx实现语音识别"
date: "2020-07-29T14:30:00+08:00"
description: "前言 我最近一直在搞一个名叫 A.N."
categories:
  - "计算机"
tags:
  - "python"
---

# 前言
我最近一直在搞一个名叫 A.N.N.A. 的 `Python` 语音机器人项目（Anna 是什么单词的缩写我就不说了，自己猜去），需要用的强大的语音识别技术。翻看全网教程，没有一篇说的通的，要么就是教会如何购买百度AI会员，要么就是教如何翻墙使用谷歌语音……

我最近发现`PocketSphinx`语音识别很不错，但是全网还是没有哪篇文章会告诉你，如何从头到尾下载这个库，用这个库进行语音识别，**并且不在电脑上留下任何垃圾**，可以随时删除的安装方法。然后你又会抱怨`PocketSphinx`有多么垃圾。

在这篇文章里，我将告诉你如何安装`pocketsphinx`，并将其嵌入`speech_recognition`库，来更好地实现最终的语音转文字。

# 电脑环境

- 系统：`macOS Catalina` v10.15.3；
- 软件
  - `Xcode` v11（版本其实无所谓）；
  - `Homebrew` （安装命令：`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`）
  - `Python 3`

# 安装`PocketSphinx`
我们先来看一下`PocketSphinx`的依赖关系图：
```
PocketSphinx
    |
    |-- SphinxBase
    |  |--libogg
    |  |--libvorbis
    |  |--flac
    |  |--libsamplerate
    |  `--libsndfile
    `-- Swig
         `--PCRE
```
1. 打开终端，运行如下`brew`命令：
```bash
$ brew install pcre
$ brew install swig
```
其中，`swig`是`pocketsphinx`的依赖，`pcre`是`swig`的依赖。`swig`不需要自己编译，直接用`brew`安装即可。

2. 再使用`brew`安装`SphinxBase`：
```bash
$ brew install SphinxBase
```
这个命令会将`SphinxBase`及其所有依赖安装到电脑上。现在，`brew list`应该如下：
```bash
index_out_of_range@imac ~ % brew list
cmu-sphinxbase	libogg		libvorbis	portaudio
flac		libsamplerate	openssl@1.1	swig
ldid		libsndfile	pcre
```
> 注：`portaudio`、`ldid`和`openssl`是我自己安装的，不用安装。

3. 克隆`PocketSphinx`仓库，我们要在之后的步骤手动安装仓库，别问我为什么：
```bash
git clone git@github.com:cmusphinx/pocketsphinx.git
# 或者（推荐）
git clone --recursive https://github.com/cmusphinx/pocketsphinx.git
# cd 到仓库
cd pocketsphinx-python
```
注意：必须`clone`，直接下载仓库会有文件缺失，因为这个库引用了其它仓库代码。如果网速太慢，可以fq或者把仓库导入`gitee`。

4. ==使用`vim`更改关键文件==（如果直接用`pip`安装，会有文件出错[^1]）：
```bash
vim deps/sphinxbase/src/libsphinxad/ad_openal.c
```
接下来用`vim`把
```objc
#include <al.h>
#include <alc.h>
```
改为
```objc
#include <OpenAL/al.h>
#include <OpenAL/alc.h>
```

5. 使用`setup.py`安装（至关重要的一步，仔细看命令！）：
```bash
python3 setup.py install
```
注意是`python3`而不是`python`。我一开始没加3，结果安装到`python2`系统目录去了。

## 测试安装

使用如下命令测试`PocketSphinx`是否安装成功：
```python
index_out_of_range@imac ~ % python3
Python 3.8.2 (v3.8.2:7b3ab5921f, Feb 24 2020, 17:52:18)
[Clang 6.0 (clang-600.0.57)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import pocketsphinx
>>>
```
如果像我一样`import`没有报错，就是安装成功了！

# 语音识别

## 英文识别

安装完`PocketSphinx`后，就进入到我们的第二个阶段，嵌入`speech_recognition`模块进行语音识别了。你可以将`speech_recognition`模块理解为众多语音识别SDK与API的一个高层封装模块。使用`pip install SpeechRecognition`安装即可。

接下来，新建一个`.py`文件，输入如下代码：
```python
# 注：安装时用的是 SpeechRecognition 这一名称，但是注意 import 时要用 speech_recognition 这一名称。
import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()

def recognize(r, mic, lang="en-US"):
    print("Please wait...", end="") # 在开始录音前等待
    
    with mic as source:
        r.adjust_for_ambient_noise(source)
        backspace = "\r" * 14 # 退格字符
        print(f'{backspace}Say something: ', end="")
        audio = r.listen(source)
    
    # 调用识别函数（这个函数只有安装了 PocketSphinx 才能调用），具体方法看官方文档
    result = r.recognize_sphinx(audio, language=lang)
    
    # 打印并返回结果
    print(result)
    return result

if __name__ == '__main__':
    recognize(r, mic)
```
使用终端运行代码（我用`VSCode`不知为何打不开麦克风）：程序首先会打印`Please wait...`，等待一会`Please wait...`会变成`Say something:`，之后说一句英文（比如`hello`），程序就会打印出`hello`。

但是问题来了，我们是中国人啊！于是你把`recognize(r, mic)`改成了`recognize(r, mic, lang="zh-CN")`，程序报错了。

## 中文识别

说白了，程序的报错原因就是你没有中文语言模型，`PocketSphinx`是默认只有英文的。接下来我们添加中文模型：
1. 到 SourceForge 的[这个项目](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models)里，找到 Mandarin（普通话），点进去有个`tar`包，下载下来并解压。
2. 将解压出的目录改名为`zh-CN`，拖动到`/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/speech_recognition/pocketsphinx-data/`目录下。
3. 按图中方式，将`zh-CN`目录里的文件按`en-US`目录里文件的命名规律改名：
![改名](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/4/30/py-sphinx-chname.jpg)

现在把程序里`recognize(r, mic)`改成`recognize(r, mic, lang="zh-CN")`，程序成功运行！不过通过实验发现，这个模型识别出来的中文貌似很垃圾……只能自己训练模型了……

# END

[^1]: https://github.com/bambocher/pocketsphinx-python/issues/28
