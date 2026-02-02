#!/usr/bin/env python3
"""
Pathfinder v2 - Cognigraph Helper
JSON 조작 및 입력/출력 빌드를 담당하는 Python 헬퍼 스크립트
"""

import json
import sys
import os
from datetime import datetime


def load_cognigraph(path):
    """cognigraph.json 로드"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_cognigraph(path, cg):
    """cognigraph.json 저장"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cg, f, ensure_ascii=False, indent=2)


def get_active_conflicts(cg):
    """resolved=false인 CONFLICTS 엣지들 반환"""
    conflicts = []
    for edge in cg.get('edges', []):
        if edge.get('type') == 'CONFLICTS' and not edge.get('resolved', False):
            conflicts.append({
                'from': edge['from'],
                'to': edge['to']
            })
    return conflicts


def get_unvisited_hypotheses(cg, hyp_type):
    """Type A 또는 Type B 중 unvisited 가설들 반환"""
    result = []
    for hyp_id, hyp in cg.get('hypotheses', {}).items():
        if hyp.get('status') == 'unvisited':
            # Type A: hyp_A*, Type B: hyp_B*
            if hyp_type == 'A' and hyp_id.startswith('hyp_A'):
                result.append(hyp_id)
            elif hyp_type == 'B' and hyp_id.startswith('hyp_B'):
                result.append(hyp_id)
    return result


def get_tested_uncertain(cg):
    """tested 상태이면서 strength가 애매한(0.4-0.6) 가설들"""
    result = []
    for hyp_id, hyp in cg.get('hypotheses', {}).items():
        if hyp.get('status') == 'tested':
            strength = hyp.get('strength', 0.5)
            if 0.4 <= strength <= 0.6:
                result.append(hyp_id)
    return result


def get_unexplored_unused(cg):
    """탐색되지 않은 키워드들"""
    unexplored = cg.get('unexplored', [])
    # used 플래그가 없거나 False인 것만 반환
    return [kw for kw in unexplored if isinstance(kw, str) or not kw.get('used', False)]


def get_hypotheses_summary(cg):
    """가설 요약 딕셔너리 생성"""
    result = {}
    for hyp_id, hyp in cg.get('hypotheses', {}).items():
        result[hyp_id] = hyp.get('summary', '')
    return result


def build_select_input(cg):
    """SELECT 페이즈 입력 생성"""
    conflicts = get_active_conflicts(cg)

    return {
        "question": cg.get('question', ''),
        "iteration": cg.get('iteration', 0),
        "health_issues": cg.get('health', {}).get('issues', []),
        "conflicts": conflicts,
        "unvisited_type_b": get_unvisited_hypotheses(cg, 'B'),
        "unvisited_type_a": get_unvisited_hypotheses(cg, 'A'),
        "tested_uncertain": get_tested_uncertain(cg),
        "unexplored_unused": get_unexplored_unused(cg),
        "lens_index": cg.get('lens_index', 0),
        "hypotheses_summary": get_hypotheses_summary(cg)
    }


def build_explore_input(cg, select_output, retry_count=0):
    """EXPLORE 페이즈 입력 생성"""
    # 다음 obs/hyp ID 계산
    obs_ids = [int(k.replace('obs_', '')) for k in cg.get('observations', {}).keys() if k.startswith('obs_')]
    hyp_ids = []
    for k in cg.get('hypotheses', {}).keys():
        if k.startswith('hyp_A'):
            try:
                hyp_ids.append(int(k.replace('hyp_A', '')))
            except ValueError:
                pass

    next_obs_id = max(obs_ids, default=0) + 1
    next_hyp_id = max(hyp_ids, default=0) + 1

    # 기존 가설 요약 리스트
    existing_hypotheses = [h.get('summary', '') for h in cg.get('hypotheses', {}).values()]

    return {
        "search_query": select_output.get('search_query', ''),
        "search_mode": select_output.get('search_mode', 'broad'),
        "target_type": select_output.get('target_type', 'hypothesis'),
        "target_id": select_output.get('target_id', ''),
        "conflict_with": select_output.get('conflict_with'),
        "existing_hypotheses": existing_hypotheses,
        "next_obs_id": next_obs_id,
        "next_hyp_id": next_hyp_id,
        "retry_count": retry_count
    }


