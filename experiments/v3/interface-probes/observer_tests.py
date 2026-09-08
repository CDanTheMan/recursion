"""Hermetic adversarial tests of trace admission and the local scripted transport."""
import copy
import io
import json
import pathlib
import sys
import unittest
import urllib.error
import urllib.request
import concurrent.futures
import datetime
import tempfile
from release import validate as validate_release, reserve
from rpc import Rpc, validate_trace
from mock_responses import MockResponses
from mock_chat import MockChat


class FakeProcess:
    def __init__(self, stdout=b'', stderr=b''):
        self.stdin=io.BytesIO(); self.stdout=io.BytesIO(stdout); self.stderr=io.BytesIO(stderr)


class ObserverTests(unittest.TestCase):
    def test_valid_response_and_raw_send_are_retained(self):
        process=FakeProcess(b'{"id":1,"result":{"ok":true}}\n')
        rpc=Rpc(process)
        rpc.send_raw(b'{invalid}\n')
        rpc.send({'id':1,'method':'fixture','params':{}})
        self.assertTrue(rpc.result(1)['result']['ok'])
        trace=rpc.finish();validate_trace(trace)
        raw=[e for e in trace['events'] if e['direction']=='send_raw']
        self.assertEqual(len(raw),1);self.assertEqual(raw[0]['payload']['utf8'],'{invalid}\n')
        self.assertEqual(sum(e['direction']=='send' for e in trace['events']),1)

    def test_stream_error_prevents_using_earlier_success(self):
        rpc=Rpc(FakeProcess(b'{"id":1,"result":{}}\nnot-json\n'))
        trace=rpc.finish()
        with self.assertRaises(RuntimeError):rpc.result(1)
        with self.assertRaises(ValueError):validate_trace(trace)

    def test_truncation_byte_and_event_bounds_fail_closed(self):
        for data, kwargs in [(b'{"a":1}',{'max_frame':4}),
                             (b'{}\n{}\n',{'max_total':4}),
                             (b'{}\n{}\n',{'max_events':1}),
                             (b'{"truncated":',{})]:
            trace=Rpc(FakeProcess(data),**kwargs).finish()
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):validate_trace(trace)

    def test_incomplete_and_reordered_receipts_rejected(self):
        valid=Rpc(FakeProcess(b'{}\n{}\n')).finish();validate_trace(valid)
        for field,value in [('stdout_ended',False),('reader_threads_alive',1),('stream_errors',['lost frame'])]:
            broken=copy.deepcopy(valid);broken[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_trace(broken)
        broken=copy.deepcopy(valid);broken['events'][1]['seq']=7
        with self.assertRaises(ValueError):validate_trace(broken)

    def test_oversized_outgoing_frame_is_not_sent(self):
        process=FakeProcess();rpc=Rpc(process,max_frame=4)
        with self.assertRaises(ValueError):rpc.send_raw(b'12345')
        self.assertEqual(process.stdin.getvalue(),b'')


class ScriptedEndpointTests(unittest.TestCase):
    def request(self,mock,path='/v1/responses'):
        return urllib.request.urlopen(urllib.request.Request(mock.url.removesuffix('/v1')+path,
            data=b'{"model":"public-fixture","input":[]}',headers={'Content-Type':'application/json'}),timeout=3)

    def test_expected_response_and_bounded_close(self):
        mock=MockResponses();mock.outputs.append({'kind':'text','text':'PUBLIC_FIXTURE'});mock.start()
        try:
            with self.request(mock) as response:body=response.read()
            self.assertIn(b'PUBLIC_FIXTURE',body);self.assertEqual(len(mock.requests),1)
            self.assertFalse(mock.requests[0]['credential_header_present'])
        finally:mock.close()
        self.assertIsNone(mock.error)

    def test_unscripted_and_wrong_path_rejected(self):
        for path in ['/v1/responses','/v1/unadmitted']:
            mock=MockResponses();mock.start()
            try:
                with self.assertRaises((urllib.error.HTTPError,ConnectionError)):
                    self.request(mock,path)
            finally:mock.close()
            self.assertIsNotNone(mock.error)


class ChatEndpointTests(unittest.TestCase):
    def get(self,mock,path):
        try:
            with urllib.request.urlopen(mock.url.removesuffix('/v1')+path,timeout=4) as r:return r.status
        except urllib.error.HTTPError as exc:return exc.code

    def test_exact_detection_negatives_and_no_query_alias(self):
        mock=MockChat();mock.start()
        try:
            for path in ['/api/v1/models','/api/tags','/v1/props','/props','/version']:
                self.assertEqual(self.get(mock,path),404)
            self.assertEqual(self.get(mock,'/v1/models'),200)
            self.assertEqual(self.get(mock,'/props?extra=1'),400)
        finally:mock.close()
        self.assertEqual(len(mock.requests),7);self.assertEqual(len(mock.errors),1);self.assertEqual(mock.active,0)

    def test_concurrent_get_bound_and_quiescent_close(self):
        mock=MockChat();mock.start()
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                codes=list(pool.map(lambda _:self.get(mock,'/props'),range(16)))
        finally:mock.close()
        self.assertEqual(len(mock.requests),12);self.assertEqual(codes.count(404),12)
        self.assertEqual(codes.count(400),4);self.assertEqual(mock.active,0)

    def test_enabled_tool_refuses_scripted_model_output(self):
        mock=MockChat();mock.start()
        try:
            req=urllib.request.Request(mock.url+'/chat/completions',data=json.dumps({'model':'public-fixture-model','stream':True,'tools':[{'name':'unadmitted'}]}).encode(),headers={'Authorization':'Bearer fixture-only','Content-Type':'application/json'})
            with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(req,timeout=3)
        finally:mock.close()
        self.assertEqual(mock.requests,[]);self.assertEqual(len(mock.errors),1);self.assertEqual(mock.active,0)


class PacketTests(unittest.TestCase):
    def test_closed_packet_cannot_reserve_or_create_a_lease(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);packet=root/'packet.json'
            packet.write_text(json.dumps({'id':'TEST-CLOSED'}))
            packet.with_name('packet-closure.json').write_text(json.dumps({'packet_id':'TEST-CLOSED','status':'closed'}))
            with self.assertRaisesRegex(ValueError,'closure receipt'):reserve(packet,root,'case',1)
            self.assertFalse((root/'private/packet-leases').exists())

    def test_prospective_release_and_fail_closed_mutants(self):
        now=datetime.datetime(2026,9,7,23,30,tzinfo=datetime.timezone.utc)
        packet={'status':'open','cases':[{'id':'case'}],'case_limit':2,'execution_limit':6,
                'at':(now-datetime.timedelta(minutes=1)).isoformat(),'deadline_utc':(now+datetime.timedelta(minutes=20)).isoformat()}
        validate_release(packet,'case',2,3,now)
        for field,value in [('status','closed'),('execution_limit',True),('execution_limit',7),
                            ('case_limit',3),('deadline_utc',(now-datetime.timedelta(seconds=1)).isoformat())]:
            bad=copy.deepcopy(packet);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):validate_release(bad,'case',2,3,now)
        for case,launches,used in [('unadmitted',1,0),('case',2,5),('case',True,0),('case',1,-1)]:
            with self.subTest(case=case,launches=launches,used=used),self.assertRaises(ValueError):validate_release(packet,case,launches,used,now)


if __name__=='__main__':unittest.main(verbosity=2)
