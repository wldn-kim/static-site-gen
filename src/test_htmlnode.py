import unittest
from htmlnode import HTMLNode

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

if __name__ == "__main__":
    unittest.main()


