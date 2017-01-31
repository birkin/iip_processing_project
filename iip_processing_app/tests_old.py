# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json, logging, os, time
import redis, rq
from django.test import TestCase
from iip_processing_app.lib.github_helper import GHHelper
from iip_processing_app.lib import processor
from iip_processing_app.lib.processor import Prepper, Puller


log = logging.getLogger(__name__)
TestCase.maxDiff = None
gh_helper = GHHelper()
puller = Puller()
prepper = Prepper()


# class RootUrlTest(TestCase):
#     """ Checks root urls. """

#     def test_root_url_no_slash(self):
#         """ Checks '/root_url'. """
#         response = self.client.get( '' )  # project root part of url is assumed
#         self.assertEqual( 302, response.status_code )  # permanent redirect
#         redirect_url = response._headers['location'][1]
#         self.assertEqual(  '/info/', redirect_url )

#     def test_root_url_slash(self):
#         """ Checks '/root_url/'. """
#         response = self.client.get( '/' )  # project root part of url is assumed
#         self.assertEqual( 302, response.status_code )  # permanent redirect
#         redirect_url = response._headers['location'][1]
#         self.assertEqual(  '/info/', redirect_url )


# class HBAuthParserTest(TestCase):
#     """ Checks parsing of http-basic-auth incoming info. """

#     def setUp(self):
#         self.test_hbauth_header = os.environ['IIP_PRC__TEST_HTTP_BASIC_AUTH_HEADER'].decode( 'utf-8' )
#         self.hbauth_good_username = os.environ['IIP_PRC__BASIC_AUTH_USERNAME'].decode( 'utf-8' )
#         self.hbauth_good_password = os.environ['IIP_PRC__BASIC_AUTH_PASSWORD'].decode( 'utf-8' )

#     def test_legit_info(self):
#         """ Checks parsing of username and password. """
#         self.assertEqual(
#             { 'received_username': self.hbauth_good_username, 'received_password': self.hbauth_good_password },
#             gh_helper.parse_http_basic_auth( self.test_hbauth_header )
#             )


# class GitHubResponseTest(TestCase):
#     """ Checks github response parsing. """

#     def test_examine_commits(self):
#         """ Checks extraction of files to process. """
#         commits_list = json.loads('''[
#             {
#               "added": [],
#               "author": {
#                 "email": "birkin.diana@gmail.com",
#                 "name": "Birkin James Diana",
#                 "username": "birkin"
#               },
#               "committer": {
#                 "email": "noreply@github.com",
#                 "name": "GitHub",
#                 "username": "web-flow"
#               },
#               "distinct": true,
#               "id": "88cb3c31a7bcec4adc0558fbff74347d0a9245e1",
#               "message": "test commit of comment.",
#               "modified": [
#                 "epidoc-files/abur0001.xml",
#                 "blah",
#                 "epidoc-files/aaa123.xml"
#               ],
#               "removed": [],
#               "timestamp": "2017-01-19T11:00:30-05:00",
#               "tree_id": "e45afe1e50d17e94e9bc2a26a35f4b3f3457bb55",
#               "url": "https://github.com/Brown-University-Library/iip-texts/commit/88cb3c31a7bcec4adc0558fbff74347d0a9245e1"
#             }
#           ]''')
#         self.assertEqual(
#             # ( [], [u'aaa123.xml', u'abur0001.xml'], [] ),  # added, modified, removed
#             ( [], [u'aaa123', u'abur0001'], [] ),  # added, modified, removed
#             gh_helper.examine_commits( commits_list )
#             )


