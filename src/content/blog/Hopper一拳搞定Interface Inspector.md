---
title: "Hopper一拳搞定Interface Inspector"
date: "2020-03-27T16:40:17+08:00"
description: "前言 最近本打算搞定 破解版，可谁知开发者用了语言编写，导致我这个小白破解总是不得逞。忽然间听说了一个叫做的软件，感觉还挺厉害的。"
categories:
  - "计算机"
tags:
  - "反编译"
---

# 前言

最近本打算搞定 `Downie 4`破解版，可谁知开发者用了`Swift`语言编写，导致我这个小白破解总是不得逞。忽然间听说了一个叫做`Interface Inspector`的软件，感觉还挺厉害的。接下来先给大家介绍一下（这是官方介绍，不是广告）：

> `Interface Inspector` 使您可以在运行时研究任何`macOS`应用程序的用户界面结构和属性。
>
> 在程序中使用`Interface Inspector`非常容易。 您可以通过使用`Interface Inspector`中的快捷键`⌘⌥A`来使用附加菜单，然后选择要附加到的应用程序。 然后，您可以检查视图属性，或尝试使用不同的值来约束和更多。
>
> 将`Interface Inspector`附加到应用程序后，您可以使用快捷键⇧⌘K通过选择模式轻松标识各个组件。 只需单击您感兴趣的组件，它就会在`Interface Inspector`中被选中，然后开始分析其属性。

总结来说`Interface Inspector`就相当于`iOS`越狱里的`FLEX`，或者相当`macOS`下的`Reveal`。不过后两者只能用于`iOS`，而`Interface Inspector`用于`macOS`。

这个软件的**最新版本**开发要追溯到2014年，算是一个很久没有更新的软件（估计以后也不会更新），不过仍然是付费的，所以`macOS`的 crakers，这一次我带你们 patch 它！你们有福利了。

# 破解过程

这次破解，我们的目标是：随便输入注册信息，即可使用App。

## 收集信息

这个软件的最后更新是2014年——如果你懂一些历史的话，你会知道那时候 Apple 的SDK非常落后，开发者的反破解方案很简陋，因此这个软件应该比较好破解。首先我们在注册 License 界面的UI中收集一些字符串（图一是要 License 主页面，图二是输错 License 的页面）：

![license 主页面](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-ui1.png)

![license 错误界面](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-ui2.png)

我们得到的字符串：

- Enter your registration details below, exacly as you recieved in your confirmation email:
- Invalid license code
- Please go back and try again.

> 注：exacly 单词其实拼错了，应该是 exactly。不过，一切以程序中为准。

## Hopper 分析

将程序二进制文件拖入 Hopper 分析，然后在`Str`一栏随便搜索一条我们得到的信息，比如第一条，之后不断按`X`，找到代码引用的源头：`-[SMEnterLicenseViewController loadView]`，地址为`0x10010ff3a`。我们再把`SMEnterLicenseViewController`作为关键词搜索。这个类就应该是图一的视图管理器。这时候，我们发现了一个很可疑的函数`register:`。

![搜索SMVC](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-search-smelvc.png)

我们在`register:`处下个断，然后运行，随便输入一个`Name`和`License`，按下`Register`键——断下来了！这就说明，`register:`函数里包含着`License`的验证流程。

打开伪代码模式：

```objective-c
/* @class SMEnterLicenseViewController */
-(void)register:(void *)arg2 {
    rdx = arg2;
    r15 = self;
    [self commitEditing];
    r14 = [[r15 licenseName] retain];
    if ([r14 length] != 0x0) {
            rbx = [[r15 licenseCode] retain];
            r12 = [rbx length];
            [rbx release];
            [r14 release];
            if (r12 != 0x0) {
                    r14 = [[r15 delegate] retain];
                    r12 = [[r15 licenseName] retain];
                    rbx = [[r15 licenseCode] retain];
                    [r14 enterLicenseViewControllerDidSelectRegister:r15 withLicenseName:r12 code:rbx];
                    rdi = rbx;
                    [rdi release];
                    [r12 release];
                    [r14 release];
            }
    }
    else {
            [r14 release];
    }
    return;
}
```

可以看见，第16行调用了方法`enterLicenseViewControllerDidSelectRegister:withLicenseName:code:`。我们双击看看这个方法：

```objective-c
/* @class SMLicenseWindowController */
-(void)enterLicenseViewControllerDidSelectRegister:(void *)arg2 withLicenseName:(void *)arg3 code:(void *)arg4 {
    r8 = arg4;
    var_30 = self;
    r12 = [arg3 retain];
    r13 = [r8 retain];
    rax = [SMLicenseManager sharedInstance];
    rax = [rax retain];
    var_38 = rax;
    rcx = r13;
    rbx = [rax registerLicenseWithName:r12 code:rcx];
    [r13 release];
    [r12 release];
    if (rbx != 0x0) {
            [var_30 loadView:0x2, rcx, r8];
            r14 = [[var_30 delegate] retain];
            [r14 licenseWindowControllerDidRegister:var_30, rcx, r8];
            [r14 release];
    }
    else {
            [var_30 loadView:0x1];
    }
    [var_38 release];
    return;
}
```

