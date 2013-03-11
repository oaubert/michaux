# -*- coding: utf-8 -*-

import os
import re
import datetime

from django.core.files import File
from django.core.management.base import BaseCommand

from base.models import Work, Image, Inscription, Exhibition, BibliographyReference

class Command(BaseCommand):
    args = '<xls file>'
    help = 'Import the Michaux data from an xls file'

    def _import_data_from_xls(self, filename):
        """Import from an xls file.
        """
        import xlrd
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)
        header = s.row_values(0)
        # cote	simplifiee	certificat	technique	precisions technique	serie	annee	annee simple	dimensions	hauteur	largeur	signature	presence	support	support2	support3	notes_michaux	notice	remarques	expositions	reproductions	inventaire

        for n in range(1, s.nrows - 1):
            #if n < 408:
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
            w.old_references = data['cote']
            if data['certificat'] != '':
                w.certificate = long(data['certificat'])
            # Remove whitespaces around commas
            w.serie = data['serie']
            w.technique = ",".join(re.split('\s*,\s*', data['technique'].strip()))
            w.note_technique = data['precisions technique']
            w.support = data['support']
            w.support_details = data['support2']
            w.note_support = data['support3']
            try:
                w.height = long(data['hauteur'])
            except ValueError:
                self.stderr.write("Missing height for %s\n" % data['cote'].encode('utf-8'))
                w.height = 0
            try:
                w.width = long(data['largeur'])
            except ValueError:
                self.stderr.write("Missing width for %s\n" % data['cote'].encode('utf-8'))
                w.width = 0
            if data[u'annee simple'] != '':
                w.creation_date_start = long(data[u'annee simple'])
            if data[u'annee simple'] == '' or (str(long(data[u'annee simple'])) != data[u'annee'].strip()):
                w.note_creation_date = data[u'annee']
            w.comment = "\n".join(data[i] for i in ('notice', 'remarques') if data[i])
            w.save()
            self.stderr.write("Saved %s %s\n" % (n, unicode(w).encode('utf-8')))
            # FIXME: Improve image name heuristic
            pic = '/home/oaubert/tmp/michaux/%s.jpg' % data['cote'].lower().replace(' / ', '_').replace(' ', '_')
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

            if data['signature'].startswith('oui'):
                sig = Inscription()
                sig.nature = 'signature'
                pos = re.findall('\((.+)\)', data['signature'])
                if pos:
                    if ',' in pos[0]:
                        sig.position, sig.note = re.split('\s*,\s*', pos[0])
                    else:
                        sig.position = pos[0]
                sig.work = w
                sig.save()

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


    def handle(self, fname, **options):
        self.stdout.write("Importing from %s\n" % fname.encode('utf-8'))
        # FIXME: add proper option/arg passing instead of the name hack?
        if 'catalogue' in fname.lower():
            self._import_data_from_xls(fname)
        elif 'exposition' in fname.lower():
            self._import_exhibitions_from_xls(fname)
        else:
            self.stderr.write("Cannot determine file type\n")
        self.stdout.write("\nDone.\nDO NOT FORGET TO RUN rebuild_index !!!\n")
