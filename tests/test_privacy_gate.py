import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from privacy import findings, verify


class PrivacyGateTests(unittest.TestCase):
    def test_rejects_private_files_paths_tokens_and_discussion(self):
        self.assertIn('private-file',findings('.git/config',b''))
        self.assertIn('private-file',findings('config/.env.local',b''))
        self.assertIn('private-file',findings('keys/signing.pem',b''))
        self.assertIn('personal-home',findings('doc.md',b'/Us'+b'ers/example/project'))
        self.assertIn('service-token',findings('data.json',b'gh' + b'p_' + b'A'*40))
        self.assertIn('discussion-record',findings('notes.md',b'Turn '+b'99'))
        self.assertIn('private-key',findings('data.txt',b'-----BEGIN '+b'PRIVATE KEY-----'))
        with self.assertRaises(RuntimeError):verify({'docs/notes.md':b'Turn '+b'99'})

    def test_keeps_public_attribution_and_identity(self):
        public=b'RHYTHMER OS / jazzy rhythmer / Based on Melodee by Kerem Kilic / AGPL-3.0-only'
        self.assertEqual(findings('README.md',public),[])
        self.assertEqual(verify({'README.md':public}),1)
