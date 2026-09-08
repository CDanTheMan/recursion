"""Loopback-only scripted Responses endpoint. Never a real model or billing meter."""
import http.server
import json
import threading
import time

class MockResponses:
    def __init__(self):
        self.requests=[]; self.outputs=[]; self.lock=threading.Lock(); self.error=None;self.active_handlers=0
        fixture=self
        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version="HTTP/1.1"
            def log_message(self,*args): pass
            def do_GET(self):
                self.send_error(405,"fixture accepts only Responses POST")
            def do_POST(self):
                with fixture.lock:fixture.active_handlers+=1
                try:
                    self.connection.settimeout(3)
                    if self.path!="/v1/responses":raise ValueError("unadmitted request path")
                    size=int(self.headers.get("Content-Length","0"))
                    if not 0<size<=2*1024**2: raise ValueError("request byte bound")
                    body=json.loads(self.rfile.read(size))
                    with fixture.lock:
                        if len(fixture.requests)>=12: raise ValueError("request count bound")
                        index=len(fixture.requests)
                        fixture.requests.append({"index":index,"path":self.path,"body":body,"at":time.monotonic(),
                                                 "credential_header_present":any(k.lower() in {'authorization','cookie','x-api-key'} for k in self.headers)})
                        if not fixture.outputs:raise ValueError("unscripted provider request")
                        output=fixture.outputs.pop(0)
                    self.send_response(200); self.send_header("Content-Type","text/event-stream")
                    self.send_header("Connection","close"); self.end_headers(); self.close_connection=True
                    rid=f"fixture_response_{index}"
                    def emit(kind,**fields):
                        value={"type":kind,**fields}
                        self.wfile.write(("event: "+kind+"\ndata: "+json.dumps(value)+"\n\n").encode()); self.wfile.flush()
                    emit("response.created",response={"id":rid,"status":"in_progress","output":[]})
                    if output.get("delay"): time.sleep(output["delay"])
                    if output["kind"]=="tool":
                        item={"id":f"fc_{index}","type":"function_call","call_id":f"call_{index}","name":output["name"],"arguments":json.dumps(output.get("arguments",{})),"status":"completed"}
                        emit("response.output_item.added",output_index=0,item=item)
                        emit("response.output_item.done",output_index=0,item=item)
                    else:
                        text=output["text"]
                        item={"id":f"msg_{index}","type":"message","role":"assistant","status":"completed","content":[{"type":"output_text","text":text,"annotations":[]}]}
                        emit("response.output_item.added",output_index=0,item={**item,"content":[],"status":"in_progress"})
                        emit("response.output_text.delta",item_id=item["id"],output_index=0,content_index=0,delta=text)
                        emit("response.output_item.done",output_index=0,item=item)
                    emit("response.completed",response={"id":rid,"status":"completed","output":[item],"usage":{"input_tokens":10,"output_tokens":5,"total_tokens":15,"input_tokens_details":{"cached_tokens":0},"output_tokens_details":{"reasoning_tokens":0}}})
                except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError): pass
                except BaseException as exc:
                    fixture.error=type(exc).__name__+": "+str(exc)
                    try:self.send_error(400,"invalid fixture request")
                    except OSError:pass
                finally:
                    with fixture.lock:fixture.active_handlers-=1
        self.server=http.server.ThreadingHTTPServer(("127.0.0.1",0),Handler)
        self.server.daemon_threads=True
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)

    @property
    def url(self):return f"http://127.0.0.1:{self.server.server_port}/v1"
    def start(self):self.thread.start()
    def close(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=2)
        deadline=time.monotonic()+5
        while self.active_handlers and time.monotonic()<deadline:time.sleep(.01)
        if self.thread.is_alive() or self.active_handlers: self.error="mock handlers did not settle"
