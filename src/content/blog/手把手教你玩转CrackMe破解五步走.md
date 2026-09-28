---
title: "手把手教你玩转CrackMe破解五步走"
date: "2021-02-17T14:44:56+08:00"
description: "www.52pojie."
categories:
  - "计算机"
tags:
  - "注册机"
  - "swift"
  - "反编译"
---

> www.52pojie.cn
>
> 作者：@TLHorse
>
> 原创作品，吾爱破解首发

# 前言

本文所破解的CrackMe出自国外MSJ论坛的竞赛题目，原题估计找不着了，所以我共享在如下链载：

> 链接：https://share.weiyun.com/hGwzo5p4
>
> 密码：5828dk

这个app我已经打开并逆向过，确认没有病毒，如果你还不放心可以拉到虚拟机里。**为了避免违规，我逆向去除了app里的MSJ链接（点击`Help me!`不会跳转）。**我看也没有多少人破解，macOS CM也挺少的，就拿来分析一下。

题目中的五部走包括：

- 分析
- 暴力破解
- Hook
- 代码还原
- 写注册机

**macOS下的逆向很少被人提及，似乎很冷门，我今天分析这个CrackMe，涵盖这四部分，希望对用macOS的朋友有帮助。**

# 分析

![pie-view](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/17/pie-view.png)

打开看一下主页面，这个CM和别的不太相同的是，它没有“确认”“验证”之类的按钮。随便输入几组值都都没有反应。 **我们猜测这个CM会在表单变动时重复刷新验证**，在符号表里搜索到的`serialFieldDidChange`验证了我们的想法：

```objective-c
/* @class PieAppDelegate */
-(void)serialFieldDidChange {
    // init UserDefaults，Apple开发的都知道这是数据持久化
    r15 = (@selector(standardUserDefaults))(@class(NSUserDefaults), &@selector(standardUserDefaults));
    // 设置UserDefaults
    (@selector(setObject:forKey:))(r15, &@selector(setObject:forKey:), (@selector(stringValue))(self->nameField, &@selector(stringValue)), @"name");
    (@selector(setObject:forKey:))(r15, &@selector(setObject:forKey:), (@selector(stringValue))(self->serialField, &@selector(stringValue)), @"serial");
    // 验证
    (@selector(verifySerial:andName:))(self, &@selector(verifySerial:andName:), (@selector(stringValue))(self->serialField, &@selector(stringValue)), (@selector(stringValue))(self->nameField, &@selector(stringValue)));
    return;
}
```

我们可以轻松发现，`verifySerial:andName:`就是验证用户名密码的关键函数。这个CM有反调试，我就拿`frida-trace`进行跟踪，**发现每输入一个字符，就会将此函数调用一次**，更印证了我们的猜测。

# 暴力破解

话不多说，先考虑暴破。不过在动手改二进制前，我们得先瞄准一个点，到底改哪呢？我就试试`verifySerial:andName:`吧，汇编代码如下（我把失败的标签从`loc_xxx`改为`failure`）：

