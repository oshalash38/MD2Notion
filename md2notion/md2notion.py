"""
This module provides a class `MD2Notion` for parsing a markdown-like text file into a structured 
list of blocks compatible with the Notion API. It handles headings, bulleted lists, and text formatting 
such as bold text, allowing hierarchical sublist nesting.

Classes:
    - MD2Notion: Main class for parsing the text and converting it into Notion API-compatible blocks.

Methods:
    - parse(text: str): Parses the input text into structured Notion blocks.
    - convert_to_block(line: str): Converts a single line of text into a Notion-compatible block.
    - create_bulleted_list_item(content: str): Helper method to create a bulleted list item block.
    - process_rich_text(text: str): Processes text to identify and handle bold formatting.

Dependencies:
    - re: Regular expression library for text processing.
"""
import re
from typing import Dict, List

class MD2Notion:
    def __init__(self) -> None:
        pass

    def parse(self, text: str) -> List[Dict]:
        """
        Parses markdown-like text into a list of Notion API-compatible blocks.

        Args:
            text (str): The input markdown-like text to parse.

        Returns:
            list: A list of Notion-compatible block objects representing the parsed structure.
        """
        lines = text.splitlines()
        blocks = []
        parent_block = None
        grandparent_block = None

        for line in lines:
            if line.startswith("    - "):  # Detect third-level sublist items
                if parent_block:
                    # Add third-level item as a child of the second-level item
                    sublist_item = self.create_bulleted_list_item(line.strip()[6:])
                    parent_block["bulleted_list_item"].setdefault("children", []).append(sublist_item)

            elif line.startswith("  - "):  # Detect second-level sublist items
                if grandparent_block:
                    # Add second-level item as a child of the top-level item
                    sublist_item = self.create_bulleted_list_item(line.strip()[2:])
                    grandparent_block["bulleted_list_item"].setdefault("children", []).append(sublist_item)
                    # Update parent_block to the current sublist item for third-level nesting
                    parent_block = sublist_item

            elif line.startswith("- "):  # Detect top-level items
                block = self.convert_to_block(line)
                if block:
                    blocks.append(block)
                    # Update grandparent_block and reset parent_block for new top-level item
                    grandparent_block = block
                    parent_block = None  # Reset for top-level items without children

            else:
                # Process any non-list item as a regular block
                block = self.convert_to_block(line)
                if block:
                    blocks.append(block)
                    parent_block = None  # Reset parent block for non-list items
                    grandparent_block = None

        return blocks

    def convert_to_block(self, line: str) -> Dict:
        """
        Converts a line of text into a Notion API-compatible block.

        Args:
            line (str): A line of text to convert.

        Returns:
            dict: A dictionary representing a Notion block or None if the line is empty.
        """
        # Heading 1 (### Summary of Key Points)
        if line.startswith("### "):
            return {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": self.process_rich_text(line[4:].strip())
                }
            }

        # Heading 2 with numbered section title (#### 1. Section Title)
        elif re.match(r"^####\s\d+\.\s", line):
            return {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": self.process_rich_text(line[5:].strip())
                }
            }

        # Heading 2 without numbers (#### Section Title)
        elif line.startswith("#### "):
            return {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": self.process_rich_text(line[5:].strip())
                }
            }

        # Bolded heading with explanatory text (e.g., - **Men's Testicles:** Explanation)
        elif re.match(r"^- \*\*(.*?)\*\*", line):
            match = re.match(r"^- \*\*(.*?)\*\*(.*)", line)
            if match:
                bold_text = match.group(1).strip()
                explanation = match.group(2).strip()
                # Process explanation for additional bold text
                explanation_rich_text = self.process_rich_text(explanation)
                return {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {"type": "text", "text": {"content": bold_text}, "annotations": {"bold": True}},
                            {"type": "text", "text": {"content": ": "}}  # Add colon after bold heading
                        ] + explanation_rich_text  # Append processed explanation
                    }
                }

        # Regular bulleted list item (e.g., - Explanation without bold)
        elif line.startswith("- "):
            return self.create_bulleted_list_item(line[2:].strip())

        # Paragraph for any remaining non-bulleted text (e.g., conclusion)
        elif line:
            return {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": self.process_rich_text(line)
                }
            }
        else:
            # Empty paragraph for blank lines
            return {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": ""}}]
                }
            }

    def create_bulleted_list_item(self, content: str) -> Dict:
        """
        Helper method to create a bulleted list item block.

        Args:
            content (str): The content of the list item.

        Returns:
            dict: A dictionary representing the bulleted list item block.
        """
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": self.process_rich_text(content)
            }
        }

    def process_rich_text(self, text: str) -> List[Dict]:
        """
        Processes a line of text to identify bold text and split it into rich text objects.

        Args:
            text (str): The text to process.

        Returns:
            list: A list of dictionaries representing rich text objects.
        """
        rich_text = []
        parts = re.split(r"(\*\*.*?\*\*)", text)  # Split on bold markers

        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                # Strip '**' markers and mark as bold
                content = part[2:-2]
                rich_text.append({"type": "text", "text": {"content": content},
                                  "annotations": {"bold": True}})
            else:
                # Regular text
                rich_text.append({"type": "text", "text": {"content": part}})

        return rich_text
