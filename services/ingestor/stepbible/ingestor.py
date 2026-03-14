


from services.ingestor.stepbible.tagged.TAHOT import TAHOT
from services.ingestor.stepbible.tagged.TAGNT import TAGNT
from services.ingestor.stepbible.tagged.TTESV import TTESV

from services.ingestor.stepbible.lexicon.TEBSG import TEBSG
from services.ingestor.stepbible.lexicon.TEBSH import TEBSH
from services.ingestor.stepbible.lexicon.TFLSJ import TFLSJ

from services.ingestor.stepbible.morphology.TEGMC import TEGMC
from services.ingestor.stepbible.morphology.TEHMC import TEHMC

from services.ingestor.stepbible.other.TIPNR import TIPNR
from services.ingestor.stepbible.other.TVTMS import TVTMS

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

    def ingest(self):
        # ================================================================================================================
        #                                                   Morphology Codes
        # ================================================================================================================

        # Translators Expansion of Greek Morphhology Codes
        TEGMC(
            manager     = self.manager,
            log         = self.log
        )
        # Translators Expansion of Hebrew Morphology Codes
        TEHMC(
            manager     = self.manager,
            log         = self.log
        )

        # # ================================================================================================================
        # #                                                   Lexicons
        # # ================================================================================================================

        # # Translators Brief lexicon of Extended Strongs for Greek
        # TEBSG(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # # Translators Brief lexicon of Extended Strongs for Hebrew
        # TEBSH(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # # Translators Formatted full LSJ Bible lexicon
        # TFLSJ(
        #     manager     = self.manager,
        #     log         = self.log
        # )

        # # ================================================================================================================
        # #                                                   Tagged Bibles
        # # ================================================================================================================

        # # Translators Amalgamated Hebrew OT
        # TAHOT(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # # Translators Amalgamated Greek NT
        # TAGNT(
        #     manager     = self.manager,
        #     log         = self.log
        # )
        # # Tyndale Translation tags for ESV
        # TTESV(
        #     manager     = self.manager,
        #     log         = self.log
        # )

        # # ================================================================================================================
        # #                                                   Entities
        # # ================================================================================================================
        
        # # Translators Individualised Proper Names with all References
        # TIPNR(
        #     manager     = self.manager,
        #     log         = self.log
        # )

        # # ================================================================================================================
        # #                                                   Versification
        # # ================================================================================================================
        
        # # Translators Versification Traditions with Methodology 
        # #       for Standardisation for Eng+Heb+Lat+Grk+Others
        # TVTMS(
        #     manager     = self.manager,
        #     log         = self.log
        # )

if __name__ == "__main__":
    manager = ManagerHandler()

    ingestor = STEPBibleIngestor(manager)