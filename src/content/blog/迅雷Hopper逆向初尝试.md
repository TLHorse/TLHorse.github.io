---
title: "迅雷Hopper逆向初尝试"
date: "2020-01-28T17:40:35+08:00"
description: "破解目标：迅雷v3.0."
categories:
  - "计算机"
tags:
  - "反编译"
---

> 破解目标：迅雷v3.0.9，登陆即是会员！  

# 缘起
这也不是第一次想着进行破解二进制了。以前用过IDA、OD、010等软件，才知道，破解既困难，又有趣。

为什么我要用Hopper Disassembler进行破解？因为Hopper是一款针对Mac&Unix类系统的破解软件；那为什么又要选择迅雷呢v3.0.9.2892？我浏览过迅雷的所有版本，只有这个版本的迅雷是一个难度适中、易破解、成就感高而又实用的App。所以，今天写一篇破解迅雷v3.0.9的详细笔记，分享给大家。

但是——也确实是这样——总有那么些人通过不法方式修改别人的东西，我就很讨厌这类人。因此，**此篇文章仅供研究学习，切勿商用或者广泛传播，否则后果自负**！

> 注：网站里的图片点开即可查看大图。

# 工具准备
1.  [Hopper Disassembler](https://www.hopperapp.com)，逆向工程工具，可让反汇编，反编译和调试应用程序。
2. 迅雷（Thunder）v3.0.9.2892。以下迅雷简称XL。[官方下载链接](http://down.sandai.net/mac/thunder_3.0.9.2892.dmg)
3. 一台Mac或iMac，能不用虚拟机就不用。最好是MacOS Catalina，为了保证Hopper与XL的正常运行。（其实Hopper也有Linux版本，但在虚拟机下不太好使）
4. 思路清晰且冷静的大脑。

# 开始破解
## 导入分析

首先，我们从应用程序里找到`Thunder`这个App，右键——显示包内容，之后进入目录`/Contents/MacOS`，可以找到`Thunder`这个可执行文件。

![查找可执行文件](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/find-exec.png)

这个可执行文件包括着整个App的运行逻辑、顺序、程序等等内容，但是不包括应用的资源。这个文件就是应用运行的关键，也是我们破解的关键。

接下来，我们打开Hopper。进入应用界面后，把可执行文件拖拽到界面的中间部分。
![拖动](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-drag-analysis.png)

接下来，Hopper会弹出提示，保持默认，一路OK即可。
![提示框](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-warning.png)

等着进度条走完（观察窗口右下角的`Working`字样）。像迅雷这样的小软件，2秒钟就够了。接下来，一幅宏伟壮丽的景象会出现在你眼前。
![主页面](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-main-ui.png)

这是Hopper的主页面。分为5个部分：上面是工具条：

![工具条用法](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-toolbar-usage.png)

左边是搜索区，可以搜索函数、字符串、星标代码等；中间是主要工作区域，里面包含的内容可以通过工具条中按键调整；右边是检索区，可以设置/预览中间的内容，跟Xcode的检索区差不多；下面是Python控制台，可以输入命令操作反编译。

就先不多讲Hopper的使用了，有机会放在别的文章阐述。接下来，进入主题，开始破解！

## 查找可能的函数

迅雷想要验证是否是会员，肯定得有函数。按照程序猿千古流传的命名习惯，不用想就猜得到函数名：`isVip`

打开Hopper左边的搜索栏，上面的选择器选`Proc.`，就是搜索函数。然后搜索`isVip`，搜索出来，完全包含这个名字的函数有三个：

![搜索 isvip](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/search-isvip.png)

我们先点开第一个（汇编指令区就会出现），然后在蓝色的那一栏单击，标“星”，方便以后查找。如图：

![标星](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/choose-and-add-star.png)

接着，点开剩下两个，进行同样的标“星”操作。注意看图中的标“星”位置。
现在，清空搜索框，然后在选择其中选择“星”：

![选择标星的一栏](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-star-func.png)

好了！查找完了！

## 汇编思路

首先点开第一个（一长串的），然后参照`按键作用解释`那幅图，打开伪代码。类似OC伪代码应该如下：

```objective-c
/* @class ___4X2XLXH3O3STBRATSECONDT7R3OL4L34E1R___ */
-(char)isVip {
    rbx = [[UserController defaultUserController] retain];
    r14 = [rbx isVip];
    [rbx release];
    rax = sign_extend_64(r14);
    return rax;
}
```

虽然我不太懂OC，但是大致可以看出是一个函数，最后返回了`rax`。那`rax`是什么？

> AX(AH、AL)：累加器。有些指令约定以AX(或AL)为源或目的寄存器。输入/输出指令必须通过AX或AL实现，例如：端口地址为43H的内容读入CPU的指令为INAL，43H或INAX，43H。目的操作数只能是AL/AX，而不能是其他的寄存器；  
> BX(BH、BL)：基址寄存器。BX可用作间接寻址的地址寄存器和基地址寄存器，BH、BL可用作8位通用数据寄存器；  
> CX(CH、CL)：计数寄存器。CX在循环和串操作中充当计数器，指令执行后CX内容自动修改，因此称为计数寄存器；  
> DX(DH、DL)：数据寄存器。除用作通用寄存器外，在1/O指令中可用作端口地址寄存器，乘除指令中用作辅助累加器；  
> EAX、ECX、EDX、EBX：ax、bx、cx、dx的延伸，各为32位元。  

那么，这个函数最终会被`return rax`，而rax是真是假取决于账号，怎么办呢？思路：我们只需强制把`rax`换成真（代表着用户是会员），然后终止下面的进程就可以了！

## 修改程序
1.  把光标放在第一行（`push`的位置），按下<kbd>option</kbd>+<kbd>a</kbd>（或者到顶部Modify > Assemble Instruction），输入如下代码：
```asm
mov rax, 0x1
```

> 为什么这样改：mov是数据转移指令，这个操作会把0x1这个数据转移给rax，这样rax就被我们强制设为真了。  

![修改1](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-change-1.png)

1.  回车，输入`ret`。
为什么这样改：`ret`是`return`的缩写，意为“结束子程序并返回到主程序“，因此，这下面其他的乱七八糟的没用指令都不会运行了。

![修改2](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-change-2.png)

2.  点击屏幕任意地方，关掉修改弹窗。下图为修改后：

![修改后](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-changed.png)

这样，这个函数就被我们修改完了！用同样的方法，把剩下两个函数也修改成这样（patch）即可。

## 有自校验，但是一碰就碎

自校验，顾名思义就是自己看自己，有没有什么毛病。程序当然也会这样啊，如果看到自己的五脏六腑都移位了，就不会给你运行。当然，还有许多程序保护机制，比如防`hook`、反调试。

接下来我们就要关闭这个系统。首先，做过苹果开发的都知道，在程序启动将要完成时，`AppDelegate`中的`applicationWillFinishLaunching`函数会运行。也就是说，迅雷想要启动时自检，必须通过这个函数。我们只要把这个函数里的脚本禁了就行了。

老样子，搜索`appdelegate applicationWillFinishLaunching`（无需区分大小写）：

![搜索校验](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-search-anticrack.jpg)

单击打开，然后选择函数的第一行，<kbd>option</kbd>+<kbd>a</kbd>修改，直接输入`ret`禁用：

![修改自校验](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-change-anticrack.png)

修改后：

![去除自校验代码](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-changed-anticrack.png)

——一碰就碎！

## 导出

1.  按下<kbd>control</kbd>+<kbd>shift</kbd>+<kbd>E</kbd>。

2.  在新弹出的窗口中，选择`Remove Signature`移除签名。

![移除签名](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-rm-sign.png)

3.  在接下来的提示小窗中，选择保存位置，名字还是`Thunder`，如果Hopper给你加了类似`.exe`的后缀，那么一定要**去掉后缀名**。

![保存](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-save-exec.png)

4.  用新的可执行文件替换掉旧的`Thunder`。

![替换](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-exec-replace.png)

经过了这么多的操作，替换成功！

# 破解完工
**以非VIP的身份登陆迅雷**，验证成果：

![破解成功1](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-xl-crack-done-1.png)
![破解成功2](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed/2020/1/29/hop-xl-crack-done-2.png)

**欢呼吧！**

> **此篇文章仅供研究学习，旨教给读者修改程序的方法，切勿商用或者广泛传播，否则后果自负！**