```assembly
                     -[PieAppDelegate verifySerial:andName:]:
0000000100001342         push       rbp
0000000100001343         mov        rbp, rsp
0000000100001346         mov        qword [rbp+var_28], rbx
000000010000134a         mov        qword [rbp+var_20], r12
000000010000134e         mov        qword [rbp+var_18], r13
0000000100001352         mov        qword [rbp+var_10], r14
0000000100001356         mov        qword [rbp+var_8], r15
000000010000135a         sub        rsp, 0xd0
0000000100001361         mov        qword [rbp+var_60], rdi
0000000100001365         mov        r13, rdx
0000000100001368         mov        r14, rcx
000000010000136b         mov        rdi, qword [qword_100002768]
0000000100001372         mov        edx, 0x4
0000000100001377         lea        rsi, qword [0x1000022b8]
000000010000137e         call       qword [0x1000022b8]
0000000100001384         mov        r15, rax
0000000100001387         lea        rsi, qword [0x1000022c8]
000000010000138e         mov        rdi, r13
0000000100001391         call       qword [0x1000022c8]
0000000100001397         cmp        rax, 0x10
000000010000139b         jne        failure

00000001000013a1         mov        edx, 0x6
00000001000013a6         lea        rsi, qword [0x1000022d8]
00000001000013ad         mov        rdi, r13
00000001000013b0         call       qword [0x1000022d8]
00000001000013b6         mov        rdi, rax
00000001000013b9         mov        edx, 0x4
00000001000013be         lea        rsi, qword [0x1000022b8]
00000001000013c5         call       qword [0x1000022b8]
00000001000013cb         mov        rbx, rax
00000001000013ce         lea        rsi, qword [0x1000022c8]
00000001000013d5         mov        rdi, rax
00000001000013d8         call       qword [0x1000022c8]
00000001000013de         mov        r12, rax
00000001000013e1         lea        rsi, qword [0x1000022e8]
00000001000013e8         mov        rdi, rbx
00000001000013eb         call       qword [0x1000022e8]
00000001000013f1         mov        rdi, rax
00000001000013f4         xor        edx, edx
00000001000013f6         mov        rsi, r12
00000001000013f9         call       imp___symbol_stub1__MD5
00000001000013fe         mov        rdx, qword [objc_cls_ref_NSString]
0000000100001405         mov        qword [rbp+var_58], rdx
0000000100001409         movzx      r9d, byte [rax+2]
000000010000140e         movzx      r8d, byte [rax+1]
0000000100001413         movzx      ecx, byte [rax]
0000000100001416         movzx      edx, byte [rax+0xf]
000000010000141a         mov        dword [rsp+0xd0+var_70], edx
000000010000141e         movzx      edx, byte [rax+0xe]
0000000100001422         mov        dword [rsp+0xd0+var_78], edx
0000000100001426         movzx      edx, byte [rax+0xd]
000000010000142a         mov        dword [rsp+0xd0+var_80], edx
000000010000142e         movzx      edx, byte [rax+0xc]
0000000100001432         mov        dword [rsp+0xd0+var_88], edx
0000000100001436         movzx      edx, byte [rax+0xb]
000000010000143a         mov        dword [rsp+0xd0+var_90], edx
000000010000143e         movzx      edx, byte [rax+0xa]
0000000100001442         mov        dword [rsp+0xd0+var_98], edx
0000000100001446         movzx      edx, byte [rax+9]
000000010000144a         mov        dword [rsp+0xd0+var_A0], edx
000000010000144e         movzx      edx, byte [rax+8]
0000000100001452         mov        dword [rsp+0xd0+var_A8], edx
0000000100001456         movzx      edx, byte [rax+7]
000000010000145a         mov        dword [rsp+0xd0+var_B0], edx
000000010000145e         movzx      edx, byte [rax+6]
0000000100001462         mov        dword [rsp+0xd0+var_B8], edx
0000000100001466         movzx      edx, byte [rax+5]
000000010000146a         mov        dword [rsp+0xd0+var_C0], edx
000000010000146e         movzx      edx, byte [rax+4]
0000000100001472         mov        dword [rsp+0xd0+var_C8], edx
0000000100001476         movzx      eax, byte [rax+3]
000000010000147a         mov        dword [rsp+0xd0+var_D0], eax
000000010000147d         lea        rdx, qword [cfstring__02X_02X_02X_02X_02X_02X_02X_02X_02X_02X_02X_02X_02X_02X_02X_02X]
0000000100001484         lea        rsi, qword [0x1000022f8]
000000010000148b         mov        rdi, qword [rbp+var_58]
000000010000148f         xor        eax, eax
0000000100001491         call       qword [0x1000022f8]
0000000100001497         mov        rdi, rax
000000010000149a         mov        rdx, qword [qword_100002770]
00000001000014a1         lea        rsi, qword [0x100002308]
00000001000014a8         call       qword [0x100002308]
00000001000014ae         test       al, al
00000001000014b0         je         failure

00000001000014b6         mov        edx, 0xd
00000001000014bb         lea        rsi, qword [0x100002318]
00000001000014c2         mov        rdi, r13
00000001000014c5         call       qword [0x100002318]
00000001000014cb         cmp        ax, 0x46
00000001000014cf         jne        failure

00000001000014d5         mov        edx, 0x4
00000001000014da         lea        rsi, qword [0x1000022b8]
00000001000014e1         mov        rdi, r14
00000001000014e4         call       qword [0x1000022b8]
00000001000014ea         mov        rbx, rax
00000001000014ed         lea        rsi, qword [0x1000022c8]
00000001000014f4         mov        rdi, rax
00000001000014f7         call       qword [0x1000022c8]
00000001000014fd         mov        r12, rax
0000000100001500         lea        rsi, qword [0x1000022e8]
0000000100001507         mov        rdi, rbx
000000010000150a         call       qword [0x1000022e8]
0000000100001510         mov        rdi, rax
0000000100001513         xor        edx, edx
0000000100001515         mov        rsi, r12
0000000100001518         call       imp___symbol_stub1__MD5
000000010000151d         movzx      r9d, byte [rax+2]
0000000100001522         movzx      r8d, byte [rax+1]
0000000100001527         movzx      ecx, byte [rax]
000000010000152a         movzx      edx, byte [rax+7]
000000010000152e         mov        dword [rsp+0xd0+var_B0], edx
0000000100001532         movzx      edx, byte [rax+6]
0000000100001536         mov        dword [rsp+0xd0+var_B8], edx
000000010000153a         movzx      edx, byte [rax+5]
000000010000153e         mov        dword [rsp+0xd0+var_C0], edx
0000000100001542         movzx      edx, byte [rax+4]
0000000100001546         mov        dword [rsp+0xd0+var_C8], edx
000000010000154a         movzx      eax, byte [rax+3]
000000010000154e         mov        dword [rsp+0xd0+var_D0], eax
0000000100001551         lea        rdx, qword [cfstring__02X_02X_02X_02X_02X_02X_02X]
0000000100001558         lea        rsi, qword [0x1000022f8]
000000010000155f         mov        rdi, qword [rbp+var_58]
0000000100001563         xor        eax, eax
0000000100001565         call       qword [0x1000022f8]
000000010000156b         mov        rdi, rax
000000010000156e         mov        edx, 0x7
0000000100001573         lea        rsi, qword [0x1000022d8]
000000010000157a         call       qword [0x1000022d8]
0000000100001580         mov        rbx, rax
0000000100001583         mov        qword [rbp+var_38], 0x7
000000010000158b         mov        qword [rbp+var_40], 0x6
0000000100001593         mov        edx, 0x6
0000000100001598         mov        ecx, 0x7
000000010000159d         lea        rsi, qword [0x100002328]
00000001000015a4         mov        rdi, r13
00000001000015a7         call       qword [0x100002328]
00000001000015ad         mov        rdi, rax
00000001000015b0         mov        rdx, rbx
00000001000015b3         lea        rsi, qword [0x100002308]
00000001000015ba         call       qword [0x100002308]
00000001000015c0         test       al, al
00000001000015c2         je         failure

00000001000015c8         mov        qword [rbp+var_48], 0x2
00000001000015d0         mov        qword [rbp+var_50], 0xe
00000001000015d8         mov        edx, 0xe
00000001000015dd         mov        ecx, 0x2
00000001000015e2         lea        rsi, qword [0x100002328]
00000001000015e9         mov        rdi, r13
00000001000015ec         call       qword [0x100002328]
00000001000015f2         mov        rdi, rax
00000001000015f5         mov        edx, 0x4
00000001000015fa         lea        rsi, qword [0x1000022b8]
0000000100001601         call       qword [0x1000022b8]
0000000100001607         mov        rdi, rax
000000010000160a         mov        rdx, r15
000000010000160d         lea        rsi, qword [0x100002338]
0000000100001614         call       qword [0x100002338]
000000010000161a         test       al, al
000000010000161c         je         failure
                        ; 下面的一段是成功注册的代码
000000010000161e         mov        rdi, qword [objc_cls_ref_NSNotificationCenter]
0000000100001625         lea        rsi, qword [0x100002238]
000000010000162c         call       qword [0x100002238]
0000000100001632         mov        rdi, rax
0000000100001635         mov        rcx, qword [rbp+var_60]
0000000100001639         lea        rdx, qword [cfstring_Registered]
0000000100001640         lea        rsi, qword [0x100002348]
0000000100001647         mov        r11, qword [0x100002348]
000000010000164e         mov        rbx, qword [rbp+var_28]
0000000100001652         mov        r12, qword [rbp+var_20]
0000000100001656         mov        r13, qword [rbp+var_18]
000000010000165a         mov        r14, qword [rbp+var_10]
000000010000165e         mov        r15, qword [rbp+var_8]
0000000100001662         leave
0000000100001663         jmp        r11
                        ; endp

                     failure:
0000000100001666         mov        rbx, qword [rbp+var_28]
000000010000166a         mov        r12, qword [rbp+var_20]
000000010000166e         mov        r13, qword [rbp+var_18]
0000000100001672         mov        r14, qword [rbp+var_10]
0000000100001676         mov        r15, qword [rbp+var_8]
000000010000167a         leave
000000010000167b         ret
                        ; endp
```

