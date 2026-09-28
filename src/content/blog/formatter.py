import os
import re
import yaml
from datetime import datetime
from pathlib import Path


def clean_markdown(text: str) -> str:
    """清洗文本中的 Markdown 语法标识符，提取纯文本"""
    # 移除代码块
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # 移除行内代码
    text = re.sub(r"`[^`]+`", "", text)
    # 移除图片 ![alt](url)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    # 移除链接 [text](url) 保留文字
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    # 移除标题标记 #
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # 移除粗体、斜体 **、__、*、_
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)
    # 移除删除线 ~~
    text = re.sub(r"~~(.*?)~~", r"\1", text)
    # 移除引用标记 >
    text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)
    # 移除列表标记 -、*、数字.
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    # 移除水平分割线
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)
    # 移除 HTML 标签
    text = re.sub(r"<[^>]+>", "", text)
    # 合并多余空白
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_first_two_sentences(content: str) -> str:
    """从正文提取前两句话作为 description"""
    clean_text = clean_markdown(content)
    
    # 按句号、问号、感叹号分割句子
    sentences = re.split(r"(?<=[。！？.!?])\s*", clean_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) >= 2:
        desc = sentences[0] + sentences[1]
    elif len(sentences) == 1:
        desc = sentences[0]
    else:
        desc = ""
    
    # 限制长度 40-160 字，过长截断
    if len(desc) > 160:
        desc = desc[:157] + "..."
    
    return desc


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 Markdown 文件的 frontmatter，返回 (元数据字典, 正文内容)"""
    if not content.startswith("---"):
        return {}, content
    
    # 找到第二个 --- 的位置
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    fm_text = parts[1].strip()
    body = parts[2].lstrip("\n")
    
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError:
        fm = {}
    
    return fm, body


def build_frontmatter(fm: dict, body: str) -> str:
    """按照 ulbo 标准构建 frontmatter"""
    # 标准化字段
    result = {}
    
    # 1. title (必填)
    result["title"] = str(fm.get("title", "未命名文章")).strip()
    
    # 2. date (必填) - 确保 ISO 8601 +08:00 格式
    date_val = fm.get("date")
    if isinstance(date_val, datetime):
        result["date"] = date_val.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    elif isinstance(date_val, str) and date_val.strip():
        # 尝试解析并标准化
        try:
            # 处理常见格式
            for fmt in [
                "%Y-%m-%dT%H:%M:%S+08:00",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d"
            ]:
                try:
                    dt = datetime.strptime(date_val.strip(), fmt)
                    result["date"] = dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
                    break
                except ValueError:
                    continue
            else:
                result["date"] = date_val.strip()
        except Exception:
            result["date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    else:
        result["date"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    # 3. updated (可选)
    updated_val = fm.get("updated")
    if updated_val:
        if isinstance(updated_val, datetime):
            result["updated"] = updated_val.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        elif isinstance(updated_val, str) and updated_val.strip():
            try:
                for fmt in [
                    "%Y-%m-%dT%H:%M:%S+08:00",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d"
                ]:
                    try:
                        dt = datetime.strptime(updated_val.strip(), fmt)
                        result["updated"] = dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
                        break
                    except ValueError:
                        continue
            except Exception:
                pass
    
    # 4. description - 从正文前两句话生成
    description = extract_first_two_sentences(body)
    if description:
        result["description"] = description
    
    # 5. draft (可选，默认 false)
    draft_val = fm.get("draft", False)
    if draft_val is True:
        result["draft"] = True
    
    # 6. categories
    categories = fm.get("categories", [])
    if isinstance(categories, str):
        categories = [categories]
    # 正式文章确保至少一个分类
    if not categories and draft_val is not True:
        categories = ["未分类"]
    result["categories"] = list(categories) if categories else []
    
    # 7. tags - 标准化为小写
    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    # 英文标签转小写，去重
    normalized_tags = []
    seen = set()
    for tag in tags:
        tag_str = str(tag).strip()
        # 纯英文转小写
        if re.match(r"^[a-zA-Z0-9\s\-]+$", tag_str):
            tag_str = tag_str.lower().replace(" ", "-")
        if tag_str and tag_str not in seen:
            seen.add(tag_str)
            normalized_tags.append(tag_str)
    result["tags"] = normalized_tags
    
    # 移除禁止字段
    forbidden = {"pubDate", "updatedDate", "heroImage", "cover", 
                 "permalink", "comments", "layout", "laout", "excerpt"}
    for key in forbidden:
        result.pop(key, None)
    
    # 构建 YAML 字符串，手动控制格式以符合规范
    lines = ["---"]
    lines.append(f'title: "{result["title"]}"')
    lines.append(f'date: "{result["date"]}"')
    
    if "updated" in result:
        lines.append(f'updated: "{result["updated"]}"')
    
    if "description" in result:
        # 处理 description 中的双引号
        desc_escaped = result["description"].replace('"', '\\"')
        lines.append(f'description: "{desc_escaped}"')
    
    if "draft" in result:
        lines.append(f"draft: {str(result['draft']).lower()}")
    
    # categories 块数组格式
    lines.append("categories:")
    if result["categories"]:
        for cat in result["categories"]:
            lines.append(f'  - "{cat}"')
    else:
        lines.append("  []")
    
    # tags 块数组格式
    lines.append("tags:")
    if result["tags"]:
        for tag in result["tags"]:
            lines.append(f'  - "{tag}"')
    else:
        lines.append("  []")
    
    lines.append("---")
    
    return "\n".join(lines)


def rename_bak_to_md(directory: str) -> int:
    """批量将 .md.bak 文件重命名为 .md，返回处理数量"""
    count = 0
    dir_path = Path(directory)
    
    for bak_file in dir_path.rglob("*.md.bak"):
        md_file = bak_file.with_suffix("")  # 移除 .bak，得到 .md
        if not md_file.exists():
            bak_file.rename(md_file)
            print(f"重命名: {bak_file.name} -> {md_file.name}")
            count += 1
        else:
            print(f"跳过（目标已存在）: {bak_file.name}")
    
    return count


def process_markdown_files(directory: str) -> int:
    """批量处理所有 .md 文件的 frontmatter，返回处理数量"""
    count = 0
    dir_path = Path(directory)
    
    for md_file in dir_path.rglob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            fm, body = parse_frontmatter(content)
            new_fm = build_frontmatter(fm, body)
            
            # 组合新内容：frontmatter + 空行 + 正文
            new_content = new_fm + "\n\n" + body.lstrip("\n")
            
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print(f"已处理: {md_file.relative_to(dir_path)}")
            count += 1
            
        except Exception as e:
            print(f"处理失败 {md_file.name}: {e}")
    
    return count


def main():
    # 博客根目录路径，修改为你的实际路径
    blog_root = "./"  # 当前目录，可改为绝对路径
    
    print("=" * 50)
    print("步骤 1: 批量重命名 .md.bak -> .md")
    print("=" * 50)
    rename_count = rename_bak_to_md(blog_root)
    print(f"\n共重命名 {rename_count} 个文件\n")
    
    print("=" * 50)
    print("步骤 2: 标准化 Frontmatter 并生成 description")
    print("=" * 50)
    process_count = process_markdown_files(blog_root)
    print(f"\n共处理 {process_count} 个 Markdown 文件")


if __name__ == "__main__":
    main()
