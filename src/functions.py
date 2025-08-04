import re
from textnode import TextType, TextNode, BlockType
from htmlnode import LeafNode, ParentNode

def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(value=text_node.text)
    
    elif text_node.text_type == TextType.BOLD:
        return LeafNode(tag="b", value=text_node.text)
    
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode(tag="i", value=text_node.text)
    
    elif text_node.text_type == TextType.CODE:
        return LeafNode(tag="code", value=text_node.text)
    
    elif text_node.text_type == TextType.LINK:
        if not text_node.url:
            raise ValueError("TextNode with type LINK must have a url.")
        return LeafNode(tag="a", value=text_node.text, props={"href": text_node.url})
    
    elif text_node.text_type == TextType.IMAGE:
        if not text_node.url:
            raise ValueError("TextNode with type IMAGE must have a url.")
        return LeafNode(tag="img", value="", props={
            "src": text_node.url,
            "alt": text_node.text
        })
    
    else:
        raise ValueError(f"Unknown TextType: {text_node.text_type}")
    
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    all_delimiters = {"**", "_", "`"}

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        if not node.text:
            continue

        segments = node.text.split(delimiter)
        if len(segments) < 3 or len(segments) % 2 == 0:
            new_nodes.append(node)
            continue

        if delimiter != "`":
            has_nested = any(
                any(other in segments[i] for other in all_delimiters if other != delimiter)
                for i in range(1, len(segments), 2)
            )
            if has_nested:
                new_nodes.append(node)
                continue

        for i, segment in enumerate(segments):
            if segment == "" and i % 2 == 0:
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(segment, TextType.TEXT))
            else:
                new_nodes.append(TextNode(segment, text_type))

    return new_nodes

def extract_markdown_images(text):
    pattern = r'!\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    pattern = r'(?<!!)\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    pattern = r"!\[([^\]]+)\]\(([^()\s]+)\)"

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        last_index = 0
        for match in re.finditer(pattern, node.text):
            alt, url = match.group(1), match.group(2)
            start, end = match.span()

            if start > last_index:
                new_nodes.append(TextNode(node.text[last_index:start], TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))

            last_index = end

        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    pattern = r"(?<!!)\[([^\]]+)\]\(([^)]+)\)"

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        last_index = 0
        for match in re.finditer(pattern, node.text):
            text, url = match.group(1), match.group(2)
            start, end = match.span()

            if start > last_index:
                new_nodes.append(TextNode(node.text[last_index:start], TextType.TEXT))
            new_nodes.append(TextNode(text, TextType.LINK, url))

            last_index = end

        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT))

    return new_nodes

def text_to_textnodes(text):
    if "**" in text and "_" in text:
        if "_**" in text or "**_" in text or "_**" in text[::-1] or "**_" in text[::-1]:
            return [TextNode(text, TextType.TEXT)]

    nodes = [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

    return nodes

def markdown_to_blocks(markdown):
    raw_blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in raw_blocks if block.strip()]
    return blocks

def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")

    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    if re.match(r"^#{1,6} ", lines[0]):
        return BlockType.HEADING
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    ordered_match = True
    for i, line in enumerate(lines):
        expected_prefix = f"{i+1}. "
        if not line.startswith(expected_prefix):
            ordered_match = False
            break
    if ordered_match:
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def text_to_children(text):
    return [text_node_to_html_node(node) for node in text_to_textnodes(text)]

def block_to_html_node(block):
    block_type = block_to_block_type(block)

    if block_type == BlockType.PARAGRAPH:
        normalized_text = " ".join(block.splitlines()).strip()
        children = text_to_children(normalized_text)
        return ParentNode("p", children)
    
    elif block_type == BlockType.HEADING:
        heading_level = len(re.match(r"^(#+)", block).group(1))
        text = block[heading_level+1:].strip()
        children = text_to_children(text)
        return ParentNode(f"h{heading_level}", children)

    elif block_type == BlockType.CODE:
        inner = block.strip()[3:-3].lstrip("\n")
        text_node = TextNode(inner, TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        return ParentNode("pre", [ParentNode("code", [html_node])])

    elif block_type == BlockType.QUOTE:
        lines = [line[1:].strip() for line in block.split("\n")]
        inner_text = " ".join(lines)
        children = text_to_children(inner_text)
        return ParentNode("blockquote", children)

    elif block_type == BlockType.UNORDERED_LIST:
        items = block.split("\n")
        li_nodes = [ParentNode("li", text_to_children(item[2:].strip())) for item in items]
        return ParentNode("ul", li_nodes)

    elif block_type == BlockType.ORDERED_LIST:
        items = block.split("\n")
        li_nodes = []
        for item in items:
            dot_index = item.find(". ")
            if dot_index != -1:
                text = item[dot_index+2:].strip()
                li_nodes.append(ParentNode("li", text_to_children(text)))
        return ParentNode("ol", li_nodes)

    else:
        raise ValueError(f"Unsupported block type: {block_type}")

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    block_nodes = [block_to_html_node(block) for block in blocks]
    return ParentNode("div", block_nodes)

def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise Exception("No H1 header found in markdown.")

