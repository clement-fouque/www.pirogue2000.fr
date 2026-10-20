# Bilan de migration depuis Jimdo

Source publique : <https://www.pirogue2000.fr/>, consultée le 20 octobre 2026. Périmètre issu de l’issue #1, confirmé avant développement : tous les contenus publics, leur navigation et leurs médias ; apparence proche, pas pixel-perfect ; édition Markdown dans GitHub ; Hugo et GitHub Pages sans dépendance d’exécution Jimdo.

Le dépôt de départ était vide. Aucun réglage Pages, enregistrement DNS, abonnement Jimdo ou paramètre de production n’a été modifié.

## Couverture des pages

Le parcours a commencé au sitemap XML, puis a suivi les liens internes du menu, du contenu, du pied de page et du plan du site. Les routes accentuées et leurs variantes encodées désignent les mêmes pages. Les liens d’administration, scripts Cloudflare, API et téléchargements ne sont pas des pages de contenu.

| Chemin source | Contenu local | Traitement |
|---|---|---|
| `/` | `content/_index.md` | Texte, objectifs, trois photos et légendes ; lien de la première photo conservé |
| `/actions/` | `content/actions/_index.md` | Présentation ; accès aux trois domaines d’action |
| `/actions/santé/` | `content/actions/santé.md` | Liste d’actions et huit photos |
| `/actions/education/` | `content/actions/education.md` | Liste d’actions et dix photos |
| `/actions/développement/` | `content/actions/développement.md` | Liste d’actions et huit photos |
| `/activités/` | `content/activités.md` | Textes, artistes et deux galeries de six et sept photos |
| `/partenaires/` | `content/partenaires.md` | Introduction et liste des dix partenaires |
| `/calendrier/` | `content/calendrier.md` | Calendrier 2026, six entrées et lien Facebook |
| `/contact/` | `content/contact.md` | Adhésion, coordonnées, email, logo et compte-rendu PDF ; formulaire remplacé |
| `/about/` | `content/about.md` | Promotion Jimdo retirée ; informations associatives connues et mentions restant à valider |
| `/sitemap/` | `content/sitemap.md` | Plan du site Markdown |
| `/j/privacy` | `content/j/privacy.md` | Notice statique de confidentialité à valider |
| `/j/legal-guarantee` | `content/j/legal-guarantee.md` | Notice statique signalant l’applicabilité à vérifier |
| `/j/withdrawal` | `content/j/withdrawal.md` | Notice statique et email ; aucun formulaire ni accusé de réception simulé |

Les dix chemins du sitemap source sont conservés, avec accents et barres finales. Les liens générés peuvent encoder les accents en UTF-8 (`sant%C3%A9`) : il s’agit du même chemin, pas d’une translittération.

Les trois anciens chemins techniques `/j/...` aboutissent désormais à des répertoires `.../index.html`. Leur forme canonique comporte donc une barre finale. Un serveur à index de répertoire redirige les anciens liens sans barre vers cette forme ; ce comportement a été constaté localement. **La redirection et les en-têtes réellement servis par GitHub Pages devront être vérifiés après publication.** Aucune règle de réécriture serveur non prise en charge par Pages n’est supposée.

## Inventaire des médias

Le manifeste [`source-inventory.json`](source-inventory.json) fournit pour chaque page sa correspondance Markdown et ses photos ; pour chaque ressource, l’URL d’origine, le fichier local, sa taille et son SHA-256. Il comprend aussi les pages auxiliaires et leur traitement.

- 43 emplacements de photos dans les neuf pages de contenu : 3 à l’accueil, 8 Santé, 10 Education, 8 Développement, 13 Activités et 1 logo Contact.
- 44 références d’images sources, en comptant le logo de l’en-tête. Trois doublons identiques octet pour octet ont été réunis : photo alimentaire accueil/Santé, matériel scolaire dans deux vues Education, et logo Contact/en-tête. Les différentes URL sources restent inscrites dans le manifeste.
- 41 fichiers d’images distincts, plus le fond d’en-tête. Les versions publiques non transformées ont été récupérées, y compris les originaux indiqués par `data-href` des galeries.
- 1 PDF : `static/documents/compte-rendu-ag-2026-01-31.pdf`, compte-rendu d’assemblée du 31 janvier 2026, quatre pages.
- 2 polices locales, Archivo Black et Imprima, avec leurs 2 licences SIL Open Font License, provenant de Google Fonts.

Au total : **50 correspondances de ressources sources, 47 fichiers distincts** après déduplication. Les icônes et logos publicitaires de la plateforme ne sont pas du contenu associatif ; ils n’ont pas été repris. La version optimisée du site génère en plus ses propres tailles WebP pendant le build. Les originaux ne sont pas remplacés ni altérés.

Les galeries du HTML initial exposaient l’ensemble de leurs images et leurs cibles d’agrandissement. Aucun média de contenu additionnel n’a été trouvé dans leurs paramètres JavaScript. L’inventaire ne prétend pas couvrir les brouillons non publiés, les fichiers privés ou des archives qui ne sont liées depuis aucune page publique.

