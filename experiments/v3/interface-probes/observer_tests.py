"""Hermetic adversarial tests of trace admission and the local scripted transport."""
import copy
import io
import json
import pathlib
import sys
import unittest
import urllib.error
import urllib.request
from rpc import Rpc, validate_trace
from mock_responses import MockResponses


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


if __name__=='__main__':unittest.main(verbosity=2)
