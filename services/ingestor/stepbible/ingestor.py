


from stepbible.TAHOT import TAHOT
from stepbible.TAGNT import TAGNT
from stepbible.TEBSG import TEBSG
from stepbible.TEBSH import TEBSH
from stepbible.TEGMC import TEGMC
from stepbible.TEHMC import TEHMC
from stepbible.TFLSJ import TFLSJ
from stepbible.TIPNR import TIPNR
from stepbible.TTESV import TTESV
from stepbible.TVTMS import TVTMS

from manager.managerhandler import ManagerHandler
from database.boundary.step_bible_boundary import StepBibleReadBoundary, StepBibleWriteBoundary, StepBibleDeleteBoundary

class STEPBibleIngestor:
    def __init__(self, manager: ManagerHandler | None = None):
        self.manager        = manager or ManagerHandler()
        self.log            = self.manager.create_log_in_folder(["logs", "ingestor", "stepbible"])
        self.db             = self.manager.get_db()

        self.write = StepBibleWriteBoundary(self.db)
        self.read  = StepBibleReadBoundary(self.db)

    def ingest(self):
        # Translators Amalgamated Hebrew OT
        TAHOT(
            manager     = self.manager,
            log         = self.log
        )
        # Translators Amalgamated Greek NT
        TAGNT(
            manager     = self.manager,
            log         = self.log
        )
        # Translators Brief lexicon of Extended Strongs for Greek
        TEBSG(
            manager     = self.manager,
            log         = self.log
        )
        # Translators Brief lexicon of Extended Strongs for Hebrew
        TEBSH(
            manager     = self.manager,
            log         = self.log
        )
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
        # Translators Formatted full LSJ Bible lexicon
        TFLSJ(
            manager     = self.manager,
            log         = self.log
        )
        # Translators Individualised Proper Names with all References
        TIPNR(
            manager     = self.manager,
            log         = self.log
        )
        # Tyndale Translation tags for ESV
        TTESV(
            manager     = self.manager,
            log         = self.log
        )
        # Translators Versification Traditions with Methodology 
        #       for Standardisation for Eng+Heb+Lat+Grk+Others
        TVTMS(
            manager     = self.manager,
            log         = self.log
        )
