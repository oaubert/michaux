# -*- coding: utf-8 -*-

import sys
import os
import re
import xlrd
import datetime

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from base.models import Work, Image, Inscription, Exhibition, BibliographyReference, ExhibitionInstance, Acquisition

class Command(BaseCommand):
    args = '[command] [param]'
    help = """Administration commands for Michaux catalogue
  works <xls file> : import the Michaux catalogue from an xls file
  exhibitions <xls file> : import the Michaux exhibition list
  ventes <xls files> : import the ventes publiques list
  gen_abbreviations : generate standard abbreviations for exhibitions
  pics <xls file> <dirname> : batch associate images
"""
    def _import_works_from_xls(self, filename):
        """Import from an xls file.
        """
        self.stdout.write("** Importing catalogue\n")
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
            w.note_technique = data[u'précisions sur la technique']
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
            if simple == '' or unicode(simple).strip() != data[u'Année'].strip():
                w.note_creation_date = data[u'Année']
            w.note = data['Notice']
            w.comment = data['Remarques']
            if data[u'Reproductions']:
                w.revision = u"\n".join(u"BIBLIO: %s" % b for b in data[u'Reproductions'].splitlines() if b.strip()) + u"\n"
            w.save()
            self.stderr.write(u"Saved %s %s\n" % (n, unicode(w)))
            # FIXME: Improve image name heuristic
            pic = '/home/oaubert/tmp/michaux/%s.jpg' % data['Cote'].lower().replace(' / ', '_').replace(' ', '_').replace('-', '_')
            if os.path.exists(pic.encode('utf-8')):
                self.stderr.write(u"   Copying image %s\n" % unicode(pic))
                i = Image()
                i.work = w
                i.photograph_name = 'Franck Leibovici'
                i.support = u'numérique'
                i.nature = u'référence'
                with open(pic, 'rb') as f:
                    i.original_image.save(os.path.basename(pic), File(f))
                i.save()

            if data[u'Signature'].startswith('oui'):
                sig = Inscription()
                sig.nature = 'signature'
                pos = re.findall('\((.+)\)', data[u'Signature'])
                if pos:
                    if ',' in pos[0]:
                        sig.position, sig.note = re.split('\s*,\s*', pos[0], 1)
                    else:
                        sig.position = pos[0]
                sig.work = w
                sig.save()

            note = data[u'Notes de Michaux']
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
                    if not ab:
                        # Blank line
                        continue
                    qs = Exhibition.objects.filter(abbreviation=ab)
                    if qs.count() == 1:
                        ex = qs[0]
                        # Found the exhibition
                        ei = ExhibitionInstance()
                        ei.work = w
                        ei.exhibition = ex
                        ei.save()
                        # Associate also "reprises"
                        for reprise in Exhibition.objects.filter(original=ex):
                            ei = ExhibitionInstance()
                            ei.work = w
                            ei.exhibition = reprise
                            ei.save()
                        msg = 'ok'
                    else:
                        msg = 'NOT FOUND'
                        notfound.append(ab)
                    self.stderr.write("   Exhibition %s... %s\n" % (ab.encode('utf-8'), msg))
                    if notfound:
                        w.revision += u"\n".join(u"EXPO: %s" % e for e in notfound if e) + u"\n"
                        w.save()

    def _import_ventes_from_xls(self, filename):
        """Import from an xls sellings file.
        """
        self.stdout.write("** Importing ventes\n")
        import xlrd
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)
        header = s.row_values(0)
        # côte	certificat	technique	précisions sur la technique	série	année	dimensions	support	support 1	support 2	support 3	signature	notes de michaux	notice	remarques	expositions	reproductions	propriétaire	image	date	lieu	catalogue	estimation	prix de vente

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
            w.old_references = data[u'côte'].strip()
            if data['certificat'] != '':
                cert = re.findall('(\d+)', data['certificat'])
                if cert:
                    w.certificate = long(cert[0])
            w.location = data['lieu'].strip()
            w.serie = data[u'série'].strip()
            # Remove whitespaces around commas
            w.technique = ",".join(re.split('\s*,\s*', data['technique'].strip()))
            w.note_technique = data[u'précisions sur la technique'].strip()
            w.support = data['support 1'].strip()
            w.support_details = data['support 2'].strip()
            w.note_support = data['support 3'].strip()
            try:
                d = data['dimensions'].strip("cm").strip()
                (l, h) = re.split('\s*x\s*', d)
                l = int(10 * float(l.replace(',', '.')))
                h = int(10 * float(h.replace(',', '.')))
                w.height = h
                w.width = l
            except ValueError:
                self.stderr.write(u"Missing height/width for %s\n" % data[u'côte'])
                w.height = 0
                w.width = 0

            annee = re.findall('(19\d\d)', data[u'année'])
            if annee:
                w.creation_date_start = long(annee[0])
            if annee == [] or unicode(long(annee[0])) != data[u'année'].strip():
                w.note_creation_date = data[u'année'].strip()

            w.note = data['notice'].strip()
            w.comment = data['remarques'].strip()
            if data[u'reproductions']:
                w.revision = u"\n".join(u"MISSINGBIBLIO: %s" % b for b in data[u'reproductions'].splitlines() if b.strip()) + u"\n"
            w.save()
            self.stderr.write(u"Saved %s %s\n" % (n, unicode(w)))

            # FIXME: Improve image name heuristic
            if data[u'image']:
                basename = os.path.splitext(data[u'image'].lower())[0]
                pic = '/home/oaubert/tmp/sdv/%s.jpg' % basename
                if os.path.exists(pic.encode('utf-8')):
                    self.stderr.write(u"   Copying image %s\n" % unicode(pic))
                    i = Image()
                    i.work = w
                    i.photograph_name = 'Franck Leibovici'
                    i.support = u'numérique'
                    i.nature = u'référence'
                    with open(pic.encode('utf-8'), 'rb') as f:
                        i.original_image.save(os.path.basename(pic.encode('ascii', 'ignore')), File(f))
                    i.save()
                else:
                    w.revision += u"MISSINGIMAGE: %s\n" %  data[u'image']
                    w.save()

            if data[u'signature'].startswith('oui'):
                sig = Inscription()
                sig.nature = 'signature'
                pos = re.findall('\((.+)\)', data[u'signature'])
                if pos:
                    if ',' in pos[0]:
                        sig.position, sig.note = re.split('\s*,\s*', pos[0], 1)
                    else:
                        sig.position = pos[0]
                sig.work = w
                sig.save()

            note = data[u'notes de michaux']
            if note:
                sig = Inscription()
                sig.nature = 'note'
                pos = re.findall('\(([hbcgd]{2})\)', note)
                if pos:
                    sig.position = pos[0]
                sig.note = note
                sig.work = w
                sig.save()

            # Process Acquisitions
            # propriétaire	date	lieu	catalogue	estimation	prix de vente
            if data['lieu'].strip():
                acq = Acquisition()
                acq.work = w
                acq.location = data['lieu'].strip()
                acq.public = True
                if data['date']:
                    try:
                        d = datetime.date.fromordinal(long(data['date']))
                        if d.year < 1900 and d.year > 0:
                            # Add 1900
                            d=datetime.date(1900 + d.year, d.month, d.day)
                        # Strange: there is a 1-year offset
                        acq.year = d.year - 1
                        acq.month = d.month
                        acq.day = d.day
                    except ValueError:
                        print "Error when parsing date"
                        pass
                acq.reference = data['catalogue'].strip()
                acq.estimation = data['estimation'].strip()
                if data['prix de vente']:
                    try:
                        acq.price = long(data['prix de vente'])
                    except ValueError:
                        pass
                acq.save()

            if data['expositions'].strip():
                notfound = []
                for ab in data['expositions'].split(';'):
                    ab = ab.strip().strip(",")
                    if not ab:
                        # Blank line
                        continue
                    qs = Exhibition.objects.filter(abbreviation=ab)
                    if qs.count() == 1:
                        ex = qs[0]
                        # Found the exhibition
                        ei = ExhibitionInstance()
                        ei.work = w
                        ei.exhibition = ex
                        ei.save()
                        # Associate also "reprises"
                        for reprise in Exhibition.objects.filter(original=ex):
                            ei = ExhibitionInstance()
                            ei.work = w
                            ei.exhibition = reprise
                            ei.save()
                        msg = 'ok'
                    else:
                        msg = 'NOT FOUND'
                        notfound.append(ab)
                    self.stderr.write(u"   Exhibition %s... %s\n" % (unicode(ab), unicode(msg)))
                    if notfound:
                        w.revision += u"\n".join(u"MISSINGEXPO: %s" % e for e in notfound if e)
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
        """Import exhibitions from an xls file.
        """
        self.stdout.write("** Importing exhibitions\n")
        import xlrd
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)
        header = s.row_values(0)

        def cleanup(s):
            if hasattr(s, 'strip'):
                return s.strip()
            else:
                return s
        for n in range(1, s.nrows - 1):
            row = s.row_values(n)
            data = dict(zip(header, (cleanup(i) for i in row)))
            e = Exhibition()
            title = data[u"titre de l'exposition"]
            # Extract additional info and put it in comment
            if '(' in title:
                m = re.match("^(.+?)\((.+?)\)(.*)$", title)
                if m:
                    l = m.groups()
                    e.comment = l[1]
                    title = l[0] + l[2]
            # Strip quotes/leading-trailing whitespace
            title = title.strip(u'«').strip(u'»').strip()
            e.title = title
            e.location =  data[u'Nom']
            e.location_type = data[u"lieu de l'exposition"]
            e.nature = data['Solo']
            # e.address =
            e.city = data['Ville']
            e.country = data['Pays']
            if data['Date']:
                e.start_year = long(data['Date'])
            else:
                e.start_year = 0

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
                # Strange: there is a 1-year offset
                e.start_year = d.year - 1
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
            self.stdout.write(str(n) + ": " + unicode(e).encode('utf-8') + "\n")

            for (num, nom, lieu, ville, pays, annee, start, end) in (
                (' (2)', 'Nom 2', "lieu d'exposition 2", 'Ville 2', 'Pays 2', 'Date 2', 'Date c', 'Date d'),
                (' (3)', 'Nom 3', "lieu d'exposition 3", 'Ville 3', 'Pays 3', 'Date 3', 'Date e', 'Date f'),
                (' (4)', 'Nom 4', "lieu d'exposition 4", 'Ville 4', 'Pays 4', 'Date 4', 'Date g', 'Date h'),
                ):
                if data[nom]:
                    # Reprises
                    e2 = Exhibition()
                    e2.original = e
                    e2.abbreviation = e.abbreviation + num
                    e2.title = e.title
                    e2.location = data[nom]
                    e2.location_type = data[lieu]
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

    def _generate_abbreviations(self, *p):
        """Generate standard abbreviations for exhibitions.

        This cannot be done during the import phase, since we need the
        old abbreviations to link them to the imported works.
        """
        self.stdout.write("** Generating abbreviations for exhibitions\n")
        for ex in Exhibition.objects.all():
            ab = u", ".join((ex.location, str(ex.start_year)))

            # Notice: we use __istartswith here since utf8 collation
            # rules on MySQL make the key case-insensitive.
            other = [ e.abbreviation
                      for e in Exhibition.objects.filter(abbreviation__istartswith=ab).exclude(pk=ex.pk) ]
            if other:
                # Another exhibition has the same abbrev. Add kw
                for suffix in u"abcdefghijklmnopqrstuvwxyz":
                    new = ab + suffix
                    if new in other:
                        # Already existing again
                        continue
                    # Not present, we have our new abbreviation
                    ab = new
                    break
                else:
                    self.stdout.write("PROBLEM: exhausted suffixes for %s" % ab)
                    return

            self.stdout.write(("  %s -> %s\n" % (ex.abbreviation, ab)).encode('utf-8'))
            ex.abbreviation = ab
            ex.save()
        # FIXME: migrate abbreviations to BibliographyReference table

    def _associate_images(self, filename, imgdir, *p):
        """Associate images from sourcedir.
        """
        book = xlrd.open_workbook(filename)
        s = book.sheet_by_index(0)

        correspondances = {}
        for n in range(1, s.nrows - 1):
            row = s.row_values(n)
            imgs = [ v for v in row[2:9] if v ]
            if imgs:
                correspondances[row[0].strip()] = imgs

        pics = {}
        for root, dirs, files in os.walk(imgdir):
            for n in files:
                pics[os.path.splitext(n.replace(" ", "").lower())[0]] = os.path.join(root, n)

        # Check all items
        for w in Work.objects.filter(image=None):
            ref = w.old_references
            nref = ref.replace(' ', '').replace('/', '').lower()
            for fname in correspondances.get(nref, []):
                pic = pics.get(fname.encode('utf-8'), "")
                if os.path.exists(pic):
                    self.stderr.write(unicode("   Copying image %s\n" % pic, 'utf-8'))
                    i = Image()
                    i.work = w
                    i.photograph_name = 'Franck Leibovici'
                    i.support = u'numérique'
                    i.nature = u'référence'
                    with open(pic, 'rb') as f:
                        i.original_image.save(unicode(os.path.basename(pic), 'ascii', 'ignore'), File(f))
                    i.save()

    def _check_images(self, imgdir, *p):
        """Check images from sourcedir.
        """
        pics = {}
        for root, dirs, files in os.walk(imgdir):
            for n in files:
                pics[os.path.splitext(n.replace(" ", "").lower())[0]] = os.path.join(root, n)
        print "Collection: %d pics" % len(pics)
        print "Checking %d Images" % Image.objects.count()

        found = []

        notfound = []
        # Check all items
        for i in Image.objects.all():
            name = os.path.splitext(os.path.basename(i.original_image.name))[0]
            if name in pics:
                found.append(name)
            else:
                notfound.append(name)
        print "Found %d matching pics" % len(found)
        print "Not found:\n\n" + "\n".join(notfound)
        
    def handle(self, *args, **options):
        if not args:
            self.print_help(sys.argv[0], sys.argv[1])
            return
        command = args[0]
        args = args[1:]
        dispatcher = {
            'works': self._import_works_from_xls,
            'exhibitions': self._import_exhibitions_from_xls,
            'gen_abbreviations': self._generate_abbreviations,
            'ventes': self._import_ventes_from_xls,
            'pics': self._associate_images,
            'check': self._check_images,
            }
        m = dispatcher.get(command)
        if m is not None:
            m(*args)
        else:
            raise CommandError("Unknown command")

        self.stdout.write("\nDone.\nDO NOT FORGET TO RUN rebuild_index !!!\n")
