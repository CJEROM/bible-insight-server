


from ingestor.stepbible.tagged.TAHOT import TAHOT
from ingestor.stepbible.tagged.TAGNT import TAGNT
from ingestor.stepbible.tagged.TTESV import TTESV

from ingestor.stepbible.lexicon.TEBSG import TEBSG
from ingestor.stepbible.lexicon.TEBSH import TEBSH
from ingestor.stepbible.lexicon.TFLSJ import TFLSJ

from ingestor.stepbible.morphology.TEGMC import TEGMC
from ingestor.stepbible.morphology.TEHMC import TEHMC

from ingestor.stepbible.other.TIPNR import TIPNR
from ingestor.stepbible.other.TVTMS import TVTMS

from manager.managerhandler import ManagerHandler
from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

class STEPBibleIngestor:
    def __init__(self, manager: ManagerHandler | None = None):
        self.manager        = manager or ManagerHandler()
        self.log            = self.manager.create_log_in_folder(["logs", "ingestor", "stepbible"])
        self.db             = self.manager.get_db()

        self.write = StepBibleWriteBoundary(self.db)
        self.read  = StepBibleReadBoundary(self.db)

        self.ingest()
        # FUTURE: Potentially ingest all the current corrections flagged, and link issue to entries

    def ingest(self):
        # ================================================================================================================
        #                                                   Morphology Codes
        # ================================================================================================================

        # Translators Expansion of Greek Morphhology Codes
        TEGMC(
            manager     = self.manager,
            log         = self.log
        )
        print("Completed: TEGMC - Translators Expansion of Greek Morphhology Codes")

        # Translators Expansion of Hebrew Morphology Codes
        TEHMC(
            manager     = self.manager,
            log         = self.log
        )
        print("Completed: TEHMC - Translators Expansion of Hebrew Morphology Codes")

        # ================================================================================================================
        #                                                   Lexicons
        # ================================================================================================================

        # Translators Brief lexicon of Extended Strongs for Greek
        TEBSG(
            manager     = self.manager,
            log         = self.log
        )
        print("Completed: TEBSG - Translators Brief lexicon of Extended Strongs for Greek")

        # Translators Brief lexicon of Extended Strongs for Hebrew
        TEBSH(
            manager     = self.manager,
            log         = self.log
        )
        print("Completed: TEBSH - Translators Brief lexicon of Extended Strongs for Hebrew")

        # Translators Formatted full LSJ Bible lexicon
        TFLSJ(
            manager     = self.manager,
            log         = self.log
        )
        print("Completed: TFLSJ - Translators Formatted full LSJ Bible lexicon")

        # # ================================================================================================================
        # #                                                   Tagged Bibles
        # # ================================================================================================================

        # # Translators Amalgamated Hebrew OT
        # TAHOT(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # print("Completed: TAHOT - Translators Amalgamated Hebrew OT")

        # # Translators Amalgamated Greek NT
        # TAGNT(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # print("Completed: TAGNT - Translators Amalgamated Greek NT")

        # # Tyndale Translation tags for ESV
        # TTESV(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # print("Completed: TTESV - Tyndale Translation tags for ESV")

        # # ================================================================================================================
        # #                                                   Entities
        # # ================================================================================================================
        
        # # Translators Individualised Proper Names with all References
        # TIPNR(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # print("Completed: TIPNR - Translators Individualised Proper Names with all References")

        # # ================================================================================================================
        # #                                                   Versification
        # # ================================================================================================================
        
        # # Translators Versification Traditions with Methodology 
        # #       for Standardisation for Eng+Heb+Lat+Grk+Others
        # TVTMS(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # print("Completed: TVTMS - Translators Versification Traditions with Methodology for Standardisation for Eng+Heb+Lat+Grk+Others")

if __name__ == "__main__":
    manager = ManagerHandler()

    ingestor = STEPBibleIngestor(manager)