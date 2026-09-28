---
title: "你没看错：动手开发GUI简单操作系统（二）"
date: "2021-02-10T18:36:42+08:00"
description: "学习目标 编写GDT 切换到32位保护模式（32-bit protected mode，又叫PM） 我突然发现写到第二篇文章就难以启齿了，因为切PM、加载内核这些东西几乎是环环相扣的，有一点差错都不行。另外劝大家一定要学好英文，怎么着也得七八千词汇量吧。"
categories:
  - "计算机"
tags:
  - "《你没听错：动手开发GUI简单操作系统》系列"
---

# 学习目标

1. 编写GDT
2. 切换到32位保护模式（32-bit protected mode，又叫PM）

> 我突然发现写到第二篇文章就难以启齿了，因为切PM、加载内核这些东西几乎是环环相扣的，有一点差错都不行。
>
> 另外劝大家一定要学好英文，怎么着也得七八千词汇量吧。

# 编写GDT

GDT是最难理解的部分，却不可避免，不好意思，我这次又整了一大段理论写在这里。我觉得下面说的还算比较全吧，如果我一下引入那么多名词，我都难以下笔。但是，必须看，如果实在读不进去，看**加粗字体**：

## 认识全局描述符表

> 为了行文方便，下文使用缩写。
>
> |   中文名称   | 英文名称                | 缩写 |
> | :----------: | ----------------------- | ---- |
> | 全局描述符表 | Global Descriptor Table | GDT  |
> |   保护模式   | Protected Mode          | PM   |
> |   真实模式   | Real Mode               | RM   |

GDT在PM下，是一个重要的必不可少的数据结构。

为什么要有GDT？我们首先考虑一下在RM（就是切PM之前）下的编程模型：在RM下，我们对一个内存地址的访问是通过`Segment:Offset`的方式来进行的，其中Segment是一个段的基地址，一个Segment的最大长度是64KB，这是16位系统所能表示的最大长度。而Offset则是相对于此段基地址的偏移量。**基地址+偏移就是一个内存绝对地址。**

由此，我们可以看出，一个段具备两个因素：基地址和段的最大长度。而对一个内存地址的访问，则是需要指出两点：

1. 使用的是哪个段；
2. 相对于这个段基地址的偏移：这个偏移应该小于此段的最大长度。

当然对于16位系统，最大长度不用指定，默认为最大长度64KB，16位的便宜也永远不可能大于最大长度。而我们在实际编程的时候，使用16位段寄存器CS，DS，SS来指定段，CPU将段寄存器中的数值向左偏移4位，放到20位的地址线上就成为20位的基地址。

到了PM，内存的管理模式分为两种，段模式和页模式，其中页模式也是基于段模式的。也就是说，PM的内存管理模式事实上是：纯段模式和段页式。进一步说，段模式是必不可少的，而页模式则是可选的——如果使用页模式，则是段页式；否则这是纯段模式。

既然是这样，我们就先不去考虑页模式。对于段模式来讲，访问一个内存地址仍然使用Segment:Offset的方式，这是很自然的。由于PM运行在32位系统上，那么Segment的两个因素：基地址和最大长度也都是32位的。IA-32允许将一个段的基地址设为32位所能表示的任何值（最大长度则可以被设为32位所能表示的2<sup>12</sup>的整数倍的任何值），而不像RM下，一个段的基地址只能是16的倍数（因为其低4位是通过左移运算得来的，只能为0，从而达到使用16位段寄存器表示20位基地址的目的），而一个段的最大长度只能为固定值64KB。

**另外PM顾名思义，就是为段访问提供了保护机制**，也就说一个段的描述符需要规定对自身的访问权限（Access）。所以在PM下，对一个段的描述则包括3方面因素：Base Address（基地址）、Limit（最大长度）、Access（访问权限），它们加在一起被放在一个64位长的数据结构中，被称为段描述符。这种情况下，如果我们直接通过一个64位段描述符来引用一个段的时候，就必须使用一个64位长的段寄存器装入这个段描述符。Intel为了保持向后兼容，但将段寄存器仍然规定为16位（尽管每个段寄存器事实上有一个64位长的不可见部分，但对于编程人员来说段寄存器就是16位的），那么很明显，我们无法通过16位长度的段寄存器来直接引用64位的段描述符。怎么办？**解决的方法就是把这些长度为64位的段描述符放入一个数组中，而将段寄存器中的值作为下标索引来间接引用（事实上，是将段寄存器中的高13位的内容作为索引）。**

