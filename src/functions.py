import re
from textnode import TextType, TextNode, BlockType
from htmlnode import LeafNode

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

def block_to_block_type(block):
    lines = block.splitlines()

    if lines[0].strip().startswith("```") and lines[-1].strip().endswith("```"):
        return BlockType.CODE

    if re.match(r"^#{1,6} ", lines[0]):
        return BlockType.HEADING

    if all(line.strip().startswith(">") for line in lines):
        return BlockType.QUOTE

    if all(line.strip().startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    ordered = True
    for i, line in enumerate(lines):
        if not re.match(rf"^{i+1}\. ", line.strip()):
            ordered = False
            break
    if ordered:
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH