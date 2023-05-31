import os
import shutil
import argparse
from lxml import etree
from pathlib import Path

def merge_alps(base_file, overlay_file, output_file):
    parser = etree.XMLParser(strip_cdata=False)
    base_tree = etree.parse(base_file, parser=parser)
    overlay_tree = etree.parse(overlay_file, parser=parser)

    # Add/Merge ActiveObjectClasses
    # (namely, the JSONifier agent)
    base_active_object_classes = base_tree.xpath('.//ActiveObjectClass')
    overlay_active_object_classes = overlay_tree.xpath('.//ActiveObjectClass')
    for overlay_class in overlay_active_object_classes:
        overlay_name = overlay_class.find('Name').text
        existing_class = next((c for c in base_active_object_classes if c.find('Name').text == overlay_name), None)
        if existing_class is not None:
            existing_class.getparent().remove(existing_class)
        base_tree.find('Model/ActiveObjectClasses').append(overlay_class)

    # Add/Merge JavaClasses
    # (also includes interfaces)
    base_java_classes = base_tree.xpath('.//JavaClass')
    overlay_java_classes = overlay_tree.xpath('.//JavaClass')
    for overlay_class in overlay_java_classes:
        overlay_name = overlay_class.find('Name').text
        existing_class = next((c for c in base_java_classes if c.find('Name').text == overlay_name), None)
        if existing_class is not None:
            existing_class.getparent().remove(existing_class)
        base_tree.find('Model/JavaClasses').append(overlay_class)

    # Copy and merge Resource tags
    # (Images used in the library)
    base_resources = base_tree.xpath('.//ModelResources/Resource')
    overlay_resources = overlay_tree.xpath('.//ModelResources/Resource')
    base_resources_paths = {res.find('Path').text for res in base_resources}
    for overlay_resource in overlay_resources:
        overlay_path = overlay_resource.find('Path').text
        if overlay_path not in base_resources_paths:
            base_tree.find('.//ModelResources').append(overlay_resource)
            base_resources_paths.add(overlay_path)

            # Copy the file to the parent folder of the base file
            overlay_parent = os.path.dirname(overlay_file)
            base_parent = os.path.dirname(base_file)
            overlay_file_path = os.path.join(overlay_parent, overlay_path)
            base_file_path = os.path.join(base_parent, overlay_path)
            shutil.copy2(overlay_file_path, base_file_path)

    # Add/Merge AOCEntry tags based on Icon16ResourceReference/ClassName value
    # (Agent export selection in Library object)
    base_aoc_entries = base_tree.xpath('.//Library/AOCEntry')
    overlay_aoc_entries = overlay_tree.xpath('.//Library/AOCEntry')
    for overlay_entry in overlay_aoc_entries:
        overlay_class_name = overlay_entry.find('Icon16ResourceReference/ClassName').text
        existing_entry = next((e for e in base_aoc_entries if e.find('Icon16ResourceReference/ClassName').text == overlay_class_name), None)
        if existing_entry is not None:
            existing_entry.getparent().remove(existing_entry)
        base_tree.find('.//Library').append(overlay_entry)

    # Find/Replace any JSONifier package names to Pypeline ones
    # (namely occur in resource references)
    pypeline_pkg = base_tree.find('Model/JavaPackageName').text
    jsonifier_pkg = overlay_tree.find('Model/JavaPackageName').text
    package_name_elements = base_tree.xpath('.//PackageName')
    for package_name_element in package_name_elements:
        if package_name_element.text == jsonifier_pkg:
            new_element = etree.Element(package_name_element.tag)
            new_element.text = etree.CDATA(pypeline_pkg)
            package_name_element.getparent().replace(package_name_element, new_element)

    # Save the merged XML file
    base_tree.write(output_file, encoding='UTF-8', xml_declaration=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helper script to merge the JSONifier library's source model into Pypeline's source model (to automate integrating JSONifier updates)")
    parser.add_argument("pypeline_alp", help="The path to Pypeline's ALP file")
    parser.add_argument("jsonifier_alp", help="The path to JSONifier's ALP file")
    parser.add_argument("-b", "--backup", action="store_true", help="Backup the Pypeline file as a precaution")
    args = parser.parse_args()

    base_file = Path(args.pypeline_alp).absolute()
    if not base_file.exists():
        raise FileNotFoundError(f"No Pypeline ALP @ {base_file}")
    mod_file = Path(args.jsonifier_alp).absolute()
    if not mod_file.exists():
        raise FileNotFoundError(f"No JSONifier ALP @ {mod_file}")

    if args.backup:
        shutil.copy2(str(base_file), str(base_file.with_suffix(".alp.bak")))

    merge_alps(str(base_file), str(mod_file), str(base_file))
