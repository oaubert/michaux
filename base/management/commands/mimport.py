# -*- coding: utf-8 -*-

import os
import re

from django.core.files import File
from django.core.management.base import BaseCommand

from base.models import Work, Image, Inscription

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
                    if ',' in pos:
                        sig.position, sig.note = re.split('\s*,\s*', pos[0])
                    else:
                        sig.position = pos[0]
                sig.work = w
                sig.save()

    def handle(self, fname, **options):
        self.stdout.write("Importing from %s\n" % fname.encode('utf-8'))
        self._import_data_from_xls(fname)
        self.stdout.write("\nDone.\nDO NOT FORGET TO RUN rebuild_index !!!\n")
