# How To Debug

## Basic description
FineDi est une application d'annotation écrite en python, basée sur Flask pour
 l'interface graphique, et sur SoX pour le traitement des fichiers sonores.

Pour faire fonctionner l'appli, il faut mettre les .wav et les fichiers .rttm (qui ont le même nom que les .wav)
dans finedi/static/audio.
L'écran d'accueil propose "start session" et "continue session". Lorsque l'on clique sur start session, cela va générer des fichiers .rttm auquel on aura rajouté le prefixe refined_ (ex ako.rttm devient refined_ako.rttm). Ces fichier "refined" contiennent les transcriptions découpés en plus petits segments de 0.5s. Ce sont dans ces fichiers "refined" que seront écrites les annotations réalisées. Si on a déjà des fichiers refined dans lequel on a déjà annoté des choses, cliquer sur "start session" va écraser ces annotations.
Si l'on choisi continue session, on continue à partir du segment où on s'était arrêté.
Lorsqu'on choisi start session, on est encore ammené à faire un choix. Le choix de base est "talker label". lorsqu'on appuie sur continuer, l'application lance une segmentation des fichiers audio pour récuperer les segments de entre 0.5s et 1s annotés comme étant "CHI". Cette segmentation est réalisée par sox (appelé au traver de subprocess). Cette étape peut prendre un peu de temps et laisse affiché la page de selection de tache, un coup d'oeil dans le terminal permet de vérifier qu'il n'y a aucune erreur à l'appel de SoX.

## Common Problems
- Des problèmes spécifiques à chaque OS ont été remarqués, donc j'ai créé deux branches sur le projet, une "estelle" pour un ordinateur linux, une "laure" pour un ordinateur Mac OS

- Un des problème qui peut survenir est que, lors du découpage des fichiers audio en petits segments, ces petits fichiers prennent comme nom: 
fichierDOrigine_onset_duration_label.wav 
et il se peut que le label soit "<NA>". Il est possible que la présence de chevrons fasse planter la commande du terminal (puisque ça ne remplace pas les "<" par des "\<"). Dans ce cas, dans utils.py, il est conseillé de changer le champ lab (ligne 321 d'utils.py) par lab[1:-1]. C'est un correctif un peu "crade", puisque des sécurité quant à l'échappement de la commande devrait être prise (en cours de dev).

- Parfois, une erreur survient lors de la validation d'une annotation, ou du passage à une nouvelle annotation, ou même parfois lors de la création des segments, qui affiche dans le terminal un probleme de lecture de fichier ( en général détécté à une ligne similaire à celle ci: 
`_1, fname, _2, on, dur, _3, label, spkr, _4 = line.strip('\n').split('\t')`
)
Dans ce cas, remonter au dessus du message d'erreur pour voir (normalement) le fichier qui a fait planter la lecture. Regarder alors le fichier en question dans audio (regarder aussi le fichier refined_ associé) pour voir s'il n'est pas corompu, ce qui apparait souvent pas des lignes remplies du caractère exotique "ÿ". Dans ce cas, si c'est possible (i.e. si ce n'est pas un fichier refined) remplacer le fichier par l'original. Si c'est un refined_ , essayer d'inférer à partir des autres lignes la fin de la ligne en question, ou bien recréer le fichier refined (cf  la fonction split_segments_rttm dans utils.py) et recopier les annotations déjà fait de l'ancien fichier refined (les annotation sont la colonne 7, quand la colonne 8 est "CHI") dans le nouveau fichier refined.

- Il arrive parfois que le paquet soit tout simplement corrompu (erreur de lecture des certains dossiers, erreur d'ecriture). Dans ce cas, faire un backup des refined et si possible du dossier media, supprimer le paquet finedi et refaire un git clone (penser à se mettre sur la bonne branche!).

- Si on est confronté à une erreur input/output, vérifier que la clef usb n'est pas pleine. Si elle est pleine, commencer par vider le dossier .Trash ou .Trashes de la clef usb. Si ça n'est pas suffisant, essayer de vider au plus possible la clef des fichiers non utils (i.e. qui ne sont pas dans FineDi/finedi/static.

