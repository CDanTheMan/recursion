"""Installed Codex protocol probe using a scripted loopback model, no credentials."""
import argparse
import datetime
import hashlib
import json
import pathlib
import time
import threading
import tomllib
import jsonschema
import sys
from win_process import Job, Process, minimal_env
from rpc import Rpc, validate_trace
from mock_responses import MockResponses
from release import reserve

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()

def configure(lab, run, url):
    home=run/"home"; fixture=run/"fixture"
    home.mkdir();fixture.mkdir()
    schema=json.loads((lab/"sources/codex-config.schema.json").read_text())
    flags=sorted(k for k,v in schema["properties"]["features"]["properties"].items() if v.get("type") != "object" and k != "tool_registry")
    lines=['model = "gpt-6-astra"','model_provider = "fixture"','model_reasoning_effort = "low"',
           'approval_policy = "never"','approvals_reviewer = "user"','sandbox_mode = "read-only"',
           'web_search = "disabled"','check_for_update_on_startup = false','project_doc_max_bytes = 0',
           'include_environment_context = false','cli_auth_credentials_store = "file"',
           '[agents]','enabled = false','[analytics]','enabled = false','[feedback]','enabled = false',
           '[skills]','include_instructions = false','[skills.bundled]','enabled = false',
           '[memories]','generate_memories = false','use_memories = false',
           '[features]',*[f'{key} = '+('true' if key in {'steer','collaboration_modes'} else 'false') for key in flags],
           '[tools.experimental_request_user_input]','enabled = true',
           '[model_providers.fixture]','name = "Scripted public fixture; no model"',
           'base_url = '+json.dumps(url),'wire_api = "responses"','requires_openai_auth = false',
           'supports_websockets = false','request_max_retries = 0','stream_max_retries = 0',
           'stream_idle_timeout_ms = 10000']
    content="\n".join(lines)+"\n"
    config=tomllib.loads(content);jsonschema.validate(config,schema)
    (home/"config.toml").write_text(content,encoding="utf-8")
    env=minimal_env()
    for key in ("HOME","USERPROFILE","CODEX_HOME"):env[key]=str(home)
    for key in ("APPDATA","LOCALAPPDATA","TEMP","TMP"):
        d=run/key.lower();d.mkdir();env[key]=str(d)
    env.update({"HTTP_PROXY":"http://127.0.0.1:9","HTTPS_PROXY":"http://127.0.0.1:9","ALL_PROXY":"http://127.0.0.1:9","NO_PROXY":"127.0.0.1,localhost"})
    return home,fixture,env

def thread_params(fixture, tools=None):
    result={"cwd":str(fixture),"model":"gpt-6-astra","modelProvider":"fixture",
            "sandbox":"read-only","approvalPolicy":"never","approvalsReviewer":"user",
            "environments":[],"allowProviderModelFallback":False,"ephemeral":False,
            "baseInstructions":"You are a public, deterministic protocol test fixture. Follow only the fixture task.",
            "developerInstructions":"No external resources, files, shell, helpers or private context. Only the explicitly supplied fixture tool is permitted."}
    if tools is not None:result["dynamicTools"]=tools
    return result

