import pytest
from uid_to_acro import uid_to_acro

@pytest.mark.parametrize(
    "uid,acro",
    [
        ('dn','DN'),
        ('pj', 'Pj'),
        ('snp', 'Snp'),
        ('sn1', 'SN\u00A01'),
        ('sn1.1', 'SN\u00A01.1'),
        ('sn1.1:1', 'SN\u00A01.1:1'),
        ('pli-tv-bu-vb-pj1', 'Pli Tv Bu Vb Pj\u00A01'),
        ('pli-tv-bu-vb-pj1:1.1', 'Pli Tv Bu Vb Pj\u00A01:1.1'),
        ('an1.21-30', 'AN\u00A01.21–30'),
        
    ]
)

def test_url_to_acro(uid, acro):
    assert uid_to_acro(uid) == acro