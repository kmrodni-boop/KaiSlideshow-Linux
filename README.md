# KaiSlideshow-Linux

En lettvekts fullskjerm lysbildeviser for Linux, skrevet i Python med PySide6 (Qt6).
Systerapp til [KaiSlideshow-Android](https://github.com/kmrodni-boop/KaiSlideshow-Android),
med samme filosofi: gjor én ting bra – vis bildene dine som en lysbildefremvisning,
uten unodvendig kompleksitet.

## Funksjoner

- **Fullskjerm lysbildefremvisning** med konfigurerbart intervall (2–120 sek)
- **Tilfeldig eller alfabetisk** rekkefolge
- **Uttoning (fade)** mellom bilder, kan sla av/pa
- **Sovetimer** som avslutter fremvisningen etter valgt tid
- **Zoom og panorering** med musehjul/klikk-og-dra nar fremvisningen er pauset
- **EXIF-riktig rotasjon** – bilder fra mobil/kamera vises riktig vei
- **Bakgrunnsinnlasting** – store mapper skanner uten a fryse grensesnittet
- **Legg til flere bilder/mapper** underveis, uten a starte pa nytt
- **Nylige mapper** huskes mellom okter
- **Info-linje** med bildenummer og filnavn
- Robust mot ulesbare/korrupte filer – de hoppes automatisk over

### Tastatur og mus

| Handling | Effekt |
|---|---|
| `Mellomrom` | Pause / fortsett |
| `→` / `Enter` | Neste bilde |
| `←` | Forrige bilde |
| `Esc` | Avslutt |
| `F` / `F11` | Veksle fullskjerm |
| Musehjul (pause) | Zoom inn/ut |
| Klikk + dra (pause, zoomet) | Panorer |
| `+` / `-` / `0` (pause) | Zoom inn / ut / nullstill |
| Beveg musen | Vis kontrollpanel og markor |

Kontrollpanelet overst (vises nar du beveger musen) har intervall, tilfeldig,
uttoning, sovetimer, forrige/neste, "Legg til bilder", "Legg til mapper" og "Avslutt".

## Installasjon

```bash
git clone https://github.com/kmrodni-boop/KaiSlideshow-Linux.git
cd KaiSlideshow-Linux
bash install.sh
```

(Hvis skriptet er kjorbart hos deg kan du ogsa bruke `./install.sh` direkte;
kjor evt. `chmod +x install.sh uninstall.sh` forst.)

`install.sh` gjor folgende, kun for din brukerkonto (ingenting installeres
system-bredt, ingen filer utenfor `$HOME` rores):

1. Sjekker at `python3` og `venv`-modulen finnes. Mangler den, foreslas riktig
   pakke for din distro (apt/dnf/pacman/zypper) og du blir spurt for noe
   installeres.
2. Oppretter et isolert virtuelt miljo i `~/.local/share/kaislideshow/venv`
   og installerer `PySide6` og appen der – rorer ikke systemets Python.
3. Legger en `kaislideshow`-kommando i `~/.local/bin` (og tilbyr a legge
   denne til i `PATH` hvis den mangler).
4. Installerer `.desktop`-fil og ikon slik at KaiSlideshow dukker opp i
   programmenyen og i "Apne med"-menyen for bilder/mapper i alle
   XDG-kompatible filbehandlere (Nautilus/GNOME Files, Dolphin, Thunar,
   PCManFM, COSMIC Files, ...).
5. Installerer en **egen "Start KaiSlideshow"-handling for Nemo** som dukker
   rett opp nar du hoyreklikker en eller flere valgte bilder/mapper – ikke
   gjemt under "Apne med".
6. Installerer et hoyreklikk-skript for Nautilus (GNOME Files) under
   Scripts-undermenyen.

Kjor `bash install.sh -y` for a svare ja pa alle sporsmal automatisk (nyttig i
skript/CI).

Fjern alt igjen med:

```bash
bash uninstall.sh
```

## Hoyreklikk-integrasjon per filbehandler

| Filbehandler | Hvordan det vises |
|---|---|
| **Nemo** (Cinnamon/Linux Mint) | Egen linje **"Start KaiSlideshow"** direkte i hoyreklikk-menyen, for én eller flere valgte bilder/mapper |
| **Nautilus** (GNOME Files) | Hoyreklikk → **Scripts** → "Start KaiSlideshow" |
| **COSMIC Files** | Hoyreklikk → **Apne med** → KaiSlideshow. COSMIC Files stotter foreløpig ikke egendefinerte handlinger slik Nemo gjor ([pop-os/cosmic-files#1445](https://github.com/pop-os/cosmic-files/issues/1445) er apen); nar den funksjonen lander oppstrom kan et eget script legges til her pa samme mate som for Nautilus |
| Dolphin, Thunar, PCManFM, m.fl. | Hoyreklikk → **Apne med** → KaiSlideshow (via standard `.desktop`-registrering) |

I alle tilfeller kan du velge **flere bilder og/eller mapper samtidig** –
KaiSlideshow slar dem sammen til én fremvisning.

## Manuell bruk

```bash
kaislideshow                       # sporsmalsdialog for a velge mapper
kaislideshow ~/Bilder/Sommerferie  # start direkte med en mappe
kaislideshow bilde1.jpg bilde2.png ~/Bilder/Ferie  # blanding av filer og mapper
```

## Innstillinger

Lagres i `~/.config/kaislideshow/settings.json` (intervall, tilfeldig,
uttoning, sovetimer, nylige mapper). Migreres automatisk fra den gamle
`~/.slideshow_settings.json`-plasseringen brukt av prototypen, hvis den finnes.

## Prosjektstruktur

```
KaiSlideshow-Linux/
├── kaislideshow/
│   ├── __main__.py     # Inngangspunkt / argumenthandtering
│   ├── window.py        # Hovedvindu: fremvisning, UI, zoom/pan, uttoning
│   ├── loader.py         # Bakgrunnstrad som skanner mapper/filer
│   ├── settings.py       # Innstillinger (XDG-config, nylige mapper)
│   └── constants.py      # Delte konstanter
├── packaging/
│   ├── kaislideshow.desktop
│   ├── icons/kaislideshow.svg
│   ├── nemo-actions/kaislideshow.nemo_action
│   └── nautilus-scripts/Start KaiSlideshow
├── install.sh / uninstall.sh
├── pyproject.toml
└── requirements.txt
```

## Utvikling

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m kaislideshow
```

## Avhengigheter

- Python 3.9+
- [PySide6](https://pypi.org/project/PySide6/) (Qt6-bindinger)

## Lisens

MIT License – se [LICENSE](LICENSE).