我们发现这个函数有一个特点，从头开始往下，一直是`cmp a, b`然后`jne/je failure`，也就是说**如果我们暴破，要把这些`jne`和`je`都`nop`掉。**太麻烦了，但是，自己想想，就真的没有好方法吗？答案是：有的。

在这里我耍了一个小聪明：既然那么多失败的路径都指向`failure`，我何不把`failure`本身改一下呢？`Option+A`改为如下：

```assembly
                     failure:
0000000100001666         jmp        0x10000161e
0000000100001668         nop
000000010000166f         nop
0000000100001670         nop
0000000100001679         nop
000000010000167b         nop
```

我贴个图让你看得更明白：

![pie-bp-guide](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/18/pie-bp-guide.png)

也就是说，“验证失败”的代码被我们暴破跳转到“验证成功”的代码。**如果哪行指令跳转到“验证失败”的代码，我们就再让它跳转到成功代码。**很巧妙吧！

`Cmd+Shift+E`输出二进制，替换即可。

# Hook

## 分析

我们先来试试Hook一下这个函数，我先把`verifySerial:andName:`贴出来。

```objc
/* @class PieAppDelegate */
-(void)verifySerial:(void *)arg2 andName:(void *)arg3 {
    var_28 = rbx;
    var_20 = r12;
    var_18 = r13;
    var_10 = r14;
    var_8 = r15;
    var_60 = self;
    r13 = arg2;
    r14 = arg3;
    r15 = (@selector(dataUsingEncoding:))(*qword_100002768, &@selector(dataUsingEncoding:), 0x4, arg3);
    if ((@selector(length))(r13, &@selector(length)) == 0x10) {
            rax = (@selector(substringToIndex:))(r13, &@selector(substringToIndex:), 0x6);
            rax = (@selector(dataUsingEncoding:))(rax, &@selector(dataUsingEncoding:), 0x4);
            r12 = (@selector(length))(rax, &@selector(length));
            rax = (@selector(bytes))(rax, &@selector(bytes));
            rax = MD5(rax, r12, 0x0);
            if (((@selector(isEqualToString:))((@selector(stringWithFormat:))(@class(NSString), &@selector(stringWithFormat:), @"%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X", *(int8_t *)rax & 0xff, *(int8_t *)(rax + 0x1) & 0xff, *(int8_t *)(rax + 0x2) & 0xff, *(int8_t *)(rax + 0x3) & 0xff, *(int8_t *)(rax + 0x4) & 0xff, *(int8_t *)(rax + 0x5) & 0xff, *(int8_t *)(rax + 0x6) & 0xff, *(int8_t *)(rax + 0x7) & 0xff, *(int8_t *)(rax + 0x8) & 0xff, *(int8_t *)(rax + 0x9) & 0xff, *(int8_t *)(rax + 0xa) & 0xff, *(int8_t *)(rax + 0xb) & 0xff, *(int8_t *)(rax + 0xc) & 0xff), &@selector(isEqualToString:), *qword_100002770) == 0x0) && ((@selector(characterAtIndex:))(r13, &@selector(characterAtIndex:), 0xd) != 0x46)) {
                    rax = (@selector(dataUsingEncoding:))(r14, &@selector(dataUsingEncoding:), 0x4);
                    r12 = (@selector(length))(rax, &@selector(length));
                    rax = (@selector(bytes))(rax, &@selector(bytes));
                    rax = MD5(rax, r12, 0x0);
                    if ((@selector(isEqualToString:))((@selector(substringWithRange:))(r13, &@selector(substringWithRange:), 0x6, 0x7), &@selector(isEqualToString:), (@selector(substringToIndex:))((@selector(stringWithFormat:))(@class(NSString), &@selector(stringWithFormat:), @"%02X%02X%02X%02X%02X%02X%02X", *(int8_t *)rax & 0xff, *(int8_t *)(rax + 0x1) & 0xff, *(int8_t *)(rax + 0x2) & 0xff, *(int8_t *)(rax + 0x3) & 0xff, *(int8_t *)(rax + 0x4) & 0xff, *(int8_t *)(rax + 0x5) & 0xff, *(int8_t *)(rax + 0x6) & 0xff, *(int8_t *)(rax + 0x7) & 0xff), &@selector(substringToIndex:), 0x7)) == 0x0) {
                            if ((@selector(isEqualToData:))((@selector(dataUsingEncoding:))((@selector(substringWithRange:))(r13, &@selector(substringWithRange:), 0xe, 0x2), &@selector(dataUsingEncoding:), 0x4), &@selector(isEqualToData:), r15) == 0x0) {
                                    (@selector(postNotificationName:object:))((@selector(defaultCenter))(@class(NSNotificationCenter), &@selector(defaultCenter)), &@selector(postNotificationName:object:), @"Registered", var_60);
                            }
                    }
            }
    }
    return;
}
```

