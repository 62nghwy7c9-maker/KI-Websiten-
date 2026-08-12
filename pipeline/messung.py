"""Stufe 1 — misst eine Website gegen den Prüfkatalog.

Liefert Rohfakten, keine Bewertung. Ob aus einem Messwert ein Befund wird,
entscheidet Stufe 2 (Konzept, Abschnitt 3).

Grundregeln:
- Nie raten. Was nicht sicher messbar ist, bekommt ok=None und einen Hinweis.
- Nichts auslösen. Formulare werden erkannt, aber niemals abgeschickt.
- Nur Standardbibliothek, damit es auf jedem Rechner ohne Installation läuft.
"""
from __future__ import annotations

import re
import socket
import ssl
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib import request
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit

from . import katalog as K
from .modelle import Kandidat, Messwert, Pruefbericht

KOPFZEILEN = {
    "User-Agent": "WebsiteCheck/1.0 (+kostenloser Website-Check; Kontakt siehe Anschreiben)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "de-DE,de;q=0.9",
}


# ── HTML-Auswertung ──────────────────────────────────────────────────────────

class _Seite(HTMLParser):
    """Zieht aus einer HTML-Seite genau das, was der Prüfkatalog braucht."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.titel: str | None = None
        self.beschreibung: str | None = None
        self.viewport: str | None = None
        self.links: list[tuple[str, str]] = []   # (href, linktext)
        self.formulare = 0
        self.text_teile: list[str] = []
        self._in_titel = False
        self._in_link: str | None = None
        self._link_text: list[str] = []
        self._ueberspringen = 0

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title" and self.titel is None:
            # Nur das erste title-Element. Manche Baukästen setzen ein zweites,
            # etwa in eingebettetem SVG — dessen Text gehört nicht in den Titel.
            self._in_titel = True
        elif tag in ("script", "style", "noscript"):
            self._ueberspringen += 1
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name == "description" and self.beschreibung is None:
                self.beschreibung = a.get("content", "").strip()
            elif name == "viewport" and self.viewport is None:
                self.viewport = a.get("content", "").strip()
        elif tag == "form":
            self.formulare += 1
        elif tag == "a" and "href" in a:
            self._in_link = a["href"].strip()
            self._link_text = []

    def handle_endtag(self, tag):
        if tag == "title":
            if self._in_titel:
                self.titel = (self.titel or "").strip()
            self._in_titel = False
        elif tag in ("script", "style", "noscript"):
            self._ueberspringen = max(0, self._ueberspringen - 1)
        elif tag == "a" and self._in_link is not None:
            self.links.append((self._in_link, " ".join(self._link_text).strip()))
            self._in_link, self._link_text = None, []

    def handle_data(self, data):
        if self._in_titel:
            self.titel = ((self.titel or "") + data).strip()
            return
        if self._ueberspringen:
            return
        if data.strip():
            self.text_teile.append(data.strip())
        if self._in_link is not None:
            self._link_text.append(data.strip())

    @property
    def sichtbarer_text(self) -> str:
        return " ".join(self.text_teile)


class Abruf:
    """Ergebnis eines HTTP-Abrufs. Wirft nie — Fehler landen in `fehler`."""

    def __init__(self, url: str) -> None:
        self.angefragt = url
        self.endgueltige_url = ""
        self.status = 0
        self.html = ""
        self.dauer_ms = 0
        self.fehler = ""

    @property
    def erreichbar(self) -> bool:
        return 200 <= self.status < 400 and not self.fehler


def hole(url: str, timeout: int = K.TIMEOUT_SEKUNDEN) -> Abruf:
    """Ruft eine URL ab und folgt Weiterleitungen."""
    a = Abruf(url)
    start = time.monotonic()
    try:
        with request.urlopen(request.Request(url, headers=KOPFZEILEN),
                             timeout=timeout) as r:
            a.status = r.status
            a.endgueltige_url = r.geturl()
            roh = r.read(3_000_000)
            zeichensatz = r.headers.get_content_charset() or "utf-8"
            a.html = roh.decode(zeichensatz, errors="replace")
    except HTTPError as e:
        a.status = e.code
        a.endgueltige_url = e.url or url
        try:
            a.html = e.read(1_000_000).decode("utf-8", errors="replace")
        except Exception:
            pass
    except (URLError, socket.timeout, ssl.SSLError, OSError) as e:
        a.fehler = f"{type(e).__name__}: {e}"
    except Exception as e:  # defekte Seiten sollen die Pipeline nicht anhalten
        a.fehler = f"{type(e).__name__}: {e}"
    a.dauer_ms = int((time.monotonic() - start) * 1000)
    return a


def zertifikat_restlaufzeit(host: str, timeout: int = 10) -> tuple[int | None, str]:
    """Tage bis zum Ablauf des TLS-Zertifikats. (None, Grund) wenn nicht prüfbar.

    Läuft absichtlich direkt gegen Port 443 und nicht über den HTTP-Abruf: Ein
    Proxy dazwischen würde sein eigenes Zertifikat zeigen, nicht das des Betriebs.
    """
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=timeout) as s:
            with ctx.wrap_socket(s, server_hostname=host) as ts:
                cert = ts.getpeercert()
        bis = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        bis = bis.replace(tzinfo=timezone.utc)
        return (bis - datetime.now(timezone.utc)).days, ""
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


# ── Einzelne Prüfpunkte ──────────────────────────────────────────────────────

def _telefonnummer_sichtbar(text: str) -> str | None:
    """Findet eine deutsche Telefonnummer im sichtbaren Text."""
    m = re.search(r"(?:\+49|0)[\s/().-]*\d(?:[\s/().-]*\d){6,13}", text)
    if not m:
        return None
    kandidat = m.group(0)
    return kandidat.strip() if sum(c.isdigit() for c in kandidat) >= 7 else None


MAIL_MUSTER = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")


def _mailadressen(seite: "_Seite") -> set[str]:
    """Alle E-Mail-Adressen einer Seite, aus Text und mailto:-Links."""
    gefunden = {a.lower() for a in MAIL_MUSTER.findall(seite.sichtbarer_text)}
    for href, _ in seite.links:
        if href.lower().startswith("mailto:"):
            adresse = href[7:].split("?")[0].strip().lower()
            if MAIL_MUSTER.fullmatch(adresse):
                gefunden.add(adresse)
    return {a for a in gefunden if not a.endswith((".png", ".jpg", ".webp", ".gif"))}


def _nur_ziffern(nummer: str) -> str:
    return re.sub(r"\D", "", nummer or "")


def _verwechselbare_mails(mails: set[str]) -> list[tuple[str, str]]:
    """Adressenpaare, die sich nur in Satzzeichen unterscheiden.

    `info@` und `jobs@` sind zwei Postfächer, kein Fehler. `gophai-thai@web.de`
    und `gophaithai@web.de` sind derselbe gemeinte Empfänger in zwei Schreibweisen
    — eine davon geht ins Leere. Genau dieser Fall stand im Gophai-Check, und die
    naive Regel „mehr als eine Adresse" hätte ihn nicht von einem normalen
    zweiten Postfach unterscheiden können.
    """
    gruppen: dict[str, set[str]] = {}
    for adresse in mails:
        lokal, _, domain = adresse.partition("@")
        schluessel = re.sub(r"[^a-z0-9]", "", lokal) + "@" + domain
        gruppen.setdefault(schluessel, set()).add(adresse)
    return [tuple(sorted(g)[:2]) for g in gruppen.values() if len(g) > 1]


def _ist_baukasten(host: str) -> str | None:
    h = host.lower()
    for muster in K.BAUKASTEN_HOSTS:
        if h == muster.strip(".") or h.endswith("." + muster.strip(".")) or muster in h:
            return muster
    return None


ALLERWELTSWOERTER = {
    "gmbh", "kg", "ohg", "ug", "co", "und", "der", "die", "das", "fuer", "für",
    "inh", "e", "k", "gbr", "ag", "betrieb", "firma", "service", "gruppe",
}


def _titel_nennt_betrieb(titel: str, firma: str) -> bool:
    """Steht der Betriebsname im Seitentitel?

    Verglichen wird über die kennzeichnenden Wortstämme des Firmennamens.
    Rechtsformen und Allerweltswörter zählen nicht mit — „GmbH" im Titel ist
    kein Betriebsname. Sind gar keine kennzeichnenden Wörter übrig, gilt der
    Titel als in Ordnung; dann ist die Frage nicht entscheidbar und der
    Prüfkatalog rät nicht.
    """
    t = titel.lower()
    woerter = [w for w in re.split(r"[^\wäöüß]+", (firma or "").lower())
               if len(w) > 2 and w not in ALLERWELTSWOERTER]
    if not woerter:
        return True
    return any(w[:6] in t for w in woerter)


JAHRESZAHL = re.compile(r"\b(20[0-4]\d)\b")


def _juengstes_jahr(text: str, heute: int) -> int | None:
    """Die neueste Jahreszahl im sichtbaren Text — oder None, wenn keine da ist.

    Jahreszahlen in der Zukunft werden verworfen: Sie stammen regelmäßig aus
    Skripten oder Formularen und sagen nichts über die Pflege der Seite.

    Bewusst die **größte** Zahl, nicht die im Fußzeilen-Copyright: Ein Betrieb,
    der „seit 1985" schreibt und daneben eine Referenz von 2024 stehen hat,
    pflegt seine Seite. Erst wenn gar nichts Neueres zu finden ist, ist die
    Seite alt.
    """
    jahre = [int(j) for j in JAHRESZAHL.findall(text or "") if int(j) <= heute]
    return max(jahre) if jahre else None


def _finde_link(seite: _Seite, woerter: tuple[str, ...]) -> tuple[str, str] | None:
    """Sucht einen Link, dessen Text oder Pfad mit einem der Wörter beginnt.

    Der Wortanfang ist entscheidend, nicht das Vorkommen irgendwo. „stellen"
    steckt sonst in Bau*stellen*, Aus*stellung*, be*stellen* und her*stellen* —
    und dann hat jeder Bau- und Elektrobetrieb scheinbar eine Karriereseite.
    Genau dieser Fehler hat bei Elektrotechnik Merzenich einen echten Befund
    verschluckt.

    Nur der Wortanfang wird verankert, nicht das Wortende: „stellen" soll
    „Stellenangebote" weiterhin finden.
    """
    for href, text in seite.links:
        haystack = f"{href} {text}".lower()
        for w in woerter:
            if re.search(r"\b" + re.escape(w), haystack):
                return href, text
    return None


PLATZHALTER_REGEX = (
    (r"\?{2,}", "Fragezeichen als Lückenfüller"),
    (r"\[[^\]\n]{2,40}\]", "eckige Klammer im Fließtext"),
    (r"\((?:bild|foto|logo|grafik|text|hier)\b[^)\n]{3,60}\)",
     "Regieanweisung in Klammern"),
    (r"\b(?:tbd|todo|xxx+)\b", "Bearbeitungsvermerk"),
    (r"\bhier (?:steht|kommt|folgt)\b", "unausgefüllte Vorlage"),
    (r"\bxx+\s*(?:jahre|jahren|mitarbeiter|kunden)\b", "Zahl nicht eingesetzt"),
)
"""Strukturelle Platzhalter — unabhängig vom Wortlaut.

