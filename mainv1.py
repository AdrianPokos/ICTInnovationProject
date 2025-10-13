import xml.etree.ElementTree as ET

def main():
    try:
        xml_data = input("Enter XML: ")
        tree = ET.fromstring(xml_data)
        print("Parsed XML:", tree.text)
    except Exception as e:
        print("Error: " + str(e))
        print("An unexpected error occurred.")

main()
