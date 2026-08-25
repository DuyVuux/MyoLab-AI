#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,time,urllib.request
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root",default=".")
    ap.add_argument("--fixture",required=True)
    args=ap.parse_args()
    root=Path(args.repo_root).resolve()
    fixture=Path(args.fixture).resolve()
    if not fixture.is_file():
        print("fixture missing:",fixture);return 3

    spec=root/"apps/web-portal/e2e/auto-data-golden-real.spec.ts"
    source=spec.read_text(encoding="utf-8")
    if "page.route(" in source or ".route(" in source:
        print("FINAL E2E MUST NOT INTERCEPT API ROUTES");return 4

    env=os.environ.copy()
    api_port=int(env.get("UI_I4_API_PORT","8024"))
    api_base=env.get("NEXT_PUBLIC_AUTOMATION_API_BASE_URL") or f"http://127.0.0.1:{api_port}"
    api_proc=None
    if env.get("UI_I4_SKIP_API_SERVER")!="true":
        api_cmd=[
          os.environ.get("PYTHON", "python3"),
          "scripts/dev/run_ui_i4_api_server.py",
          "--host","127.0.0.1",
          "--port",str(api_port),
        ]
        api_proc=subprocess.Popen(api_cmd,cwd=root,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        deadline=time.time()+30
        healthy=False
        while time.time()<deadline:
            if api_proc.poll() is not None:
                break
            try:
                with urllib.request.urlopen(f"{api_base}/health",timeout=1) as response:
                    if response.status==200:
                        healthy=True
                        break
            except Exception:
                time.sleep(0.5)
        if not healthy:
            if api_proc.poll() is None:
                api_proc.terminate()
            print("UI-I4 API server did not become healthy")
            return 5
        if api_proc.poll() is not None:
            stdout,stderr=api_proc.communicate()
            print("UI-I4 API server exited early")
            print(stdout[-1000:])
            print(stderr[-1000:])
            return api_proc.returncode or 5

    env["UI_I4_NORAXON_SINGLE_CSV"]=str(fixture)
    env["NEXT_PUBLIC_AUTOMATION_API_BASE_URL"]=api_base
    env.setdefault("PLAYWRIGHT_BASE_URL", "http://127.0.0.1:3114")
    env.setdefault("PLAYWRIGHT_WEB_SERVER_COMMAND", "pnpm exec next dev --port 3114")
    cmd=["pnpm","--dir","apps/web-portal","exec","playwright","test","e2e/auto-data-golden-real.spec.ts"]
    try:
        proc=subprocess.run(cmd,cwd=root,env=env,text=True,capture_output=True)
    finally:
        if api_proc is not None:
            api_proc.terminate()
            try:
                api_proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                api_proc.kill()
                api_proc.communicate()

    fixture_sha256 = hashlib.sha256(fixture.read_bytes()).hexdigest()
    try:
        relative_fixture = fixture.relative_to(root)
    except ValueError:
        relative_fixture = None
    fixture_label = fixture.name
    if relative_fixture is not None and relative_fixture.parts[:2] == ("data-platform", "raw"):
        fixture_label = "REDACTED_RAW_HEALTHCARE_SOURCE"

    payload={
      "status":"PASS" if proc.returncode==0 else "FAIL",
      "browser_flow":"NORAXON_SINGLE_CSV_TO_QUALITY_EVIDENCE",
      "mock_route_interception":False,
      "fixture_path_recorded_as_basename":fixture_label,
      "fixture_sha256":fixture_sha256,
      "command":" ".join(cmd),
      "api_base_url":api_base,
      "exit_code":proc.returncode,
      "stdout_tail":proc.stdout[-4000:],
      "stderr_tail":proc.stderr[-4000:]
    }
    out=root/"qa-validation/evidence/ui-i4-golden-browser-e2e.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2),encoding="utf-8")
    print(out)
    return proc.returncode
if __name__=="__main__":raise SystemExit(main())
