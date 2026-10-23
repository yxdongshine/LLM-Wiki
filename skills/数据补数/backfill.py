#!/usr/bin/env python3
"""
数据补数脚本 - 数据资产平台 runManualTask 逐日触发
用法: python3 backfill.py --start 2026-08-20 --end 2026-08-28 --task-id 1902295609584566274 --project-id 1733358219907629058 --name P_SPARK_HA17_USERMEMBER_DAYDATA_SUMMARY_DD_SS --jwt <JWT_TOKEN> --cookie <AUTH_COOKIE> [--interval 20]
凭据从环境变量或命令行参数读取，不在脚本中硬编码。
"""
import argparse, subprocess, time, datetime, sys, os, json

def generate_dates(start, end):
    from datetime import timedelta
    s = datetime.datetime.strptime(start, '%Y-%m-%d')
    e = datetime.datetime.strptime(end, '%Y-%m-%d')
    dates = []
    while s <= e:
        dates.append(s.strftime('%Y-%m-%d'))
        s += timedelta(days=1)
    return dates

def run_one(bd, jwt, cookie, task_id, project_id, name, tenant_id='1001', user_id='641', env=5):
    payload = json.dumps({
        "_t": int(time.time() * 1000),
        "tenantId": tenant_id,
        "userId": user_id,
        "projectId": project_id,
        "projectIds": [project_id],
        "env": env,
        "regionCode": "default",
        "businessDateEnd": bd,
        "businessDateStart": bd,
        "isBusinessTimeAes": True,
        "isParallel": False,
        "name": name,
        "taskId": task_id
    }, ensure_ascii=False)

    result = subprocess.run([
        'curl', '-s',
        'https://dataasset-xc.cmft.com/api/ops/circleTask/runManualTask',
        '-H', 'Content-Type: application/json; charset=UTF-8',
        '-b', f'Authorization={cookie}',
        '-H', f'JwtToken: {jwt}',
        '-H', 'Login-Type: nuc',
        '-H', 'ProductKey: CyberData',
        '--data-raw', payload
    ], capture_output=True, text=True, timeout=30)

    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description='数据资产平台补数脚本')
    parser.add_argument('--start', required=True, help='开始日期 YYYY-MM-DD')
    parser.add_argument('--end', required=True, help='结束日期 YYYY-MM-DD')
    parser.add_argument('--task-id', required=True, help='任务ID')
    parser.add_argument('--project-id', required=True, help='项目ID')
    parser.add_argument('--name', required=True, help='任务名称')
    parser.add_argument('--jwt', default=os.environ.get('DATA_ASSET_JWT', ''), help='JwtToken (或环境变量 DATA_ASSET_JWT)')
    parser.add_argument('--cookie', default=os.environ.get('DATA_ASSET_COOKIE', ''), help='Authorization Cookie (或环境变量 DATA_ASSET_COOKIE)')
    parser.add_argument('--interval', type=int, default=20, help='每次间隔秒数 (默认20)')
    parser.add_argument('--log', default=None, help='日志文件路径')
    parser.add_argument('--dry-run', action='store_true', help='只打印日期列表不执行')
    args = parser.parse_args()

    if not args.jwt or not args.cookie:
        print("错误: 需要提供 --jwt 和 --cookie，或设置环境变量 DATA_ASSET_JWT / DATA_ASSET_COOKIE")
        sys.exit(1)

    dates = generate_dates(args.start, args.end)
    total = len(dates)

    if args.dry_run:
        print(f"日期范围: {args.start} ~ {args.end} ({total}天)")
        for d in dates:
            print(f"  {d}")
        return

    log_path = args.log or os.path.expanduser(f'~/Desktop/补数日志_{args.name}.log')

    with open(log_path, 'a') as f:
        f.write(f"\n=== 补数开始 {datetime.datetime.now()} ===\n")
        f.write(f"任务: {args.name}\n")
        f.write(f"范围: {args.start} ~ {args.end} ({total}天, {args.interval}s间隔)\n")
        f.write("---\n")

    print(f"补数开始: {args.start} ~ {args.end} ({total}天)", flush=True)

    success = 0
    fail = 0
    fail_dates = []

    for i, bd in enumerate(dates, 1):
        resp = run_one(bd, args.jwt, args.cookie, args.task_id, args.project_id, args.name)
        ts = datetime.datetime.now().strftime('%H:%M:%S')

        if '"code":"200"' in resp:
            status = '✅'
            success += 1
        else:
            status = '❌'
            fail += 1
            fail_dates.append(bd)

        line = f"{ts} | {bd} | {status} {i}/{total} | {resp}"
        with open(log_path, 'a') as f:
            f.write(line + '\n')
        print(line, flush=True)

        # token失效或参数异常时停止
        if '"code":"1"' in resp or 'oauth' in resp.lower():
            with open(log_path, 'a') as f:
                f.write(f"!!! 异常停止: {resp} !!!\n")
            print(f"!!! 异常停止: {resp} !!!", flush=True)
            sys.exit(1)

        if i < total:
            time.sleep(args.interval)

    summary = f"=== 补数完成 {datetime.datetime.now()} | 总计{total} 成功{success} 失败{fail} ==="
    if fail_dates:
        summary += f"\n失败日期: {' '.join(fail_dates)}"

    with open(log_path, 'a') as f:
        f.write("---\n")
        f.write(summary + '\n')
    print(summary, flush=True)

if __name__ == '__main__':
    main()
