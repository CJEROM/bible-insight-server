
import re

from ingestor.stepbible.morphology.codes.base_parser import BaseParser

from ingestor.stepbible.morphology.codes.base.case_code import CaseCode
from ingestor.stepbible.morphology.codes.base.extra_code import ExtraCode
from ingestor.stepbible.morphology.codes.base.form_code import FormCode
from ingestor.stepbible.morphology.codes.base.function_code import FunctionCode
from ingestor.stepbible.morphology.codes.base.gender_code import GenderCode
from ingestor.stepbible.morphology.codes.base.name_type_code import NameTypeCode
from ingestor.stepbible.morphology.codes.base.number_code import NumberCode
from ingestor.stepbible.morphology.codes.base.person_code import PersonCode
from ingestor.stepbible.morphology.codes.base.state_code import StateCode
from ingestor.stepbible.morphology.codes.base.stem_code import StemCode

from ingestor.stepbible.morphology.codes.derived.action_code import ActionCode
from ingestor.stepbible.morphology.codes.derived.mood_code import MoodCode
from ingestor.stepbible.morphology.codes.derived.tense_code import TenseCode
from ingestor.stepbible.morphology.codes.derived.voice_code import VoiceCode

from ingestor.stepbible.morphology.codes._greek_codes import GreekCode
from ingestor.stepbible.morphology.codes._hebrew_codes import HebrewCode

class CodeParser(BaseParser):
    def __init__(self, manager, log, code):
        super().__init__(
            manager = manager, 
            log     = log, 
            code    = code
        )

        self.get_function()
        self.check_code_system()

    def get_function(self):
        # Can't tell for very small codes what system, so instead don't link to one
        #       they will only contain function anyway so map to that straight
        pass

    def check_code_system(self):
        code_parts = self.code.split("-")
        if len(code_parts) > 0:
            GreekCode(
                manager = self.manager,
                log     = self.log,
                code    = self.code
            )

    def check_aramaic(self):
        pass
        # What is original language of item with code, and is this mapped to aramaic
        
    def process_line_one(self, line: str):
        code, elements = line.split("\t", 1)

        all_values = []

        for segment in elements.split(";"):
            name, data = segment.split("=")

            feature_id = self.write.write_morphology_features(
                name    = name.strip()
            )

            parent_value_id = self.write.write_morphology_feature_value(
                feature_id  = feature_id,
                feature     = name.strip(),
                value       = data.strip()
            )
            all_values.append(parent_value_id)
        
        return code, all_values
    
    def process_line_one(self, line: str):
        code, elements = line.split("\t", 1)

        normal_elements = re.sub(r"\(hence\s*[^)]*\)", "", elements)
        all_values = []

        matches = re.findall(r"\(hence\s*([^)]*)\)", elements)
        derived_elements = [None] * len(matches)
        derived_parents = [None] * len(matches)

        for i, match in enumerate(matches):
            matched_split = elements.split("(hence")

            derived_elements[0] = match.strip() # Grab first derived hence
            derived_parents[0] = matched_split[i].split(";")[-1].strip()
            
        for segment in normal_elements.split(";"):
            if segment.strip() == "":
                continue
            
            name, data = segment.split("=")

            feature_id = self.write.write_morphology_features(
                name    = name.strip()
            )

            parent_value_id = self.write.write_morphology_feature_value(
                feature_id  = feature_id,
                feature     = name.strip(),
                value       = data.strip()
            )
            all_values.append(parent_value_id)

            for i, parent in enumerate(derived_parents):
                if segment.strip() == parent and parent != None:
                    for segment in derived_elements[i].split(";"):
                        derived_name, derived_data = segment.split("=")

                        derived_feature_id = self.write.write_morphology_features(
                            name    = derived_name.strip()
                        )

                        derived_value_id = self.write.write_morphology_feature_value(
                            feature_id  = derived_feature_id,
                            feature     = derived_name.strip(),
                            value       = derived_data.strip()
                        )
                        all_values.append(derived_value_id)

                        self.write.write_morphology_derived_feature_value(
                            from_value      = parent_value_id,
                            derived_value   = derived_value_id
                        )
        
        return code, all_values