函数体很长，关键在于它并没有返回一个特定的值，比如布尔或者字符。这个函数把验证和注册两个过程绑在一起。一个一个把跳转改成nop，太费时间。那还有什么办法呢？我看着这一层层if嵌套，突然萌生了一个想法：不用一层层改条件，只需要一个Hook，直接执行最里面的代码。

在这里我使用MonkeyDev框架，新建工程，将`Pie.app`拖入：

![详细步骤](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/17/pie-proj-guide.png)

## 代码编写

按照Cydia Substrate的文档，我们需要在动态库加载入口作函数替换，需要用`MSHookMessageEx`。这里是官方文档的用法（我翻译的）：

```objc
void MSHookMessageEx(Class _class, SEL message, IMP hook, IMP *old);
```

| 参数      | 作用                                                         |
| --------- | ------------------------------------------------------------ |
| `_class`  | OC类，消息将在该类上被hook。这个类可以是一个元类，这样就可以hook住非实例或类消息。 |
| `message` | 被hook的OC选择器（sel）。这可以用 `@selector` ，或在运行时用 `sel_registerName`生成。 |
| `hook`    | `message`的替代函数，IMP指针类型。(注意传入的时候一定是指针) |
| `old`     | 一个空的函数指针。这个空的函数指针在hook时会被原函数填充，这样你在写新函数的时候，就可以调用原函数体了。如果你不需要调用原函数，此处可以留成NULL。 |