我们仔细品这段代码。第11行`rbx`右调用了另一个函数，不过不要紧，`rbx`应该是一个布尔值。因为第14行的判断说明，如果`rbx`为真，那么就会执行`if`代码。你再看看`if`里的第17行代码里调用了`licenseWindowControllerDidRegister`方法，从字面来看有“注册成功”的意思，因此`if`里的代码是我们想要执行的，而不是`else`里的代码。

上面一自然段完全是我的逻辑判断。如果你觉得我说得啰嗦，你可以通过**下断点**来一步步判断代码到底执行了`if`，还是`else`。

## 修改 License 验证

想必这一步在坐各位都会了吧！打开`CFG Mode`，然后按照图中的方式 patch：

![CFG Patch](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-cfg-patch.png)

```asm
jne loc_10010d137
```

我们导出二进制，然后打开应用，成……咦？

![签名错误](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-signerr.png)

## 修复签名验证

就如提示框说的一样，这个开发者也确实不是傻子，还知道验证个签名，防止程序被 Crack。不过别着急，先用提示框中的文字搜索一波 String：

![搜索签名 string](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-search-sign.png)

看到了吗？红框中的 String 就是提示框中的字符串。

> 这里教大家一个小常识，开发软件中怎样不让别人在逆向中搜索你的 String：你可以将必要的提示框间接写在一个`.html`中，这样字符串就不会再程序里直接出现。

之后，我们随便点开一个字符串，不断按`X`查找引用，终于在`applicationWillFinishLaunching:`启动函数中的`loc_100024851`找到。

```assembly
loc_100024851:
    r14 = [[NSAlert alloc] init];
    var_F8 = r14;
    r13 = [[NSBundle mainBundle] retain];
    rbx = [[r13 localizedStringForKey:@"Signature of the Interface Inspector is broken" value:@"" table:0x0] retain];
    [r14 setMessageText:rbx];
    [rbx release];
    [r13 release];
    r13 = [[NSBundle mainBundle] retain];
    rbx = [[r13 localizedStringForKey:@"The application has an unepected signature and seems to be broken or modified. Please re-download the application." value:@"" table:0x0] retain];
    [var_F8 setInformativeText:rbx];
    rdi = rbx;
    rbx = *_objc_release;
    [rdi release];
    [r13 release];
    r12 = rbx;
    [var_F8 setAlertStyle:0x2];
    r13 = [[NSBundle mainBundle] retain];
    rbx = [[r13 localizedStringForKey:@"Quit" value:@"" table:0x0] retain];
    [[[var_F8 addButtonWithTitle:rbx] retain] release];
    [rbx release];
    [r13 release];
    r13 = [[NSBundle mainBundle] retain];
    rbx = [[r13 localizedStringForKey:@"Visit Website" value:@"" table:0x0] retain];
    rdx = rbx;
    [[[var_F8 addButtonWithTitle:rdx] retain] release];
    [rbx release];
    [r13 release];
    if ([var_F8 runModal] == 0x3e8) {
            [**_NSApp terminate:0x0];
    }
    else {
            r14 = [[NSWorkspace sharedWorkspace] retain];
            r13 = [[[[NSBundle mainBundle] retain] localizedStringForKey:@"http://www.interface-inspector.com" value:@"" table:0x0] retain];
            rbx = [[NSURL URLWithString:r13, @"", 0x0] retain];
            [r14 openURL:rbx, @"", 0x0];
            (r12)(rbx, @selector(openURL:), rbx, @"", 0x0);
            (r12)(r13, @selector(openURL:), rbx, @"", 0x0);
            (r12)(rax, @selector(openURL:), rbx, @"", 0x0);
            (r12)(r14, @selector(openURL:), rbx, @"", 0x0);
            [**_NSApp terminate:0x0, @"", 0x0];
    }
    [var_F8 release];
    goto loc_100024b88;
```

在`CFG Mode`里，流程如下：

![签名CFG流程](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-signcfg.png)

我们只需要把主程序的最后一行`jne`改为`je`即可，也就是说，如果签名没有修改，那么就会报错；如果签名被修改，反而不会报错。

将`000000010002447e`的代码修改为：

```assembly
je loc_100024851
```

# 改头换面

接下来，我们该修改一下程序的`About`资源了。在`/Applications/Interface Inspector.app/Contents/Resources/`目录下找到`Credits.rtf`，之后在上面加上你自己的 Credit，然后在应用程序顶栏`Interface Inspector`->`About Interface Inspector`，即可看到你的 Credit：

![你的 credit](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ii-credits.png)

哈哈！我把我的名字加上去了！

# 总结

虽然这么一个简简单单的小程序，搞起来也不是多么容易。况且我第一次上手时，搜索关键词来来回回搞了很多次呢。就算我们这样破解下来，还有个小小的 bug：每次程序启动，你必须重新输入一遍 Name 和 License，只能算是不完美破解。但是搞下来还是很有收获的——毕竟这个软件本身也来之不易啊！