**——这个全局的数组就是GDT。**事实上，在GDT中存放的不仅仅是段描述符，还有其它描述符，它们都是64-bit长，我们随后再讨论。GDT可以被放在内存的任何位置，那么当程序员通过段寄存器来引用一个段描述符时，C**PU必须知道GDT的入口，也就是基地址放在哪里，所以Intel的设计者门提供了一个寄存器`gdtr`用来存放GDT的入口地址**。程序员将GDT设定在内存中某个位置之后，可以通过LGDT指令将GDT的入口地址装入此寄存器，从此以后，CPU就根据此寄存器中的内容作为GDT的入口来访问GDT了。GDT是PM所必须的数据结构，也是唯一的——不应该，也不可能有多个GDT。

另外，正像它的名字Global Descriptor Table所揭示的，它是全局可见的，对任何一个任务而言都是这样。除了GDT之外，IA-32还允许程序员构建与GDT类似的数据结构，它们被称作LDT，但与GDT不同的是，**LDT在系统中可以存在多个，并且从LDT的名字可以得知，LDT不是全局可见的，它们只对引用它们的任务可见，每个任务最多可以拥有一个LDT。**

**另外，每一个LDT自身作为一个段存在，它们的段描述符被放在GDT中。**IA-32为LDT的入口地址也提供了一个寄存器LDTR，因为在任何时刻只能有一个任务在运行，所以**LDT寄存器全局也只需要有一个**。如果一个任务拥有自身的LDT，那么当它需要引用自身的LDT时，它需要通过LLDT将其LDT的段描述符装入此寄存器。

LLDT指令与LGDT指令不同的是，LGDT指令的操作数是一个32位的内存地址，这个内存地址处存放的是一个32位GDT的入口地址，以及16位的GDT最大长度。而LLDT指令的操作数是一个16位的选择子，这个选择子主要内容是：**被装入的LDT的段描述符在GDT中的索引值**——这一点和刚才所讨论的通过段寄存器访问段的情况是一样的。

现在你知道为什么要有GDT了吧……

## GDT结构

![gdt结构](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/11/gdt-struct-table.png)

这是GDT的结构。其中Flags和Access Byte部分又分为如下表格：

![gdt详细](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/11/gdt-struct-detail.png)

## 编写GDT

我们先讲讲上面两个图每一项都代表什么，并且应该设置什么值。

| 图中标签    | 中文         | 英文                                         | 值   | 说明                                                         |
| :---------- | ------------ | -------------------------------------------- | ---- | ------------------------------------------------------------ |
| Pr          | 展示         | present                                      | 1    | 段在内存中被展示                                             |
| Privl       | 访问权限     | privilege                                    | 0    | 俗话说的ring级别。ring0 = 最高权限（内核）；ring3 = 最低权限（用户App） |
| S           | 描述符类型   | descriptor type                              | 1    | 设为1，表示是CS/DS                                           |
| Ex          | 是否为可执行 | Executable                                   | 1    | 1表示可执行，说明是代码；0表示不可执行，说明是数据           |
| DC          | 指示/遵循    | Direction/Conforming                         | 0    | 代码段中，0：代码只能被Privl权限执行，1：代码可以被≤Privil权限执行。数据段中，0：段从下到上，1：段从上到下。 |
| RW          | 读写性       | Readable/Writable                            | 1    | 对于代码段：1是可读（可以获取常量），0是可执行，不可写；对于数据段：1是可写，2是可读，不可执行 |
| Ac          | 已访问段     | Accessed                                     | 0    | 设为0。当CPU访问段，access会设成1，由CPU控制                 |
| Gr          | 粒度         | Granularity                                  | 1    | 如果是1，我们的limit会扩大四倍                               |
| Sz          | 大小         | Size                                         | 1    | 1代表使用32位PM，0是使用16位PM                               |
| 0（第一个） | 64位代码段   | 64-bit CS                                    | 0    | 32位处理器我们不用，0                                        |
| 0（第二个） | 系统可使用   | AVailabLe for use by system software （AVL） | 0    | 调试用，0                                                    |

