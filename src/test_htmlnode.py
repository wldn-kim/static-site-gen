import unittest

from textnode import TextNode, TextType, BlockType
from htmlnode import HTMLNode, LeafNode, ParentNode
from functions import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, markdown_to_blocks, block_to_block_type

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_multiple_attributes(self): 
        node = HTMLNode(
            tag="a",
            value="Click here",
            props={"href": "https://www.google.com", "target": "_blank"}
        )
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_single_attribute(self):
        node = HTMLNode(
            tag="img",
            props={"src": "image.png"}
        )
        expected = ' src="image.png"'
        self.assertEqual(node.props_to_html(), expected)

    def test_props_to_html_no_attributes(self):
        node = HTMLNode(tag="p")
        expected = ''
        self.assertEqual(node.props_to_html(), expected)

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_leaf_to_html_span_with_props(self):
        node = LeafNode("span", "Label", {"class": "highlight"})
        self.assertEqual(node.to_html(), '<span class="highlight">Label</span>')

    def test_leaf_to_html_h1(self):
        node = LeafNode("h1", "Welcome!")
        self.assertEqual(node.to_html(), "<h1>Welcome!</h1>")

    def test_leaf_to_html_anchor_with_href(self):
        node = LeafNode("a", "Visit site", {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">Visit site</a>')

    def test_leaf_to_html_plain_text_no_tag(self):
        node = LeafNode(value="Just text, no tag.")
        self.assertEqual(node.to_html(), "Just text, no tag.")

    def test_leaf_to_html_empty_value(self):
        node = LeafNode("br", "")
        self.assertEqual(node.to_html(), "<br></br>")

class TestParentNode(unittest.TestCase):

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    def test_to_html_with_multiple_children(self):
        children = [
            LeafNode("h1", "Header"),
            LeafNode("p", "Paragraph"),
            LeafNode("a", "Link", {"href": "https://example.com"})
        ]
        parent_node = ParentNode("section", children)
        expected = (
            "<section><h1>Header</h1><p>Paragraph</p>"
            '<a href="https://example.com">Link</a></section>'
        )
        self.assertEqual(parent_node.to_html(), expected)

    def test_to_html_with_nested_parents_and_props(self):
        tree = ParentNode("div", [
            ParentNode("ul", [
                LeafNode("li", "Item 1"),
                LeafNode("li", "Item 2")
            ], props={"class": "list"}),
            LeafNode("p", "Footer")
        ], props={"id": "main"})
        expected = (
            '<div id="main"><ul class="list"><li>Item 1</li><li>Item 2</li></ul>'
            '<p>Footer</p></div>'
        )
        self.assertEqual(tree.to_html(), expected)

    def test_to_html_with_no_tag_raises(self):
        child = LeafNode("p", "text")
        with self.assertRaises(ValueError) as context:
            node = ParentNode(None, [child])
        self.assertIn("ParentNode must have a tag", str(context.exception))

    def test_to_html_with_no_children_raises(self):
        with self.assertRaises(ValueError) as context:
            node = ParentNode("div", None)
        self.assertIn("ParentNode must have children", str(context.exception))

    def test_to_html_with_empty_children_list(self):
        node = ParentNode("div", [])
        self.assertEqual(node.to_html(), "<div></div>")  # valid but empty content

    def test_to_html_with_text_only_leaf_children(self):
        node = ParentNode("p", [
            LeafNode(value="Hello "),
            LeafNode("b", "bold"),
            LeafNode(value=" world.")
        ])
        self.assertEqual(node.to_html(), "<p>Hello <b>bold</b> world.</p>")

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_single_code_block(self):
        node = TextNode("This is `code`", TextType.TEXT)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, expected)

    def test_multiple_code_blocks(self):
        node = TextNode("`first` middle `second` end", TextType.TEXT)
        expected = [
            TextNode("first", TextType.CODE),
            TextNode(" middle ", TextType.TEXT),
            TextNode("second", TextType.CODE),
            TextNode(" end", TextType.TEXT),
        ]
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, expected)

    def test_no_delimiters(self):
        node = TextNode("Just plain text", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [node])

    def test_odd_number_of_delimiters(self):
        node = TextNode("Unmatched `delimiter here", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [node])

    def test_italic_text(self):
        node = TextNode("Some _italic_ text", TextType.TEXT)
        expected = [
            TextNode("Some ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(result, expected)

    def test_bold_text(self):
        node = TextNode("**Bold** statement", TextType.TEXT)
        expected = [
            TextNode("Bold", TextType.BOLD),
            TextNode(" statement", TextType.TEXT),
        ]
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(result, expected)

    def test_mixed_text_node_types(self):
        node1 = TextNode("Text with `code`", TextType.TEXT)
        node2 = TextNode("Already bold", TextType.BOLD)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            node2
        ]
        result = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        self.assertEqual(result, expected)

    def test_empty_string(self):
        node = TextNode("", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [])

    def test_only_delimiters(self):
        node = TextNode("``", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, [TextNode("", TextType.CODE)])

    def test_nested_delimiters_not_handled(self):
        # Note: This function does not support nested or overlapping formatting
        node = TextNode("This is _not `nested_ code`", TextType.TEXT)
        expected = [
            TextNode("This is _not ", TextType.TEXT),
            TextNode("nested_ code", TextType.CODE),
        ]
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(result, expected)

class TestMarkdownExtractors(unittest.TestCase):
    def test_extract_markdown_images_single(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")],
            matches
        )

    def test_extract_markdown_images_multiple(self):
        text = "Check ![one](url1.png) and ![two](url2.jpg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("one", "url1.png"), ("two", "url2.jpg")],
            matches
        )

    def test_extract_markdown_images_with_extra_text(self):
        text = "![alt](img1.png) some text ![another](img2.gif)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("alt", "img1.png"), ("another", "img2.gif")],
            matches
        )

    def test_extract_markdown_images_no_matches(self):
        text = "Just some text and [a link](https://example.com)"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_images_malformed(self):
        text = "![no end (http://img.png) ![alt](no-close"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_links_single(self):
        matches = extract_markdown_links(
            "A [link](https://www.example.com)"
        )
        self.assertListEqual(
            [("link", "https://www.example.com")],
            matches
        )

    def test_extract_markdown_links_multiple(self):
        text = "[Google](https://google.com) and [Bing](https://bing.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("Google", "https://google.com"), ("Bing", "https://bing.com")],
            matches
        )

    def test_extract_markdown_links_mixed_with_images(self):
        text = "A link: [Link](https://link.com) and image: ![Img](https://img.png)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("Link", "https://link.com")],
            matches
        )

    def test_extract_markdown_links_no_matches(self):
        text = "Just text and ![alt](img.png)"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_links_malformed(self):
        text = "[not closed(link.com [bad](incomplete"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

