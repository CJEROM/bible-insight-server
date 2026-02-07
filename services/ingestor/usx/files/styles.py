from ingestor.usx.files.base_file import BaseFile

from bs4 import BeautifulSoup

from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manager.managerhandler import ManagerHandler
    from manager.logmanager import LogManager

class Styles(BaseFile):
    def __init__(self, styles_file_id: int, main_manager: "ManagerHandler", log: "LogManager", source_id: int | None, file_path: Path = None):
        super().__init__(main_manager, log, source_id, file_path)
        self.log.log_to_file(f"Processing Styles ...", "STYLES", "INFO")
        
        self.style_dict = {}

        self.createStylesAndProperties(self.read_file(), styles_file_id)

    def get_style_dict(self):
        return self.style_dict

    def createStylesAndProperties(self, styles_string, styles_file_id):
        style_additions         = 0
        property_additions      = 0

        styles_xml              = BeautifulSoup(styles_string, "xml")
        properties              = styles_xml.find_all("property")

        previous_style_parent   = None
        style_id                = None

        for property in properties:
            style_parent    = property.find_parent("style")
            
            property_name   = property.get("name")
            property_unit   = property.get("unit")
            property_value  = property.text

            if style_parent == None:
                # General Properties (without a parent style in stylesheet)
                self.write.persist_style_property(
                    name    = property_name,
                    value   = property_value,
                    unit    = property_unit
                )
                property_additions +=1
                continue

            if previous_style_parent != style_parent:
                # Create new style
                style               = style_parent.get("id")
                style_name          = style_parent.find("name").text
                style_description   = style_parent.find("description").text
                style_versetext     = style_parent.get("versetext")
                style_publishable   = style_parent.get("publishable")

                self.write.persist_style(
                    style           = style,
                    name            = style_name,
                    description     = style_description,
                    is_versetext    = style_versetext,
                    is_publishable  = style_publishable,
                    source_file_id  = styles_file_id
                )
                style_additions += 1

                self.style_dict[style]              = {}
                self.style_dict[style]["id"]        = style_id
                self.style_dict[style]["versetext"] = style_versetext

                previous_style_parent = style_parent

            self.write.persist_style_property(
                name        = property_name,
                value       = property_value,
                unit        = property_unit,
                style_id    = style_id
            )
            property_additions +=1

        if style_additions > 0:
            print(f"    [{style_additions}] Styles loaded into database")

        if property_additions > 0:
            print(f"    [{property_additions}] Properties loaded into database")

        self.log.log_to_file(f"Initialised {style_additions} Styles!", "STYLES", "INFO")
        self.log.log_to_file(f"Initialised {property_additions} Properties!", "STYLES", "INFO")
