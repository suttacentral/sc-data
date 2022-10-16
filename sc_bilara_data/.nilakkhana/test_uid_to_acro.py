import pytest
from uid_to_acro import uid_to_acro

@pytest.mark.parametrize(
    "uid,acro",
    [
        ('dn','DN'),
        ('pj', 'Pj'),
        ('snp', 'Snp'),
        ('sn1', 'SN 1'),
        ('sn1.1', 'SN 1.1'),
        ('sn1.1:1', 'SN 1.1:1'),
        ('pli-tv-bu-vb-pj1', 'Pli Tv Bu Vb Pj 1'),
        ('pli-tv-bu-vb-pj1:1.1', 'Pli Tv Bu Vb Pj 1:1.1'),
        ('an1.21-30', 'AN 1.21–30'),
        
    ]
)

def test_url_to_acro(uid, acro):
    assert uid_to_acro(uid) == acro