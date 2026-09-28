---
title: "再战CleanMyMac X完美暴破"
date: "2021-02-07T21:20:05+08:00"
description: "因为的破解屡次被代理商投诉，并且有被黑心网站挖掘文章的可能，故不能发布成品。文章这么长，其实是就是几个和，更多的是分析，再说论坛上的同志都不是白给的，肯定搞得定。"
categories:
  - "计算机"
tags:
  - "反编译"
---

> **因为`CleanMyMac X`的破解屡次被代理商投诉，并且有被黑心网站挖掘文章的可能，故不能发布成品。文章这么长，其实是就是几个`frida-trace`和`Hopper`，更多的是分析，再说论坛上的同志都不是白给的，肯定搞得定。**

自从写了[《一次意外的 CleanMyMac X 破解》](https://tlhorse.github.io/posts/16190/)后，在手的CleanMyMac X 4.5.3就一直没更新换代。笔者撰写此文，CleanMyMac X 已经发展到4.7.4了，于是便想着重新破解一遍。如果还未读过上篇文章的，建议读一遍。

# Hopper分析

按照上一篇文章的思路，我们先找` -[CMActivationManager isAppActivated]`这个函数。竟然还在：

![cmmnew-search-sym](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/11/cmmnew-search-sym.png)

但是，为了避免像我破解4.6.7时频繁输密码的问题，安装`frida`，我们使用`frida-trace`进行调试修改：

```sh
frida-trace -m "-[* isAppActivated]" "CleanMyMac X"
```

这个命令我需要解释一下。`-m`是trace（跟踪）`OBJC_METHOD`的参数，后面第一个字符串参数是一个搜索关键词，其中*是通配符，不论是哪个class的`isAppActivated`都会被我们监视到。后面的`"CleanMyMac X"`是进程名称。

但是可惜的是在激活命令之前，我们需要把CMM打开，这样`frida`才能attach到进程。也就是说，CMM和命令几乎要同时打开。我在调试的过程中一直是把app和回车同时按下去，很麻烦，知道写文章才发觉自己好可爱，为什么不用下面的命令呢：

```sh
open /Applications/CleanMyMac\ X.app && frida-trace -m "-[* isAppActivated]" "CleanMyMac X"
```

之后我们会看到下面的输出：

```
Instrumenting...                                                        
-[CMActivationManager isAppActivated]: Auto-generated handler at "/Users/alex080318/Developer.localized/CMMTweak/__handlers__/CMActivationManager/isAppActivated.js"
-[CMSubscriptionStatusManager isAppActivated]: Auto-generated handler at "/Users/alex080318/Developer.localized/CMMTweak/__handlers__/CMSubscriptionStatusManager/isAppActivated.js"
-[CMSubscriptionRequestSchedule isAppActivated]: Auto-generated handler at "/Users/alex080318/Developer.localized/CMMTweak/__handlers__/CMSubscriptionRequestSchedule/isAppActivated.js"
Started tracing 3 functions. Press Ctrl+C to stop.
```

可以看到有三个函数被调用，也就是说这是三个函数都得被hook，终于不用像以前傻呵呵只改一个函数了。

# 破解过程

为了省时间，在这里就不用Hopper了。我们在`frida`生成的`__handlers__`文件夹（位于当前目录，也就是在trace之前要`cd`到一个准备好的目录）中，分别将三个函数的`onLeave`改成1：

```js
onLeave(log, retval, state) {
  retval.replace(1);
}
```

之后再运行`frida-trace`，打开软件，提示信息消失。正当欣喜若狂开始清理垃圾时，突然停止清理，提示我买会员。噩耗传来：**这是伪破解。不过别泄气啊。**

仔细观察软件会发现，有的地方是未注册的UI，有的地方是已注册的UI，也就是暴破函数没找全。我们查看一下`-[CMActivationManager isAppActivated]`伪代码，发现，里面的`sub_100334850`在做着不为人知的事情：

```objc
/* @class CMActivationManager */
-(char)isAppActivated {
    rax = sub_100334850(0x0);
    return rax;
}
```

`sub_100334850`：

```objc
int sub_100334850(int arg0) {
    var_2E8 = arg0;
    rax = objc_autoreleasePoolPush();
    var_300 = 0x0;
    var_2A0 = &var_300;
    var_318 = rax;
    if (**_NSApp != 0x0) {
            var_320 = qword_1007a3b28(**_NSApp, 0x1007a3b70);
            var_328 = var_320;
    }
    else {
            var_328 = 0x0;
    }
    var_2A8 = var_328;
    sub_100392510("DM_ENABLE_DEBUG_LOGGING_ACTIVATION", @"_get_: %p", var_2A8, 0x0, r8, r9, stack[-1704]);
    if ((var_2A8 == 0x0) || (var_2A0 == 0x0)) goto loc_1003349b4;
  // ......
```

代码很长，就不全部展示了。<kbd>Shift</kbd><kbd>X</kbd>查看交叉引用，顺藤摸瓜，结果让我眼前大吃一惊，好多啊……

![搜索交叉引用](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/08/cmmnew-subx.png)

原来，这个sub是个判断激活的进程**，不止`isAppActivated`调用了它，还有许许多多的类和方法，包括`EntryPoint`。**

想要hook这个sub，还需获取在内存中的地址，着实麻烦，就不写`frida`了。**Hopper直接改返回值。**双击空格，切到ASM模式：

```assembly
mov rax, 0x1
ret
```

<kbd>Cmd</kbd><kbd>Shift</kbd><kbd>E</kbd>，生成可执行文件，给源文件改名，替换——三步走，之后打开`CleanMyMac X`：

![1](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/08/cmmnew-ked-1.png)

![2](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/08/cmmnew-ked-2.png)

祝大家新年快乐，牛年大吉，破解技术共获提升，软件使用快乐！