class PrepperTest(TestCase):
    """ Checks processor.py functions. """

    def setUp(self):
        self.queue_name = unicode( os.environ['IIP_PRC__QUEUE_NAME'] )
        self.xml_dir = unicode( os.environ['IIP_PRC__CLONED_INSCRIPTIONS_PATH'] )

    def test_call_git_pull(self):
        """ Checks for successful pull. """
        self.assertEqual(
            0,  # 0 means no problems; 1 means a problem
            puller.call_git_pull()
            )

    def test_run_call_git_pull(self):
        """ Triggers processing; checks for no failed jobs. """
        ## confirm no processing jobs running
        q = rq.Queue( self.queue_name, connection=redis.Redis() )
        self.assertEqual( 0, len(q.jobs) )
        ##
        ## confirm no processing failed jobs
        failed_queue = rq.queue.get_failed_queue( connection=redis.Redis() )
        failed_count = 0
        for job in failed_queue.jobs:
            if job.origin == self.queue_name:
                failed_count += 1
        self.assertEqual( 0, failed_count )
        ##
        ## call processor.run_call_git_pull( to_process_dct )
        to_process_dct = {
            u'files_removed': [],
            u'files_updated': ['abur0001'],
            u'timestamp': u'2017-01-24 09:52:38.911009' }
        processor.run_call_git_pull( to_process_dct )
        ##
        ## confirm no processing failed jobs
        time.sleep( 2 )
        failed_queue = rq.queue.get_failed_queue( connection=redis.Redis() )
        failed_count = 0
        for job in failed_queue.jobs:
            if job.origin == self.queue_name:
                failed_count += 1
        self.assertEqual( 0, failed_count )

    # def test_transform_xml(self):
    #     """ Checks transform. """
    #     filepath = '{}/epidoc-files/abur0001.xml'.format( self.xml_dir )
    #     with open( filepath ) as f:
    #         xml_utf8 = f.read()
    #     source_xml = xml_utf8.decode( 'utf-8' )
    #     unicode_doc = prepper.make_initial_solr_doc( source_xml )
    #     self.assertEqual(
    #         True,
    #         u'Κύριε' in unicode_doc,
    #         )

    def test_update_status(self):
        """ Checks addition of display_status. """
        display_status = 'foo'
        initial_solr_xml = '''<?xml version="1.0" encoding="UTF-8"?><add><doc><field name="inscription_id">abur0001</field><field name="region">Judaea</field><field name="city">Bethennim</field><field name="placeMenu">Bethennim  (Judaea)</field><field name="placeMenu">Judaea</field><field name="place_found">[Bethennim, Judaea. Room A in church. ]
Judaea. Bethennim (Khirbet Abu Rish), in the church complex, Room A.
</field><field name="notAfter">0700</field><field name="notBefore">0300</field><field name="type">invocation</field><field name="language">grc</field><field name="language_display">Greek</field><field name="religion">christian</field><field name="physical_type">mosaic</field><field name="figure_desc">square mosaic</field><field name="transcription">&lt;span&gt;

               Κύριε
               [
                  Ἰησοῦ
                  Χριστέ μνήσθητ]ι &lt;br/&gt;το[ῦ δούλου σου [-----]
               ]ά&lt;br/&gt;λα[-----]
               [τοῦ]
               &lt;br/&gt;πρε[σβυτέρου καί π]άν-&lt;br/&gt;των [τῶν π]ροσκυ-&lt;br/&gt;νούντων ἐν τῴ&lt;br/&gt;τόπῳ τούτῳ καί&lt;br/&gt;τῶν καρποφο-&lt;br/&gt;ρούντων ἐν τῷ&lt;br/&gt;τόπῳ τούτῳ

&lt;/span&gt;

    </field><field name="transcription_search">

               Κε Κύριε

                  Ἰῦ Ἰησοῦ
                  Χέ Χριστέ μνήσθητι τοῦ δούλου σου
               άλα
               τοῦ
               πρεσβυτέρου καί πάν-των τῶν προσκυ-νούντων ἐν τῴτόπῳ τούτῳ καίτῶν καρποφο-ρούντων ἐν τῷτόπῳ τούτῳ
         </field><field name="translation">Lord Jesus Christ [remember your servant ...] the priest and all the pilgrims to
                    this place [or: all those who pray in this place] and those who contribute to
                    this place.</field><field name="translation_search">
            Lord Jesus Christ [remember your servant ...] the priest and all the pilgrims to
                    this place [or: all those who pray in this place] and those who contribute to
                    this place.
         </field><field name="diplomatic">&lt;span&gt;
            ΚΕ [ΙΥ ΧΕ ΜΝΗΣΘΗΤ]Ι&lt;br/&gt;ΤΟ[Υ ΔΟΥΛΟΥ ΣΟΥ] Α&lt;br/&gt;ΛΑ [-----]
               [ΤΟΥ]
               &lt;br/&gt;ΠΡΕ[ΣΒΥΤΕΡΟΥ ΚΑΙ Π]ΑΝ-&lt;br/&gt;ΤΩΝ [ΤΩΝ Π]ΡΟΣΚΥ-&lt;br/&gt;ΝΟΥΝΤΩΝ ΕΝ ΤΩ&lt;br/&gt;ΤΟΠΩ ΤΟΥΤΩ ΚΑΙ&lt;br/&gt;ΤΩΝ ΚΑΡΠΟΦΟ-&lt;br/&gt;ΡΟΥΝΤΩΝ ΕΝ ΤΩ&lt;br/&gt;ΤΟΠΩ ΤΟΥΤΩ

&lt;/span&gt;

    </field><field name="dimensions">h: 1 m; w: 1 m; d: unknown; let: N/A</field><field name="bibl">bibl=IIP-487.xml|nType=page|n=147-148</field><field name="bibl">bibl=IIP-544.xml|nType=page|n=339-358</field><field name="biblDiplomatic">bibl=IIP-487.xml|nType=page|n=147-148</field><field name="biblTranscription">bibl=IIP-487.xml|nType=page|n=147-148</field><field name="biblTranslation">bibl=IIP-487.xml|nType=page|n=147-148</field><field name="short_description">Bethennim (Khirbet Abu Rish). 300-700 CE. Mosaic in a square frame. Invocation.</field><field name="description">
            The mosaic was discovered in the earliest structure (Room A) of the church complex at Khirbet Abu Rish, a site nestled in the 'Anun valley, which separates the Hebron Mountains from the Judean Desert. The church complex comprises a large courtyard, water cisterns, wine-pressing installations, and several tombs. The sides of the mosaic in Room A are all one meter in length. The framed inscription is situated in the center of the mosaic. The letters are made out of black stones and placed on a white background. The inscription does not have spelling or grammatical errors. The only abbreviation used was that of the sacra nomina, or the sacred name, in the first line. The first five lines of the inscription are damaged. The text is a supplication, in which a person asks a supernatural deity to provide something. The individual who wrote the inscription is asking Jesus to remember a person who has passed away, whose name has not been preserved, and he/she is also asking for the remembrance of those who pray and contribute to this place. The inscription therefore showcases the significance of this place for Christians.
         </field></doc></add>'''
        updated_xml = prepper.update_status( display_status, initial_solr_xml )
        self.assertEqual(
            True,
            '<field name="display_status">foo</field>' in updated_xml
            )