Feste Phrasen wie „Lorem ipsum" fangen nur, was die Vorlage mitgeliefert hat.
Was Betriebe tatsächlich stehen lassen, sieht anders aus: „mehr als ?? Jahren
Erfahrung", „[bitte eintragen]", „(Bild in Beratungssituation)". Solche Funde
wirken auf einem Check besonders stark, weil der Inhaber sie sofort erkennt.
"""


def _platzhalter_funde(text: str, muster: tuple[str, ...]) -> list[str]:
    """Findet Platzhalter im sichtbaren Text, wörtlich zitiert.

    Zitiert wird der Treffer, nicht die Regel — nur so lässt sich die Aussage
    auf dem Check belegen, ohne die Seite erneut zu öffnen.
    """
    klein = text.lower()
    funde = [w for w in muster if w in klein]
    for regel, benennung in PLATZHALTER_REGEX:
        for treffer in re.findall(regel, text, re.I):
            fund = f"„{treffer.strip()}“ ({benennung})"
            if fund not in funde:
                funde.append(fund)
    return funde[:6]


# ── Stufe 1 ──────────────────────────────────────────────────────────────────

def messen(kandidat: Kandidat, lcp_ms: int | None = None) -> Pruefbericht:
    """Misst alle automatischen Prüfpunkte gegen die Website des Kandidaten.

    `lcp_ms` kommt aus der PageSpeed-Insights-API und wird von außen übergeben,
    damit die Messung ohne Netzzugang zu Google testbar bleibt.
    """
    bericht = Pruefbericht(kandidat=kandidat)
    erlaubt = {p.nr for p in K.fuer_branche(kandidat.branche)}

    def m(mw: Messwert) -> None:
        """Nimmt einen Messwert auf — Branchenpunkte nur in ihrer Branche.

        Ohne diesen Filter würde einem Imbiss die fehlende Karriereseite als
        Befund angerechnet. Der Prüfpunkt gilt laut Katalog nur für Handwerk.
        """
        if mw.id in erlaubt:
            bericht.messung.append(mw)
    url = kandidat.url.strip()
    if "//" not in url:
        url = "https://" + url
    host = urlsplit(url).hostname or ""

    # 1 Erreichbarkeit
    abruf = hole(url)
    if abruf.fehler:
        m(Messwert(1, "Erreichbarkeit", f"nicht erreichbar ({abruf.fehler})",
                   "HTTP", ok=False, roh={"url": url, "fehler": abruf.fehler}))
        bericht.hinweise.append(
            "Seite nicht abrufbar — alle weiteren Prüfpunkte konnten nicht gemessen "
            "werden. Vor dem Check von Hand nachsehen, ob die Adresse stimmt.")
        return bericht
    m(Messwert(1, "Erreichbarkeit",
               f"HTTP {abruf.status} nach {abruf.dauer_ms} ms",
               "HTTP", ok=abruf.erreichbar,
               roh={"status": abruf.status, "endgueltige_url": abruf.endgueltige_url,
                    "dauer_ms": abruf.dauer_ms}))
    if not abruf.erreichbar:
        bericht.hinweise.append(
            f"HTTP {abruf.status} — weitere Prüfpunkte auf dieser Antwort sind "
            "wenig aussagekräftig.")

    seite = _Seite()
    try:
        seite.feed(abruf.html)
    except Exception as e:
        bericht.hinweise.append(f"HTML nicht vollständig lesbar: {type(e).__name__}")
    text_klein = seite.sichtbarer_text.lower()
    end_host = urlsplit(abruf.endgueltige_url or url).hostname or host

    # 2 HTTPS
    ist_https = (abruf.endgueltige_url or url).startswith("https://")
    tage, tls_fehler = zertifikat_restlaufzeit(end_host) if ist_https else (None, "kein HTTPS")
    http_abruf = hole("http://" + end_host, timeout=10)
    leitet_um = (http_abruf.endgueltige_url or "").startswith("https://")
    if not ist_https:
        wert, ok = "kein HTTPS", False
    elif tage is None:
        wert, ok = f"HTTPS vorhanden, Zertifikat nicht prüfbar ({tls_fehler})", None
        bericht.hinweise.append(
            "TLS-Zertifikat nicht direkt prüfbar (oft ein Proxy dazwischen). "
            "Vor dem Check im Browser ansehen.")
    elif tage < 0:
        wert, ok = f"Zertifikat seit {abs(tage)} Tagen abgelaufen", False
    elif not leitet_um and not http_abruf.fehler:
        wert, ok = "HTTPS vorhanden, aber http leitet nicht weiter", False
    else:
        wert, ok = f"gültig, läuft in {tage} Tagen ab", True
    m(Messwert(2, "HTTPS", wert, "TLS", ok=ok,
               roh={"https": ist_https, "zertifikat_tage": tage,
                    "http_leitet_um": leitet_um}))

    # 3 Mobiltauglichkeit — nur die viewport-Angabe ist ohne Browser messbar
    if seite.viewport is None:
        m(Messwert(3, "Mobiltauglichkeit", "keine viewport-Angabe im Quelltext",
                   "HTML", ok=False))
    else:
        m(Messwert(3, "Mobiltauglichkeit", f"viewport: {seite.viewport}",
                   "HTML", ok=True, roh={"viewport": seite.viewport}))
        bericht.hinweise.append(
            f"viewport ist gesetzt. Ob die Seite bei {K.MOBIL_BREITE_PX} px "
            "horizontal scrollt, ist ohne Browser nicht messbar — am Handy ansehen.")

    # 4 Ladezeit
    if lcp_ms is None:
        m(Messwert(4, "Ladezeit mobil", "nicht gemessen", "PageSpeed Insights",
                   auto=True, ok=None))
        bericht.hinweise.append(
            "LCP nicht gemessen. Mit --psi-key <Schlüssel> nachholen oder unter "
            "pagespeed.web.dev von Hand prüfen.")
    else:
        ok = lcp_ms <= K.LCP_SCHLECHT_MS
        m(Messwert(4, "Ladezeit mobil", f"LCP {lcp_ms / 1000:.1f} s",
                   "PageSpeed Insights", ok=ok, roh={"lcp_ms": lcp_ms}))

    # 5 Klickbare Telefonnummer
    tel_links = [h for h, _ in seite.links if h.lower().startswith("tel:")]
    nummer = _telefonnummer_sichtbar(seite.sichtbarer_text)
    if tel_links:
        m(Messwert(5, "Klickbare Telefonnummer", f"{len(tel_links)} tel:-Link(s)",
                   "HTML", ok=True, roh={"tel": tel_links[:3]}))
    elif nummer:
        m(Messwert(5, "Klickbare Telefonnummer",
                   f"Nummer sichtbar ({nummer}), aber kein tel:-Link",
                   "HTML", ok=False, roh={"nummer": nummer}))
    elif kandidat.telefon:
        # Die Nummer steht in der Lead-Liste, auf der Seite aber weder als Text
        # noch als Link. Bei Flash- oder Bildkopfzeilen ist der sichtbare Text
        # leer — der Befund gilt trotzdem, denn antippbar ist nichts.
        m(Messwert(5, "Klickbare Telefonnummer",
                   f"kein tel:-Link; Nummer laut Verzeichnis {kandidat.telefon}",
                   "HTML", ok=False, roh={"quelle_nummer": "Lead-Liste"}))
    else:
        m(Messwert(5, "Klickbare Telefonnummer",
                   "keine Telefonnummer auf der Startseite gefunden", "HTML", ok=None))

    # 6 Kontaktweg / 10 Formular
    mailto = [h for h, _ in seite.links if h.lower().startswith("mailto:")]
    wege = []
    if seite.formulare:
        wege.append(f"{seite.formulare} Formular(e)")
    if mailto:
        wege.append(f"{len(mailto)} mailto:-Link(s)")
    if tel_links:
        wege.append(f"{len(tel_links)} tel:-Link(s)")
    m(Messwert(6, "Kontaktweg", ", ".join(wege) if wege else "kein Kontaktweg gefunden",
               "HTML", ok=bool(wege),
               roh={"formulare": seite.formulare, "mailto": mailto[:3]}))
    # Punkt 10 fragt nach einem Formular, nicht nach irgendeinem Kontaktweg —
    # das ist Punkt 6. Vorher galt eine mailto-Adresse als Formular, dadurch
    # blieb bei Sander-Bau ein echter Befund unentdeckt.
    m(Messwert(10, "Formular",
               f"{seite.formulare} Formular(e) im Quelltext — nicht abgeschickt"
               if seite.formulare else "kein Formular auf der Startseite",
               "HTML", ok=bool(seite.formulare),
               roh={"formulare": seite.formulare, "mailto": mailto[:3]}))

    impressum_text = ""
    platzhalter_funde = _platzhalter_funde(
        seite.sichtbarer_text, K.PLATZHALTER_MUSTER)
    # 7 Impressum
    treffer = _finde_link(seite, K.IMPRESSUM_WOERTER)
    if not treffer:
        m(Messwert(7, "Impressum", "kein Link auf ein Impressum gefunden",
                   "HTML", ok=False))
    else:
        imp_url = urljoin(abruf.endgueltige_url or url, treffer[0])
        # Viele Baukästen legen das Impressum als Abschnitt derselben Seite an
        # (href="#imprint"). Dann darf nicht neu geladen werden — sonst wird die
        # Startseite ein zweites Mal geholt und mit sich selbst verglichen.
        gleiche_seite = treffer[0].lstrip().startswith("#")
        imp = abruf if gleiche_seite else hole(imp_url, timeout=12)
        if gleiche_seite:
            bericht.hinweise.append(
                "Das Impressum ist ein Abschnitt der Startseite, keine eigene Seite. "
                "Ob alle Pflichtangaben dort stehen, von Hand prüfen.")
        if not imp.erreichbar:
            m(Messwert(7, "Impressum", f"Impressumsseite nicht abrufbar ({imp.status})",
                       "HTTP", ok=False, roh={"url": imp_url}))
        else:
            if gleiche_seite:
                ip = seite
            else:
                ip = _Seite()
                try:
                    ip.feed(imp.html)
                    impressum_text = ip.sichtbarer_text
                except Exception:
                    pass
            itext = ip.sichtbarer_text
            hat_plz = bool(re.search(r"\b\d{5}\b", itext))
            imp_mails = _mailadressen(ip)
            imp_tel = _telefonnummer_sichtbar(itext) or next(
                (h[4:] for h, _ in ip.links if h.lower().startswith("tel:")), None)
            fehlt = [n for n, da in (("Anschrift (PLZ)", hat_plz),
                                     ("Telefon", bool(imp_tel)),
                                     ("E-Mail", bool(imp_mails))) if not da]

            # Querabgleich mit der Startseite. Widersprüchliche Kontaktdaten sind
            # ein eigener, gut belegbarer Mangel — bei Gophai waren es zwei
            # verschiedene Mailadressen (gophai-thai@ vs. gophaithai@).
            start_mails = _mailadressen(seite)
            start_tel = next((h[4:] for h, _ in seite.links
                              if h.lower().startswith("tel:")), None) or nummer
            abweichung = []
            for a, b in _verwechselbare_mails(start_mails | imp_mails):
                abweichung.append(f"zwei Schreibweisen derselben Adresse: {a} und {b}")
            if start_mails and imp_mails and not (start_mails & imp_mails):
                abweichung.append(
                    f"E-Mail Startseite {sorted(start_mails)[0]} ≠ "
                    f"Impressum {sorted(imp_mails)[0]}")
            if start_tel and imp_tel and _nur_ziffern(start_tel)[-8:] and \
                    _nur_ziffern(start_tel)[-8:] != _nur_ziffern(imp_tel)[-8:]:
                abweichung.append(
                    f"Telefon Startseite {start_tel.strip()} ≠ Impressum {imp_tel.strip()}")

            if fehlt:
                wert, ok = "vorhanden, es fehlt: " + ", ".join(fehlt), False
            elif abweichung:
                wert, ok = "widersprüchliche Angaben — " + "; ".join(abweichung), False
            else:
                wert, ok = "vorhanden, vollständig genug", True
            # Firmenname und Rechtsform sind automatisch nicht sicher erkennbar.
            m(Messwert(7, "Impressum", wert, "HTML", ok=ok,
                       roh={"url": imp_url, "fehlt": fehlt,
                            "abweichung": abweichung,
                            "mails_startseite": sorted(start_mails),
                            "mails_impressum": sorted(imp_mails)}))
            bericht.hinweise.append(
                "Impressum: Firmenname und Rechtsform sind automatisch nicht sicher "
                "prüfbar. Vor dem Check kurz selbst lesen.")

    # 8 Aktualität
    heute = datetime.now(timezone.utc).year
    jahr = _juengstes_jahr(seite.sichtbarer_text + " " + impressum_text, heute)
    if jahr is None:
        m(Messwert(8, "Aktualität", "keine Jahreszahl auf der Seite gefunden",
                   "HTML", ok=None))
        bericht.hinweise.append(
            "Aktualität nicht automatisch bestimmbar — auf der Seite steht keine "
            "Jahreszahl. Beim Draufsehen einschätzen.")
    elif heute - jahr >= K.ALT_AB_JAHREN:
        m(Messwert(8, "Aktualität", str(jahr), "HTML", ok=False,
                   roh={"juengstes_jahr": jahr, "abstand": heute - jahr}))
    else:
        m(Messwert(8, "Aktualität", f"jüngste Spur aus {jahr}", "HTML", ok=True,
                   roh={"juengstes_jahr": jahr}))

    # 15 auch auf dem Impressum: Dort stehen die peinlichsten Platzhalter, weil
    # die Seite selten gelesen wird — etwa „[bitte eintragen]" als Anschrift.
    if impressum_text:
        for fund in _platzhalter_funde(impressum_text, K.PLATZHALTER_MUSTER):
            if fund not in platzhalter_funde:
                platzhalter_funde.append(fund)

    # 9 Karriereseite / 22 Bewerbungsweg
    karriere = _finde_link(seite, K.KARRIERE_WOERTER)
    m(Messwert(9, "Karriereseite",
               f"Link gefunden: {karriere[1] or karriere[0]}" if karriere
               else "kein Link auf Karriere, Jobs oder Stellen",
               "HTML", ok=bool(karriere),
               roh={"href": karriere[0] if karriere else ""}))
    if karriere:
        k_url = urljoin(abruf.endgueltige_url or url, karriere[0])
        kabruf = hole(k_url, timeout=12)
        if kabruf.erreichbar:
            kp = _Seite()
            try:
                kp.feed(kabruf.html)
            except Exception:
                pass
            weg = bool(kp.formulare) or any(
                h.lower().startswith("mailto:") for h, _ in kp.links)
            m(Messwert(22, "Bewerbungsweg",
                       "Formular oder Mailadresse vorhanden" if weg
                       else "weder Formular noch Mailadresse auf der Karriereseite",
                       "HTML", ok=weg, roh={"url": k_url}))

    # 11 Seitentitel
    titel = (seite.titel or "").strip()
    if not titel:
        m(Messwert(11, "Seitentitel", "kein Titel im Quelltext", "HTML", ok=False))
    elif titel.lower().strip(" .-–—|") in K.TITEL_VORLAGENWERTE:
        m(Messwert(11, "Seitentitel", f"Vorlagenwert: „{titel}“", "HTML", ok=False,
                   roh={"titel": titel}))
    elif not _titel_nennt_betrieb(titel, kandidat.firma):
        # „Über uns" oder „Home" als Titel der Startseite: In der Google-Trefferliste
        # steht dann genau das als Überschrift, nicht der Betriebsname.
        m(Messwert(11, "Seitentitel",
                   f"„{titel}“ — ohne Betriebsnamen", "HTML", ok=False,
                   roh={"titel": titel, "firma": kandidat.firma}))
    else:
        m(Messwert(11, "Seitentitel", f"„{titel}“", "HTML", ok=True,
                   roh={"titel": titel}))

    # 12 Meta-Description
    besch = (seite.beschreibung or "").strip()
    if not besch:
        m(Messwert(12, "Meta-Description", "fehlt", "HTML", ok=False))
    elif len(besch) < K.BESCHREIBUNG_MIN_ZEICHEN:
        m(Messwert(12, "Meta-Description", f"nur {len(besch)} Zeichen", "HTML",
                   ok=False, roh={"text": besch}))
    else:
        m(Messwert(12, "Meta-Description", f"{len(besch)} Zeichen", "HTML", ok=True,
                   roh={"text": besch}))

    # 13 Eigene Domain
    baukasten = _ist_baukasten(end_host)
    m(Messwert(13, "Eigene Domain",
               f"Baukasten-Adresse ({baukasten})" if baukasten else f"eigene Domain ({end_host})",
               "HTTP", ok=not baukasten, roh={"host": end_host, "muster": baukasten or ""}))

    # 15 Platzhalter- und Fremdtext — Heuristik, entscheidet nie allein.
    # ok bleibt bei None statt True: Die Suche deckt bekannte Platzhalterphrasen ab,
    # aber keinen fremdsprachigen Vorlagentext. Genau der war bei Gophai der stärkste
    # Befund („Le nostre specialità" auf einer deutschen Thai-Seite) und ist
    # automatisch nicht erkennbar. „Kein Treffer" hieße sonst fälschlich „geprüft".
    funde = platzhalter_funde
    m(Messwert(15, "Platzhalter- und Fremdtext",
               "Verdacht: " + ", ".join(funde) if funde
               else "keine bekannte Platzhalterphrase — Sichtprüfung offen",
               "HTML", auto=False, ok=False if funde else None,
               roh={"treffer": funde}))
    bericht.hinweise.append(
        "Seite überfliegen: fremdsprachige Überschriften, Vorlagentexte, „Le nostre "
        "specialità“-Fälle. Die Suche findet nur bekannte Platzhalterphrasen.")

    # 20/21 Gastro
    if (kandidat.branche or "").lower() == "gastro":
        bestellwort = any(w in text_klein for w in
                          ("online bestellen", "jetzt bestellen", "warenkorb", "lieferando"))
        weg = bool(seite.formulare) or bestellwort
        m(Messwert(21, "Bestell- oder Anfrageweg",
                   "Bestell- oder Anfrageweg vorhanden" if weg
                   else "kein Formular und kein Online-Bestellweg gefunden",
                   "HTML", ok=weg))
        # Ob die Karte echter Text oder nur ein Bild ist, lässt sich nicht
        # zuverlässig automatisch entscheiden: Ein PDF-Link ist ein Indiz, ein
        # eingebettetes Bild sieht im Quelltext aus wie jedes andere Bild.
        karte = _finde_link(seite, ("speisekarte", "karte", "menü", "menu", "gerichte"))
        pdf = bool(karte and karte[0].lower().endswith(".pdf"))
        m(Messwert(20, "Speisekarte als Text",
                   "Karte als PDF verlinkt" if pdf
                   else "Sichtprüfung offen — ist die Karte echter Text oder ein Bild?",
                   "HTML", auto=False, ok=False if pdf else None,
                   roh={"link": karte[0] if karte else ""}))
        bericht.hinweise.append(
            "Speisekarte ansehen: echter Text, oder Foto/PDF? Wenn Bild oder PDF, "
            "kann Google keine Gerichte lesen — das ist ein starker Befund.")

    # 14 Google-Profil: bewusst manuell, kein offener API-Zugang für fremde Betriebe
    m(Messwert(14, "Google-Unternehmensprofil", "manuell zu prüfen",
               "manuell", auto=False, ok=None))
    bericht.hinweise.append(
        f"Google-Profil von Hand prüfen: „{kandidat.firma} {kandidat.ort}“ suchen und "
        "Adresse sowie Telefon mit der Website vergleichen.")

    return bericht


# ── PageSpeed Insights (optional) ────────────────────────────────────────────

def lcp_von_psi(url: str, api_key: str = "", timeout: int = 60) -> tuple[int | None, str]:
    """Holt den mobilen LCP-Wert. Ohne Schlüssel stark ratenbegrenzt."""
    import json
    from urllib.parse import urlencode
    ziel = ("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?"
            + urlencode({k: v for k, v in
                         (("url", url), ("strategy", "mobile"),
                          ("category", "performance"), ("key", api_key)) if v}))
    try:
        with request.urlopen(request.Request(ziel, headers=KOPFZEILEN),
                             timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8"))
        audit = d["lighthouseResult"]["audits"]["largest-contentful-paint"]
        return int(round(audit["numericValue"])), ""
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
