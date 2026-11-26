---
name: poteto-mode
description: pstack의 분석·설계·구현·교차 리뷰·검증 절차를 Herdr에서 실행한다. poteto-mode 또는 pstack 방식으로 작업해 달라는 요청에 사용한다.
---

# Herdr에서 pstack 실행

이 파일이 실행 진입점이다. 현재 요청을 받은 에이전트가 총괄하고, 필요한 작업만 다른 에이전트에게 맡긴다.

1. 프로젝트의 `AGENTS.md`와 연결된 작업 규칙을 읽는다.
2. [Herdr 연결 규칙](references/herdr.md)을 읽는다. 이 규칙은 원본의 Cursor 도구·경로·모델 설정을 현재 환경에 연결한다.
3. [원본 poteto-mode](vendor/pstack/skills/poteto-mode/SKILL.md)를 읽고, 요청에 맞는 작업 절차와 필요한 하위 스킬을 실행한다. 원본의 상대 링크는 해당 원본 파일을 기준으로 해석한다.
4. 위임 전에 [할당량을 조회](references/herdr.md#할당량-조회와-대체-실행)하고 [위임 스크립트](scripts/delegate.py)를 사용한다. 단일 조사는 `--role investigate`, 구현은 `--role implement`로 맡긴다. 별도 패널을 요청받았으면 연결 규칙의 앱 배치 절차도 따른다.
5. 실제 결과물과 검증 근거를 읽고 취합한다. 실행·전달·완료·검증 여부를 구분해 한국어로 보고한다.

위임받은 자식은 자기 작업 범위만 수행한다. 이 진입점을 읽었다는 이유로 전체 작업 절차를 다시 실행하거나 다른 에이전트를 만들지 않는다.

원본 pstack의 58개 스킬·참고 파일·작업 절차는 `vendor/pstack/`에 함께 들어 있다. 모드 안에서는 프로젝트에 따로 설치된 과거 8개 스킬 대신 이 묶음의 하위 스킬을 읽는다. 추가 의존성인 `deslop`·`control-cli`·`control-ui`는 `vendor/cursor-team-kit/skills/`에 있다.

`setup-pstack` 요청은 [Herdr 연결 규칙의 모델 설정](references/herdr.md#모델과-역할)을 따른다. 이 설치가 Cursor의 `.mdc` 설정을 만들거나 전역 모델을 바꾸지는 않는다.
