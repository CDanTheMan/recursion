"""Public Chat Completions fixture for the real Hermes agent; never calls a model."""
import http.server
import json
import threading
import time


class MockChat:
    def __init__(self):
        self.requests=[];self.errors=[];self.active=0;self.lock=threading.Lock();self.stop=threading.Event()
        owner=self
        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version='HTTP/1.0'
            def log_message(self,*args):pass
            def setup(self):
                super().setup();self.connection.settimeout(3)
            def handle(self):
                with owner.lock:owner.active+=1
                try:super().handle()
                finally:
                    with owner.lock:owner.active-=1
            def do_GET(self):
                negative={'/api/v1/models','/api/tags','/v1/props','/props','/version'}
                with owner.lock:
                    if len(owner.requests)>=12:
                        owner.errors.append('request limit exceeded');self.send_error(400);return
                    if self.path in negative:
                        owner.requests.append({'method':'GET','path':self.path,'status':404,'purpose':'pinned local-server detection negative'})
                    elif self.path=='/v1/models':
                        owner.requests.append({'method':'GET','path':self.path})
                    else:
                        owner.errors.append('unadmitted GET path: '+self.path)
                        owner.requests.append({'method':'GET','path':self.path,'rejected':True})
                if self.path in negative:
                    self.send_error(404);return
                if self.path!='/v1/models':
                    self.send_error(400);return
                body=json.dumps({'object':'list','data':[{'id':'public-fixture-model','object':'model','created':0,'owned_by':'fixture'}]}).encode()
                self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
            def do_POST(self):
                try:
                    length=int(self.headers.get('Content-Length','0'))
                    if self.path!='/v1/chat/completions' or length<=0 or length>2*1024**2:raise ValueError('unadmitted POST path or size')
                    body=json.loads(self.rfile.read(length))
                    if body.get('tools'):raise ValueError('unexpected enabled tools')
                    if body.get('model')!='public-fixture-model' or not body.get('stream'):raise ValueError('unexpected model or streaming mode')
                    if self.headers.get('Authorization')!='Bearer fixture-only':raise ValueError('unexpected authentication configuration')
                    with owner.lock:
                        number=1+sum(r['method']=='POST' for r in owner.requests)
                        if number>2 or len(owner.requests)>=12:raise ValueError('script/request limit exceeded')
                        owner.requests.append({'method':'POST','path':self.path,'body':body,'auth':'public dummy fixture','script_index':number})
                    self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Cache-Control','no-cache');self.end_headers()
                    def send(delta,finish=None,usage=None):
                        payload={'id':'public-chat-'+str(number),'object':'chat.completion.chunk','created':0,'model':'public-fixture-model',
                                 'choices':[] if usage else [{'index':0,'delta':delta,'finish_reason':finish}]}
                        if usage:payload['usage']=usage
                        self.wfile.write(('data: '+json.dumps(payload)+'\n\n').encode());self.wfile.flush()
                    send({'role':'assistant','content':'PUBLIC_HISTORY_COMPLETE' if number==1 else 'PUBLIC_INTERRUPT_PARTIAL '})
                    if number==2:
                        for i in range(100):
                            if owner.stop.wait(.05):break
                            send({'content':'public-token '})
                    send({},'stop');send({},usage={'prompt_tokens':11,'completion_tokens':7,'total_tokens':18})
                    self.wfile.write(b'data: [DONE]\n\n');self.wfile.flush()
                except (BrokenPipeError,ConnectionResetError):
                    # Expected when the interrupted real client closes its stream.
                    pass
                except BaseException as exc:
                    owner.errors.append(type(exc).__name__+': '+str(exc))
                    try:self.send_error(400)
                    except OSError:pass
        class Server(http.server.ThreadingHTTPServer):
            daemon_threads=False
            block_on_close=True
        self.server=Server(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
    @property
    def url(self):return 'http://127.0.0.1:'+str(self.server.server_port)+'/v1'
    def start(self):self.thread.start()
    def close(self):
        self.stop.set();self.server.shutdown();self.server.server_close();self.thread.join(3)
        if self.thread.is_alive() or self.active:self.errors.append('mock handlers did not settle')
