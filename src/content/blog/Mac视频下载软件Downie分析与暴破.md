---
title: "Mac视频下载软件Downie分析与暴破"
date: "2022-02-16T16:37:11+08:00"
description: "Downie，全能的网络视频下载软件。在论坛中搜索Downie，一大把一大把的TNT破解出现在眼前。"
categories:
  - "计算机"
tags:
  - "反编译"
---

Downie，全能的网络视频下载软件。在论坛中搜索Downie，一大把一大把的TNT破解出现在眼前。但是求人不如求己，因此本文主要介绍Downie暴破，技术含量不是很大，包含中变量的tweak，和动态库之间交互的分析。

# 软件分析
打开Downie，在一系列的初始化后，会弹出试用期限窗口，提醒试用倒计时（14天）。操作可知，在试用期限中，软件的所有功能都可以正常使用。点开菜单栏中的`Downie 4`，可以看到几个关于注册的按钮。
![downie-1](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2022/02/16/downie-1.png)
通过我们观察到的元素，可以分析出如下三种逆向方案：
1. **分析算法写注册机**：现在软件都是联网注册，分析算法没啥用；
2. **修改剩余天数为定值**：分析非常简单；
3. **修改全局已注册变量**：也很简单，需同时去除校对验证函数。

本文介绍二三两种方法。

# 代码分析
把主程序二进制拖进Hopper进行分析。对于这种应用程序的启动弹窗来说，懂Apple开发的都知道，我们可以从macOS应用程序的生命周期入手。搜索`appDidFinishLaunching`可以找到如下符号：
```
s6Downie13XUAppDelegateC29applicationDidFinishLaunchingyy10Foundation12NotificationVF
```
该函数会在程序启动完成后被调用。我们在`loc_100037546`中可以找到一些有关license的代码：
```asm
call imp___stubs__$s9Licensing11CMLicensingCMa
mov  r13, rax
call imp___stubs__$s9Licensing11CMLicensingC6sharedACvgZ
mov  rbx, rax
mov  rax, qword [_$s9Licensing11CMLicensingC8delegateAA0B8Delegate_pSgvpWvd_100118910]
mov  qword [rbp+var_30], r14
mov  r12, qword [rax]
lea  r14, qword [rbx+r12]
lea  rsi, qword [rbp+var_E8]
mov  edx, 0x1
mov  rdi, r14
xor  ecx, ecx
call imp___stubs__swift_beginAccess
lea  rax, qword [_$s6Downie13XUAppDelegateC9Licensing011CMLicensingC0AAWP]
```
随便找一个call跟踪进去，都可以看到外部代码，在注释中都可看到如下路径：
```asm
; in @executable_path/../Frameworks/Licensing.framework/Versions/A/Licensing
```
我们发现，Downie对license的验证流程原来写到了Licensing附加库中。把它拖到Hopper中，转而分析Licensing！

# 破解一：修改剩余天数
观察代码风格，很明显Licensing是Swift写的。搜索`days`这样的字眼，在搜索结果中找`getter`，很明显可以找到一个Swift整型变量：`s9Licensing11CMLicensingC21numberOfDaysRemainingSivg`（符号），返回一个`int`值。在汇编中，把返回寄存器`rax`改为定值。
```asm
mov rax, 0xff
ret
```
![downie-3](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2022/02/25/downie-3.png)
嘿嘿，剩余天数从14天一下飙升到255天。在系统设置里怎么改日期，都不会变！朋友们，破解已经成功！

其实有一个遗憾，每次启动都会弹出这个窗口。我总想把它去掉，但找了许多有关的函数和`windowDidLoad`方法，很奇怪都未能实现。

# 破解二（完美）：修改全局注册变量

抱着试试看的心态。我搜索了`islicensed`关键词，没想到还真有这么明显的匹配项：
```
s9Licensing11CMLicensingC10isLicensedSbvg
```
赶快把`rax`改成0x1，启动调试，仍然未注册（节省空间，此处不贴图）。这说明软件获取注册状态调用的不是这个函数。到底是哪个环节出了问题？瞟一眼伪代码：
```objc
int _$s9Licensing11CMLicensingC10isLicensedSbvg() {
    [sub_11600() release];
    [rdx release];
    r14 = [rcx activated];
    [rcx release];
    rax = r14 != 0x0 ? 0x1 : 0x0;
    return rax;
}
```
莫名其妙发现了一个名为`activated`的selector，无交叉引用，无来源。很有可能是外部符号。看看Downie还有什么库：还有Paddle没用呢！

