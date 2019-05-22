import pytest
import re
import sys
import getpass
from urllib.request import urlopen
from hypothesis import given
from hypothesis import strategies as st
sys.path.append('.')
from utilities import ArgParser, get_pub_keys, is_key_imported, import_key, is_valid_web_url, get_github_keys_url, is_valid_username


PUBLIC_DIR = '/home/' + getpass.getuser() + '/public/'  # files will be copied to this dir


class TestArgParser(object):
    parser = ArgParser()
    valid_key = 'ssh-rsa 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 test@test.com'
    pub_key_file_path = 'tests/data/id_rsa.pub'
    auth_keys_file_path = 'tests/data/authorized_keys'
    github_keys = list(map(lambda x: x.decode('utf-8').replace('\n', ''), urlopen('https://github.com/viktorbarzin.keys').readlines()))

    @given(st.from_regex(re.compile(r'[a-zA-Z0-9]+'), fullmatch=True))  # random text - should not match any files
    def test_invalid_pub_key_file_raises(self, s):
        with pytest.raises(OSError):
            args = self.parser.parse_args(['--import', s])
            open(args.pub_key_arg, 'r')

    def test_valid_pub_key_file(self):
        args = self.parser.parse_args(['--import', 'tests/data/id_rsa.pub'])
        open(args.pub_key_arg, 'r')

    # @given(st.from_regex(re.compile(r'[a-zA-Z0-9]+')))
    # def test_get_pub_key_from_invalid_string(self, s):
    #     invalidate_url = 'test_test' + s
    #     extracted = get_pub_keys(invalidate_url)  # TODO: remove this hack
    #     assert extracted == []

    def test_get_pub_key_from_valid_string(self):
        # inputting valid pub key should be just returned
        result = get_pub_keys(self.valid_key)
        assert type(result) is list
        assert len(result) == 1
        assert result[0] == self.valid_key

    def test_get_pub_key_from_file(self):
        file_path = self.pub_key_file_path
        key = open(file_path, 'r').readline().replace('\n', '')
        result = get_pub_keys(file_path)
        assert type(result) is list
        assert len(result) == 1
        assert key == result[0]

    def test_get_pub_keys_from_valid_url(self):
        # maybe a better idea to mock this test
        pub_key_url = 'https://github.com/viktorbarzin.keys'
        # f = urlopen(pub_key_url)

        # real_key = f.read().decode('utf-8').replace('\n', '')
        assert sorted(self.github_keys) == sorted(get_pub_keys(pub_key_url))

    @given(st.text())
    def test_is_valid_web_url_invalid_url(self, s):
        assert not is_valid_web_url(s)

    def test_is_valid_web_url_valid_url(self):
        assert is_valid_web_url('http://google.com')

    def test_key_in_authorized_keys_when_present_key(self):
        import_key(self.valid_key, self.auth_keys_file_path)
        assert is_key_imported(self.valid_key, self.auth_keys_file_path)

    @given(st.from_regex(re.compile('[a-zA-Z0-9]+')))
    def test_key_in_authorized_keys_when_missing_key(self, s):
        assert not is_key_imported(s, self.auth_keys_file_path)

    def test_insert_key_inserts_it(self):
        before = open(self.auth_keys_file_path, 'r').readlines()
        key = 'ssh-rsa test_key_doesnt_matter_if_valid_or_not user@host'
        import_key(key, self.auth_keys_file_path)
        after = open(self.auth_keys_file_path, 'r').readlines()
        if key not in open(self.auth_keys_file_path, 'r').read():
            assert after != before
            assert len(after) == len(before) + 1
        secure_options = 'command="rsync --server -e.LsfxC . ' + PUBLIC_DIR + '",no-pty,no-agent-forwarding,no-port-forwarding'
        assert after[-1] == secure_options + ' ' + key + '\n'

    def test_get_pub_keys_from_empty_retunrs_empty(self):
        assert get_pub_keys(None) == []
        assert get_pub_keys('') == []

    def test_get_pub_keys_from_valid_string(self):
        # assume this string was downloaded - should get both keys
        keys_str = '''ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbXhblodPfaYUyWlI1Hvz2rLLDWi2YHZhbURyXt43g0lFEuTKa3tnWKiZKOIQWHr3WgT+EAlVgEgLjTXsIjHMrWvJcuGxPSm1Z/iXclHk1eYxPhi1/b1rQGK0PBknDivb8FqxQNbsMu6lOAVqcUuSVCSRr5tcB+NZoKVWLqjBsNuuQEaxu4dYkSbPmwTEZeSI8XnqRlVFAF9E8PuFgbl+G86SxB/RYKBiZpGr/T5ikrY2Rv68oSeL73kdPwrOj3HAmRwuiOTsSAFG4pZqRBzqL7vWlnndslXKJ9CCRzuvtWpU7G0e7uBL72b0QwgehIxQARyc8y4xSRGkCz9hofVcN
ssh-rsa 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
'''
        result = get_pub_keys(keys_str)
        assert type(result) is list
        assert len(result) == 2
        assert result[0] == keys_str.split('\n')[0]
        assert result[1] == keys_str.split('\n')[1]

    def test_get_github_url_from_invalid_username(self):
        assert get_github_keys_url('') is None
        assert get_github_keys_url(None) is None

    def test_get_keys_github_url_from_valid_username(self):
        username = 'viktorbarzin'
        expected_result = 'https://github.com/' + username + '.keys'
        assert expected_result == get_github_keys_url(username)

    def test_get_pub_keys_from_github_valid_user(self):
        username = 'viktorbarzin'
        # get url from username, get keys from url and test
        assert self.github_keys == get_pub_keys(get_github_keys_url(username))

    @given(st.from_regex(r'[^a-zA-Z0-9]+'))
    def test_is_valid_username_with_invalid_string(self, s):
        assert not is_valid_username(s)

    def test_is_valid_username_with_valid_string(self):
        assert is_valid_username('test')
        assert is_valid_username('another-test')
        assert is_valid_username('testing-is-fun')

    # def test_get_pub_keys_recognizes_github_username(self):
    #     username = 'viktorbarzin'
    #     # test if function corretly identifies string as username
    #     assert self.github_keys == get_pub_keys(username)


if __name__ == "__main__":
    TestArgParser().test_get_pub_keys_from_github_valid_user()
