---
title: "使用动态库注入优雅破解 CrossOver"
date: "2020-04-13T21:23:41+08:00"
description: "前言 上次我写过一篇叫做Hopper 之 CrossOver 19 破解的文章，那么今天，我再写一篇 CrossOver 19 的破文。上一篇文章里，我用了“直接修改二进制文件”的方法来破解应用，而这次，我则通过动态库注入的方法来破解 CrossOver 19——这是一个巧妙、新奇的方法，说白了就是 hook，你..."
categories:
  - "计算机"
tags:
  - "反编译"
  - "hook"
---

# 前言

上次我写过一篇叫做[Hopper 之 CrossOver 19 破解](https://www.52pojie.cn/thread-1126808-1-1.html)的文章，那么今天，我再写一篇 CrossOver 19 的破文。上一篇文章里，我用了“直接修改二进制文件”的方法来破解应用，而这次，我则通过动态库注入的方法来破解 CrossOver 19——这是一个巧妙、新奇的方法，说白了就是 hook，你会喜欢上它的。我还要感谢[@云在天](https://www.52pojie.cn/home.php?mod=space&uid=476930)大神在我的[CleanMyMac X 破解贴](https://www.52pojie.cn/thread-1132170-1-1.html)里的指导，要不是她，可能我到现在还不知道什么是动态库注入。

前言的最后，我再说一下来意。我只是想教大家“破解方法”，而不是给大家“破解软件”。就拿例子说吧，我现在用的 Hopper Disassembler 可是正版的。因此，如果你喜欢 CrossOver 19，请购买正版。

# 准备

- 从[CrossOver 官网](https://www.crossoverchina.com)上下载最新版的 CrossOver 19 。
- [Hopper Disassembler v4](https://www.hopperapp.com) 一枚。
- 与上篇文章不同的是，我们需要 Xcode（我的版本是11）。 

# 分析软件

## 分析 UI

首先打开`CrossOver`，简单的看了一下，分析出几个信息：

- 打开软件后弹出了一个要钱弹窗，弹窗里提示了试用剩余天数，并提示你购买软件或者进行使用；
- 要钱弹窗中有两个需要关注的按钮，一个是 `现在试用`，另一个是 `使用购买信息解锁` ;
- 按下 `现在试用` 按钮，可以直接跳转到App里，开始14天试用；
- 开始试用App后，在`CrossOver`里仍然可以进行App激活操作。
- CrossOver 没有附加反调试工具。

  于是，我们就有如下的破解思路：

1. Patch 剩余天数；
2. Patch 使用购买信息解锁的验证流程。

本文中只讲述第一种方法。

## 使用 Hopper 分析

拖进 Hopper，先分析一波，看看有什么函数。本来想搜索UI中的字符串，字符串搜索无果后，根据“剩余天数”的英文“left”，搜索关键词：

![搜索left](https://i.loli.net/2020/03/27/DhqpY65tncdk3fO.png)

我们发现，第一个函数`-[CXApplication daysLeft]`，于是打开伪代码发现，这个函数返回的是一个`int`，极有可能是剩余的天数。我们可以尝试 Patch 这里，使得该函数永远返回十六进制`0x8ef8`（等同于 36600 天）。

按照上一篇文章的破解方法，我们只需要：
```assembly
mov rax, 0x8ef8
ret
```
然后试用天数就永远是 36600 天了。但是别忘了，我们今天是要讲如何使用动态库注入来 hook 函数的，接下来，咱们就开始 hook。

# 构建动态库

## 动态库注入原理

在`macOS`下的应用程序，绝大多数都会用`Objective-C`或`Swift`进行编译（`Python`这类的先不谈）。

如果程序使用了`Objective-C`编译，我们可以仗着`Objective-C`的动态消息传送机制与`runtime`，在程序运行时进行函数的调换。

然而我们 crakers 都面对的是已经编译好的程序，所以我们要把函数调换的过程写到一个动态库中，然后再用动态库注入工具（`insert_dylib`之类的）注入到原来的二进制文件中。

## 新建项目

首先，[打开 Xcode](xcode://)（按一下这里你会神奇地发现 Xcode 打开了），新建项目，选择`macOS` > `Library`，新建动态库项目，如图：

![选择类型](https://i.loli.net/2020/03/30/bsBnRwa75o4zJu8.png)

动态库的名称可以随便起，此处叫做`CrossOverPatch`，`Framework`选择`Cocoa`，`Type`选择`Dyamic`（动态）。随便找个地方保存项目即可。

现在你会得到一个动态库项目。

## 编写动态库

首先打开工程文件里的`CrossOverPatch.m`文件，输入：
```objc
#import "CrossOverPatch.h"
#import <objc/runtime.h>
```
我们用两个`#import`语句，将`CrossOverPatch.h`文件与`objc/runtime.h`库引入。`CrossOverPatch.h`文件（头文件），是每个`.m`文件里必须引用的。而`objc/runtime.h`库就是大名鼎鼎的运行时类库。

之后我们在下面声明一个实现`@implementation`
```objc
@implementation CrossOverPatch

@end
```
接下来，我们在实现里定义一个 hook 方法：
```objc
- (int)daysLeftHook {
    NSLog(@"====== METHOD PATCHING ======");
    return 36600;
}
```
**我们在下面的步骤中要用这个方法来替换原函数`daysLeft`，实现 hook。**这里需要注意一点，我们定义的这个函数的返回值（`int`）和参数列表（无）**需要与原函数相同**。`NSLog`则是打印语句，方便我们后期检测程序。最后的`return`语句，让函数返回了36600这个值。你当然也可以把36600写作0x8ef8。

我们在实现里添加一个`+ (void) load`方法，如下：
```objc
+ (void)load {
    NSLog(@"====== START DYLIB INJECT ======");
    NSLog(@"====== GETTING METHOD ======");
    Method origMethod = class_getInstanceMethod(NSClassFromString(@"CXApplication"), NSSelectorFromString(@"daysLeft"));
    Method newMethod = class_getInstanceMethod([CrossOverPatch class], @selector(orphansArray:));
    method_exchangeImplementations(origMethod, newMethod);
    NSLog(@"====== METHOD SWIZZLED ======");
}
```
我们一行一行地讲解代码：
1. 函数`load`定义。`load`函数会在动态库**被加载时**触发；
2. 打印日志；
3. 同上；
4. 定义变量`origMethod`，它的类型是`Method`，它的值是**原程序的**`daysLeft`方法。
    1. `class_getInstanceMethod::`函数可以获取一个类（第一个参数）的一个实例方法（第二个参数）；
    2. `NSSelectorFromString:`可以通过一个字符串（第一个参数）来获取一个类；
    3. `NSSelectorFromString`可以通过一个字符串（第一个参数）获取一个`Selector`；
5. 定义变量`newMethod`，类型是`Method`，它的值是**我们刚才自定义的`daysLeftHook`方法**，我们要用这个方法来替换第4行的`daysLeft`方法。
6. 将第四行和第五行定义的新、旧两个函数通过`method_exchangeImplementations::`交换。这样的话，原程序的`daysLeft`就成了我们自定义的`daysLeftHook`，而我们自定义的`daysLeftHook`就成了原程序的`daysLeft`，也就意味着成功 hook 了。
7. 打印日志。

`CrossOverPatch.m`写完了。别忘了打开`CrossOverPatch.h`文件，声明函数：
```objc
@interface CrossOverPatch : NSObject
+(void)load;
@end
```
按下`Cmd` + `B`编译一下，最终得到动态库文件：`libCrossOverPatch.dylib`！

# 注入动态库

离破解只差一步——注入。方法有许多：运行`bash`脚本、修改`info.plist`……不过我更倾向于使用`insert_dylib`工具注入。点击[这个链接](xcode://clone?repo=https%3A%2F%2Fgithub.com%2FTyilo%2Finsert_dylib)即可将`insert_dylib`项目克隆到`Xcode`，编译得到`insert_dylib`可执行文件。

1. 把`insert_dylib`、`CrossOverPatch.dylib`和 CrossOver 19 应用程序的**原来的二进制文件**的**绝对**路径记录下来。
2. 打开终端，输入命令：
    ```bash
    $ cd [insert_dylib的路径]
    $ ./insert_dylib [dylib的路径] [原来的二进制文件的路径]
    ```

回车后，如果出现`LC_CODE_SIGNATURE load command found. Remove it? [y/n]`，那么就按下`y`，回车。

如果出现`Added LC_LOAD_DYLIB to /Applications/CrossOver.app/Contents/MacOS/CrossOver_patched`，代表注入成功。

打开访达，进入`/Applications/CrossOver.app/Contents/MacOS/`位置，你还会发现有两个文件：`CrossOver`和`CrossOver_patched`。其中`CrossOver_patched`就是**已经被我们注入的**文件。将原来的`CrossOver`二进制删除或更改名称，将`CrossOver_patched`更名为`CrossOver`。

# 改头换面

通过下图找到电子权利信息：

![电子权利信息路径](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-creditspath.png)

找到后，用文本编辑打开，在文件开头加上一句类似下面的话：

> 这个版本的CrossOver已经由xxx破解。你可以放心使用。注意，请勿广泛传播……

# 验证破解

双击`CrossOver`二进制文件，即可打开应用程序。可以看见试用天数已经破解：

![剩余天数破解成功](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-36600.png)

电子权利信息也被修改：

<img src="https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-co-credits.png" alt="留下足迹" style="zoom:50%;" />

与此同时，你的电脑应该会弹出终端窗口：

```bash
====== START DYLIB INJECT ======
====== GETTING METHOD ======
====== METHOD PATCHING ======
====== METHOD SWIZZLED ======
```