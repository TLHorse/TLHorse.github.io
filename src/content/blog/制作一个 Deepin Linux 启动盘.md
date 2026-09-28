---
title: "制作一个 Deepin Linux 启动盘"
date: "2020-05-20T10:47:27+08:00"
description: "前言 Linux 乃是操作系统之王，其可玩性、扩展性、操作性和美化性远远超过了 Windows、OS X（Darwin）等传统操作系统。Deepin Linux 是 Linux 发行版中较好的一个。"
categories:
  - "计算机"
tags:
  - "系统底层"
---

# 前言

Linux 乃是操作系统之王，其可玩性、扩展性、操作性和美化性远远超过了 Windows、OS X（Darwin）等传统操作系统。Deepin Linux 是 Linux 发行版中较好的一个。我们来比较一下 Linux 的安装方式：

1. 安装到双系统：将 Linux 与 Windows 或 OS X 并行安装，形成双系统，不过容易毁坏电脑或系统引导；
2. 安装到虚拟机：这倒是没问题，但是你总不能走哪都带个虚拟机运行软件吧？；
3. 安装到可启动 U 盘：说白了就是让电脑使用 U 盘里的操作系统进行启动。

第三种很酷？这次教大家用第三种方式安装（思想不限于 Deepin Linux）。

# 准备

- [x] 电脑一个；
- [x] 存储介质一个（硬盘、U 盘等，空间 ≥ 16GB）；
- [x] Parallels Desktop 15；
- [x] Deepin Linux [`.iso`镜像](https://www.deepin.org/download/)。

# 新建用于安装的操作系统

选择 Deepin Linux [`.iso`镜像](https://www.deepin.org/download/)，新建一个 Parallels Desktop 虚拟机：

![选择iso](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-choose-iso.png)

当虚拟机被加载出来后，直接停止虚拟机：

<img src="https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-quit.png" alt="停止虚拟机" style="zoom:50%;" />



插上你的存储介质，使用虚拟机右上角的⚙️按钮进入设置，作出如下配置：

![配置启动顺序](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-conf-seq.png)

> 注：“外部引导设备”里，要选择你的存储介质，比如我的 USB 3.0。

![配置内存](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-conf-ram.png)

# 启动虚拟机安装

存储介质保持插入状态。启动虚拟机后，会出现命令行界面的 BIOS。按下图操作：

![进入bios](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-inst-bios.png)

**为什么要在 BIOS 里“绕一圈”呢？其实这个动作相当于在拖延 Deepin 安装程序的启动，让存储介质在 BIOS 里提前被识别，这样才能让 Deepin 安装程序启动后找到识别我们的安装介质。**最后一步按下3后，即可进入安装程序：

![安装程序启动菜单](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-inst-start.png)

![选择安装存储介质](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-sel-disk.png)

![安装过程](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-installing.png)

![安装成功](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-install-success.png)

安装成功后，直接强制停止虚拟机：

<img src="https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-quit.png" alt="停止虚拟机" style="zoom:50%;" />

到此，安装成功。安装成功后，存储介质不会被电脑识别，因为 OS X 不能读取`ext4`分区。

# 安装介质的启动

安装成功的存储介质，可以通过 Windows 电脑中的 BIOS 进行 Legacy Boot。问题是 OS X 系统（更适合说成 Mac 电脑上）并不支持 Legacy Boot，只支持 EFI 启动。也就是说无法直接使用硬盘启动（即使在启动时按下<kbd>option</kbd>键也不行）。怎么办？这回 Parallels Desktop又派上了用场。

1. 新建（虚拟机）；
2. 从 DVD 或镜像文件；
3. 继续；
4. 手动选择；
5. 没有指定源也继续（相当于创建空白虚拟机）；
6. 选择操作系统 -> 更多 Linux -> 其它 Linux；
7. 虚拟机名称：U Machine（随便起名）。

创建完成后，直接停止虚拟机，在设置里作出如下配置：

![配置内存](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-conf-ram.png)

![配置启动顺序](https://cdn.jsdelivr.net/gh/TLHorse/TLBlogBed@master/2020/5/20/deepin-um-conf-seq.png)

现在启动一下虚拟机（你的存储介质应该是插着的），虚拟机会自动检测出你的存储介质，并从中启动。这样不论是在什么电脑上，都可以从你的存储介质中启动系统了！