## Points conservés et points à faire valider

**Adresse postale incohérente dans la source.** Contact indique `45560 Saint Jean Le Blanc`, tandis que le pied de page indique `45650 St Jean Le Blanc`. Les deux valeurs sont conservées à leurs emplacements ; l’association doit confirmer la bonne valeur avant une correction.

**Bulletin d’adhésion absent.** Contact annonçait « le lien suivant » sans lien ni document associé. Le seul téléchargement public découvert est le compte-rendu PDF. Le texte historique est conservé et accompagné d’une indication pour demander le bulletin par email ; aucun formulaire ou document d’adhésion n’a été inventé.

**Calendrier.** L’entrée Vélotour est datée simplement `05` dans la source. Elle est conservée telle quelle, comme toutes les autres dates. Il revient aux rédacteurs de clarifier cette date et d’actualiser manuellement le calendrier.

**Email public.** `pirogue2000@yahoo.fr` a été décodé depuis le champ public `data-cfemail`, puis écrit directement en Markdown. Les scripts de protection Cloudflare ne sont pas nécessaires.

**Mentions légales et pages commerciales.** `/about/` était une publicité Jimdo ; `/j/privacy` n’affichait aucun texte substantiel. La garantie légale et la rétractation étaient des fonctionnalités commerciales génériques de plateforme. Selon le choix confirmé par l’utilisateur, leurs chemins sont gardés avec des notices de statut, sans reprendre des conditions comme si elles étaient propres à l’association. Le responsable de publication, les informations complètes d’éditeur/hébergeur et les modalités de traitement des courriels restent à compléter et valider.

## Apparence et comportement

Le nouveau site reprend le fond photographique, le logo, les polices, la palette verte, la navigation, les titres centrés, la largeur de contenu, les photos d’accueil et les colonnes des actions. Les deux rangées de la page Activités alternent photos et texte. La composition est responsive ; l’indentation excessive par quatre blocs de citation imbriqués de l’ancien accueil n’est pas reproduite.

Les galeries utilisent des commandes explicites, le défilement tactile et les flèches du clavier, **sans rotation automatique**. Les images Markdown seules s’agrandissent dans une boîte de dialogue, fermable par Échap ou un bouton, avec retour du focus. Sans JavaScript, les photos restent visibles et leurs liens ouvrent les originaux. Une image déjà liée conserve sa destination.

Les trois boutons de partage Facebook identiques de l’ancien pied de page sont remplacés par un accès à la page de l’association et un lien de partage, sans widget. Connexion, publicité Jimdo, contrôles cookies, formulaires et scripts de plateforme ont été retirés. Aucun suivi n’a été ajouté. Les licences des deux polices sont conservées avec leurs fichiers.

## Contrôles et limites de publication

La construction Hugo est épinglée à `0.168.0`. Le contrôle `python3 scripts/check_site.py` vérifie les quatorze routes, les liens et ancres internes, les ressources HTML/CSS locales, les originaux et leurs empreintes, le PDF, le domaine préparé et l’absence de formulaires ou de dépendances runtime Jimdo. Les tests de ce contrôle utilisent uniquement la bibliothèque standard Python. La comparaison du texte source avec la sortie a également confirmé la conservation des dix-sept modules de texte éditorial des neuf pages de contenu, hors formulaires de plateforme remplacés.

Une vérification locale dans Chromium couvre les quatorze routes aux largeurs 1440, 390 et 320 pixels, les chargements d’images, les galeries, l’agrandissement et le retour du focus, la navigation mobile, les liens d’images, le fonctionnement sans JavaScript et les anciens chemins techniques. Les captures de comparaison sont des artefacts de session, pas des fichiers publiés. Aucun service externe n’est nécessaire pour afficher le site.

Le workflow suit le modèle de `clement-fouque/choisypourtous.fr`, avec installation et contrôle de l’archive Hugo, construction et contrôles avant le téléversement de `public/`, puis déploiement dans un job dépendant utilisant l’environnement `github-pages`. Les échecs du build ou de ses contrôles ne lancent pas ce job. La concurrence est sérialisée sans interruption d’un déploiement en cours.

**Aucun déploiement GitHub réel n’est attesté par cette migration locale.** L’activation de GitHub Pages, les permissions effectives et la publication sur `main` restent à vérifier dans GitHub une fois les changements intégrés. Les commandes locales ne prouvent pas à elles seules le comportement de l’environnement distant.

La mise en service revient au propriétaire : valider les informations associatives et légales, activer Pages avec GitHub Actions, vérifier une publication réussie, configurer/vérifier le domaine personnalisé, effectuer lui-même la bascule DNS et contrôler HTTPS, les routes accentuées et les redirections. Ne résilier Jimdo qu’après ses propres contrôles de la nouvelle publication.
