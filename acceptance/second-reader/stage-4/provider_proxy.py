"""Timing instrumentation forwarding the real mock's answers; optional short5xx transport delay."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json,os,threading,time,urllib.request,urllib.error
events=[]
error_delay=0.0
lock=threading.Lock()
target=os.environ['PROBE_TARGET']
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):self.handle_request()
    def do_POST(self):self.handle_request()
    def do_DELETE(self):self.handle_request()
    def handle_request(self):
        global error_delay
        if self.path=='/__probe/error-delay':
            data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
            error_delay=float(data.get('seconds',0))
            self.send_response(204);self.end_headers();return
        if self.path=='/__probe/log':
            with lock:body=json.dumps({'calls':list(events),'now':time.monotonic()}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body);return
        if self.path=='/__probe/reset':
            with lock:events.clear()
            self.send_response(204);self.end_headers();return
        body=self.rfile.read(int(self.headers.get('Content-Length','0')))
        try:arguments=json.dumps(json.loads(body),sort_keys=True,separators=(',',':')) if body else ''
        except Exception:arguments='<unparseable>'
        event={'method':self.command,'path':self.path,'arguments':arguments,'started':time.monotonic()}
        headers={k:v for k,v in self.headers.items() if k.lower() not in ['host','content-length','connection','accept-encoding']}
        request=urllib.request.Request(target+self.path,data=body if body else None,headers=headers,method=self.command)
        try:
            try:response=urllib.request.urlopen(request,timeout=90)
            except urllib.error.HTTPError as exc:response=exc
            data=response.read()
            if response.status>=500 and error_delay:time.sleep(error_delay)
            event['answered']=time.monotonic();event['status']=response.status
            with lock:events.append(event)
            self.send_response(response.status)
            self.send_header('Content-Type',response.headers.get('Content-Type','application/json'))
            self.send_header('Content-Length',str(len(data)));self.end_headers()
            try:self.wfile.write(data)
            except OSError:pass
        except (urllib.error.URLError,OSError):
            event['answered']=time.monotonic();event['status']=None
            with lock:events.append(event)
            self.close_connection=True
ThreadingHTTPServer(('0.0.0.0',8080),Handler).serve_forever()
