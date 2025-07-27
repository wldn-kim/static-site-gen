import unittest
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node

# HTMLNode testing
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

# LeafNode testing
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

# ParentNode testing
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

# TextNode to HTMLNode testing
class TestTextNodeToHTMLNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN)
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


