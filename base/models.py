# -*- coding: utf-8 -*-

import re
import os

from gettext import gettext as _
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from coop_tag.managers import TaggableManager

class Work(models.Model):
    """Representation of a Work
    """
    EDITING_STATUS = 'editing'
    PENDING_STATUS = 'pending'
    AUTHENTICATED_STATUS = 'authenticated'
    STATUS_CHOICES = (
        (AUTHENTICATED_STATUS, _("Authentifié")),
        (PENDING_STATUS, _("En attente")),
        (EDITING_STATUS, _("En cours d'édition")),
        )
    class Meta:
        verbose_name_plural = _("oeuvres")
        verbose_name = _("oeuvre")
        #ordering = ('status', 'created')
        #get_latest_by = 'created'

    creator = models.ForeignKey(User,
                                verbose_name=_('créateur'),
                                help_text=_('Créateur de la fiche'),
                                editable=False,
                                related_name='created')

    created = models.DateTimeField(_('création'),
                                   help_text=_('Date de création de la fiche'),
                                   null=True, editable=False,
                                   auto_now_add=True)

    contributor = models.ForeignKey(User,
                                    verbose_name=_('éditeur'),
                                    help_text=_('Dernier éditeur de la fiche'),
                                    editable=False,
                                    related_name='modified')

    modified = models.DateTimeField(_('dernière modification'),
                                    help_text=_('Date de dernière modification de la fiche'),
                                    null=True, editable=False,
                                    auto_now=True)

    status = models.CharField(_('statut'),
                              help_text=_('Statut éditorial de la fiche'),
                              max_length=64,
                              choices=STATUS_CHOICES,
                              default=EDITING_STATUS,
                              editable=True)

    cote = models.AutoField(_("cote"), primary_key=True, editable=False)

    master = models.ForeignKey('self',
                               verbose_name=_("cote de référence"),
                               help_text=_("En cas de doublon identifié, indique la cote de la fiche de référence pour l’oeuvre. Les autres champs de cette fiche-ci peuvent être vidés/ignorés."),
                               null=True, blank=True)

    # ancienne(s) références(s) : (kc000, ou mp000 ou cmp000, etc.) Contenu: [\w\d\s-/]+
    old_references = models.CharField(_('anciennes références'),
                                      help_text=_("Liste d'anciennes références, séparées par des virgules"),
                                      max_length=255,
                                      blank=True)

    certificate = models.IntegerField(_('certificat'),
                                      help_text=_("Certificat d'authenticité"),
                                      blank=True, null=True)

    note_references = models.TextField(_('notes sur les références'),
                                       help_text=_("Notes (privées) sur les références"),
                                       blank=True)

    # Technique et support

    # titre de la série (mouvements, mescalinien)
    serie = models.CharField(_("série"),
                             help_text=_("Titre de la série dans l'oeuvre de Michaux"),
                             max_length=255,
                             blank=True)

    # technique (technique) : choix parmi une énumération extensible (huile, huile et acrylique, aquarelle...)
    technique = models.CharField(_("technique"),
                                 help_text=_("Technique utilisée"),
                                 max_length=255)

    note_technique = models.CharField(_("notes sur la technique"),
                                      help_text=_("Notes sur la technique utilisée"),
                                      max_length=255, blank=True)

    # support : choix parmi une énumération extensible (papier, toile, cartoil, papier toilé, japon, etc) - type générique
    support = models.CharField(_("support"),
                               help_text=_("Support utilisé, de type générique: papier, toile, cartoil, papier toilé, etc"),
                               max_length=255)

    #précisions de support : précisions sur le support (gamme - tramé, chiffon,, ou marque - arches, etc)
    support_details = models.CharField(_("précisions de support"),
                                       help_text=_("précisions sur le support (gamme - tramé, chiffon, ou marque - arches, etc)"),
                                       max_length=255,
                                       blank=True)

    note_support = models.TextField(_("notes sur le support"),
                                   help_text=_("Notes (privées) sur le support"),
                                   blank=True)

    # hauteur : nombre entier (en mm)
    height = models.IntegerField(_("hauteur"),
                                 help_text=_("Hauteur (en mm)"),
                                 null=True)

    # largeur : nombre entier (en mm)
    width = models.IntegerField(_("largeur"),
                                help_text=_("Largeur (en mm)"),
                                null=True)

    # Date de Création
    # source de la date : texte libre (Henri Michaux / catalogue / nom de l’expert / etc.)
    creation_date_source = models.CharField(_("source de la date"),
                                           help_text=_("Origine de la datation: Henri Michaux, catalogue, nom de l'expert, etc"),
                                           max_length=255,
                                           blank=True)

    # incertitude : texte libre
    creation_date_uncertainty = models.CharField(_("incertitude sur la date"),
                                                 help_text=_("Incertitude sur la date: avant, après, environ, etc"),
                                                 max_length=64,
                                                 blank=True)

    # début : année [entier, du type 1956] - optionnel (pour exprimer par exemple qu’un oeuvre a été réalisée avant une date: on ne remplit alors que le champ fin).
    creation_date_start = models.IntegerField(_("année de début"),
                                             help_text=_("Année [entier, du type 1956] - optionnelle (pour exprimer par exemple qu’une oeuvre a été réalisée après une date: on ne remplit alors que le champ début)."),
                                             blank=True, null=True)

    # fin : année [entier, du type 1956] - optionnel (pour exprimer par exemple qu’un oeuvre a été réalisée avant une date: on ne remplit alors que le champ fin).
    creation_date_end = models.IntegerField(_("année de fin"),
                                             help_text=_("Année [entier, du type 1956] - optionnelle (pour exprimer par exemple qu’une oeuvre a été réalisée avant une date: on ne remplit alors que le champ fin)."),
                                             blank=True, null=True)

    # notes : texte libre
    note_creation_date = models.TextField(_("notes sur la date"),
                                   help_text=_("Notes (privées) sur le support"),
                                   blank=True)

    # date alternative : la source de la date alternative est alors indiquée dans les notes
    creation_date_alternative = models.IntegerField(_("année alternative"),
                                                    help_text=_("Date alternative : la source de cette date alternative est alors indiquée dans les notes"),
                                                    blank=True, null=True)

    tags = TaggableManager(help_text=_("Tags associés"), blank=True,)

    # Tags: Liste de tags associés (on interdit les : dans les noms
    # des tags de manière à permettre une éventuelle évolution vers
    # les “tags machine” à la Flickr) permettre les tags comprenant un
    # espace il faut préserver l’information d’origine (auteur) du tag
    # notion de diffusion (privé / public) laisser la possibilité à
    # chaque utilisateur de supprimer ses propres tags Notion de
    # galerie/album : prévoir la possibilité de distinguer des
    # albums/collections par rapport à des tags classiques (en terme
    # d’affichage/point d’entrée ou de filtrage dans la liste des
    # tags: on n’afficherait par défaut que les tags qui ne sont pas
    # des albums). Ça peut être mis en oeuvre via un tag machine
    # “album:nom de l’album” par exemple.  groupes “anonyme” : on peut
    # vouloir définir une collection sans la nommer (dans un premier
    # temps). On pourrait proposer un système de tags anonymes
    # automatiques (avec un numéro par exemple anonymous:123) pour
    # cela.

    # commentaire : texte libre pouvant être affiché au public

    comment = models.TextField(_("commentaire"),
                               help_text=_("Texte libre pouvant être affiché au public"),
                               blank=True)

    revision = models.TextField(_("révisions"),
                                help_text=_("Révisions à effectuer : texte libre, indiquant les révisions encore à faire sur la fiche. Des conventions de nommage peuvent être adoptées pour catégoriser ces révisions par exemple."),
                                blank=True)

    @property
    def printable_year(self):
        if self.creation_date_start is not None:
            if self.creation_date_end is None:
                r = str(self.creation_date_start)
            else:
                r = "%d-%d" % (self.creation_date_start, self.creation_date_end)
        elif self.creation_date_end is not None:
            r = str(self.creation_date_end)
        else:
            return "N/C"
        if self.creation_date_uncertainty:
            return self.creation_date_uncertainty + " " + r
        else:
            return r

    @property
    def picture(self):
        if self.image_set.count():
            # More than 1 image. We can find a thumbnail
            # FIXME: use self.image_set.filter(nature__eq='reproduction')
            return self.image_set.iterator().next()
        else:
            return None

    @property
    def thumbnail(self):
        p = self.picture
        if p:
            return p.thumbnail
        else:
            return None

    @property
    def image(self):
        p = self.picture
        if p:
            return p.image
        else:
            return None

    def get_absolute_url(self):
        return reverse('base.views.work', args=[str(self.cote)])

    def __unicode__(self):
        d = {'printable_year': self.printable_year}
        d.update(self.__dict__)
        return u"#%(cote)d - %(technique)s sur %(support)s %(support_details)s (%(printable_year)s)" % d

    @staticmethod
    def import_worksheet(filename):
        """Import a google refine worksheet.
        """
        import xlrd
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)
        header = s.row_values(0)
        for n in range(1, s.nrows - 1):
            if n < 408:
                continue
            if n > 600:
                break
            row = s.row_values(n)
            data = dict(zip(header, row))
            w = Work()
            # FIXME: get appropriate value
            w.creator_id = 1
            w.contributor_id = 1
            w.status = Work.AUTHENTICATED_STATUS
            w.old_references = row[0]
            if data['Certificat'] != '':
                w.certificate = long(data['Certificat'])
            tech = data['Technique']
            for serie in ('mescalinien ', '"post-mescalinien"',
                          '"mouvements"'):
                if serie in tech:
                    w.serie = serie
                    tech = tech.replace(serie, '')
                    break
            w.technique = tech
            support = data['Papier'].split()
            if support:
                w.support = support[0]
                w.note_support = " ".join(support[1:])
            try:
                w.height = long(data['Hauteur'])
            except ValueError:
                print "Missing height"
                w.height = 0
            try:
                w.width = long(data['Largeur'])
            except ValueError:
                print "Missing width"
                w.width = 0
            if data[u'Année simplifiée'] != '':
                w.creation_date_start = long(data[u'Année simplifiée'])
            if data[u'Année simplifiée'] == '' or (str(long(data[u'Année simplifiée'])) != data[u'Année'].strip()):
                w.note_creation_date = data[u'Année']
            w.comment = "\n".join((data['Notice'], data['Remarques']))
            w.save()
            print "Saved", n, unicode(w).encode('utf-8')
            pic = '/home/oaubert/tmp/michaux/%s.jpg' % row[0].upper().replace(' ', '_')
            if os.path.exists(pic.encode('utf-8')):
                print "Copying image"
                i = Image()
                i.work = w
                i.photograph_name = 'Franck Leibovici'
                i.support = 'numérique'
                i.nature = 'référence'
                with open(pic, 'rb') as f:
                    i.original_image.save(os.path.basename(pic), File(f))
                i.save()

            if data['Signature'].startswith('oui'):
                sig = Inscription()
                sig.nature = 'signature'
                pos = re.findall('\((.+)\)', data['Signature'])
                if pos:
                    sig.position = pos[0]
                sig.work = w
                sig.save()