现在，我们编辑`PieTweak.m`，编辑`constructor`：

```objc
static void __attribute__((constructor)) initialize(void) {
    MSHookMessageEx(objc_getClass("PieAppDelegate"), @selector(verifySerial:andName:), (IMP)&new_PieAppDelegate_verifySerial, NULL);
}
```

其中`new_PieAppDelegate_verifySerial`是我们要实现的。我们可以写一个`origin_PieAppDelegate_verifySerial`。由于我们不需要在hook里调用原函数，所以留空填`NULL`。

接下来就该写我们的替代函数体了，`new_PieAppDelegate_verifySerial`。**我们首先得考虑一下参数列表**，除了Hopper解析出的`serial`和`name`，**还有两个固定参数：`self`和`_cmd`。**

```objc
@class PieAppDelegate; // 为了在参数中写self，在这里我们声明类

static void new_PieAppDelegate_verifySerial(
    PieAppDelegate* self, // 两个固定参数
    SEL _cmd, 
    void *serial, // 此处复制粘贴Hopper
    void *name
) {
    // ...
}
```

**那么函数体呢？**这得根据Hopper的伪代码进行还原。伪代码最内层有这么一句：

```objc
(@selector(postNotificationName:object:))((@selector(defaultCenter))(@class(NSNotificationCenter), &@selector(defaultCenter)), &@selector(postNotificationName:object:), @"Registered", var_60);
```

我们可以推测出：

```objc
[NSNotificationCenter.defaultCenter postNotificationName:@"Registered" object:self];
```

把还原的语句放到`new_PieAppDelegate_verifySerial`里。

现在大家可能被我绕的有点晕，所有的代码纵观如下：

```objc
#import "PieTweak.h"
#import "substrate.h"

@class PieAppDelegate;

static void new_PieAppDelegate_verifySerial(PieAppDelegate* self, SEL _cmd, void *serial, void *name) {
    [NSNotificationCenter.defaultCenter postNotificationName:@"Registered" object:self]; // 我们从伪代码还原的语句
}

static void __attribute__((constructor)) initialize(void) {
    MSHookMessageEx(objc_getClass("PieAppDelegate"), @selector(verifySerial:andName:), (IMP)&new_PieAppDelegate_verifySerial, NULL);
    // 调用substrate进行hook
}
```

`Cmd+B`编译，MonkeyDev会自动给我们注入：

![pie-hook-success](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/17/pie-hook-success.png)

**不错吧！一打开就注册好了。**我们只需要把`Pie.app`从`TargetApp`里面拖出去，就是我们的成品啦！

# 注册机编写

如果不用hook暴破，那就是写注册机了。注册机使我们破解得更优雅，但是代码的分析更麻烦。这个CM不是有反调试吗，所以说只有靠我们看伪代码了。

这里希望提醒大家几点：

- 看伪代码首先要**利用Hopper功能**，把arg2、arg3这样的无意义参数名更名，比如`serial`和`name`；
- 一定要善于进行**代码还原**。Hopper会把不知道的方法都翻译成`@selector`，语法非常的别扭。具体的还原方法hook中有所涉及，但是我会在文末单独成节；
- 在自己重写代码时，**使用自己的变量**，而不是`r12`、`r13`这样的无意义变量；
- 有时候Hopper会把代码逻辑解析得很麻烦，比如在这个例子中，它把MD5的*加密数据*和*转换成字符串的MD5*分别放在变量和if条件里，就会让你感觉摸不着头，所以说**一定要有自主判断能力。**

## 代码分析

我们首先把验证函数的流程捣腾清楚：

```objc
var_28 = rbx; // 定义一堆没用的，不过一定要清楚
var_20 = r12;
var_18 = r13;
var_10 = r14;
var_8 = r15;
var_60 = self;
r13 = arg2; // serial序列号变量
r14 = arg3; // name名称变量
r15 = (@selector(dataUsingEncoding:))(*qword_100002768, &@selector(dataUsingEncoding:), 0x4, arg3); // 把名称进行编码，4其实是NSStringEncoding的NSUTF8StringEncoding，是个常量
```

一开头，定义了一堆没用的，不过要清楚r13和r14是`serial`和name。r15处把`name`编码，查开发者文档可知0x4其实是`NSStringEncoding`的NSUTF8StringEncoding，是个常量。

```objc
if ((@selector(length))(r13, &@selector(length)) == 0x10) {
```

判断serial的长度，如果是16位（0x10），通过。

```objc
rax = (@selector(substringToIndex:))(r13, &@selector(substringToIndex:), 0x6); // 取序列号前6位
rax = (@selector(dataUsingEncoding:))(rax, &@selector(dataUsingEncoding:), 0x4);
r12 = (@selector(length))(rax, &@selector(length)); // 计算长度
rax = (@selector(bytes))(rax, &@selector(bytes)); // 计算字节
rax = MD5(rax, r12, 0x0); // 计算序列号前6位的MD5值
```

