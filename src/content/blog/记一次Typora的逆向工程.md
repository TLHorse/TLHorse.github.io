---
title: "记一次Typora的逆向工程"
date: "2021-12-31T12:30:51+08:00"
description: "前言 学业负担逐渐加重，好久没有整逆向工程了。正巧最近我用的Markdown编辑器发布了1."
categories:
  - "计算机"
tags:
  - "反编译"
---

# 前言

学业负担逐渐加重，好久没有整逆向工程了。

正巧最近我用的Markdown编辑器发布了1.0版本，到官网看看，发现开始收费了，售价 $14.99 ，最多三台设备。可以先进行试用，试用期到了，就需要付费。抱着试试看的心态，今天就拿Typora Mac练练手。

# 分析

把Typora丢进Hopper里分析一波。对于这个简单轻量级的软件，我很容易就可以搜到关键词。拿subscription、trial、days、license这些敏感词试一试，就可以发现一些相关的OC类，例如`LicenseManager`和`LicenseWindowController`。我将一些之后需要逆向的函数加了黑。

<img src="https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/12/11/typora-search.png" alt="搜索关键词" style="zoom:50%;" />

先打开` -[LicenseManager hasLicense]`，看上去是判断是否有许可证的函数。生成伪代码，很容易发现是个简单的逻辑判断流程，rax寄存器储存返回值。

```objc
/* @class LicenseManager */
-(char)hasLicense {
    rdi = self->_hasLicense;
    if (rdi != 0x0) {
            rax = [rdi boolValue];
            rax = rax != 0x0 ? 0x1 : 0x0;
    }
    else {
            rax = 0x1;
    }
    rax = rax & 0xff;
    return rax;
}
```

我们直接在汇编中按下<kbd>Option+A</kbd>，输入`mov rax, 0x1; ret`进行暴破，如图。

![暴破](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/12/11/typora-bp.png)

接下来，用调试器运行。很讽刺的一件事是，试用期提醒的弹窗直接消失了。我把系统时间往后调，软件仍然可以正常运行，这不是伪破解。所以，这就破解完了……

但是，还有一件事。我发现虽然暴破的软件可以正常使用，但是菜单栏上有个“查看许可证”按钮。点开它，软件就会检测出，剩余试用天数已经归零，此时弹出的窗口只有激活和退出两个按钮。

![“查看许可证”按钮](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/12/11/typora-licensebt.png)

为了防止误触这个键，就得把对话框去掉。我不想再tweak试用天数了，更懒得写注册机，所以我准备让它弹出另一个对话框，显示软件已破解。

# 逆向

既要暴破软件，还要加对话框，我就用了动态库注入破解。我用的是`MonkeyDev`框架，也就是`substrate`。先新建`MonkeyAppMac`工程，命名`TyporaTweak`，然后将Typora拖进`TargetApp`，最后打开`TyporaTweak.m`文件。

先写两个替代函数：

```objc
#include <Cocoa/Cocoa.h> // 记得引入Cocoa

@class LicenseManager; // 定义类

// hook是否有许可证
static char new_hasLicense(LicenseManager* self, SEL _cmd) {
    return 1;
}

// hook许可证弹窗
static void new_showLicense(LicenseManager* self, SEL _cmd, char arg2){
 	  // 新建一个警告弹窗
    NSString *message = @"您正在使用Typora破解版";
    NSAlert *alert = [NSAlert new];
    [alert addButtonWithTitle:@"知道了"];
    [alert setMessageText:message];
    [alert setAlertStyle:NSAlertStyleCritical];
    [alert runModal];
}
```

然后在动态库加载入口hook（一些基本的语法，可在官网上搜索，不再解释）：

```objc
static void __attribute__((constructor)) initialize(void) {
    MSHookMessageEx(objc_getClass("LicenseManager"), @selector(hasLicense), (IMP)&new_hasLicense, NULL);
    MSHookMessageEx(objc_getClass("LicenseManager"), @selector(showLicense:), (IMP)&new_showLicense, NULL);
}
```

所有的代码看起来像这样：

```objc
#import "TyporaTweak.h"
#import "substrate.h"
#include <Cocoa/Cocoa.h>

@class LicenseManager;

static char new_hasLicense(LicenseManager* self, SEL _cmd) {
    return 1;
}

static void new_showLicense(LicenseManager* self, SEL _cmd, char arg2){
    NSString *message = @"您正在使用Typora破解版";
    NSAlert *alert = [NSAlert new];
    [alert addButtonWithTitle:@"知道了"];
    [alert setMessageText:message];
    [alert setAlertStyle:NSAlertStyleCritical];
    [alert runModal];
}

static void __attribute__((constructor)) initialize(void) {
    MSHookMessageEx(objc_getClass("LicenseManager"), @selector(hasLicense), (IMP)&new_hasLicense, NULL);
    MSHookMessageEx(objc_getClass("LicenseManager"), @selector(showLicense:), (IMP)&new_showLicense, NULL);
}
```

运行一下，大功告成！

![typora破解后](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/12/11/typora-product.png)

# 动态库注入

拿到了`libTyporaTweak.lib`，就可以对二进制注入了。

```sh
 ./insert_dylib <动态库路径> <Mach-O>
```

但MonkeyDev已经帮我们完成了这一步。将Typora.app从TargetApp文件夹里拖出，即是我们的成品。

# 总结

Typora就这么被逆向完了。不得不说，它在反破解方面还有待提高。没有反调试、没有加密加壳，什么都没有。这是值得开发者维护的地方。但就软件本身而言，它的确是个良心的Markdown编辑器，值得我们去购买支持。