class Inscription(models.Model):
    class Meta:
        verbose_name_plural = _("Inscriptions")

    # Inscription: On veut pouvoir parfois entrer plusieurs inscriptions (par exemple au recto une signature, une date, et au verso, des annotations techniques)
    work = models.ForeignKey(Work,
                             verbose_name=_("Oeuvre"))

    # type d’inscription : signature / date / dédicace / indications techniques / autre (date, note de michaux)
    nature = models.CharField(_("type d'inscription"),
                              help_text=_("signature / date / dédicace / indications techniques / autre (date, note de michaux) / etc"),
                              max_length=255,
                              blank=True)
    # position : choix parmi une énumération extensible (recto, verso, bas droite, bas gauche, etc)
    position = models.CharField(_("position de l'inscription"),
                                help_text=_("Position: choix parmi une énumération extensible (recto, verso, bas droite, bas gauche, etc)"),
                                max_length=255,
                                blank=True)
    note = models.TextField(_("note"),
                             help_text=_("Note: contenu, détails, etc"),
                             blank=True)

class Image(models.Model):
    work = models.ForeignKey(Work,
                             verbose_name=_("Oeuvre"))

    photograph_name = models.CharField(_("nom du photographe"),
                                       max_length=255,
                                       blank=True)
    reference = models.CharField(_("référence"),
                                 help_text=_("Référence de la photo dans l’inventaire du photographe"),
                                 max_length=255,
                                 blank=True)
    support = models.CharField(_("support"),
                                 help_text=_("Type de photo : argentique / numérique / ektachrome, diapositive / scan de reproduction papier"),
                                 max_length=255,
                                 blank=True)

    #nature de l’image : représentation de référence / représentation pour impression / représentation alternative / image annexe (par exemple image de l’oeuvre en situation dans une revue ou une expo, ou une lettre)
    nature = models.CharField(_("nature"),
                                 help_text=_("nature de l’image : représentation de référence / représentation pour impression / représentation alternative / image annexe (par exemple image de l’oeuvre en situation dans une revue ou une expo, ou une lettre)"),
                                 max_length=255,
                                 blank=True)

    # Lors de l’upload de l’image en  haute résolution, la plate-forme convertira automatiquement l’image en des versions “web” (1600x1200 + vignette + 2048x1536 [ipad3])
    original_image = models.ImageField(_("image"),
                                       upload_to='images',
                                       max_length=512,
                                       height_field='height',
                                       width_field='width')

    image = ImageSpecField([ResizeToFit(1600, 1200)],
                           image_field='original_image',
                           format='JPEG',
                           options={'quality': 90})

    thumbnail = ImageSpecField([ResizeToFit(120, 120)],
                               image_field='original_image',
                               format='JPEG',
                               options={'quality': 90})

    created = models.DateTimeField(_('création'),
                                   help_text=_("Date de téléchargement de l'image"),
                                   null=True, editable=False,
                                   auto_now=True)

    height = models.IntegerField(_("hauteur"),
                                 help_text=_("Hauteur (en pixels)"),
                                 editable=False)


    width = models.IntegerField(_("largeur"),
                                help_text=_("Largeur (en pixels)"),
                                editable=False)

    note = models.TextField(_('note'),
                            help_text=_("Notes"),
                            blank=True)

    def __unicode__(self):
        return u"%(nature)s (%(width)sx%(height)s) par %(photograph_name)s - %(note)s" % self.__dict__

    @property
    def orientation(self):
        if self.width >= self.height:
            return "landscape"
        else:
            return "portrait"