def build_ideate_input(cg):
    """IDEATE 페이즈 입력 생성"""
    # observations 요약
    obs_summary = {}
    for obs_id, obs in cg.get('observations', {}).items():
        obs_summary[obs_id] = obs.get('summary', '')

    # hypotheses 요약 (상태/strength 포함)
    hyp_summary = {}
    for hyp_id, hyp in cg.get('hypotheses', {}).items():
        source_type = 'IDEATE' if hyp_id.startswith('hyp_B') else 'INITIAL'
        status = hyp.get('status', 'unvisited').upper()
        strength = hyp.get('strength', 0.5)
        hyp_summary[hyp_id] = f"[{source_type}|{status}|{strength}] {hyp.get('summary', '')}"

    # 활성 충돌
    conflicts = get_active_conflicts(cg)

    # 관련 엣지들
    edges = []
    for edge in cg.get('edges', []):
        if edge.get('type') in ['SUPPORTS', 'CONTRADICTS']:
            edges.append({
                'from': edge['from'],
                'to': edge['to'],
                'type': edge['type']
            })

    # 다음 Type B ID 계산
    b_ids = []
    for k in cg.get('hypotheses', {}).keys():
        if k.startswith('hyp_B'):
            try:
                b_ids.append(int(k.replace('hyp_B', '')))
            except ValueError:
                pass
    next_hyp_id = max(b_ids, default=0) + 1

    return {
        "question": cg.get('question', ''),
        "health_issues": cg.get('health', {}).get('issues', []),
        "observations": obs_summary,
        "hypotheses": hyp_summary,
        "conflicts": conflicts,
        "edges": edges,
        "next_hyp_id": next_hyp_id
    }


def apply_explore_updates(cg, select_output, explore_output):
    """EXPLORE 결과를 cognigraph에 반영"""
    # observations 추가
    for obs in explore_output.get('observations', []):
        obs_id = obs.get('id')
        if obs_id:
            cg.setdefault('observations', {})[obs_id] = {
                'summary': obs.get('summary', ''),
                'source_url': obs.get('source_url', ''),
                'source_type': obs.get('source_type', 'unknown'),
                'authority': obs.get('authority', 0.5),
                'iteration': cg.get('iteration', 0)
            }

    # Type A hypotheses 추가
    for hyp in explore_output.get('type_a_hypotheses', []):
        hyp_id = hyp.get('id')
        if hyp_id:
            cg.setdefault('hypotheses', {})[hyp_id] = {
                'summary': hyp.get('summary', ''),
                'verify_keywords': hyp.get('verify_keywords', []),
                'status': 'unvisited',
                'strength': 0.5,
                'iteration': cg.get('iteration', 0)
            }

    # edges 추가
    for edge in explore_output.get('edges', []):
        cg.setdefault('edges', []).append({
            'from': edge.get('from', ''),
            'to': edge.get('to', ''),
            'type': edge.get('type', 'SUPPORTS'),
            'weight': edge.get('weight', 0.5),
            'iteration': cg.get('iteration', 0)
        })

    # conflict_resolution 처리
    resolution = explore_output.get('conflict_resolution')
    if resolution and resolution.get('conflict_edge'):
        # 해당 충돌 엣지를 resolved로 표시
        for edge in cg.get('edges', []):
            if edge.get('type') == 'CONFLICTS':
                if edge.get('from') == select_output.get('target_id') or edge.get('to') == select_output.get('target_id'):
                    edge['resolved'] = True
                    edge['resolution_type'] = resolution.get('resolution_type')
                    edge['resolution_desc'] = resolution.get('description')

    # 타겟 가설 상태 업데이트
    target_id = select_output.get('target_id')
    if target_id and target_id in cg.get('hypotheses', {}):
        hyp = cg['hypotheses'][target_id]
        if hyp.get('status') == 'unvisited':
            hyp['status'] = 'tested'
        # strength 업데이트 (SUPPORTS/CONTRADICTS 엣지 기반)
        supports = sum(1 for e in explore_output.get('edges', []) if e.get('type') == 'SUPPORTS' and e.get('to') == target_id)
        contradicts = sum(1 for e in explore_output.get('edges', []) if e.get('type') == 'CONTRADICTS' and e.get('to') == target_id)
        if supports + contradicts > 0:
            delta = (supports - contradicts) * 0.1
            hyp['strength'] = max(0.0, min(1.0, hyp.get('strength', 0.5) + delta))

    return cg


def apply_ideate_updates(cg, ideate_output):
    """IDEATE 결과를 cognigraph에 반영"""
    hyp_data = ideate_output.get('hypothesis', {})
    hyp_id = hyp_data.get('id')

    if hyp_id:
        cg.setdefault('hypotheses', {})[hyp_id] = {
            'summary': hyp_data.get('summary', ''),
            'verify_keywords': hyp_data.get('verify_keywords', []),
            'reasoning_tool': hyp_data.get('reasoning_tool', ''),
            'derived_from': hyp_data.get('derived_from', []),
            'status': 'unvisited',
            'strength': 0.5,
            'iteration': cg.get('iteration', 0)
        }

    return cg


def finalize_iteration(cg, select_output, explore_output):
    """iteration 마무리 및 상태 전환"""
    # iteration 증가
    cg['iteration'] = cg.get('iteration', 0) + 1

    # lens_index 증가 (6lens 사용 시)
    if select_output.get('target_type') == '6lens':
        cg['lens_index'] = cg.get('lens_index', 0) + 1

    # retry_keywords를 unexplored에 추가
    retry_keywords = explore_output.get('retry_keywords', [])
    for kw in retry_keywords:
        if kw and kw not in cg.get('unexplored', []):
            cg.setdefault('unexplored', []).append(kw)

    return cg


