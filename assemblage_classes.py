"""Verschillende classes en functies om de structuur van de assemblage module te definiëren.

Een seriesysteem bestaat uit meerdere elementen. Elk element draagt bij aan de faalkans van het seriesysteem.

De `class` KansElement bevat de volgende attributen:
- pof: De faalkans van het element per jaar.
- beta: De betrouwbaarheidindex van het element.

De `class` Element bevat de volgende attributen:
- `id`: Unieke identificatie van het element.
- `timestamp`: Tijdstip van creatie van het element.
- `M_van`: de locatie van het begin van het element [meters].
- `M_tot`: de locatie van het einde van het element [meters].
- `L`: De lengte van het element of dijkvak [meters].
- `a`: Deel van het vak waarvoor de opschaalfactor wordt berekend (0-1).
- `faalmechanisme`: Het initiële faalmechanisme van het element.
- `Pf_dsn`: De doorsnedekans van het element per jaar.
- `Pf_vak`: De opgeschaalde faalkans van het element per vak.
- `invloedsfactor_belasting`: Invloedsfactor van de belasting van het element.

De `class` Faalmechanisme bevat de volgende attributen:
- `id`: Unieke identificatie van het faalmechanisme.
- `naam`: Naam van het initiële faalmechanisme.
- `beschrijving`: Beschrijving van het faalmechanisme.
- `dL`: Equivalente onafhankelijke mechanismelengte [meters].
- `wijze van opschaling`: MAX of SUM

De `class` Systeemkans bevat de volgende attributen:
- `id`: Unieke identificatie van de systeemkans.
- list `elementen`: Lijst van elementen die bijdragen aan de systeemkans.
- `timestamp`: Tijdstip van creatie van de systeemkans.
- `naam`: Naam van de systeemkans. Dit kan de naam van het Faalmechanisme zijn.
- `M_van`: de locatie van het begin van het systeemkans [meters].
- `M_tot`: de locatie van het einde van het systeemkans [meters].
- `beschrijving`: Beschrijving van de systeemkans.
- `kans`: De kans dat het systeem faalt.

"""

from dataclasses import dataclass, field
from datetime import datetime
import math
from typing import Optional, List
import scipy.stats as stats  # importeer de scipy.stats module
import numpy as np



@dataclass
class KansElement:
    pof: Optional[float] = None  # Faalkans van het element per jaar
    beta: Optional[float] = None  # Betrouwbaarheidindex van het element

    def __post_init__(self):
        if self.pof is not None:
            if not (0.0 <= self.pof <= 1.0):
                raise ValueError("pof moet tussen 0.0 en 1.0 liggen.")

        if self.beta is not None:
            if not math.isfinite(self.beta):
                raise ValueError("beta moet een eindige waarde zijn.")
            if (-38.0 <= self.beta <= 38.0) is False:
                raise ValueError("beta moet tussen -38.0 en 38.0 liggen.")

        if self.pof is None and self.beta is not None:
            self.pof = float(stats.norm.cdf(-1.0 * self.beta))

        if self.beta is None and self.pof is not None:
            self.beta = -1.0 * float(stats.norm.ppf(self.pof))


@dataclass
class Faalmechanisme:
    id: int
    naam: str
    beschrijving: str
    dL: float  # Equivalente onafhankelijke mechanismelengte [meters]
    wijze_van_opschaling: List[str] = field(default_factory=lambda: ["MAX", "SUM"])


@dataclass
class Element:
    id: int
    M_van: float  # Locatie van het begin van het element [meters]
    M_tot: float  # Locatie van het einde van het element [meters]
    a: float  # Deel van het vak waarvoor de opschaalfactor wordt berekend (0-1)
    faalmechanisme: Faalmechanisme  # Initiële faalmechanisme
    Pf_dsn: KansElement  # Doorsnedekans van het element per jaar
    invloedsfactor_belasting: float = 0.5  # Invloedsfactor van de belasting
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def L(self) -> float:
        return abs(self.M_tot - self.M_van)
    
    @property
    def N_vak(self) -> float:
        from assemblage_functions import bepaal_N_vak
        return bepaal_N_vak(self.L, self.a, self.faalmechanisme.dL)
    
    @property
    def Pf_vak(self) -> KansElement:
        Pf_vak = self.N_vak * float(self.Pf_dsn.pof)
        return KansElement(pof=Pf_vak)

@dataclass
class Systeemkans:
    # id: int
    # naam: str  # Naam van de systeemkans. Dit kan de naam van het Faalmechanisme zijn.
    # M_van: float  # Locatie van het begin van het systeemkans [meters]
    # M_tot: float  # Locatie van het einde van het systeemkans [meters]
    # beschrijving: str
    # kans: float  # De kans dat het systeem faalt
    faalmechanisme: Faalmechanisme
    elementen: List["Element"] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def M_van(self) -> float:
        if not self.elementen:
            return 0.0
        return min(element.M_van for element in self.elementen)

    @property
    def M_tot(self) -> float:
        if not self.elementen:
            return 0.0
        return max(element.M_tot for element in self.elementen)
    
    @property
    def systeemkans(self) -> KansElement:
        from assemblage_functions import combin_seriesysteem
        pof_values = [element.Pf_vak.pof for element in self.elementen if element.Pf_vak.pof is not None]
        ondergrens, bovengrens = combin_seriesysteem(np.array(pof_values))
        if self.faalmechanisme.wijze_van_opschaling[0] == "MAX":
            Pf_systeem = ondergrens
        elif self.faalmechanisme.wijze_van_opschaling[0] == "SUM":
            Pf_systeem = bovengrens
        else:
            raise ValueError("Ongeldige wijze van opschaling.")
        return KansElement(pof=Pf_systeem)
