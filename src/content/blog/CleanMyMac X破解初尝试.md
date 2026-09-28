---
title: "CleanMyMac X破解初尝试"
date: "2020-03-15T09:16:00+08:00"
description: "缘起 应该是每个Mac用户耳熟能详的电脑清洁软件，以下简称。我几天前用的是版本，是在xx破解网站上搜索的TNT版本，结果今天一打开CMM发现，已经有了4."
categories:
  - "计算机"
tags:
  - "反编译"
---

# 缘起

`CleanMyMac X`应该是每个Mac用户耳熟能详的电脑清洁软件，以下简称`CMM`。我几天前用的是`CMM 4.5.3`版本，是在xx破解网站上搜索的TNT版本，结果今天一打开CMM发现，已经有了4.6.0版本的更新。与其到xx破解网站上搜破解版，不如自己再动手破解一遍，于是就有了这篇文章。我真的……一开始我也没想到这次破解会这么顺……


# 准备

- `CMM 4.6.0`一枚；
- `Hopper Disassembler v4`一枚。

# 破解

## 查找线索

首先将CMM拖进Hopper。我先搜索了一波UI中的Strings。搜索无果后，尝试搜索`vip` `register` `activate`关键词，发现`activate`关键词有很多激活相关项。

![搜索字符串](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/15/hop-cmm-search-str.jpg)

我找到了四个方法，名为`isAppActivated`。我想，相比其他复杂的函数与方法，那是不是把这四个方法patch了，整个CMM就能用了呢？

然而我又发现了第一个方法` -[CMActivationManager isAppActivated]`的伪代码调用了一个函数`_mLyGsJNgru0iJKGfhK`，并将这个函数的返回值（是`int`类型）赋予给了`rax`，而这个函数的内部逻辑很复杂，很可能就是验证激活的过程。

## 修改程序

接着上一个步骤，双击进入`_mLyGsJNgru0iJKGfhK`，打开伪代码模式，看着一长串的代码别着急，从程序入口开始，按照程序的`goto`走，顺藤摸瓜，最后`return`了一个`rax`——那简单，跳到汇编模式，直接：

```asm
mov rax, 0x1
ret
```

再打开伪代码，你会发现这个方法的伪代码已经变成：

```objc
int _mLyGsJNgru0iJKGfhK(int arg0) {
    return 0x1;
}
```

这就对了！

# 留下足迹

为什么要有这一步，在我的[CrossOver 19](https://www.52pojie.cn/thread-1126808-1-1.html)破解文章里已经说明了。在CMM中，我们要达到这样的效果：

![留下足迹](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/15/hop-cmm-mod-credits.png)

> 注：这个窗口可以在程序顶栏 CleanMyMac X > 关于CleanMyMac里找到。

这段文字是一个`.rtf`，在`/Applications/CleanMyMac X.app/Contents/Resources/zh-Hans.lproj/Credits.rtf`。打开这个文件，在开头按格式添加上你的Credit，注意一点，这个文件开头的几个空行要保留，否则达不到CMM的滚动效果。

之后，就大功告成了！

# BUG

1. 使用时，应用缺少权限，即使已经在设置里设置了磁盘完全访问。