class BibliographyReference(models.Model):
    class Meta:
        verbose_name = _("référence bibliographique")
        verbose_name_plural = _("références bibliographiques")

    nature = models.CharField(_("type de référence"),
                              help_text=_("catalogue, article de journal, monographie, livre, chapitre de livre..."),
                              max_length=255,
                              blank=True)
    abbreviation = models.CharField(_("abréviation"),
                                    help_text=_("nom, titre ou lieu d’exposition, année, (a, b, c quand il y en a plusieurs la même année)"),
                                    max_length=255,
                                    blank=True)

    creator = models.CharField(_("auteur"),
                              help_text=_("Auteur de l'article/ouvrage/essai"),
                              max_length=255,
                              blank=True)
    title = models.CharField(_("titre"),
                              help_text=_("Titre de l'article/ouvrage/essai"),
                              max_length=512,
                              blank=True)

    # Dans le cas d’un article dans le cadre d’une oeuvre plus large (livre, revue, etc):
    container_title = models.CharField(_("titre du contenant"),
                                       help_text=_("Titre du livre/revue/etc contenant la référence"),
                                       max_length=512,
                                       blank=True)
    container_creator = models.CharField(_("auteur du contenant"),
                                         help_text=_("Auteur/éditeur de livre/revue"),
                                         max_length=255,
                                         blank=True)
    container_others = models.TextField(_("textes de"),
                                        help_text=_("textes de [texte libre] : prénom - nom - titre du texte"),
                                        blank=True)

    editor = models.CharField(_("édition"),
                              help_text=_("Maison d'édition/lieu d'exposition"),
                              max_length=512,
                              blank=True)

    city = models.CharField(_("ville"),
                              help_text=_("Ville"),
                              max_length=255,
                              blank=True)

    number = models.CharField(_("numéro"),
                              help_text=_("Numéro du volume/de la revue"),
                              max_length=255,
                              blank=True)

    publication_date = models.DateField(_("date de publication"),
                                        blank=True, null=True)
    page_number = models.IntegerField(_("numéro de page"),
                                      help_text=_("numéro de page de l’article contenu"),
                                      blank=True, null=True)

    comment = models.TextField(_("commentaire"),
                               help_text=_("Texte libre pouvant être affiché au public"),
                               blank=True)
    note = models.TextField(_("notes"),
                            help_text=_("Notes (privées)"),
                            blank=True)

    def __unicode__(self):
        return u"Réf. bib. %(title)s (%(creator)s)" % self.__dict__

