import unittest

from textnode import TextNode, TextType
from functions import text_to_textnodes, text_node_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_not_equal_different_text(self):
        node1 = TextNode("Text A", TextType.BOLD)
        node2 = TextNode("Text B", TextType.BOLD)
        self.assertNotEqual(node1, node2)

    def test_not_equal_different_type(self):
        node1 = TextNode("Same text", TextType.ITALIC)
        node2 = TextNode("Same text", TextType.CODE)
        self.assertNotEqual(node1, node2)

    def test_not_equal_different_url(self):
        node1 = TextNode("Click here", TextType.LINK, "https://example.com")
        node2 = TextNode("Click here", TextType.LINK, "https://another.com")
        self.assertNotEqual(node1, node2)

    def test_equal_with_none_url(self):
        node1 = TextNode("Hello", TextType.TEXT)
        node2 = TextNode("Hello", TextType.TEXT, None)
        self.assertEqual(node1, node2)

class TestTextToTextNodes(unittest.TestCase):
    def test_plain_text_only(self):
        text = "Just plain text here"
        result = text_to_textnodes(text)
        self.assertEqual(result, [TextNode("Just plain text here", TextType.TEXT)])

    def test_single_bold(self):
        text = "This is **bold** text"
        result = text_to_textnodes(text)
        self.assertEqual(result, [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ])

    def test_multiple_styles(self):
        text = "Here is _italic_, **bold**, and `code`"
        result = text_to_textnodes(text)
        self.assertEqual(result, [
            TextNode("Here is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(", ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(", and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ])

    def test_images_and_links(self):
        text = "See ![pic](img.png) and [link](https://example.com)"
        result = text_to_textnodes(text)
        self.assertEqual(result, [
            TextNode("See ", TextType.TEXT),
            TextNode("pic", TextType.IMAGE, "img.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ])

    def test_all_combined(self):
        text = (
            "Text with **bold**, _italic_, `code`, ![alt](img.png), and [a link](https://url.com)"
        )
        result = text_to_textnodes(text)
        self.assertEqual(result, [
            TextNode("Text with ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(", ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(", ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(", ", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, "img.png"),
            TextNode(", and ", TextType.TEXT),
            TextNode("a link", TextType.LINK, "https://url.com"),
        ])

    def test_nested_styles_not_supported(self):
        text = "_**bold italic**_"
        result = text_to_textnodes(text)
        self.assertEqual(result, [
            TextNode("_**bold italic**_", TextType.TEXT)
        ])

    def test_unmatched_delimiters(self):
        text = "Text with **unmatched bold and _italic"
        result = text_to_textnodes(text)
        self.assertEqual(result, [
            TextNode("Text with **unmatched bold and _italic", TextType.TEXT)
        ])

    def test_empty_string(self):
        result = text_to_textnodes("")
        self.assertEqual(result, [])

class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_code(self):
        node = TextNode("code snippet", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "code snippet")

    def test_link(self):
        node = TextNode("Visit site", TextType.LINK, url="https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Visit site")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_link_missing_url_raises(self):
        node = TextNode("Link text", TextType.LINK)
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(node)
        self.assertIn("must have a url", str(context.exception))

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, url="https://img.com/cat.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {
            "src": "https://img.com/cat.png",
            "alt": "Alt text"
        })

    def test_image_missing_url_raises(self):
        node = TextNode("No URL", TextType.IMAGE)
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(node)
        self.assertIn("must have a url", str(context.exception))

    def test_invalid_text_type_raises(self):
        class FakeTextType: pass
        node = TextNode("Invalid", FakeTextType)
        with self.assertRaises(ValueError) as context:
            text_node_to_html_node(node)
        self.assertIn("Unknown TextType", str(context.exception))

if __name__ == "__main__":
    unittest.main()