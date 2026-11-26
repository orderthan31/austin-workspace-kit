---
name: realistic-demo-data-workflow
description: Use when mock, fixture, seed, or demo data must look realistic and internally consistent for customer demos, QA, screenshots, or stakeholder review.
---

# Realistic Demo Data Workflow

## 목적

시연용 mock data를 실제 업무 데이터처럼 만든다.

단순 반복, modulo, 무작위 값, 서로 맞지 않는 금액/상태/관계/판단 결과를 피한다.

## 적용 상황

- 고객 시연이 예정되어 있다.
- 화면 QA에서 mock data가 너무 가짜처럼 보인다.
- 목록, 상세, 상태, 금액, 날짜, 관계 데이터가 서로 맞지 않는다.
- 검증/판단 결과와 원천 데이터가 서로 맞지 않는다.

## 작성 원칙

1. 하나의 데이터 묶음에 업무 서사가 있어야 한다.
2. 목록 카드, 상세 화면, 통계, 검증 결과가 같은 원천값을 바라봐야 한다.
3. 금액, 수량, 합계, 날짜, 상태 전이가 말이 되어야 한다.
4. 부모/자식, 참조 id, mapping, association이 서로 맞아야 한다.
5. 검증 결과의 evidence 값이 실제 원천 데이터와 맞아야 한다.
6. `index %`, `index <` 같은 반복 꼼수로 데이터를 만들지 않는다.
7. 표준 코드/enum/상태명은 실제 코드 목록에 있는 값을 사용한다.

## 데이터 점검표

| 영역 | 점검 기준 |
|---|---|
| 식별자 | id, documentId, orderNo, parentId 같은 연결 키가 실제 관계와 맞는가 |
| 날짜 | 생성일, 처리일, 만료일, 이벤트 순서가 자연스러운가 |
| 금액/수량 | line item, subtotal, total, discount, tax가 맞는가 |
| 상태 | 상태값과 가능한 사용자 액션이 맞는가 |
| 상세 | 목록에서 보인 핵심값이 상세에서도 일관되는가 |
| 검증 결과 | 성공/경고/누락/오류 판단이 원천 데이터와 맞는가 |
| 코드값 | enum/code 값이 프로젝트 dictionary와 맞는가 |

## 금지 예시

```ts
const item = fixtures[index % fixtures.length];
const serviceDate = index < 4 ? "2026-05-21" : "2026-05-22";
```

반복 생성이 필요해도 내용 fixture는 명시적으로 작성한다.

## 완료 전 검색

```sh
rg -n "index %|index <|Math.random|TODO|임시|샘플" src
```

## 완료 보고

```md
시연용 mock data를 실제 업무 흐름처럼 정리했습니다.

반영:
- 목록/상세/상태값 정합성
- 부모/자식 연결 정합성
- 검증 결과와 원천 데이터 정합성
```
