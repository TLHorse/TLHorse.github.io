---
title: "Hopper之CrossOver 19 破解"
date: "2020-03-09T09:16:00+08:00"
description: "前言 这篇文章不仅放在了我的博客上，还是本人在吾爱破解上的第一个帖子。我在吾爱破解论坛上发布帖子后，又将语言表达顺了一遍，放在了我的博客上，文中的图片链接全部引用自吾爱破解，可以看到吾爱破解的水印。"
categories:
  - "计算机"
tags:
  - "反编译"
---

# 前言

这篇文章不仅放在了我的博客上，还是本人在[吾爱破解](https://www.52pojie.cn/thread-1126808-1-1.html)上的第一个帖子。我在吾爱破解论坛上发布帖子后，又将语言表达顺了一遍，放在了我的博客上，文中的图片链接全部引用自吾爱破解，可以看到吾爱破解的水印。**此篇文章未经允许，谢绝转载，并仅供学习研究。**

最近一直在鼓捣各种软件的逆向与反编译，又准备要在Mac上运行Windows程序，于是准备上手`CrossOver`。但是感觉在五花八门的破解网站上下载的东西不安全，求人不如求己，所以我就当练练手，自己破解试试看，而后就有了这篇文章。

# 准备

- 从[CrossOver 官网](https://www.crossoverchina.com)上下载最新版的 CrossOver 19 。
- [Hopper Disassembler v4](https://www.hopperapp.com) 一枚。

# 开始破解

## 分析软件

首先打开`CrossOver`，简单的看了一下，分析出几个信息：

- 打开软件后弹出了一个要钱弹窗，弹窗里提示了试用剩余天数，并提示你购买软件或者进行使用；

- 要钱弹窗中有两个需要关注的按钮，一个是 `现在试用`，另一个是 `使用购买信息解锁` ;

- 按下 `现在试用` 按钮，可以直接跳转到App里，开始14天试用；

- 按下 `使用购买信息解锁` 按钮，可以进行邮箱/密码激活，或者使用邮箱+密码+验证码激活；

- 开始试用App后，在`CrossOver`里仍然可以进行App激活操作。

- 嘿嘿，CrossOver竟然没有反调试。

  于是，我们就有如下的破解思路：

- Patch剩余天数；
- Patch使用购买信息解锁的验证流程。

## 修改程序

### Patch剩余天数

本篇文章选用第一种思路“Patch剩余天数”，因为第一种思路相对简单直接。我试过第二种思路，对新手来说相对复杂，我就不再阐述了。

打开 `Hopper`，将`CrossOver`拖入分析。本来想搜索UI中的字符串，字符串搜索无果后，根据“剩余天数”的英文“left”，搜索关键词：

![搜索left](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-serach-left.png)

我们发现，第一个函数`-[CXApplication daysLeft]`，于是打开伪代码发现，这个函数返回的是一个`int`，极有可能是剩余的天数。我们可以尝试Patch这里，使得该函数永远返回十六进制`0x8ef8`。将汇编代码改为：

```asm
mov rax, 0x8ef8
ret
```

这里我们要注意一点：十六进制`0x8ef8`对应的是十进制的`36600`（天）。我设置成36600，只是为了好看——36600天就是100多年。事实上，这个数值可以设置为任意大于0的整数，别忘了这个数值已经被我们 patch 了，是不会变动的。接着，我们动态调试运行一下，成功：

![剩余天数破解成功](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-36600.png)

### Patch 激活窗口

你肯定觉得这篇文章不可能这么快结束。接下来，我要让你认识到一点：在App里面，仍然有某些按钮可以进行激活操作。比如程序顶栏上的`CrossOver` > `解锁 CrossOver`按键，如下图：

![某些解锁按钮仍然存在](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-regwin.png)

而这些按键恰恰是我们不需要的。为了App的简洁，我们现在要把App里所有激活相关的按键禁用。与其禁用所有按钮，不如把这些按钮弹出来的**同一个**激活窗口禁用掉。这怎么做到呢？其实非常简单。这里有个小技巧，在`macOS`里，弹出窗口必须通过`windowDidLoad:`函数，因此我们可以将`windowdidload`作为关键词搜索：

![windowdidload搜索](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-search-windowdl.png)

这时我看中了`DemoRegisterController`，它应该是一个注册管理类，所以他的`windowDidLoad:`方法弹出来的窗口很有可能是那个激活窗口。我们再把`DemoRegisterController`作为关键词搜索，把这个类的相关函数（图中红框内的方法）都`ret`掉即可。

![DemoRegisterController搜索](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-drcret.png)

指令为：

```asm
ret
```

修改后，以调试的方式运行`CrossOver`，发现注册相关的按钮已经按不动了。成功！

# 留下足迹

我之所以把这个步骤设置成一级内容，是因为它实际跟破解没有关系。通过这一步，我要告诉你，任何一位craker为了保证自己的破解作品不被盗用或广泛传播（真正的craker破解出来的东西不会随便发给别人），都会注明程序是自己破解的。就像这样：

<img src="https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-credits.png" alt="留下足迹" style="zoom:50%;" />

> 注：此窗口可以在程序顶栏`CrossOver`>`关于`中调出。

这个怎么办到呢？其实，如果你的App有着跟上图类似的界面，那么这个界面中间的电子权利信息（也就是文字部分）通常会被储存为一个`.html`、`.txt`或`.rtf`文件。你可以根据一下规则尝试找到它：

1. 如果程序支持**多语言**，那么它**有可能**在程序资源的多语言文件夹里，也就是：xxx.app/Contents/Resources/xxx.lproj/xxx.xxx。

2. 如果程序只支持**单语言**，那么它**可能**在：xxx.app/Contents/Resources/xxx.xxx。

在这个App里，我们可以根据第一个规则（此App是多语言的），通过下图找到电子权利信息：

![电子权利信息路径](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-creditspath.png)

找到后，用文本编辑打开，在文件开头加上一句类似下面的话：

> 这个版本的 CrossOver 已经由xxx破解。你可以放心使用。注意，请勿广泛传播……

保存文件，再打开`CrossOver`，终于破解完成！