把Paddle拽到Hopper分析，搜索`activated`，得到结果：
```objc
/* @class PADProduct */
-(char)activated {
    rax = [self licenseController];
    rax = (*(*rax + 0x58))(rax);
    return rax;
}
```
很标准的类方法，返回`char`类型，就是它了。打开汇编，`rax`改为1：
```asm
mov rax, 1
ret
```
![downie-4](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2022/02/25/downie-4.png)
很可恶，Downie直接崩溃！但这是个好消息，证明了我们的tweak是成功的，只是被某个检验流程检测到了。别慌，接着找找同类的关键词：
![downie-5](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2022/02/25/downie-5.png)
开发者小心思真多！两个verify函数，第一个指向第二个，我们看看0x95c5的代码：
```objc
/* @class PADProduct */
-(void)verifyActivationDetailsWithCompletion:(void *)arg2 {
    r13 = self;
    r14 = [arg2 retain];
    rax = [r13 licenseController];
    if (((*(*rax + 0x50))(rax) == 0x0) && ([r13 activated] == 0x0)) {
            r15 = [[PADErrorFactory errorWithCode:0xffffffffffffff94] retain];
            if (r14 != 0x0) {
                    var_88 = *__NSConcreteStackBlock;
                    *(&var_88 + 0x8) = 0xffffffffc2000000;
                    *(&var_88 + 0x10) = ___52-[PADProduct verifyActivationDetailsWithCompletion:]_block_invoke;
                    *(&var_88 + 0x18) = ___block_descriptor_48_ea8_32bs40s_e5_v8?0l;
                    *(&var_88 + 0x20) = [r14 retain];
                    *(&var_88 + 0x28) = [r15 retain];
                    dispatch_async(*__dispatch_main_q, &var_88);
                    [*(&var_88 + 0x28) release];
                    [*(&var_88 + 0x20) release];
            }
            else {
                    [r13 sendErrorToPaddleDelegateIfResponsive:r15];
            }
            rdi = r15;
    }
    else {
            rax = [NSDate date];
            rax = [rax retain];
            [r13 setLastVerifyDate:rax];
            [rax release];
            [r13 saveProductFile];
            r12 = [r13 determineActivationService];
            r15 = [r13 licenseController];
            var_58 = *__NSConcreteStackBlock;
            *(&var_58 + 0x8) = 0xffffffffc2000000;
            *(&var_58 + 0x10) = ___52-[PADProduct verifyActivationDetailsWithCompletion:]_block_invoke.209;
            *(&var_58 + 0x18) = ___block_descriptor_48_ea8_32s40bs_e28_v32?0q8q16"NSDictionary"24l;
            *(&var_58 + 0x20) = r13;
            *(&var_58 + 0x28) = [r14 retain];
            (*(*r15 + 0x68))(r15, r12, &var_58);
            rdi = var_30;
    }
    [rdi release];
    [r14 release];
    return;
}
```
观察到`PADErrorFactory`类，检测到问题会调用这个类的函数。怪不得程序会崩溃！转到汇编，赶紧`ret`掉。
```asm
ret
```
![downie-6](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2022/02/25/downie-6.png)
这波破解顺理成章，基本没怎么调试，完美暴破！

从破解的过程，可以梳理出Downie的业务逻辑结构如下：
![关系](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2022/02/17/downie-2.png)

# 禁用取消激活功能
破解完后我们发现一个小问题，即点击取消激活后Downie会先弹出对话框，确定后app崩溃。
![取消激活](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2022/02/26/downie-7.png)
与其分析算法不如直接去掉这个功能。我们大致可推测功能应该在Licensing中。搜索deactivate关键词可搜到好多函数，但我们选择下面这个：
```objc
void _$s9Licensing11CMLicensingC17deactivateLicenseyyF(int arg0, int arg1, int arg2, int arg3, int arg4) {
    rdx = arg2;
    [sub_11600() release];
    [rdx release];
    r14 = [arg3 activated];
    [arg3 release];
    if (r14 == 0x0) goto loc_10ba3;

loc_10830:
    var_30 = [objc_allocWithZone(@class(NSAlert)) init];
    if (*qword_28418 != 0xffffffffffffffff) {
            swift_once(qword_28418, sub_a6b0, rdx);
    }
    sub_1ca70();

// ............
```
为啥选的是这个？因为这个函数里有`NSAlert`的初始化。如果想去掉，`ret`即可。

# 总结

可以看到Downie的静态库还真不少。这次破解主要是以静态分析为主，但要调试的话，也没问题。我破解速度并不是很快，总是不断试错。本人逆向能力也需要提升啊。