class Exhibition(models.Model):
    class Meta:
        verbose_name_plural = _("expositions")
        verbose_name = _("exposition")

    abbreviation  = models.CharField(_("abréviation"),
                                     help_text=_("Sous la forme date (nombre entier, année) + nom du lieu d’exposition (texte libre)"),
                                     max_length=255,
                                     unique=True, blank=False)
    title = models.CharField(_("titre"),
                             help_text=_("Titre complet de l’exposition"),
                             max_length=512,
                             blank=True)
    location = models.CharField(_("lieu"),
                             help_text=_("Lieu de l'exposition"),
                             max_length=512,
                             blank=True)
    nature = models.CharField(_("type d'exposition"),
                              help_text=_("Type d'exposition"),
                              max_length=32,
                              choices=( ("solo", _("Solo")),
                                        ("groupe", _("En groupe")) ),
                              default="solo")
    address = models.CharField(_("adresse"),
                             help_text=_("Adresse de l'exposition"),
                             max_length=512,
                             blank=True)
    city = models.CharField(_("ville"),
                            help_text=_("Ville"),
                            max_length=255,
                            blank=True)
    country = models.CharField(_("pays"),
                               help_text=_("Pays"),
                               max_length=255,
                               blank=True)

    start_year = models.IntegerField(_("Année"),
                                     help_text=_("Année de début"),
                                     blank=True)
    start_month = models.IntegerField(_("Mois"),
                                      help_text=_("Mois de début - [par convention, si on met 0 pour mois et/ou 0 pour jour, ça signifie qu’on ne dispose pas de cette information. On ne prendra alors en compte que l’année - qui sera toujours spécifiée]"),
                                      blank=True, null=True)
    start_day = models.IntegerField(_("Jour"),
                                    help_text=_("Jour de début"),
                                    blank=True, null=True)
    end_year = models.IntegerField(_("Année"),
                                   help_text=_("Année de fin - peut être 0 si inconnu"),
                                   blank=True, null=True)
    end_month = models.IntegerField(_("Mois"),
                                      help_text=_("Mois de fin - [par convention, si on met 0 pour mois et/ou 0 pour jour, ça signifie qu’on ne dispose pas de cette information. On ne prendra alors en compte que l’année - qui sera toujours spécifiée]"),
                                      blank=True, null=True)
    end_day = models.IntegerField(_("Jour"),
                                    help_text=_("Jour de fin"),
                                    blank=True, null=True)

    curator = models.CharField(_("Commissaire"),
                               help_text=_("Commissaire d'exposition"),
                               max_length=512,
                               blank=True)

    catalogue = models.ForeignKey(BibliographyReference,
                                  verbose_name=_("catalogue d'exposition"),
                                  blank=True, null=True)

    original = models.ForeignKey('self',
                                 verbose_name=_("exposition initiale"),
                                 help_text=_("Exposition initiale (en cas de reprise)"),
                                 blank=True, null=True)
    comment = models.TextField(_("commentaire"),
                               help_text=_("Commentaire : texte libre, pouvant être affiché au public"),
                               blank=True)
    note = models.TextField(_("notes"),
                            help_text=_("Notes (privées)"),
                            blank=True)
    def __unicode__(self):
        return u"Exposition %(abbreviation)s" % self.__dict__

