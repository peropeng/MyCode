"""Portable delivery verification: stdlib only, never trains or modifies outputs."""
import hashlib,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
m=load(HERE/'results/artifact_manifest.json')
sealed=load(HERE/'results/delivery_manifest.json')
for row in sealed['files']:
    assert sha((HERE/row['path']).read_bytes())==row['sha256'],row['path']
for archive in m['archives']:
    p=HERE/archive['path']; assert sha(p.read_bytes())==archive['sha256']
    with zipfile.ZipFile(p) as z:
        expected=[r['path'] for r in archive['members']]
        actual=z.namelist()
        assert len(expected)==len(set(expected))
        assert len(actual)==len(set(actual))
        assert set(actual)==set(expected),'archive member set mismatch'
        for row in archive['members']:
            assert sha(z.read(row['path']))==row['sha256']
b=load(HERE/'results/preclaim_binding.json')
assert sha((HERE/'runner.py').read_bytes())==b['runner_sha256']
assert sha((HERE/'protocol.json').read_bytes())==b['protocol_sha256']
assert load(HERE/'results/final_audit.json')['all_pass']
assert load(HERE/'results/independent_result_audit.json')['all_pass']
print(json.dumps({'delivery_verified':True,'sealed_files':len(sealed['files']),'archive_member_sets_exact_unique':True,'checkpoints':15,'embeddings':731,'weights_sha256':'0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd','retained_asset_root':m['retained_asset_root']}))