def health_check(cg):
    """건강 체크 - 문제 감지"""
    issues = []

    # ALL_WEAK: 모든 가설이 strength < 0.55
    hypotheses = cg.get('hypotheses', {})
    if hypotheses:
        all_weak = all(h.get('strength', 0.5) < 0.55 for h in hypotheses.values())
        if all_weak and len(hypotheses) >= 3:
            issues.append('ALL_WEAK')

    # STALEMATE: 해결되지 않은 충돌이 3개 이상
    unresolved_conflicts = len(get_active_conflicts(cg))
    if unresolved_conflicts >= 3:
        issues.append('STALEMATE')

    # LOW_QUALITY: 최근 5개 관찰의 authority 평균이 0.4 미만
    observations = list(cg.get('observations', {}).values())
    if len(observations) >= 5:
        recent = sorted(observations, key=lambda x: x.get('iteration', 0), reverse=True)[:5]
        avg_authority = sum(o.get('authority', 0.5) for o in recent) / 5
        if avg_authority < 0.4:
            issues.append('LOW_QUALITY')

    return issues


def check_saturation(cg):
    """포화 상태 감지"""
    # 조건: 최근 3회 iteration에서 새 가설이 없음
    iteration = cg.get('iteration', 0)
    if iteration < 6:
        return False

    recent_hyps = [
        h for h in cg.get('hypotheses', {}).values()
        if h.get('iteration', 0) >= iteration - 3
    ]

    return len(recent_hyps) == 0


def get_stats(cg):
    """통계 정보 반환"""
    obs_count = len(cg.get('observations', {}))
    hyp_count = len(cg.get('hypotheses', {}))
    hyp_a_count = sum(1 for k in cg.get('hypotheses', {}).keys() if k.startswith('hyp_A'))
    hyp_b_count = sum(1 for k in cg.get('hypotheses', {}).keys() if k.startswith('hyp_B'))
    edge_count = len(cg.get('edges', []))
    unresolved = len(get_active_conflicts(cg))

    return {
        'iteration': cg.get('iteration', 0),
        'observations': obs_count,
        'hypotheses': hyp_count,
        'hyp_a': hyp_a_count,
        'hyp_b': hyp_b_count,
        'edges': edge_count,
        'unresolved_conflicts': unresolved,
        'saturated': check_saturation(cg)
    }


# CLI 인터페이스
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: cognigraph.py <command> <cognigraph_path> [args...]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    cg_path = sys.argv[2]

    if command == 'build_select_input':
        cg = load_cognigraph(cg_path)
        result = build_select_input(cg)
        print(json.dumps(result, ensure_ascii=False))

    elif command == 'build_explore_input':
        cg = load_cognigraph(cg_path)
        select_output = json.loads(sys.argv[3])
        retry_count = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        result = build_explore_input(cg, select_output, retry_count)
        print(json.dumps(result, ensure_ascii=False))

    elif command == 'build_ideate_input':
        cg = load_cognigraph(cg_path)
        result = build_ideate_input(cg)
        print(json.dumps(result, ensure_ascii=False))

    elif command == 'apply_explore':
        cg = load_cognigraph(cg_path)
        select_output = json.loads(sys.argv[3])
        explore_output = json.loads(sys.argv[4])
        cg = apply_explore_updates(cg, select_output, explore_output)
        save_cognigraph(cg_path, cg)
        print("OK")

    elif command == 'apply_ideate':
        cg = load_cognigraph(cg_path)
        ideate_output = json.loads(sys.argv[3])
        cg = apply_ideate_updates(cg, ideate_output)
        save_cognigraph(cg_path, cg)
        print("OK")

    elif command == 'finalize':
        cg = load_cognigraph(cg_path)
        select_output = json.loads(sys.argv[3])
        explore_output = json.loads(sys.argv[4])
        cg = finalize_iteration(cg, select_output, explore_output)
        save_cognigraph(cg_path, cg)
        print("OK")

    elif command == 'health_check':
        cg = load_cognigraph(cg_path)
        issues = health_check(cg)
        cg.setdefault('health', {})['issues'] = issues
        cg['health']['last_check'] = cg.get('iteration', 0)
        save_cognigraph(cg_path, cg)
        print(json.dumps(issues, ensure_ascii=False))

    elif command == 'stats':
        cg = load_cognigraph(cg_path)
        result = get_stats(cg)
        print(json.dumps(result, ensure_ascii=False))

    elif command == 'get':
        cg = load_cognigraph(cg_path)
        key = sys.argv[3]
        if '.' in key:
            parts = key.split('.')
            val = cg
            for p in parts:
                val = val.get(p, {}) if isinstance(val, dict) else {}
            print(json.dumps(val, ensure_ascii=False) if isinstance(val, (dict, list)) else str(val))
        else:
            print(json.dumps(cg.get(key, ''), ensure_ascii=False))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)
