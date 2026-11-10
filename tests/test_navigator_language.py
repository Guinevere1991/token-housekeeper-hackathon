import copy
import hashlib
import json
import unittest
from unittest.mock import patch
from plugin import navigator, schemas, register


def payload(route='compare'):
    return dict(goal='比較原文，不要寄出', requested_route=route,
                sources=[dict(source_id='a', text='甲：不要寄出 <>&`\u202e'),
                         dict(source_id='b', text='乙：期限未知')],
                facts=[dict(text='保留限制', source_id='a', quote='不要寄出')],
                assumptions=[], constraints=['不要寄出'], unknowns=['期限'])


class NavigatorLanguageTests(unittest.TestCase):
    def test_default_equals_explicit_english_for_both_routes(self):
        for route in ('compare', 'extract_actions'):
            with self.subTest(route=route):
                p = payload(route)
                result = navigator.prepare(p)
                self.assertEqual(result, navigator.prepare(dict(p, language='en')))
                self.assertEqual(result['status'], 'data_ready')
                self.assertIn('# Task Navigator task card', result['markdown'])
                self.assertIn('### Sources and complete original text', result['markdown'])
                self.assertTrue(result['handoff']['reason'].isascii())
                self.assertTrue(result['handoff']['next_step'].isascii())
                self.assertTrue(result['handoff']['expected_output'].isascii())
                self.assertTrue(all(x.isascii() for x in result['handoff']['stop_conditions']))

    def test_chinese_opt_in_for_both_routes(self):
        for route in ('compare', 'extract_actions'):
            r = navigator.prepare(dict(payload(route), language='zh-CN'))
            self.assertIn('任务卡', r['markdown'])
            self.assertIn('调用方请求', r['handoff']['reason'])

    def test_original_evidence_and_input_are_unchanged(self):
        p = payload(); original = copy.deepcopy(p)
        for language in ('en', 'zh-CN'):
            r = navigator.prepare(dict(p, language=language))
            h = r['handoff']
            self.assertEqual(h['task_goal'], p['goal'])
            self.assertEqual(h['constraints'], p['constraints'])
            self.assertEqual(h['unknowns'], p['unknowns'])
            for src, ref in zip(p['sources'], h['source_refs']):
                self.assertEqual(src['text'], ref['text'])
                self.assertEqual(hashlib.sha256(src['text'].encode()).hexdigest(), ref['sha256'])
            c = h['facts'][0]['citation']
            self.assertEqual(c['quote'], '不要寄出')
            self.assertEqual(p['sources'][0]['text'][c['start']:c['end']], c['quote'])
        self.assertEqual(p, original)

    def test_escaping_is_preserved(self):
        for language in ('en', 'zh-CN'):
            md = navigator.prepare(dict(payload(), language=language))['markdown']
            for char in '<>&`\u202e':
                self.assertNotIn(char, md)
            self.assertIn('\\u202e', md)
            self.assertIn('\\u003c', md)

    def test_invalid_language_types_and_values_fail_closed(self):
        for value in ('fr', '', 'EN', None, [], {}, 1, 'x'*10000):
            with self.subTest(value=type(value).__name__):
                r = navigator.prepare(dict(payload(), language=value))
                self.assertEqual(r['status'], 'invalid_input')
                self.assertEqual(r['errors'], ['Language must be en or zh-CN.'])
                self.assertIsNone(r['handoff'])

    def test_invalid_payload_types_fail_closed(self):
        for value in (None, [], 3, 'text', {}):
            self.assertEqual(navigator.prepare(value)['status'], 'invalid_input')

    def test_unknown_key_still_rejected(self):
        self.assertEqual(navigator.prepare(dict(payload(), extra=True))['status'], 'invalid_input')

    def test_missing_material(self):
        p = payload(); del p['sources']
        r = navigator.prepare(p)
        self.assertEqual(r['status'], 'needs_input')
        self.assertIn('Data status: needs_input', r['markdown'])
        self.assertTrue(r['questions'][0].isascii())

    def test_unsupported_route(self):
        r = navigator.prepare(payload('execute'))
        self.assertEqual(r['status'], 'unsupported')
        self.assertTrue(r['markdown'].isascii())

    def test_source_and_quote_validation(self):
        p = payload(); p['facts'][0]['quote'] = 'invented'
        self.assertEqual(navigator.prepare(p)['status'], 'invalid_input')
        p = payload(); p['sources'][0]['text'] = 'x'*8193
        self.assertEqual(navigator.prepare(p)['status'], 'invalid_input')
        p = payload(); p['sources'].append(dict(source_id='c', text='third'))
        self.assertEqual(navigator.prepare(p)['status'], 'invalid_input')

    def test_output_limit_still_fails_closed(self):
        with patch.object(navigator, '_markdown', return_value='x'*131073):
            r = navigator.prepare(payload())
            self.assertEqual(r['status'], 'invalid_input')
            self.assertIsNone(r['handoff'])
            self.assertEqual(r['errors'], ['Prepared output exceeds the byte limit.'])

    def test_no_execution_authority(self):
        for language in ('en', 'zh-CN'):
            r = navigator.prepare(dict(payload(), language=language))
            self.assertFalse(r['execution_authorized'])
            self.assertEqual(r['capability_status'], 'unverified')
            self.assertEqual(r['downstream_status'], 'not_started')

    def test_schema_language_is_optional(self):
        self.assertNotIn('language', schemas.INPUT_SCHEMA['required'])
        self.assertEqual(schemas.INPUT_SCHEMA['properties']['language']['default'], 'en')
        self.assertEqual(schemas.INPUT_SCHEMA['properties']['language']['enum'], ['en', 'zh-CN'])

    def test_registered_handler_uses_new_default(self):
        class Context:
            def __init__(self): self.tools = {}; self.hooks = {}
            def register_tool(self, **kw): self.tools[kw['name']] = kw
            def register_skill(self, *a, **kw): pass
            def register_hook(self, name, handler): self.hooks[name] = handler
        ctx = Context(); register(ctx)
        r = json.loads(ctx.tools['navigator_prepare']['handler'](payload()))
        self.assertIn('# Task Navigator task card', r['markdown'])
        self.assertEqual(set(ctx.tools), {'navigator_prepare', 'housekeeper_prepare'})
        self.assertIsNone(ctx.hooks['pre_llm_call']('hello'))
        self.assertIn('housekeeper_prepare', ctx.hooks['pre_llm_call']('Please compare two reports'))

if __name__ == '__main__': unittest.main()
