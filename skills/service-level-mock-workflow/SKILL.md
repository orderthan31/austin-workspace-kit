---
name: service-level-mock-workflow
description: Use when building frontend mock responses at the service/data-access layer without enabling network interceptors, because other live APIs must continue working or the project does not want global mock behavior.
---

# Service-Level Mock Workflow

## 목적

MSW 같은 전역 네트워크 인터셉터를 켜지 않고 service/data-access 계층에서 mock response를 반환한다.

컴포넌트는 mock 여부를 몰라야 한다.

## 적용 상황

- 프로젝트의 다른 화면/API는 실제 서버를 호출 중이다.
- 특정 기능만 임시 mock이 필요하다.
- API DTO가 아직 확정되지 않았지만 화면 시연이 필요하다.
- React Query, SWR, Apollo, 자체 store 등 기존 data hook 구조는 유지해야 한다.

## 구조

```text
component
  -> data hook/store/action
  -> service/data-access method
  -> mock data 반환
```

나중에 실제 API가 준비되면 service/data-access method 내부만 실제 HTTP 호출로 바꾼다.

## 파일 패턴

| 역할 | 예시 |
|---|---|
| type/schema | `src/types/...`, `src/schemas/...` |
| service/data-access | `src/services/...`, `src/api/...` |
| data hook/store | `src/queries/...`, `src/hooks/...`, `src/stores/...` |
| mock data | `src/mocks/...`, `src/fixtures/...` |

## 규칙

- 컴포넌트 내부에 mock data를 두지 않는다.
- 전역 mock handler를 추가하지 않는다.
- 실제 HTTP 호출을 주석 처리하는 방식으로 구현하지 않는다.
- service method가 실제 API와 같은 async shape를 반환하게 한다.
- mock request/response 타입을 실제 API 예상 타입과 최대한 맞춘다.
- mock 전환 조건은 파일 상단 상수, env flag, feature flag 등 프로젝트 관례를 따른다.

## 검증

- `npm run typecheck`
- 관련 service test
- `rg -n "msw|handler|mock|fixture" src`

## 완료 보고

```md
service-level mock으로 구성했습니다.

반영:
- service: ...
- query: ...
- mock data: ...

MSW는 사용하지 않았습니다.
```
