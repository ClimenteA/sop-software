from .sops import router as SopR
from .users import router as UserR
from .legal import router as LegalR

routers = [UserR, SopR, LegalR]