我们根据需要的值写一个GDT。GDT有不止一种写法（也有许多比这高级的），我这种写法是定义了一个数据体，简单明了，但是可能不易于后期维护，项目里新建`gdt.asm`：

```assembly
gdt_start: ; 在这里写一个标签，待会用来计算大小

gdt_null:  ; 这个叫做空段，是Intel预留的
    dd 0   ; DD = double word  （此处也可以把两个dd合并为一个dq）
    dd 0   ;    = 4 byte

gdt_code: 
    dw 0xFFFF    ; Limit            0-15 bits
    dw 0         ; Base address     0-15
    db 0         ; 同上              16-23
    db 10011010B ; 按照图二Access Byte从右至左（0-7）的顺序填写。注意Privl因为值可以是0-3，所以说占两字节，填两个0
    db 11001111B ; 按图二flags从右至左填写。我们再看图一，flags右边还有limits最后4位，不满8位编译不通过，所以把limits合并在flags右面，0xF=0b1111
    db 0         ; Base             24-31

gdt_data:        ; 同上
    dw 0xFFFF
    dw 0
    db 0  
    db 10010010B ; 不同的是这里把Ex改成0，因为这里是数据段
    db 11001111B
    db 0

gdt_end:         ; gdt结束标签，

; GDT
gdt_descriptor:
    dw gdt_end - gdt_start - 1 ; 大小=结束-开始-1（真实大小永远-1）
    dd gdt_start               ; 开始地址

; 常量
CODE_SEG equ gdt_code - gdt_start ; CS
DATA_SEG equ gdt_data - gdt_start ; DS
```

GDT大功告成！**如果你没有编译成功，出了问题，请留言跟帖或者私信，我一定会回复！**

# 在32位保护模式下打印

我们现在写一个文件`32bit-print`，用来在32位保护模式下打印，不过只用来测试，到时候加载了内核切了GUI就可以删了。

```assembly
[bits 32]

VIDEO_MEMORY equ 0xB8000 ; 这是VGA开始的地方
WHITE_ON_BLACK equ 0x0F  ; 是一个颜色代码，黑背景，白色字符

print_string_pm:
    pusha
    mov edx, VIDEO_MEMORY

print_string_pm_loop:
    mov al, [ebx]          ; [ebx]是字符串参数
    mov ah, WHITE_ON_BLACK ; ah颜色参数

    cmp al, 0 ; 是不是已经到末尾？
    je print_string_pm_done ; 结束

    ; 如果不是
    mov [edx], ax ; 在Vram中保存字符
    add ebx, 1 ; 下一个字符
    add edx, 2 ; 下一个Vram字符位置，+2

    jmp print_string_pm_loop ; 递归

print_string_pm_done:
    popa
    ret
```

# 切换到32位保护模式

简单说一下为什么会有所谓保护模式：仔细想一想就能知道，如果这个OS给用户用就是开玩笑，就好像用户和操作系统一块在计算机里玩，而不是用户在操作系统里玩，它没有安全性可言，可以随便访问内存，更别提什么ring0、ring3的了，所以说切PM是为了让OS得到保护。

新建代码`switch_pm.asm`，很简单。主要目标是认识并使用这个控制寄存器cr0：

```assembly
[bits 16] ; 代表在16位模式下。中括号可以去掉
switch_to_pm:
    cli                   ; 1. 一定要关掉CPU中断！让CPU专心干一件事
    lgdt [gdt_descriptor] ; 2. 还记得lgdt命令吗？加载我们的gdt_descriptor标签
    mov eax, cr0          ; 把cr0暂存到eax
    or eax, 0x1           ; 3. cr0设置为1，切到32位PM
    mov cr0, eax
    jmp CODE_SEG:init_pm  ; 4. 远跳转，跳到代码段（下面）

[bits 32] ; 32位！
init_pm:
    mov ax, DATA_SEG ; 5. 更新段寄存器
    mov ds, ax
    mov ss, ax
    mov es, ax  ; 把每个都刷一遍
    mov fs, ax
    mov gs, ax

    mov ebp, 0x90000 ; 6. 基址指针寄存器，其内存放着一个指针，该指针永远指向系统栈最上面一个栈帧的底部，把它放到0x90000，待会加载内核
    mov esp, ebp

    call BEGIN_PM ; 跳到bootsect
```

`cr0`全称叫做Control Register 0，这个控制寄存器专门用来在RM和PM之间切换。