class ExhibitionInstance(models.Model):
    work = models.ForeignKey(Work,
                             verbose_name=_("Oeuvre"))

    exhibition = models.ForeignKey(Exhibition,
                                   verbose_name=_("exposition"),
                                   help_text=_("Exposition"))

    reference = models.CharField(_("référence"),
                                 help_text=_("Numéro de référence dans l’exposition"),
                                 max_length=255,
                                 blank=True)

    illustration = models.BooleanField(_("illustration"),
                                       help_text=_("Coché si une illustration était disponible dans le catalogue de l’exposition"),
                                       blank=True)

    illustration_description = models.TextField(_("description de l'illustration"),
                                                blank=True)

    note = models.TextField(_("note"),
                            help_text=_("Note (privée)"),
                            blank=True)

class Event(models.Model):
    class Meta:
        verbose_name = _("événement")

    work = models.ForeignKey(Work,
                             verbose_name=_("oeuvre"))
    date = models.DateField(_("date"))
    nature = models.CharField(_("type d'événement"),
                              help_text=_("Type d’événement (vente publique, cession privée, restauration...) - énumération extensible"),
                              max_length=64,
                              blank=True)
    description = models.TextField(_("description"),
                                   blank=True)

    def __unicode__(self):
        return u"Événement %(nature)s - %(date)s" % self.__dict__

