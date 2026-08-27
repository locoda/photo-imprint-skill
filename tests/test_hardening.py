from __future__ import annotations
import json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1];BIN=ROOT/'bin'
def run(script,*args,ok=True):
    r=subprocess.run([sys.executable,str(BIN/script),*(str(a) for a in args)],text=True,capture_output=True)
    if ok and r.returncode!=0:raise AssertionError(f"{script} failed {r.returncode}\n{r.stdout}\n{r.stderr}")
    return r

def brief(name):
    return {'subject_priority':name,'thumbnail_read':name,'preserve_anchors':['anchor'],'abstract_or_omit':['minor detail'],
        'material_depth_cues':['depth cue'],'structural_lines':[{'element':'main direction','operation':'retain_but_simplify'}],
        'forbidden_inventions':['invented line']}

class HardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.w=Path(self.tmp.name)
        self.config=self.w/'resolved.json';run('resolve_config.py','--preset',ROOT/'presets/travel-food-journal.json','--output',self.config)
    def tearDown(self):self.tmp.cleanup()
    def test_generic_regression_fixture_covers_four_visual_cases(self):
        d=json.loads((ROOT/'tests/fixtures/generic-visual-cases.json').read_text())
        self.assertEqual([p['case'] for p in d['pages']],['open-sky cloud study','courtyard tree','glass facade','high-altitude city'])
        self.assertEqual({x['operation'] for x in d['revision_examples']},{'remove','retain_but_simplify','add_as_secondary','preserve_unchanged'})
    def test_default_config_includes_complete_workflow_and_style_contract(self):
        d=json.loads(self.config.read_text());wf=d['workflow_defaults'];style=d['profiles']['style']
        self.assertTrue(wf['qa']['page_level_required']);self.assertTrue(wf['qa']['set_level_required'])
        self.assertFalse(style['sample_style_contract_defaults']['generated_page_is_style_reference'])
        self.assertIn(style['plate_normalization']['mode'],{'paper-key-soft','alpha-required','disabled'})
    def test_clean_plate_removes_background_and_blocks_frame(self):
        config=json.loads(self.config.read_text());config['profiles']['composition']['canvas'].update(width=96,height=96);self.config.write_text(json.dumps(config))
        raw=self.w/'raw.png';im=Image.new('RGB',(96,96),'white');ImageDraw.Draw(im).line((25,48,70,48),fill='black',width=3);im.save(raw)
        out=self.w/'plate.png';rep=self.w/'plate.json';r=run('clean_plate.py','normalize','--input',raw,'--config',self.config,'--output',out,'--report',rep)
        with Image.open(out) as got:self.assertEqual(got.getpixel((0,0))[3],0);self.assertGreater(got.getpixel((48,48))[3],0)
        cfg=json.loads(self.config.read_text());cfg['profiles']['style']['plate_normalization']={'mode':'alpha-required','frame_policy':'forbid','max_corner_alpha_mean':8,'max_empty_area_noise_ratio':.01};strict=self.w/'strict.json';strict.write_text(json.dumps(cfg))
        framed=self.w/'framed.png';f=Image.new('RGBA',(96,96),(0,0,0,0));d=ImageDraw.Draw(f);d.rectangle((0,0,95,95),outline=(0,0,0,255),width=2);f.save(framed)
        blocked=run('clean_plate.py','validate','--input',framed,'--config',strict,'--report',self.w/'bad.json',ok=False)
        self.assertEqual(blocked.returncode,4)
    def make_plan_state_stage(self):
        plan=self.w/'plan.json';plan.write_text(json.dumps({'schema_version':'2.0.0','pages':[{'page':i,'production_brief':brief(str(i)),'render_prompt':'base'} for i in range(1,5)]}))
        final=self.w/'final';final.mkdir(exist_ok=True)
        for i in range(1,5):Image.new('RGB',(64,96),(241,235,221)).save(final/f'{i:02d}.webp')
        stage=self.w/'stage.json';run('package_verified.py','stage','--input',final,'--output',stage)
        state=self.w/'state.json';state.write_text(json.dumps({'status':'batch_approved','sample_page':1,'render_plan_path':str(plan.resolve()),'render_plan_sha256':__import__('hashlib').sha256(plan.read_bytes()).hexdigest(),'revision_ledger':[]}))
        return plan,state,stage,final
    def test_page_local_revision_preserves_unchanged_and_sample_change_resets_gate(self):
        plan,state,stage,_=self.make_plan_state_stage();changes=self.w/'changes.json';changes.write_text(json.dumps({'changes':[
            {'page':4,'domain':'page-content','operation':'retain_but_simplify','target':'major roads','instruction':'keep fewer wider directions'},
            {'page':4,'domain':'page-content','operation':'preserve_unchanged','target':'high viewpoint','instruction':'retain altitude'}]}))
        out=self.w/'revision.json';run('revision_scope.py','--render-plan',plan,'--state',state,'--staging-manifest',stage,'--changes',changes,'--request-text','roads should be more abstract','--impact','page-local','--output',out)
        scope=json.loads(out.read_text());self.assertEqual(scope['render_scope']['page_numbers'],[4]);self.assertEqual(scope['render_scope']['unchanged_pages'],[1,2,3])
        # fresh state: changing sample page must invalidate instead of emitting a local scope
        plan,state,stage,_=self.make_plan_state_stage();changes.write_text(json.dumps({'changes':[{'page':1,'domain':'page-content','operation':'remove','target':'border','instruction':'remove frame'}]}))
        blocked=run('revision_scope.py','--render-plan',plan,'--state',state,'--staging-manifest',stage,'--changes',changes,'--request-text','remove sample frame','--impact','page-local','--output',out,ok=False)
        self.assertEqual(blocked.returncode,5);self.assertEqual(json.loads(state.read_text())['status'],'gate_invalidated_by_revision')
        # non-local domain cannot be disguised as page-local
        plan,state,stage,_=self.make_plan_state_stage();changes.write_text(json.dumps({'changes':[{'page':4,'domain':'style-reference','operation':'preserve_unchanged','target':'reference technique','instruction':'change shared mark quality'}]}))
        blocked=run('revision_scope.py','--render-plan',plan,'--state',state,'--staging-manifest',stage,'--changes',changes,'--request-text','change the drawing method','--impact','page-local','--output',out,ok=False)
        self.assertEqual(blocked.returncode,5);self.assertEqual(json.loads(state.read_text())['status'],'gate_invalidated_by_revision')
    def test_one_page_batch_scope_is_explicitly_empty_after_approval(self):
        import hashlib
        plan=self.w/'one-plan.json';production=self.w/'one-plan.md';sample=self.w/'sample.png';plate=self.w/'sample-plate.png'
        production.write_text('plan');Image.new('RGBA',(8,8),(0,0,0,0)).save(sample);Image.new('RGBA',(8,8),(0,0,0,0)).save(plate)
        cfg_hash=hashlib.sha256(self.config.read_bytes()).hexdigest()
        plan.write_text(json.dumps({'resolved_config_lock':{'path':str(self.config.resolve()),'sha256':cfg_hash},'style_reference_locks':[],
            'sample_style_contract':{'generated_page_is_style_reference':False},'pages':[{'page':1}]}))
        state=self.w/'one-state.json';state.write_text(json.dumps({'status':'batch_approved','render_plan_path':str(plan.resolve()),
            'render_plan_sha256':hashlib.sha256(plan.read_bytes()).hexdigest(),'production_plan_path':str(production.resolve()),
            'production_plan_sha256':hashlib.sha256(production.read_bytes()).hexdigest(),'sample_path':str(sample.resolve()),
            'sample_sha256':hashlib.sha256(sample.read_bytes()).hexdigest(),'sample_plate_path':str(plate.resolve()),
            'sample_plate_sha256':hashlib.sha256(plate.read_bytes()).hexdigest(),'explicit_approval':{'actor':'user','text':'approved'}}))
        out=self.w/'one-batch.json';run('render_scope.py','--render-plan',plan,'--state',state,'--mode','batch','--output',out)
        self.assertEqual(json.loads(out.read_text())['render_scope']['page_numbers'],[])
    def test_qa_two_dimensions_block_then_verified_package_passes(self):
        plan,state,stage,final=self.make_plan_state_stage()
        qa=self.w/'qa';run('qa_images.py','--input',final,'--output',qa,'--config',self.config,'--render-plan',plan)
        checklist=qa/'review-checklist.json';blocked=run('review_checklist.py','validate','--checklist',checklist,ok=False);self.assertEqual(blocked.returncode,4)
        data=json.loads(checklist.read_text())
        for page in data['page_level_compliance']['pages']:
            for entry in page['checks'].values():entry.update(status='pass',evidence='manual full and phone review')
            page['status']='pass'
        data['page_level_compliance']['status']='pass'
        for entry in data['set_level_cohesion']['checks'].values():entry.update(status='pass',evidence='manual set review')
        data['set_level_cohesion']['status']='pass';checklist.write_text(json.dumps(data))
        run('review_checklist.py','validate','--checklist',checklist)
        z=self.w/'release.zip';manifest=self.w/'release.json';run('package_verified.py','package','--input',final,'--staging-manifest',stage,'--review-checklist',checklist,'--state',state,'--output',z,'--manifest-output',manifest)
        run('package_verified.py','verify','--zip',z)
        with zipfile.ZipFile(z,'a') as archive:archive.writestr('extra.txt','tamper')
        blocked=run('package_verified.py','verify','--zip',z,ok=False);self.assertEqual(blocked.returncode,4)

if __name__=='__main__':unittest.main()
