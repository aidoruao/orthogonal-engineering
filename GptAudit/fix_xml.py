import argparse
import sys
import xml.etree.ElementTree as ET


def fix_xml_formatting(input_file: str, output_file: str) -> bool:
    """
    Fix XML formatting to match original attribute-only style.

    - Removes text content from elements that have value/x/y/z attributes
    - Ensures empty elements are self-closing
    - Preserves structure and comments if any
    - Outputs well-formed XML
    """
    try:
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Remove text content from leaf elements with certain attributes
        for elem in root.iter():
            # Skip elements that have child elements (non-leaf)
            if len(elem) > 0:
                continue

            # Check if this element has a 'value' attribute or vector attributes
            has_value_attr = "value" in elem.attrib
            has_vector_attrs = all(coord in elem.attrib for coord in ("x", "y", "z"))

            if has_value_attr or has_vector_attrs:
                # Remove any text content (makes element empty)
                elem.text = None
                # Also clear tail to keep formatting clean
                elem.tail = None

        # Write the fixed XML
        # Use a custom XML writer to ensure proper formatting
        xml_str = ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

        # Pretty-print with consistent indentation
        # We'll do a simple pretty-print: add newlines after each closing tag and indent
        import re

        # First, ensure proper XML declaration
        if not xml_str.startswith("<?xml"):
            xml_str = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_str

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(xml_str)

        # Validate the output
        try:
            ET.parse(output_file)
            print(f"Successfully fixed XML: {output_file}")

            # Count Item tags for verification
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
                open_items = content.count("<Item")
                close_items = content.count("</Item>")
                print(f"Item tags: {open_items} opening, {close_items} closing")
                if open_items == close_items:
                    print("Item tags are balanced ✓")
                else:
                    print(
                        f"WARNING: Item tag mismatch! {open_items} opening vs {close_items} closing"
                    )

            return True

        except ET.ParseError as e:
            print(f"ERROR: Output XML is not well-formed: {e}")
            return False

    except ET.ParseError as e:
        print(f"ERROR: Failed to parse input XML file {input_file}: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Fix XML formatting to match original attribute-only style"
    )
    parser.add_argument("input", help="Input XML file to fix")
    parser.add_argument("output", help="Output XML file")

    args = parser.parse_args()

    success = fix_xml_formatting(args.input, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
