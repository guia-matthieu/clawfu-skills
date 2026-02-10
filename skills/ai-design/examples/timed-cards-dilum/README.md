# Timed Cards Opening - Dilum Sanjaya

> Effet de cartes destinations tourisme avec auto-advance et transitions GSAP

## Source

| | |
|---|---|
| **CodePen** | https://codepen.io/dilums/pen/NWodZMd |
| **Auteur** | [Dilum Sanjaya](https://x.com/DilumSanjaya) |
| **Licence** | MIT (CodePen default) |

## Stack

- **HTML/CSS/JS** (vanilla)
- **GSAP** - Animations et transitions
- **Fonts** - Inter + Oswald (Google Fonts)
- **Couleurs** - Dark `#1a1a1a` + Gold accent `#ecad29`

## Effet

1. Cartes miniatures alignées en bas à droite
2. Auto-advance toutes les ~3 secondes avec indicateur de progression
3. Carte active s'étend en fullscreen avec animation fluide
4. Texte animé avec slide-up reveal (titre, description, CTA)
5. Navigation manuelle possible (flèches gauche/droite)

## Destinations (6)

| # | Lieu | Titre |
|---|------|-------|
| 1 | Switzerland Alps | Saint Antönien |
| 2 | Japan Alps | Nagano Prefecture |
| 3 | Sahara Desert - Morocco | Marrakech → Merzouga |
| 4 | Sierra Nevada - USA | Yosemite National Park |
| 5 | Tarifa - Spain | Los Lances Beach |
| 6 | Cappadocia - Turkey | Göreme Valley |

## Images

Les images sont hébergées sur le CDN CodePen :
```
https://assets.codepen.io/3685267/timed-cards-1.jpg
https://assets.codepen.io/3685267/timed-cards-2.jpg
https://assets.codepen.io/3685267/timed-cards-3.jpg
https://assets.codepen.io/3685267/timed-cards-4.jpg
https://assets.codepen.io/3685267/timed-cards-5.jpg
https://assets.codepen.io/3685267/timed-cards-6.jpg
```

## Fichiers

- `index.html` - Structure HTML
- `style.scss` - Styles SCSS (compiler en CSS)
- `script.js` - Logique GSAP

## Utilisation

1. Compiler le SCSS en CSS
2. Inclure GSAP : `<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>`
3. Ouvrir `index.html`

## Adaptation

Pour adapter les destinations, modifier le tableau `data` dans `script.js` :

```javascript
const data = [
    {
        place: 'Switzerland Alps',
        title: 'SAINT',
        title2: 'ANTONIEN',
        description: 'Description...',
        image: 'https://...'
    },
    // ...
]
```

---

*Sauvegardé le 2026-02-03*
*Référence pour skill `ai-ui-generation`*
