# -*- coding: utf-8 -*-

import os
import re
import datetime

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from base.models import Work, Image, Inscription, Exhibition, BibliographyReference, ExhibitionInstance

class Command(BaseCommand):
    args = '<xls file>'
    help = 'Import the Michaux data (catalogue or exhibitions) from an xls file'

    def _import_data_from_xls(self, filename):
        """Import from an xls file.
        """
        import xlrd
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)
        header = s.row_values(0)
        # Cote	Cote simplifiée	Certificat	technique	précisions sur la technique	série	Année	Année simplifiée	Dimension	Hauteur	Largeur	Signature	Présence signature	Support 1	Support 2 1	Support 2 2	Notes de Michaux	Notice	Remarques	Expositions	Reproductions	Numéro d'inventaire

        for n in range(1, s.nrows - 1):
            #if n < 80:
            #    continue
            #if n > 600:
            #    break
            row = s.row_values(n)
            data = dict(zip(header, row))
            w = Work()
            # FIXME: get appropriate value
            w.creator_id = 1
            w.contributor_id = 1
            w.status = Work.AUTHENTICATED_STATUS
            w.old_references = data['Cote']
            if data['Certificat'] != '':
                w.certificate = long(data['Certificat'])
            # Remove whitespaces around commas
            w.serie = data[u'série']
            w.technique = ",".join(re.split('\s*,\s*', data['technique'].strip()))
            w.note_technique = data['précisions sur la technique']
            w.support = data['Support 1']
            w.support_details = data['Support 2 1']
            w.note_support = data['Support 2 2']
            try:
                w.height = long(data['Hauteur'])
            except ValueError:
                self.stderr.write("Missing height for %s\n" % data['Cote'].encode('utf-8'))
                w.height = 0
            try:
                w.width = long(data['Largeur'])
            except ValueError:
                self.stderr.write("Missing width for %s\n" % data['Cote'].encode('utf-8'))
                w.width = 0
            simple = data[u'Année simplifiée']
            if simple != '':
                w.creation_date_start = long(simple)
            if simple == '' or str(simple) != data[u'Année'].strip():
                w.note_creation_date = data[u'Année']
            w.comment = "\n".join(data[i] for i in ('Notice', 'Remarques') if data[i])
            if data[u'Reproductions']:
                w.revision = 'BIBLIO:' + data[u'Reproductions']
            w.save()
            self.stderr.write("Saved %s %s\n" % (n, unicode(w).encode('utf-8')))
            # FIXME: Improve image name heuristic
            pic = '/home/oaubert/tmp/michaux/%s.jpg' % data['Cote'].lower().replace(' / ', '_').replace(' ', '_')
            if os.path.exists(pic.encode('utf-8')):
                self.stderr.write("   Copying image %s\n" % pic.encode('utf-8'))
                i = Image()
                i.work = w
                i.photograph_name = 'Franck Leibovici'
                i.support = u'numérique'
                i.nature = u'référence'
                with open(pic, 'rb') as f:
                    i.original_image.save(os.path.basename(pic), File(f))
                i.save()

            if data['Présence signature'].startswith('oui'):
                sig = Inscription()
                sig.nature = 'signature'
                pos = re.findall('\((.+)\)', data['Présence signature'])
                if pos:
                    if ',' in pos[0]:
                        sig.position, sig.note = re.split('\s*,\s*', pos[0], 1)
                    else:
                        sig.position = pos[0]
                sig.work = w
                sig.save()

            note = data['Notes de Michaux']
            if note:
                sig = Inscription()
                sig.nature = 'note'
                pos = re.findall('\(([hbcgd]{2})\)', note)
                if pos:
                    sig.position = pos[0]
                sig.note = note
                sig.work = w
                sig.save()

            if data['Expositions'].strip():
                notfound = []
                for ab in data['Expositions'].split('\n'):
                    ab = ab.strip().strip(",")
                    qs = Exhibition.objects.filter(abbreviation=ab)
                    if qs.count() == 1:
                        # Found the exhibition
                        ei = ExhibitionInstance()
                        ei.work = w
                        ei.exhibition = qs[0]
                        ei.save()
                        msg = 'ok'
                    else:
                        msg = 'NOT FOUND'
                        notfound.append(ab)
                    self.stderr.write("   Exhibition %s... %s\n" % (ab.encode('utf-8'), msg))
                    if notfound:
                        w.revision += u"\n".join("EXPO: %s" % e for e in notfound)
                        w.save()

    def dummydate2date(self, data):
        """Parse a dummy date (DDMMYYYY as a number) into its components.
        """
        try:
            d = long(data)

            if d < 10000:
                return (d, 0, 0)
            else:
                return (d % 10000,
                        (d / 10000) % 100,
                        (d / 1000000))
        except ValueError:
            return (0, 0, 0)

    def _import_exhibitions_from_xls(self, filename):
        """Import from an xls file.
        """
        import xlrd
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)
        header = s.row_values(0)

        for n in range(1, s.nrows - 1):
            row = s.row_values(n)
            data = dict(zip(header, row))
            e = Exhibition()
            e.title = data[u"titre de l'exposition"]
            e.location = data[u"lieu de l'exposition"]
            e.nature = data['Solo']
            # e.address =
            e.city = data['Ville']
            e.country = data['Pays']
            e.start_year = long(data['Date'])

            if data[u'abréviation']:
                ab = data[u'abréviation']
            else:
                # Have to generate one...
                ab = "%s %s, %d" % (e.location, e.city, e.start_year)
            if Exhibition.objects.filter(abbreviation=ab).exists():
                ab = "DOUBLON " + ab
            e.abbreviation = ab

            try:
                d = datetime.date.fromordinal(long(data['Date a']))
                if d.year < 1900 and d.year > 0:
                    # Add 1900
                    d=datetime.date(1900 + d.year, d.month, d.day)
                e.start_year = d.year
                e.start_month = d.month
                e.start_day = d.day
            except ValueError:
                pass
            # End date is a string disguised as a number...
            d = self.dummydate2date(data['Date b'])
            if d[0]:
                e.end_year, e.end_month, e.end_day = d
            e.curator = data['commissaire']
            # FIXME: commissaire 2 : no space for him/her
            c = None

            if data['Catalogue'] == 'oui':
                c = BibliographyReference()
                c.nature = 'catalogue'
                c.abbreviation = data[u'abréviation']
                c.container_others = data['Textes']
                c.city = data['Ville']
                c.note = data['Titre']
                c.save()

                e.catalogue = c

            # e.original =
            # e.comment =
            e.note = data['Remarques']
            e.save()
            self.stdout.write(unicode(e).encode('utf-8') + "\n")

            for (num, nom, lieu, ville, pays, annee, start, end) in (
                (' (2)', 'Nom 2', "lieu d'exposition 2", 'Ville 2', 'Pays 2', 'Date 2', 'Date c', 'Date d'),
                (' (3)', 'Nom 3', "lieu d'exposition 3", 'Ville 3', 'Pays 3', 'Date 3', 'Date e', 'Date f'),
                (' (4)', 'Nom 4', "lieu d'exposition 4", 'Ville 4', 'Pays 4', 'Date 4', 'Date g', 'Date h'),
                ):
                if data[nom]:
                    # Second exhibition
                    e2 = Exhibition()
                    e2.original = e
                    e2.abbreviation = e.abbreviation + num
                    e2.title = e.title
                    e2.location = data[lieu]
                    e2.city = data[ville]
                    e2.country = data[pays]
                    if data[annee]:
                        e2.start_year = long(data[annee])
                    else:
                        e2.start_year = e.start_year
                    d = self.dummydate2date(data[start])
                    if d[0]:
                        e2.start_year, e2.start_month, e2.start_day = d
                    d = self.dummydate2date(data[end])
                    if d[0]:
                        e2.end_year, e2.end_month, e2.end_day = d
                    if c is not None:
                        e2.catalogue = c
                    e2.save()
                    self.stdout.write("   " + unicode(e2).encode('utf-8') + "\n")


    def handle(self, *args, **options):
        if not args:
            raise CommandError("Missing parameter")
        for fname in args:
            self.stdout.write("* Importing from %s\n" % fname.encode('utf-8'))
            # FIXME: add proper option/arg passing instead of the name hack?
            if 'catalogue' in fname.lower():
                self._import_data_from_xls(fname)
            elif 'exposition' in fname.lower():
                self._import_exhibitions_from_xls(fname)
            else:
                self.stderr.write("Cannot determine file type\n")

        self.stdout.write("\nDone.\nDO NOT FORGET TO RUN rebuild_index !!!\n")