def run(lab, executable, mode, packet):
    if sys.flags.optimize: raise RuntimeError('Probe oracles require assertions enabled')
    release=reserve(packet,lab,'codex-'+mode,2 if mode=='interaction' else 1)
    run_dir=lab/"private"/("codex-"+mode+"-"+datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S%f"))
    run_dir.mkdir()
    mock=MockResponses(); mock.start()
    job=Job();process=rpc=None;outcomes=[];failure=None
    try:
        home,fixture,env=configure(lab,run_dir,mock.url)
    except BaseException as exc:
        job.close();mock.close()
        failure=type(exc).__name__+": "+str(exc)
        (run_dir/"setup-failure.json").write_text(json.dumps({"at":now(),"failure":failure,"process_started":False},indent=2)+"\n")
        return {"result":str(run_dir/"setup-failure.json"),"failure":failure,"requests":0,"active_owned_processes":0}
    admission={"at":now(),"packet_release":release,"kind":"installed-harness-scripted-model","model_inference":False,"credentials":"absent",
               "executable_sha256":sha(executable),"config_sha256":sha(home/"config.toml"),
               "tooling":{p.name:sha(p) for p in pathlib.Path(__file__).parent.glob('*.py')},
               "provider_destination":mock.url,"network_boundary":"configured loopback provider and rejecting ambient HTTP proxies; not OS egress certification",
               "fixture":str(fixture),"effects":"owned process, local fixture state and loopback HTTP only",
               "max_seconds":120,"max_provider_requests":12,"max_frame_bytes":2097152,"max_stream_bytes":16777216,
               "max_processes":16,"job_memory_bytes":2147483648,"cleanup":"terminate only this owned Job and close local listener"}
    (run_dir/"admission.json").write_text(json.dumps(admission,indent=2)+"\n")
    (run_dir/"tooling").mkdir()
    for p in pathlib.Path(__file__).parent.glob('*.py'):(run_dir/"tooling"/p.name).write_bytes(p.read_bytes())
    started=time.monotonic()
    timed_out=threading.Event()
    def expire():
        timed_out.set()
        job.terminate()
    watchdog=threading.Timer(120,expire);watchdog.daemon=True;watchdog.start()
    try:
        process=Process([str(executable),"app-server","--stdio","--strict-config"],fixture,env,job)
        rpc=Rpc(process)
        init=rpc.request("initialize",{"clientInfo":{"name":"public_fixture_probe","version":"1"},"capabilities":{"experimentalApi":True}})
        rpc.send({"method":"initialized","params":{}})
        outcomes.append({"check":"initialize","result":init})
        account=rpc.request("account/read",{"refreshToken":False})
        assert account["result"]["account"] is None, "unexpected inherited account"
        config=rpc.request("config/read",{"cwd":str(fixture),"includeLayers":True})
        outcomes.append({"check":"effective_config","result":config})
        tools=[{"type":"function","name":"fixture_barrier","description":"Wait for the public fixture controller.","inputSchema":{"type":"object","properties":{},"additionalProperties":False}}]
        params=thread_params(fixture,tools)
        jsonschema.validate(params,json.loads((lab/"sources/codex-schema-experimental/v2/ThreadStartParams.json").read_text()))
        thread=rpc.request("thread/start",params); tid=thread["result"]["thread"]["id"]
        outcomes.append({"check":"thread_start","result":thread})
        if mode=="calibration":
            mock.outputs.append({"kind":"text","text":"PUBLIC_FIXTURE_COMPLETE"})
            turn=rpc.request("turn/start",{"threadId":tid,"input":[{"type":"text","text":"Reply PUBLIC_FIXTURE_COMPLETE."}]})
            uid=turn["result"]["turn"]["id"]
            done=rpc.event("turn/completed",match=lambda x:x["params"]["turn"]["id"]==uid)
            outcomes.append({"check":"completed","result":done})
            assert done["params"]["turn"]["status"]=="completed",done
            assert any(e["direction"]=="receive" and 'PUBLIC_FIXTURE_COMPLETE' in json.dumps(e["payload"]) for e in rpc.events)
        elif mode=="interaction":
            # Real installed dispatcher and turn state; every model output is scripted.
            mock.outputs.extend([{"kind":"tool","name":"fixture_barrier"},{"kind":"text","text":"PUBLIC_OWNER_STEER_B"}])
            turn=rpc.request("turn/start",{"threadId":tid,"input":[{"type":"text","text":"Call fixture_barrier before answering."}]})
            first=turn["result"]["turn"]["id"]
            barrier=rpc.event("item/tool/call")
            wrong=rpc.request("turn/steer",{"threadId":tid,"expectedTurnId":"public_stale_turn","input":[{"type":"text","text":"PUBLIC_STALE_MUST_NOT_APPEAR"}]},allow_error=True)
            assert "error" in wrong,wrong
            outcomes.append({"check":"stale_steer_rejected","result":wrong})
            fork_inflight=rpc.request("thread/fork",{"threadId":tid,"lastTurnId":first},allow_error=True)
            outcomes.append({"check":"inflight_fork_result","result":fork_inflight})
            assert "error" in fork_inflight,fork_inflight
            steer=rpc.request("turn/steer",{"threadId":tid,"expectedTurnId":first,"input":[{"type":"text","text":"Use PUBLIC_OWNER_STEER_B."}]})
            outcomes.append({"check":"active_steer","result":steer})
            rpc.send({"id":barrier["id"],"result":{"contentItems":[{"type":"inputText","text":"READY"}],"success":True}})
            done=rpc.event("turn/completed",match=lambda x:x["params"]["turn"]["id"]==first)
            assert done["params"]["turn"]["status"]=="completed",done
            assert "PUBLIC_OWNER_STEER_B" in json.dumps(mock.requests[-1]["body"])
            assert "PUBLIC_STALE_MUST_NOT_APPEAR" not in json.dumps(mock.requests)
            outcomes.append({"check":"steer_reached_same_turn_provider_input","result":done})
            question={"questions":[{"id":"public_color","header":"Color","question":"Choose the public fixture color.","options":[{"label":"blue","description":"Use blue."},{"label":"red","description":"Use red."}]}]}
            plan={"mode":"plan","settings":{"model":"gpt-6-astra","reasoning_effort":"low","developer_instructions":None}}
            mock.outputs.append({"kind":"tool","name":"request_user_input","arguments":question})
            turn=rpc.request("turn/start",{"threadId":tid,"input":[{"type":"text","text":"Ask the public color question."}],"collaborationMode":plan})
            interrupted=turn["result"]["turn"]["id"]
            old_question=rpc.event("item/tool/requestUserInput")
            assert old_question["params"]["isBlocking"] is True,old_question
            interrupt=rpc.request("turn/interrupt",{"threadId":tid,"turnId":interrupted})
            terminal=rpc.event("turn/completed",match=lambda x:x["params"]["turn"]["id"]==interrupted)
            outcomes.append({"check":"blocking_question_interrupt","request":old_question,"ack":interrupt,"terminal":terminal})
            assert terminal["params"]["turn"]["status"]=="interrupted",terminal
            mock.outputs.extend([{"kind":"tool","name":"request_user_input","arguments":question},{"kind":"text","text":"PUBLIC_BLUE_CONFIRMED"}])
            turn=rpc.request("turn/start",{"threadId":tid,"input":[{"type":"text","text":"Ask the color question again."}],"collaborationMode":plan})
            current=turn["result"]["turn"]["id"]
            current_question=rpc.event("item/tool/requestUserInput")
            assert current_question["id"]!=old_question["id"]
            assert current_question["params"]["threadId"]==tid and current_question["params"]["turnId"]==current
            assert old_question["params"]["threadId"]==tid and old_question["params"]["turnId"]==interrupted
            requests_before=len(mock.requests)
            rpc.send({"id":old_question["id"],"result":{"answers":{"public_color":{"answers":["red"]}}}})
            time.sleep(.3)
            assert len(mock.requests)==requests_before,"late old answer released current waiter"
            outcomes.append({"check":"late_old_answer_did_not_release_current_waiter","observation_window_s":.3,"provider_requests_before":requests_before,"provider_requests_after":len(mock.requests)})
            rpc.send({"id":current_question["id"],"result":{"answers":{"public_color":{"answers":["blue"]}}}})
            terminal=rpc.event("turn/completed",match=lambda x:x["params"]["turn"]["id"]==current)
            assert terminal["params"]["turn"]["status"]=="completed",terminal
            answer_outputs={item.get("call_id"):item.get("output") for item in mock.requests[-1]["body"]["input"] if item.get("type")=="function_call_output"}
            assert json.loads(answer_outputs[current_question["params"]["itemId"]])["answers"]["public_color"]["answers"]==["blue"]
            started_turns=[e["payload"]["params"]["turn"]["id"] for e in rpc.events if e["direction"]=="receive" and isinstance(e["payload"],dict) and e["payload"].get("method")=="turn/started"]
            assert started_turns==[first,interrupted,current],started_turns
            outcomes.append({"check":"current_question_answer_completed","terminal":terminal})
            fork=rpc.request("thread/fork",{"threadId":tid,"lastTurnId":first,"cwd":str(fixture),"modelProvider":"fixture","model":"gpt-6-astra","approvalPolicy":"never","approvalsReviewer":"user","sandbox":"read-only"})
            forkid=fork["result"]["thread"]["id"];assert forkid!=tid
            history=rpc.request("thread/read",{"threadId":forkid,"includeTurns":True})
            assert "PUBLIC_OWNER_STEER_B" in json.dumps(history),history
            assert "PUBLIC_BLUE_CONFIRMED" not in json.dumps(history),history
            assert history["result"]["thread"]["forkedFromId"]==tid
            assert [t["id"] for t in history["result"]["thread"]["turns"]]==[first]
            outcomes.append({"check":"fork_boundary_history","result":history})
            # Crash the actual owned server, then reuse only this fixture's state.
            job.terminate();process.wait();oldtrace=rpc.finish();validate_trace(oldtrace);oldaccount=job.accounting()
            assert oldaccount["ActiveProcesses"]==0
            process.close();job.close();job=Job()
            outcomes.append({"check":"crash_process_settlement","job":oldaccount,"trace":oldtrace})
            process=Process([str(executable),"app-server","--stdio","--strict-config"],fixture,env,job);rpc=Rpc(process)
            rpc.request("initialize",{"clientInfo":{"name":"public_fixture_probe","version":"1"},"capabilities":{"experimentalApi":True}});rpc.send({"method":"initialized","params":{}})
            resumed=rpc.request("thread/resume",{"threadId":tid,"cwd":str(fixture),"model":"gpt-6-astra","modelProvider":"fixture","sandbox":"read-only","approvalPolicy":"never","approvalsReviewer":"user"})
            assert resumed["result"]["thread"]["id"]==tid
            history=rpc.request("thread/read",{"threadId":tid,"includeTurns":True})
            assert "PUBLIC_BLUE_CONFIRMED" in json.dumps(history)
            assert [(t["id"],t["status"]) for t in history["result"]["thread"]["turns"]]==[(first,"completed"),(interrupted,"interrupted"),(current,"completed")]
            outcomes.append({"check":"post_crash_history_resume","result":history})
            # No inference is started after resume: environment capability persistence
            # and fresh-turn grant reapplication remain a separate admission question.
        else: raise ValueError("unimplemented bounded case")
        assert mock.error is None,mock.error
        assert len(mock.requests)==(1 if mode=="calibration" else 5)
        for req in mock.requests:
            assert req["path"]=="/v1/responses" and req["body"]["model"]=="gpt-6-astra" and not req["credential_header_present"]
            assert {t.get("name",t.get("type")) for t in req["body"].get("tools",[])}=={"update_plan","request_user_input","skills","fixture_barrier"}
    except BaseException as exc:
        failure=type(exc).__name__+": "+str(exc)
    finally:
        watchdog.cancel()
        watchdog.join(timeout=5)
        job.terminate()
        if process:
            try:process.wait(10)
            except BaseException as exc:failure=(failure or "")+" cleanup: "+str(exc)
        trace=rpc.finish() if rpc else None
        accounting=job.accounting()
        if process:process.close()
        job.close();mock.close()
        try:
            validate_trace(trace)
            if accounting["ActiveProcesses"] or mock.error or timed_out.is_set() or watchdog.is_alive():raise ValueError("owned process, timeout or mock observer failed cleanup: "+str(mock.error))
        except BaseException as exc:failure=(failure or "")+" final observation: "+str(exc)
        report={"started_at":admission["at"],"ended_at":now(),"elapsed_s":round(time.monotonic()-started,6),
                "mode":mode,"failure":failure,"outcomes":outcomes,"trace":trace,
                "scripted_endpoint_requests":mock.requests,"actual_model_calls":0,"simulated_usage":True,
                "cleanup_job_accounting":accounting,"watchdog_fired":timed_out.is_set(),"admission_sha256":sha(run_dir/"admission.json")}
        (run_dir/"result.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return {"result":str(run_dir/"result.json"),"failure":failure,"requests":len(mock.requests),"active_owned_processes":accounting["ActiveProcesses"]}

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--lab",type=pathlib.Path,required=True);parser.add_argument("--executable",type=pathlib.Path,required=True);parser.add_argument("--mode",choices=["calibration","interaction"],default="calibration")
    parser.add_argument('--packet',type=pathlib.Path,required=True)
    args=parser.parse_args();result=run(args.lab,args.executable,args.mode,args.packet);print(json.dumps(result));raise SystemExit(bool(result["failure"]))