class TestSplitMarkdownNodes(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_image_only(self):
        node = TextNode("![alt](https://img.com/pic.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([
            TextNode("alt", TextType.IMAGE, "https://img.com/pic.png")
        ], new_nodes)

    def test_split_image_with_non_text_type(self):
        node = TextNode("![alt](https://img.com/pic.png)", TextType.IMAGE, "https://img.com/pic.png")
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_image_with_extra_text(self):
        node = TextNode("Before ![img](url.png) After", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([
            TextNode("Before ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "url.png"),
            TextNode(" After", TextType.TEXT)
        ], new_nodes)

    def test_split_image_malformed(self):
        node = TextNode("Text ![bad](url with missing ) or extra ![noend](https://url", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_split_link_only(self):
        node = TextNode("[click](http://url.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([
            TextNode("click", TextType.LINK, "http://url.com")
        ], new_nodes)

    def test_split_link_mixed_with_image(self):
        node = TextNode("Link [go](url.com) and ![pic](img.png)", TextType.TEXT)
        nodes_after_link = split_nodes_link([node])
        nodes_final = split_nodes_image(nodes_after_link)
        self.assertListEqual([
            TextNode("Link ", TextType.TEXT),
            TextNode("go", TextType.LINK, "url.com"),
            TextNode(" and ", TextType.TEXT),
            TextNode("pic", TextType.IMAGE, "img.png")
        ], nodes_final)

    def test_split_link_malformed(self):
        node = TextNode("[bad](url", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_split_link_with_non_text_type(self):
        node = TextNode("Some link", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_empty_input(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_whitespace_only(self):
        md = "   \n  \n\n\n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_trailing_and_leading_whitespace(self):
        md = """

    # Heading


Paragraph with spaces around


"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Heading",
                "Paragraph with spaces around"
            ],
        )

    def test_multiple_list_blocks(self):
        md = """
- Item 1
- Item 2

- Item A
- Item B
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "- Item 1\n- Item 2",
                "- Item A\n- Item B",
            ],
        )

class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Level 6"), BlockType.HEADING)
        self.assertNotEqual(block_to_block_type("####### Too much"), BlockType.HEADING)

    def test_code_block(self):
        code = "```\ndef hello():\n    return 'hi'\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

        bad_code = "```\ndef hello():\n    return 'hi'\n``"  # not properly closed
        self.assertNotEqual(block_to_block_type(bad_code), BlockType.CODE)

    def test_quote_block(self):
        quote = "> This is a quote\n> With multiple lines"
        self.assertEqual(block_to_block_type(quote), BlockType.QUOTE)

        bad_quote = "> Valid\nNot valid"
        self.assertNotEqual(block_to_block_type(bad_quote), BlockType.QUOTE)

    def test_unordered_list(self):
        ul = "- Item one\n- Item two\n- Item three"
        self.assertEqual(block_to_block_type(ul), BlockType.UNORDERED_LIST)

        bad_ul = "- Item one\n* Item two"
        self.assertNotEqual(block_to_block_type(bad_ul), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        ol = "1. First\n2. Second\n3. Third"
        self.assertEqual(block_to_block_type(ol), BlockType.ORDERED_LIST)

        skip_number = "1. First\n3. Third"
        self.assertNotEqual(block_to_block_type(skip_number), BlockType.ORDERED_LIST)

        unordered_format = "1) One\n2) Two"
        self.assertNotEqual(block_to_block_type(unordered_format), BlockType.ORDERED_LIST)

    def test_paragraph(self):
        paragraph = "This is just a regular paragraph with **bold** and _italic_."
        self.assertEqual(block_to_block_type(paragraph), BlockType.PARAGRAPH)

        multiline_para = "Line one of paragraph\nLine two of paragraph"
        self.assertEqual(block_to_block_type(multiline_para), BlockType.PARAGRAPH)

if __name__ == "__main__":
    unittest.main()