这5行代码先取序列号前6位，然后计算出了相关长度、字节，最后计算出序列号前6位的MD5。

```objc
if (((@selector(isEqualToString:))((@selector(stringWithFormat:))(@class(NSString), &@selector(stringWithFormat:), @"%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X", *(int8_t *)rax & 0xff, *(int8_t *)(rax + 0x1) & 0xff, *(int8_t *)(rax + 0x2) & 0xff, *(int8_t *)(rax + 0x3) & 0xff, *(int8_t *)(rax + 0x4) & 0xff, *(int8_t *)(rax + 0x5) & 0xff, *(int8_t *)(rax + 0x6) & 0xff, *(int8_t *)(rax + 0x7) & 0xff, *(int8_t *)(rax + 0x8) & 0xff, *(int8_t *)(rax + 0x9) & 0xff, *(int8_t *)(rax + 0xa) & 0xff, *(int8_t *)(rax + 0xb) & 0xff, *(int8_t *)(rax + 0xc) & 0xff), &@selector(isEqualToString:), *qword_100002770) == 0x0) && ((@selector(characterAtIndex:))(r13, &@selector(characterAtIndex:), 0xd) != 0x46)) { // 这个if的条件要满足两部分：1. 序列号的前6位的MD5是66EAD6FE7CBE7987B7C4B1A1EED0E5A5；2. 序列号的第13位是ASCII 0x46，也就是字符F
```

这个条件很长，但是细心的你会发现中间有个逻辑运算`&&`，条件分为两部分：

1. 序列号的前6位的MD5是`66EAD6FE7CBE7987B7C4B1A1EED0E5A5`，通过某网站的反查得知是“KRACK-”，这是个序列号前缀；
2. 序列号的第13位是ASCII 0x46，也就是字符F。

```objc
rax = (@selector(dataUsingEncoding:))(r14, &@selector(dataUsingEncoding:), 0x4); // 编码name
r12 = (@selector(length))(rax, &@selector(length)); // 计算name长度
rax = (@selector(bytes))(rax, &@selector(bytes)); // 计算name字节
rax = MD5(rax, r12, 0x0); // 使用MD5加密name
```

这个和刚才代码分析中第二个代码框中的5行结构是一模一样，计算name属性，然后加密name。

```objc
if ((@selector(isEqualToString:))((@selector(substringWithRange:))(r13, &@selector(substringWithRange:), 0x6, 0x7), &@selector(isEqualToString:), (@selector(substringToIndex:))((@selector(stringWithFormat:))(@class(NSString), &@selector(stringWithFormat:), @"%02X%02X%02X%02X%02X%02X%02X", *(int8_t *)rax & 0xff, *(int8_t *)(rax + 0x1) & 0xff, *(int8_t *)(rax + 0x2) & 0xff, *(int8_t *)(rax + 0x3) & 0xff, *(int8_t *)(rax + 0x4) & 0xff, *(int8_t *)(rax + 0x5) & 0xff, *(int8_t *)(rax + 0x6) & 0xff, *(int8_t *)(rax + 0x7) & 0xff), &@selector(substringToIndex:), 0x7)) == 0x0) {
```

又是一长串条件，好像是在判断serial的某个子字符串（也就是某部分）跟name的md5值相等。

这里要说明一下`substringWithRange:`的参数，研究了半天发现，0x6表示子字符串开始，**0x7表示包含开头往后数七位，是子字符串的长度**，也就是说这个函数返回的是serial的6到12位（我这里指的是索引）。相当于这个if条件在将name的md5值与serial的6-12位对比。

```objc
if ((@selector(isEqualToData:))((@selector(dataUsingEncoding:))((@selector(substringWithRange:))(r13, &@selector(substringWithRange:), 0xe, 0x2), &@selector(dataUsingEncoding:), 0x4), &@selector(isEqualToData:), r15) == 0x0) {
```

又是一个if。现在我们一目了然，这是在把serial索引为14、15的子字符串编码后和r15对比。诶？r15不是name的utf8编码吗？不对啊？两位和一长串名称对比，肯定返回false。别着急，我们瞧瞧ASM：

```assembly
                     -[PieAppDelegate verifySerial:andName:]:
0000000100001342         push       rbp
0000000100001343         mov        rbp, rsp
0000000100001346         mov        qword [rbp+var_28], rbx
000000010000134a         mov        qword [rbp+var_20], r12
000000010000134e         mov        qword [rbp+var_18], r13
0000000100001352         mov        qword [rbp+var_10], r14
0000000100001356         mov        qword [rbp+var_8], r15
000000010000135a         sub        rsp, 0xd0
0000000100001361         mov        qword [rbp+var_60], rdi
0000000100001365         mov        r13, rdx
0000000100001368         mov        r14, rcx
000000010000136b         mov        rdi, qword [qword_100002768]                ; qword_100002768
0000000100001372         mov        edx, 0x4
0000000100001377         lea        rsi, qword [0x1000022b8]                    ; &@selector(dataUsingEncoding:)
000000010000137e         call       qword [0x1000022b8]                         ; @selector(dataUsingEncoding:)
0000000100001384         mov        r15, rax
0000000100001387         lea        rsi, qword [0x1000022c8]                    ; &@selector(length)
000000010000138e         mov        rdi, r13
0000000100001391         call       qword [0x1000022c8]                         ; @selector(length)
0000000100001397         cmp        rax, 0x10
000000010000139b         jne        loc_100001666
```

我们发现，函数的开头，竟然有一个我们忽略了的`qword_100002768`！跳转一下，发现它指向一个“BC”的字符串：

```assembly
    qword_100002768:
0000000100002768 dq 0x0000000100002168 ; @"BC", DATA XREF=-[PieAppDelegate verifySerial:andName:]+41
```

那为什么说这个qword是r15呢？因为反汇编中，从rdi被赋值到被覆盖期间，只有rax传给了r15。我们推测BC就是serial索引为14、15的子字符串。

回到代码分析，最后一个if嵌套的就是成功的弹窗了。

## 流程复现

我们把上面的伪代码用Swift 5 100%重写一下，不作修改。先实现两个字符串扩展，MD5方法和`characterAtIndex`：

```swift
extension String {
    // 获得字符串在索引处的字符
    func characterAtIndex(index: Int) -> Character? {
        var cur = 0
        for char in self {
            if cur == index {
                return char
            }
            cur += 1
        }
        return nil
    }
    var md5: String {
        let utf8 = cString(using: .utf8)
        var digest = [UInt8](repeating: 0, count: Int(CC_MD5_DIGEST_LENGTH))
        CC_MD5(utf8, CC_LONG(utf8!.count - 1), &digest) // 记得import CommonCrypto
        return digest.reduce("") { $0 + String(format: "%02X", $1) }
    }
    // 这样我们就可以通过xxx.md5的方式加密了，非常便捷
}
```

再写验证函数：

```swift
func verifySerial(_ serial: String, name: String) {
    let encodedName = name.data(using: .utf8)
    if serial.count == 16 {
        let processedSerial = String(serial.prefix(6))
        // let processedSerialData = NSData(data: processedSerial.data(using: .utf8)!)
        // let snLength = processedSerialData.count
        // let snBytes = processedSerialData.bytes // 计算相关值
        // let md5val = MD5(snBytes, snLength, 0x0); // MD5 encryption
        // 有了我们的md5函数上面的计算都不需要了
        var md5str = processedSerial.md5
        
        if processedSerial.md5.uppercased() == "66EAD6FE7CBE7987B7C4B1A1EED0E5A5" && serial.characterAtIndex(index: 13) == "F" {
            // md5val = [name dataUsingEncoding:NSUTF8StringEncoding];
            // md5vallen = [md5val length]; // 计算相关值
            // md5valbytes = [md5valbytes bytes];
            // md5OfMd5val = MD5(md5valbytes, md5vallen, 0x0);
            // 上面的全都不需要了
            
            // 创建一些索引，方便我们截取字符串
            let index6 = serial.index(serial.startIndex, offsetBy: 6)
            let index12 = serial.index(serial.startIndex, offsetBy: 12)
            let index14 = serial.index(serial.startIndex, offsetBy: 14)
            let index15 = serial.index(serial.startIndex, offsetBy: 15)
            if name.md5.prefix(7) == serial[index6...index12] { // prefix用来取前7位
                if serial[index14...index15] == "BC" {
                    // Registered
                    // (@selector(postNotificationName:object:))((@selector(defaultCenter))(@class(NSNotificationCenter), &@selector(defaultCenter)), &@selector(postNotificationName:object:), @"Registered", var_60);
                    print("Registered! ")
                }
            }
        }
    }
}
```

上面的if有点多，我们再以经典Swift风格写一手优雅的代码，让它返回一个值：

```swift
func verifySerial(_ serial: String, name: String) -> Bool {
    guard serial.count == 16 else { return false }
    
    let processedSerial = String(serial.prefix(6))
    guard processedSerial == "KRACK-" else { return false }
    guard serial.characterAtIndex(index: 13) == "F" else { return false }
    
    let index6 = serial.index(serial.startIndex, offsetBy: 6)
    let index12 = serial.index(serial.startIndex, offsetBy: 12)
    let index14 = serial.index(serial.startIndex, offsetBy: 14)
    let index15 = serial.index(serial.startIndex, offsetBy: 15)
    
    guard serial[index6...index12] == name.md5.prefix(7).uppercased() else { return false }
    guard serial[index14...index15] == "BC" else { return false }
    
    return true
}
```