class Reproduction(models.Model):
    class Meta:
        verbose_name = _("reproduction")

    work = models.ForeignKey(Work,
                             verbose_name=_("oeuvre"))
    reference = models.ForeignKey(BibliographyReference,
                                  verbose_name=_("référence bibliographique"))
    page = models.IntegerField(_("page"),
                               blank=True, null=True)
    number = models.CharField(_("numéro"),
                              help_text=_("Numéro dans la page - ça sera le plus souvent un nombre, mais on peut avoir besoin d’y ajouter des précisions"),
                              max_length=16,
                              blank=True)
    comment = models.TextField(_("commentaire"),
                               help_text=_("commentaire : texte libre, pouvant être affiché au public"),
                               blank=True)

    def __unicode__(self):
        return u"Reproduction de %(work)s" % self.__dict__

class Owner(models.Model):
    class Meta:
        verbose_name = _("propriétaire")

    firstname = models.CharField(_("prénom"),
                                 help_text=_("Prénom"),
                                 max_length=255,
                                 blank=False)
    name = models.CharField(_("nom"),
                            help_text=_("Nom"),
                            max_length=255,
                            blank=False)
    address = models.CharField(_("adresse"),
                               help_text=_("Adresse de l'exposition"),
                               max_length=512,
                               blank=True)
    city = models.CharField(_("ville"),
                            help_text=_("Ville"),
                            max_length=255,
                            blank=True)
    country = models.CharField(_("pays"),
                               help_text=_("Pays"),
                               max_length=255,
                               blank=True)
    note = models.TextField(_("notes"),
                            help_text=_("Notes (privées)"),
                            blank=True)

    def __unicode__(self):
        return u"%(firstname)s %(name)s (%(city)s %(country)s)" % self.__dict__

class Acquisition(models.Model):
    work = models.ForeignKey(Work,
                             verbose_name=_("oeuvre"))
    current_owner = models.BooleanField(_("current owner"))
    # FIXME: est-ce que c'est vraiment relatif à l'acquisition ? Un
    # même propriétaire pourrait avoir plusieurs collections de
    # statuts différents
    private = models.BooleanField(_("private collection"))
    owner = models.ForeignKey(Owner,
                              verbose_name=_("propriétaire"))
    date = models.DateField(_("date d'acquisition"),
                            blank=True)
    note = models.TextField(_("notes"),
                            help_text=_("Notes (privées)"),
                            blank=True)

    # FIXME: use django-reversion or https://bitbucket.org/q/django-simple-history/src for history ?
    # date + heure + commentaire sur les modifications: commentaire standard (tels champs modifiés) généré automatiquement + possibilité de corriger/ajouter des informations supplémentaires lors de la validation.
