import tempfile
import unittest
import check_mailq_filter as cmq_f


class CheckMQTest(unittest.TestCase):

    dummy_output = """
DD029602418    23128 Mon Dec 17 20:15:57  notification@facebookmail.com
(host alt1.gmail-smtp-in.l.google.com[108.177.14.27] said: 421-4.7.0 [178.32.59.28      15] Our system has detected an unusual rate of 421-4.7.0 unsolicited mail originating from your IP address. To protect our 421-4.7.0 users from spam, mail sent from your IP address has been temporarily 421-4.7.0 rate limited. Please visit 421-4.7.0  https://support.google.com/mail/?p=UnsolicitedRateLimitError to 421 4.7.0 review our Bulk Email Senders Guidelines. g8-v6si13825966lji.127 - gsmtp (in reply to end of DATA command))
                                         imaginary-mail-address@gmail.com

10A3460004A    23463 Sun Dec 16 10:09:30  notification@facebookmail.com
(host alt1.gmail-smtp-in.l.google.com[108.177.14.27] said: 421-4.7.0 [178.32.59.28      15] Our system has detected an unusual rate of 421-4.7.0 unsolicited mail originating from your IP address. To protect our 421-4.7.0 users from spam, mail sent from your IP address has been temporarily 421-4.7.0 rate limited. Please visit 421-4.7.0  https://support.google.com/mail/?p=UnsolicitedRateLimitError to 421 4.7.0 review our Bulk Email Senders Guidelines. h129si13351042lfh.115 - gsmtp (in reply to end of DATA command))
                                         imaginary-mail-address@gmail.com

1198860332E    22742 Thu Dec 13 21:01:54  notification@facebookmail.com
(host alt1.gmail-smtp-in.l.google.com[108.177.14.27] said: 421-4.7.0 [178.32.59.28      15] Our system has detected an unusual rate of 421-4.7.0 unsolicited mail originating from your IP address. To protect our 421-4.7.0 users from spam, mail sent from your IP address has been temporarily 421-4.7.0 rate limited. Please visit 421-4.7.0  https://support.google.com/mail/?p=UnsolicitedRateLimitError to 421 4.7.0 review our Bulk Email Senders Guidelines. d2si12570844lfh.138 - gsmtp (in reply to end of DATA command))
                                         imaginary-mail-address@gmail.com

195B4600E07     7246 Mon Dec 17 12:28:44  SRS0=r9XwDo=O2=carakrebs.com=cara@eigbox.net
(host alt1.gmail-smtp-in.l.google.com[108.177.14.27] said: 421-4.7.0 [178.32.59.28      15] Our system has detected that this message is 421-4.7.0 suspicious due to the nature of the content and/or the links within. 421-4.7.0 To best protect our users from spam, the message has been blocked. 421-4.7.0 Please visit 421 4.7.0  https://support.google.com/mail/answer/188131 for more information. g26-v6si12195940ljd.55 - gsmtp (in reply to end of DATA command))
                                         imaginary-mail-address@gmail.com
"""


    def test_empty_status(self):
        '''check test for Mail queue is empty works'''
        self.assertEqual(cmq_f.check_mailq('Mail queue is empty', '', 0, None, None),
                         (0, 0, 0))

    def test_normal_mailq_run(self):
        '''check mailq runs'''
        stdout, stderr, rc = cmq_f.run_mailq()
        self.assertTrue(isinstance(stdout, str))
        self.assertTrue(stdout != '')

    def test_mailq_nofilters(self):
        '''fake queued mails - no filters'''
        with tempfile.NamedTemporaryFile() as mq:
            mq.write(str.encode(CheckMQTest.dummy_output))
            mq.flush()
            rmq = cmq_f.run_mailq(['/usr/bin/cat', mq.name])
            total, excluded, included = cmq_f.check_mailq(*rmq, None, None)
        self.assertEqual(total, 4)
