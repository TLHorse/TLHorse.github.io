---
title: "使用动态库优雅破解 AppDelete"
date: "2020-03-29T16:40:17+08:00"
description: "前言 我最近一直在寻找如何使用动态库注入的方法完美 Hook 应用程序的方法。像、这样的框架都找遍了，可就是找不到真正的香格里拉——要么就是版本太低，要么就是缺少文档。"
categories:
  - "计算机"
tags:
  - "反编译"
  - "hook"
---

# 前言

我最近一直在寻找如何使用动态库注入的方法完美 Hook `macOS` 应用程序的方法。像`MonkeyAppMac`、`EasySIMBL`这样的框架都找遍了，可就是找不到真正的香格里拉——要么就是版本太低，要么就是缺少文档。

我刷飘云阁论坛时偶然看到了 tree_fly 大神原创的[这篇帖子](https://www.chinapyg.com/forum.php?mod=viewthread&tid=82610&highlight=mac)，介绍了如何破解`AppDelete`。它真正让我明白了 `macOS` 动态库注入的工作原理与注入方法，然而文章有些地方写的却过于跳步、不尽人意。我~~有感而发~~，把原帖的某些地方改了改，将不容易理解的地方进一步解释，然后改编成这篇文章。

# 准备

- [AppDelete](http://www.reggieashworth.com)：`AppDelete`是Mac的卸载程序，不仅可以删除应用程序，还可以删除小部件，首选项窗格，插件和屏幕保护程序及其关联文件。 如果没有`AppDelete`，这些关联的项目将被留下来占用空间并可能引起问题。 下载完软件后没你可以先打开软件熟悉一下，
- Hopper Disassembler v4
- Xcode：此处用的版本是`Version 11.3.1 (11C504)`。

# 分析软件

因为软件支持中文，所以我们可以通过字符串本地化文件来判断中文对应的英文。打开软件的资源目录中的中文目录：

```
/Applications/AppDelete.app/Contents/Resources/zh_CN.lproj
```

找到本地中文资源文件 `Localizable.strings`，注意到如下信息：

```
"AppDelete Registration" = "AppDelete 注册";
"Registration Accepted" = "接受注册";
"Registration Rejected" = "拒绝注册";
"Register" = "注册";
```

将软件载入Hopper，查找上面的英文字符串。通过寻找引用的方法（X），找到程序验证的核心：

```objective-c
/* @class ADController */
/* Address: 0x1000118add */
-(void)deletePaths:(void *)arg2 {
    r14 = [[self->plistOne stringValue] retain];
    r15 = [[r14 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
    var_30 = [r15 isEqualTo:@""];
    [r15 release];
    [r14 release];
    var_38 = self;
    r15 = [[self->extensionMaster stringValue] retain];
    rbx = [[r15 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
    rdx = @"";
    r14 = [rbx isEqualTo:rdx];
    [rbx release];
    [r15 release];
    if (var_30 != 0x1) {
            rdx = @"";
            if (r14 != 0x1) {
                    r14 = [[var_38->extensionMaster stringValue] retain];
                    rbx = [[r14 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
                    rdx = rbx;
                    r15 = [var_38 orphansArray:rdx]; // 1
                    [rbx release];
                    [r14 release];
                    if (r15 != 0x0) {
                            // 2
                            rbx = [[NSBundle mainBundle] retain];
                            r15 = [[rbx localizedStringForKey:@"Registration Accepted" value:@"" table:0x0] retain];
                            var_48 = r15;
                            [rbx release];
                            intrinsic_movsd(xmm1, *double_value_0_607843);
                            intrinsic_movsd(xmm3, *double_value_1);
                            intrinsic_xorpd(xmm0, xmm0);
                            rax = [NSColor colorWithCalibratedRed:@"Registration Accepted" green:@"" blue:r8 alpha:r9];
                            rax = [rax retain];
                            rbx = *ivar_offset(zipFiles);
                            [*(var_38 + rbx) setTextColor:rax, @""];
                            [*(var_38 + rbx) setStringValue:r15, @""];
                            [*(var_38 + rbx) setHidden:0x0, @""];
                            [var_38->zButton setEnabled:0x0, @""];
                            [var_38->qButton setEnabled:0x0, @""];
                            [var_38->plistOne setEnabled:0x0, @""];
                            r15 = *ivar_offset(extensionMaster);
                            [*(var_38 + r15) setEnabled:0x0, @""];
                            [var_38->helpP setEnabled:0x0, @""];
                            r13 = [[*(var_38 + r15) stringValue] retain];
                            rbx = [[r13 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
                            var_40 = [[rbx dataUsingEncoding:0x4, @""] retain];
                            [rbx release];
                            [r13 release];
                            rbx = [[NSUserDefaults standardUserDefaults] retain];
                            r12 = [[var_38->plistOne stringValue] retain];
                            [rbx setObject:r12 forKey:@"ADFieldOne"];
                            [r12 release];
                            [rbx release];
                            rbx = [[NSUserDefaults standardUserDefaults] retain];
                            [rbx setObject:var_40 forKey:@"ADFieldTwo"];
                            [rbx release];
                            *(int8_t *)&var_38->archiveRun = 0x1;
                            *(int8_t *)&var_38->undoList = 0x0;
                            [var_40 release];
                            [rax release];
                            rdi = var_48;
                    }
                    else {
                            // 3
                            r15 = [[var_38->plistOne stringValue] retain];
                            rbx = [[r15 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
                            NSLog(@"AD Rejected Name ~ %@", rbx);
                            [rbx release];
                            [r15 release];
                            r15 = [[var_38->extensionMaster stringValue] retain];
                            rbx = [[r15 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
                            NSLog(@"AD Rejected Serial Number ~ %@", rbx);
                            [rbx release];
                            [r15 release];
                            rbx = [[NSBundle mainBundle] retain];
                            r15 = [[rbx localizedStringForKey:@"Registration Rejected" value:@"" table:0x0] retain];
                            [rbx release];
                            intrinsic_movsd(xmm0, *double_value_0_921569);
                            intrinsic_movsd(xmm3, *double_value_1);
                            intrinsic_xorpd(xmm1, xmm1);
                            r14 = [[NSColor colorWithCalibratedRed:@"Registration Rejected" green:@"" blue:r8 alpha:r9] retain];
                            rbx = *ivar_offset(zipFiles);
                            [*(var_38 + rbx) setTextColor:r14, @""];
                            [*(var_38 + rbx) setStringValue:r15, @""];
                            [*(var_38 + rbx) setHidden:0x0, @""];
                            [var_38->plistOne setStringValue:@"", @""];
                            [var_38->extensionMaster setStringValue:@"", @""];
                            *(int8_t *)&var_38->archiveRun = 0x0;
                            [r14 release];
                            rdi = r15;
                    }
            }
            else {
                    r15 = [[var_38->plistOne stringValue] retain];
                    rbx = [[r15 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
                    NSLog(@"AD Rejected Name ~ %@", rbx);
                    [rbx release];
                    [r15 release];
                    r15 = [[var_38->extensionMaster stringValue] retain];
                    rbx = [[r15 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
                    NSLog(@"AD Rejected Serial Number ~ %@", rbx);
                    [rbx release];
                    [r15 release];
                    rbx = [[NSBundle mainBundle] retain];
                    r15 = [[rbx localizedStringForKey:@"Registration Rejected" value:@"" table:0x0] retain];
                    [rbx release];
                    intrinsic_movsd(xmm0, *double_value_0_921569);
                    intrinsic_movsd(xmm3, *double_value_1);
                    intrinsic_xorpd(xmm1, xmm1);
                    r14 = [[NSColor colorWithCalibratedRed:@"Registration Rejected" green:@"" blue:r8 alpha:r9] retain];
                    rbx = *ivar_offset(zipFiles);
                    [*(var_38 + rbx) setTextColor:r14, @""];
                    [*(var_38 + rbx) setStringValue:r15, @""];
                    [*(var_38 + rbx) setHidden:0x0, @""];
                    [var_38->plistOne setStringValue:@"", @""];
                    [var_38->extensionMaster setStringValue:@"", @""];
                    *(int8_t *)&var_38->archiveRun = 0x0;
                    [r14 release];
                    rdi = r15;
            }
    }
    else {
            r15 = [[var_38->plistOne stringValue] retain];
            rbx = [[r15 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
            NSLog(@"AD Rejected Name ~ %@", rbx);
            [rbx release];
            [r15 release];
            r15 = [[var_38->extensionMaster stringValue] retain];
            rbx = [[r15 stringByReplacingOccurrencesOfString:@" " withString:@""] retain];
            NSLog(@"AD Rejected Serial Number ~ %@", rbx);
            [rbx release];
            [r15 release];
            rbx = [[NSBundle mainBundle] retain];
            r15 = [[rbx localizedStringForKey:@"Registration Rejected" value:@"" table:0x0] retain];
            [rbx release];
            intrinsic_movsd(xmm0, *double_value_0_921569);
            intrinsic_movsd(xmm3, *double_value_1);
            intrinsic_xorpd(xmm1, xmm1);
            r14 = [[NSColor colorWithCalibratedRed:@"Registration Rejected" green:@"" blue:r8 alpha:r9] retain];
            rbx = *ivar_offset(zipFiles);
            [*(var_38 + rbx) setTextColor:r14, @""];
            [*(var_38 + rbx) setStringValue:r15, @""];
            [*(var_38 + rbx) setHidden:0x0, @""];
            [var_38->plistOne setStringValue:@"", @""];
            [var_38->extensionMaster setStringValue:@"", @""];
            *(int8_t *)&var_38->archiveRun = 0x0;
            [r14 release];
            rdi = r15;
    }
    [rdi release];
    return;
}
```

1. `orphansArray:`函数应该是一个判断函数。如果你点进去，你可以看到函数声明中有严谨的判断流程；
2. 如果代码执行到这里，那么就代表验证成功，可以使用App；
3. 执行到这里，就是验证失败。

此时如果你把`orphansArray:`的返回值修改为0x1：

```assembly
mov eax, 0x1
ret
```

那么你会发现软件运行、重启后，注册验证都通过了，同时注册按钮已经变灰，注册成功！你也可以根据`orphansArray:`的验证流程来写注册机。当然这些不是本篇文章的重点，接下来为大家介绍如何使用动态库注入来修改函数返回值。

# 代码劫持

## 原理

简单的说，在`Windows`下，很多时候我们在软件`.exe`同一目录下放置`version.dll`、`lpk.dll`等劫持文件，依照规则`.exe`优先加载了当前目录下`.dll`，可以偷偷摸摸做很多想做的事。

同理，在`macOS`下，思路是相同的，你可以想尽一切办法让App加载我们的动态库。加载完自定义的动态库，破解即成功。

## 动态库编写

1. 首先，[打开Xcode](xcode://)（你会神奇的发现如果你点击这个链接你的Xcode就会打开）。在`macOS`平台里选择 `Framework & Library `> `Library`。使用此模板新建一个项目，名称随便起，此处叫做`AppDeletePatch`，`Framework`选择`Cocoa`，`Type`选择`Dyamic`（动态）。

   ![选择模版](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ad-choose-temp.png)

   这一步可以创建一个动态库工程。这个动态库就是我们要注入的动态库。

   其次，我们打开`AppDeletePatch.m`文件。接下来我一步步带你编写动态库代码：

2. 我们用两个`#import`语句，将`AppDeletePatch.h`文件与`objc/runtime.h`。`AppDeletePatch.h`文件（头文件），是每个`.m`文件里必须引用的。而`objc/runtime.h`库是什么？这就是很多小白不了解的地方之一。简单的解释，`runtime`是`C`类语言**"运行时"机制**的一个强大的库。通过这个库里的方法，可以在运行时实现对OC函数的 hook。

   ```objective-c
#import "AppDeletePatch.h"
   #import <objc/runtime.h>
   ```
   
   现在，这两行代码明白了吧！

3. 接下来，在两个引入语句的下面编写：

   ```objective-c
   @implementation AppDeletePatch
   
   
   
   @end
   ```

   在`Objective-C`语言中，可以使用`implementation`进行一个类的具体实现，类的实现代码以`@implementation`开始，以`@end`结束。这就类似于`Python`、`Swift`的`class`。**这部分代码通常都是放在`.m`文件中**。

4. 然后，我们在`@implementation`的内部，声明一个函数：

   ```objective-c
   - (char)orphansArray:(NSString *)data {
       NSLog(@"====== METHOD PATCHING ======");
       return 0x1;
   }
   ```

   这又涉及了`OC`的语法，我们简单说一下。这样写，是实现了一个函数，函数名是`orphansArray:`。而冒号后面跟的是函数的参数列表`(NSString *)data`。这里声明了一个类型为`NSString`的参数`data`。而前面的`(char)`则代表函数的返回值。

   如果你把原程序里`orphansArray:`的函数声明伪代码与这里的函数声明做对比，你会发现，这里的函数声明与原程序的函数声明一模一样。

   你可能会疑问，函数前面的减号是干嘛的？类方法以`+`号开头，对象方法以`-`号开头。

   函数里的两行代码就好解释了。`NSLog:`就是日志输出，相当于`Swift`和`Python`下的`print()`，这里我打印了一条信息以便记录；`return`就是返回的意思，此处返回了`0x1`一值。

   `orphansArray:`的实现就到此结束了。

5. 在`orphansArray:`的实现后，空上几行，然后输入`load`。`Xcode`的自动补全功能会弹出列表。在列表第一行回车，之后在添上大括号：

   ```objective-c
   + (void)load {
   
   }
   ```

   这个方法是干什么的？每当将类或类别添加到Objective-C的`runtime`时会被调用； 实现此方法以在加载时执行特定于类的行为。`load`方法的初始化顺序如下：
   1. 您链接到的任何框架中的所有初始化程序。
   2. 图片中的所有` + load`方法。
   3. 图像中的所有`C++`静态初始化程序和`C` / `C ++` `__attribute __(constructor)`函数。
   4. 链接到您的框架中的所有初始化程序。

   我们在`load`里键入：

   ```objective-c
   NSLog(@"====== START DYLIB INJECT ======");
   
   NSLog(@"====== GETTING METHOD ======");
   Method origMethod = class_getInstanceMethod(NSClassFromString(@"ADController"), NSSelectorFromString(@"orphansArray:")); // 1
   Method newMethod = class_getInstanceMethod([AppDeletePatch class], @selector(orphansArray:)); // 2
   
   method_exchangeImplementations(origMethod, newMethod); // 3
   NSLog(@"====== METHOD SWIZZLED ======");
   ```

   1. 通过`class_getInstanceMethod`函数，获取程序里`orphansArray:`的原函数；
   2. 这一行代码与`3`同理，只不过是获取我们声明的替换函数`orphansArray:`；
   3. 通过`method_exchangeImplementations`函数替换刚才获取的两个新旧函数。

   其中：

   - `NSClassFromString`可以通过字符串获取类；
   - `NSSelectorFromString`可以通过字符串获取方法；
   - `[AppDeletePatch class]`代表`AppDeletePatch`类的`class`本身；
   - 通过`@selector`直接获取一个函数。

到此，动态库的代码编写结束。整体的代码应该长这样：

```objective-c
#import "AppDeletePatch.h"
#import <objc/runtime.h>

@implementation AppDeletePatch

- (char)orphansArray:(NSString *)data {
    NSLog(@"====== METHOD PATCHING ======");
    return 0x1;
}

+ (void)load {
    NSLog(@"====== START DYLIB INJECT ======");

    NSLog(@"====== GETTING METHOD ======");
    Method origMethod = class_getInstanceMethod(NSClassFromString(@"ADController"), NSSelectorFromString(@"orphansArray:"));
    Method newMethod = class_getInstanceMethod([AppDeletePatch class], @selector(orphansArray:));

    method_exchangeImplementations(origMethod, newMethod);
    NSLog(@"====== METHOD SWIZZLED ======");
}

@end
```

## 动态库注入

编写完动态库，就可以注入了。按下`Cmd`+`B`编译，得到`.dylib`文件。

之后我们要注入。原作者用的是`bash`脚本，但是这样做比较费事，容易发生权限错误，因此我们用`insert_dylib`工具注入。点击[这个链接](xcode://clone?repo=https%3A%2F%2Fgithub.com%2FTyilo%2Finsert_dylib)将`insert_dylib`项目克隆到`Xcode`，并且编译，得到`insert_dylib`二进制文件。

我们将动态库、二进制文件和`AppDelete`应用程序的路径分别记录下来，然后打开终端，执行命令（记得替换路径）：

```bash
$ ./insert_dylib xxx/libAppDeletePatch.dylib xxx/AppDelete.app/Contents/MacOS/AppDelete
```

注：`./insert_dylib`的用法是：

```bash
./insert_dylib [要被注入的动态库的路径] [要注入的二进制文件]
```

注意第二个参数，是要注入的**二进制文件**，而不是`.app`文件，或者其他。还要注意，路径要使用**绝对路径**。

回车后，如果出现`LC_CODE_SIGNATURE load command found. Remove it? [y/n]`，那么就按下`y`，回车。

如果出现`Added LC_LOAD_DYLIB to /Applications/AppDelete.app/Contents/MacOS/AppDelete_patched`，代表注入成功。

回到`/Applications/AppDelete.app/Contents/MacOS/`路径，会发现多出一个`AppDelete_patched`文件。这就是已注入动态库的二进制文件。把原先的`AppDelete`二进制更名或删除，然后将`AppDelete_patched`更名为`AppDelete`。

![重命名](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/3/27/hop-ad-chname.png)

# 验证破解

我们现在不要用正常的方法打开软件。我们还保持上一步的目录（`MacOS`），然后双击已经被注入的二进制文件，应用也会打开。不过同时会打开一个终端窗口，在这个窗口中就可以看到我们在写代码时使用`NSLog`语句打印的内容了：

```bash
====== START DYLIB INJECT ======
====== GETTING METHOD ======
====== METHOD PATCHING ======
====== METHOD SWIZZLED ======
```

成功破解！