> `guard <statement> else {}`的作用是，确保`<statement>`为真，否则执行`else`代码块。

## 序列号生成

有了验证函数做基础，我们就知道什么样的SN能被`verifySerial`接受。格式是：`KRACK-<用户名的md5值取前7位>FBC`。写一个Keygen，超级简单。

```swift
func generateSerial(from name: String) -> String {
    let nameMD5 = name.md5.prefix(7).uppercased()
    return "KRACK-\(nameMD5)FBC"
}
```

果然是破解容易分析难啊！

## 完善注册机

完善注册机，把我们的Keygen做成命令行形式，有`-gv`两个功能，g是生成模式，v是验证模式。

全部代码`main.c`：

```swift
import Foundation
import CommonCrypto

func verifySerial(_ serial: String, name: String) -> Bool {
    guard serial.count == 16 else { return false }
    let processedSerial = String(serial.prefix(6))
    guard processedSerial == "KRACK-" else { return false }
    guard serial.characterAtIndex(index: 13) == "F" else { return false }
    let index6 = serial.index(serial.startIndex, offsetBy: 6)
    let index12 = serial.index(serial.startIndex, offsetBy: 12)
    let index14 = serial.index(serial.startIndex, offsetBy: 14)
    let index15 = serial.index(serial.startIndex, offsetBy: 15)
    guard name.md5.prefix(7).uppercased() == serial[index6...index12] else { return false }
    guard serial[index14...index15] == "BC" else { return false }
    return true
}

func generateSerial(from name: String) -> String {
    let nameMD5 = name.md5.prefix(7).uppercased()
    return "KRACK-\(nameMD5)FBC"
}

func askAndGenerate() {
    print("Username:", terminator: " ")
    if let uname = readLine() {
        print("Serial: \(generateSerial(from: uname))")
    }
    print("-----------------------")
    askAndGenerate()
}

func askAndValidate() {
    print("Username:", terminator: " ")
    if let uname = readLine() {
        print("Serial:", terminator: " ")
        if let sn = readLine() {
            let result = verifySerial(sn, name: uname)
            print(result ? "Serial is valid." : "Serial is invalid.")
        }
    }
    print("-----------------------")
    askAndValidate()
}

print("Keygen of Pie.app - by @TLHorse from www.52pojie.cn")

let argv = ProcessInfo.processInfo.arguments
guard argv.count == 2 else {
    for i in argv {print(i)}
    print("PieKeygen: error: 2 arguments is needed")
    exit(1)
}
switch argv[1] {
case "-g":
    print("--- Generation mode ---")
    askAndGenerate()
case "-v":
    print("--- Validation mode ---")
    askAndValidate()
default:
    print("PieKeygen: error: illegal operand\nusage: PieKeygen [-gv]")
}

extension String {
    func characterAtIndex(index: Int) -> Character? {
        var cur = 0
        for char in self {
            if cur == index {
                return char
            }
            cur += 1
        }
        return nil
    }
    var md5: String {
        let utf8 = cString(using: .utf8)
        var digest = [UInt8](repeating: 0, count: Int(CC_MD5_DIGEST_LENGTH))
        CC_MD5(utf8, CC_LONG(utf8!.count - 1), &digest)
        return digest.reduce("") { $0 + String(format:"%02X", $1) }
    }
}
```

![pie-kg-product](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/17/pie-kg-product.png)

# 到底如何还原代码

如何把Hopper的伪代码尽可能还原成真实的OC？我在Hook中有所提及，但是在这里我细说一下我研究的方法。

比如拿

```objc
(@selector(postNotificationName:object:))((@selector(defaultCenter))(@class(NSNotificationCenter), &@selector(defaultCenter)), &@selector(postNotificationName:object:), @"Registered", var_60);
```

来说吧：

1. 首先，去掉所有**单独成括号的选择器**，特征是`(@selector(x​xx))`，只带@不带&号，这些选择器没有地址不被调用：

   ```objc
   (@class(NSNotificationCenter), &@selector(defaultCenter)), &@selector(postNotificationName:object:), @"Registered", var_60);
   ```

2. 现在整条语句只剩下一个括号，里面有许多“项”，由逗号分隔。从开头一直往后，逐项翻译成父子关系，**遇到方法名称时，将方法名称后面的所有项翻译成这个方法的参数**，把它们按照OC语法拼在一起：

   ```objc
   [NSNotificationCenter.defaultCenter postNotificationName:@"Registered" object:var_60];
   ```

3. 最后，把伪代码中的变量通过上下文替换成真实值。在伪代码中`var_60 = self;`，所以进行替换。最终还原的代码：

   ```objc
   [NSNotificationCenter.defaultCenter postNotificationName:@"Registered" object:self];
   ```

其实就是把Hopper生成的替换成hook环境中真实的东西的过程。

# THE END

**分析，Hook，KG一条龙，总算是完成了。**