我们编辑一下`bootsect.asm`，使用上面的“函数”：

```assembly
[org 0x7C00]
    mov bp, 0x9000
    mov sp, bp

    mov bx, MSG_REAL_MODE
    call print ; 在实模式下打印

    call switch_to_pm ; 切PM
    ; 这里不管加什么代码都不会被执行

%include "print.asm"
%include "gdt.asm"
%include "32bit-print.asm"
%include "switch_pm.asm"

[bits 32] ; 32位
BEGIN_PM: ; 切换后跳转到这里
    mov ebx, MSG_PROT_MODE ; 打印
    call print_string_pm ; 注意！！！这个信息会被打印到整个屏幕的最左上角，覆盖BIOS的打印
    jmp $ ; 挂起

MSG_REAL_MODE db "Started in 16-bit real mode", 0
MSG_PROT_MODE db "Loaded 32-bit protected mode", 0

times 510-($-$$) db 0
dw 0xAA55
```

编译运行两步走：

![32pm-load-success](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/11/32pm-load-success.png)

# 加载并执行空内核

切32位PM是为加载内核准备的，我就一块整了吧，不然切PM毫无用处。

首先我们得认识到，汇编作为底层语言的代价是功能太少，不方便我们编程。内核编程需要用到C。但是一个操作系统项目里，怎么能容得下两种语言编译呢？你别着急，我们的做法是将启动扇区和内核部分分开，启动扇区编译成一个bin，内核编译成一个bin，编译的过程中我们把ld命令做一些调整，使数据便宜到0x1000，之后把两个bin用cat合并。

## 内核编写

所以说咱们先开始写内核吧，新建`kernel.c`：

```c
void main() {
    char *video_memory = (char*) 0xb8000;
    *video_memory = 'V';
    char *video_memory1 = (char*) 0xb8002;
    *video_memory1 = 'e';
    char *video_memory2 = (char*) 0xb8004;
    *video_memory2 = 'n';
    char *video_memory3 = (char*) 0xb8006;
    *video_memory3 = 'u';
    char *video_memory4 = (char*) 0xb8008;
    *video_memory4 = 's';
}

```

它的作用就是到VGA的地址打印`Venus`。

## 汇编编写

同级新建`kernel_entry.asm`，仅有四行代码：

```assembly
[bits 32]
[extern main] ; 像C一样，对外部函数得先声明。这个main就是kernel.c里面那个
call main     ; 执行
jmp $
```

是时候到`bootsect.asm`加载了：

```assembly
[org 0x7c00]
KERNEL_OFFSET equ 0x1000 ; 定义常量，这个常量是内核的位置

    mov [BOOT_DRIVE], dl ; BIOS会自动把磁盘编号设置到dl。我们在下面间一个常量，先存起来，因为dl可能会被覆盖
    mov bp, 0x9000
    mov sp, bp

    mov bx, MSG_REAL_MODE ; 实模式打印
    call print
    call print_nl

    call load_kernel  ; 加载内核
    call switch_to_pm ; 切PM

%include "print.asm"
%include "print_hex.asm"
%include "disk.asm"
%include "gdt.asm"
%include "print.asm"
%include "switch_pm.asm"

[bits 16]
load_kernel:
    mov bx, MSG_LOAD_KERNEL
    call print
    call print_nl

    mov bx, KERNEL_OFFSET ; 读取到内核偏移地址
    mov dh, 2
    mov dl, [BOOT_DRIVE]
    call disk_load
    ret

[bits 32]
BEGIN_PM:
    mov ebx, MSG_PROT_MODE
    call print_string_pm
    call KERNEL_OFFSET ; 执行内核代码
    jmp $


BOOT_DRIVE db 0
MSG_REAL_MODE db "Started in 16-bit Real Mode", 0
MSG_PROT_MODE db "Landed in 32-bit Protected Mode", 0
MSG_LOAD_KERNEL db "Loading kernel into memory", 0

times 510 - ($-$$) db 0
dw 0xAA55
```

![kern-exec](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2021/02/11/kern-exec.png)

今天就到这里，**以后更新可能会慢点**，太累了，我还要干别的呢。我发现不少坛友貌似有点功利性质，说什么期待后续如果可以再下手，哈哈，我理解你们，毕竟项目要么就不做，要么就做成。我的个人理念是不做就不做，做就做大。