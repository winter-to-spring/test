# CoChat — 해커톤 개발 마스터 문서

> 이 문서 하나면 충분합니다. **모든 팀원이 이 페이지만 보고 바로 개발을 시작할 수 있도록** 확정된 내용을 모두 담았습니다.
> 

> 마지막 업데이트: 2026-04-02
> 

---

# 🎯 01. 서비스 한 줄 정의

> **여러 업무 채널의 알림을 한 페이지로 통합하고, AI가 중요도 분류와 한 줄 요약을 붙여 사용자의 딥워크 시간을 보호하는 서비스.**
> 

## 핵심 가치

- 중요한 알림만 먼저 보이게 한다
- 딥워크 중에는 방해를 줄이고, 끝나면 브리핑으로 복기한다
- 사용자 피드백을 AI 학습 데이터로 전환해 분류 정확도를 높인다

---

# ✅ 02. 확정된 결정 사항

> 아래 항목은 이미 합의 완료된 사항입니다. 번복하지 않습니다.
> 

| 항목 | 결정 내용 |
| --- | --- |
| 자체 로그인/회원가입 | ❌ 구현하지 않음. `users` 테이블 없음 |
| 백엔드 언어/프레임워크 | Python + FastAPI |
| 프론트엔드 프레임워크 | Next.js (TypeScript) |
| 실시간 이벤트 수신 방식 | SSE (Server-Sent Events) |
| 비동기 처리 | Worker 분리 (웹훅 수신 → 비동기 큐 → AI 처리) |
| AI 파이프라인 | LangGraph 기반, Claude API 사용 |
| 임베딩 대상 | 원문이 아닌 **LLM 요약 결과만** 임베딩 |
| 개인정보 처리 | AI 학습 시 마스킹 처리 예정 (구조 설계만 선확보) |
| 레포 구조 | service-frontend / service-backend / infra 3개 분리 |
| ML 코드 위치 | service-backend에 통합 (별도 레포 없음) |
| Slack 연동 방식 | Bolt for Python, 비엑스파이어링 Bot Token |
| Discord 연동 방식 | WebSocket Gateway — 별도 async Bot 프로세스 필요 |
| Gmail 연동 방식 | Gmail → GCP Pub/Sub → CoChat 3단계 파이프라인 |
| Google 통합 | Gmail + Calendar 동일한 `google` provider 토큰 공유 |
| Slack 토큰 | `refresh_token`, `expires_at` nullable 허용 |
| Jira/Gmail 토큰 | `refresh_token`, `expires_at` NOT NULL |

---

# 📅 03. 개발 타임라인 — 해커톤 전까지

> 해커톤 당일 현장에서 처음 시작하는 게 아닙니다. **미리 개발해가야 합니다.**
> 

## 전체 흐름

![image.png](CoChat%20%E2%80%94%20%ED%95%B4%EC%BB%A4%ED%86%A4%20%EA%B0%9C%EB%B0%9C%20%EB%A7%88%EC%8A%A4%ED%84%B0%20%EB%AC%B8%EC%84%9C/image.png)

## 페이즈별 목표

| 페이즈 | 시점 | 완료 목표 | 담당 |
| --- | --- | --- | --- |
| **Phase 1** | 지금 ~ D-3 | 백엔드 파이프라인 + AI 파이프라인 + 인프라 완성 | 오진우, 이창현, 김구, 김선호 |
| **Phase 2** | D-3 (디자인 완료 후) | 프론트 1차 개발 완성 (디자인 기반 실제 구현) | 오진우, 이창현 |
| **Phase 3** | D-Day 현장 | 백엔드 마무리 + 프론트 추가 개발 + 통합 | 오진우·이창현 → 백엔드 / 마수한·문정현 → 프론트 |

> 💡 **핵심 전제:** 문정현 디자이너님이 D-3까지 전체 화면 디자인 완료 확정.
> 

> D-3 이전까지 오진우·이창현은 **백엔드에 집중**하고, D-3부터 프론트로 전환.
> 

> D-Day 현장에서는 오진우·이창현이 **백엔드 마무리**에 집중하고, 마수한·문정현이 **프론트 추가 개발** 담당.
> 

---

# 🏗️ 04. 아키텍처 & 처리 파이프라인

## 핵심 데이터 흐름

```
[1] 연동 시작
  사용자 → Slack OAuth → integration_accounts + integration_tokens 생성

[2] 이벤트 수신
  Slack Webhook → 서명 검증 → raw_events 저장 → Worker Job 큐잉

[3] 비동기 AI 처리
  Worker → NotificationEvent 정규화 → LangGraph 분류/요약 → notifications 저장

[4] 실시간 노출
  notifications 저장 완료 → SSE 발행 → 대시보드 갱신

[5] 피드백 루프
  사용자 리포트 버튼 → feedback_reports 저장 → 모델/프롬프트 개선 데이터
```

## P0 확정 기능 목록

| 기능 | 설명 |
| --- | --- |
| Slack 다계정 연동 | 여러 workspace를 독립적으로 연결, 이벤트 식별 |
| 웹훅 수집 및 정규화 | raw event 저장 후 공통 NotificationEvent 구조로 변환 |
| AI 중요도 분류 + 요약 | 새 알림마다 priority + one-line summary 생성 |
| 알림 대시보드 | priority / provider / integrationId 기준 필터링 |
| SSE 실시간 갱신 | 새 알림 대시보드 즉시 반영 |
| 딥워크 세션 | 시작/종료 버튼, 세션 상태 관리 |
| 브리핑 | 딥워크 종료 후 주요 알림 AI 요약 |
| 피드백 리포트 | 알림별 오분류/요약 오류 신고, feedback_reports 저장 |

## ⚠️ 오늘 회의에서 결정할 기능 (미확정)

| 기능 | 결정 필요 사항 |
| --- | --- |
| 딥워크 웹캠 | 브라우저 단 분석 vs 버튼식 상태 관리 |
| 답장 초안 작성 | P0 추가 / P1 / 제외 |
| Jira 연동 | 구현 / 껍데기 / 제외 |
| Discord 연동 | 구현 / 껍데기 / 제외 |
| Gmail 연동 | 구현 / 껍데기 / 제외 |
| Google Calendar | 구현 / 껍데기 / 제외 |

---

# 📁 05. Repo 구조

```jsx
CoChat/
├── docs/
│   └── api-spec.md                    ← 오진우 + 이창현 공동 관리
│
├── service-frontend/
│   └── src/
│       ├── app/
│       │   ├── dashboard/page.tsx
│       │   ├── settings/integrations/page.tsx
│       │   ├── deepwork/page.tsx
│       │   └── briefing/page.tsx
│       ├── features/
│       │   ├── notifications/         ← 알림 카드, 필터, 뱃지
│       │   ├── integrations/          ← OAuth 버튼, 연결 목록
│       │   ├── deepwork/
│       │   └── briefing/
│       ├── hooks/
│       │   ├── useNotifications.ts
│       │   ├── useIntegrations.ts
│       │   └── useRealtime.ts         ← SSE 수신 → 상태 업데이트
│       ├── services/
│       │   ├── api.ts
│       │   ├── notification.service.ts
│       │   ├── integration.service.ts
│       │   ├── briefing.service.ts
│       │   └── oauth.service.ts       ← Slack/Jira/Discord OAuth 플로우
│       └── types/
│           ├── notification.ts
│           ├── integration.ts
│           └── briefing.ts
│
├── service-backend/
│   └── app/
│       ├── api/
│       │   ├── endpoints/
│       │   │   ├── notifications.py
│       │   │   ├── briefing.py
│       │   │   ├── integrations.py
│       │   │   └── streams.py         ← SSE endpoint
│       │   └── schemas/
│       │
│       ├── ingress/                   ← 외부 이벤트 진입점 통일
│       │   ├── slack_webhook.py       ← HTTP Webhook 수신 + 서명 검증
│       │   ├── jira_webhook.py
│       │   └── discord_gateway.py    ← WebSocket Gateway (별도 async)
│       │
│       ├── integrations/
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── normalizer.py          ← ⭐ NotificationEvent 공통 모델 (최우선)
│       │   ├── slack/
│       │   │   ├── client.py
│       │   │   ├── events.py
│       │   │   └── normalizer.py
│       │   ├── jira/
│       │   └── discord/
│       │
│       ├── core/
│       │   └── config.py              ← pydantic-settings 기반 설정 클래스
│       │
│       ├── db/
│       │   ├── session.py             ← AsyncEngine, AsyncSession, get_db 의존성 주입
│       │   └── base.py                ← Alembic 모델 자동 탐지용 전체 모델 import
│       │
│       ├── models/
│       │   ├── integration_account.py  ✅ 완료
│       │   ├── integration_token.py    ✅ 완료
│       │   ├── raw_event.py            ✅ 완료
│       │   ├── notification.py         ✅ 완료
│       │   ├── focus_session.py        ✅ 완료
│       │   ├── briefing.py             ✅ 완료
│       │   └── feedback_report.py      ✅ 완료
│       │
│       ├── repositories/
│       │   ├── integration_repository.py
│       │   ├── raw_event_repository.py
│       │   ├── notification_repository.py
│       │   └── briefing_repository.py
│       │
│       ├── services/
│       │   ├── notification_service.py
│       │   ├── classification_service.py
│       │   ├── briefing_service.py
│       │   ├── integration_service.py
│       │   └── realtime_service.py
│       │
│       ├── workers/
│       │   └── notification_worker.py ← raw event → normalize → pipeline → DB
│       │
│       └── pipelines/
│           ├── classifier.py
│           ├── summarizer.py
│           ├── prompts/
│           │   ├── classify.py
│           │   └── summarize.py
│           └── shared/
│               └── embeddings.py
│
└── infra/
    ├── docker/
    │   ├── frontend.Dockerfile
    │   └── backend.Dockerfile
    ├── nginx/nginx.conf
    └── docker-compose.yml
```

> ⭐ `integrations/normalizer.py`의 `NotificationEvent` 모델은 **개발 첫날 오전에 오진우 + 이창현 + 김구 셋이 30분 내 합의 후 고정**해야 합니다. 모든 팀원이 이 파일에 의존합니다.
> 

---

# 🔌 06. API 명세 (P0 확정)

> 아래는 오늘 회의와 무관하게 **이미 확정된 엔드포인트**입니다.
> 

> Request/Response body 상세는 오늘 회의 후 `docs/api-spec.md`에 반영 예정
> 

## 연동 (Integration)

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/api/v1/integrations` | 연결된 workspace/account 목록 및 상태 |
| GET | `/api/v1/integrations/slack/oauth-url` | Slack OAuth 시작 URL 발급 |
| GET | `/api/v1/integrations/slack/callback` | OAuth code → integration 생성/갱신 |

## 웹훅 수신 (Webhook)

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/api/v1/webhooks/slack` | Slack 이벤트 검증 → raw event 저장 → worker job |

## 알림 (Notifications)

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/api/v1/notifications` | priority / provider / integrationId 필터 지원 |
| PATCH | `/api/v1/notifications/{notificationId}` | 읽음/보류 등 상태 변경 |
| GET | `/api/v1/notifications/stream` | SSE — 새 알림 실시간 수신 |

## 딥워크 세션 (Focus Sessions)

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/api/v1/focus-sessions` | 딥워크 세션 시작 |
| PATCH | `/api/v1/focus-sessions/{sessionId}` | 세션 종료 / 상태 변경 |

## 브리핑 (Briefings)

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/api/v1/briefings` | 딥워크 종료 후 브리핑 생성 |
| GET | `/api/v1/briefings/latest` | 최신 브리핑 조회 |

## 피드백 (Feedback Reports)

| Method | Endpoint | 설명 |
| --- | --- | --- |
| POST | `/api/v1/feedback-reports` | 알림별 오분류/요약 오류 신고 저장 |
| GET | `/api/v1/feedback-reports` | 누적 리포트 목록 조회 (관리용) |

## 대시보드

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/api/v1/dashboard` | 중요 알림 요약, 카운트, 최근 상태 |

## ⚠️ 오늘 회의 결과에 따라 추가될 수 있는 엔드포인트

| Method | Endpoint | 조건 |
| --- | --- | --- |
| GET | `/api/v1/integrations/discord/connect` | Discord 구현 시 |
| POST | `/api/v1/webhooks/discord` | Discord 구현 시 |
| GET | `/api/v1/integrations/gmail/connect` | Gmail 구현 시 |
| POST | `/api/v1/webhooks/gmail/push` | Gmail 구현 시 |
| POST | `/api/v1/webhooks/jira` | Jira 구현 시 |
| POST | `/api/v1/focus-sessions/{sessionId}/signals` | 웹캠 기능 구현 시 |

---

# 🗄️ 07. DB 스키마 초안

> ⚠️ 오늘 회의에서 컬럼/타입/ENUM 값 최종 합의 후 확정 예정
> 

> ✅ **[2026-04-02 업데이트]** SQLAlchemy 모델 7개 전체 작성 완료 (브랜치: `chore/init-project-setup`). 모든 PK UUID, 날짜 DateTime(timezone=True) 사용. 아래 협의 필요 사항 참고.
> 

## integration_accounts

```sql
CREATE TABLE integration_accounts (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider            VARCHAR NOT NULL,   -- 'slack' | 'jira' | 'discord' | 'gmail'
  account_identifier  VARCHAR NOT NULL,   -- (구 workspace_id) Slack: team_id, Discord: guild_id, Gmail: email 등 범용화
  account_name        VARCHAR,            -- (구 workspace_name) 범용화
  status              VARCHAR NOT NULL,   -- 'active' | 'inactive' | 'error'
  created_at          TIMESTAMPTZ DEFAULT now()
);
```

> ⚠️ **필드명 변경**: `workspace_id` → `account_identifier`, `workspace_name` → `account_name` (Slack 외 Gmail·Jira 등 확장 대응을 위해 범용화. SQLAlchemy 모델 기준으로 확정)
> 

## integration_tokens

```sql
CREATE TABLE integration_tokens (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id   UUID REFERENCES integration_accounts(id),
  access_token     TEXT NOT NULL,
  refresh_token    TEXT,              -- Slack은 NULL 허용, Jira/Gmail은 NOT NULL
  expires_at       TIMESTAMPTZ,      -- Slack은 NULL 허용, Jira/Gmail은 NOT NULL
  updated_at       TIMESTAMPTZ DEFAULT now()
);
```

## raw_events

```sql
CREATE TABLE raw_events (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider        VARCHAR NOT NULL,
  integration_id  UUID REFERENCES integration_accounts(id),
  payload         JSONB NOT NULL,
  received_at     TIMESTAMPTZ DEFAULT now()
);
```

## notifications

```sql
CREATE TABLE notifications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id  UUID REFERENCES integration_accounts(id),
  raw_event_id    UUID REFERENCES raw_events(id),
  priority        VARCHAR NOT NULL,  -- 'critical' | 'high' | 'medium' | 'low'
  summary         TEXT NOT NULL,     -- AI 생성 한 줄 요약
  actor           VARCHAR,           -- 발신자
  channel         VARCHAR,           -- DM이면 NULL
  status          VARCHAR NOT NULL,  -- 'unread' | 'read' | 'snoozed'  (⚠️ 오늘 확정)
  created_at      TIMESTAMPTZ DEFAULT now()
);
```

## focus_sessions

```sql
CREATE TABLE focus_sessions (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  planned_duration_minutes INT,
  started_at               TIMESTAMPTZ DEFAULT now(),
  ended_at                 TIMESTAMPTZ,
  status                   VARCHAR NOT NULL  -- 'active' | 'completed' | 'cancelled'
);
```

## briefings

```sql
CREATE TABLE briefings (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id    UUID REFERENCES focus_sessions(id),
  content       TEXT NOT NULL,   -- AI 생성 전체 요약
  highlights    JSONB,           -- 주요 알림 ID 목록
  generated_at  TIMESTAMPTZ DEFAULT now()
);
```

## feedback_reports

```sql
CREATE TABLE feedback_reports (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  notification_id     UUID REFERENCES notifications(id),
  report_type         VARCHAR NOT NULL,  -- 'wrong_priority' | 'bad_summary' | 'duplicate' | 'unnecessary'  (⚠️ 오늘 확정)
  expected_priority   VARCHAR,
  comment             TEXT,
  model_version       VARCHAR,
  created_at          TIMESTAMPTZ DEFAULT now()
);
```

## 테이블 관계

- `integration_accounts` → `integration_tokens` (1:1)
- `integration_accounts` → `raw_events` (1:N)
- `integration_accounts` → `notifications` (1:N)
- `raw_events` → `notifications` (1:N)
- `notifications` → `feedback_reports` (1:N)
- `focus_sessions` → `briefings` (1:N)

## ⚠️ 협의 필요 사항 (자동 입력 대기 중 — AI 개발자 + 백엔드 개발자)

1. **`notifications` 테이블 AI 출력 필드 스펙 확정** — `priority`, `summary` 외에 `reason`, `suggested_action` 등 추가 필드 필요 여부
2. **`raw_events.payload` JSONB AI 파이프라인 접근 방식** — worker가 payload를 직접 읽는지, 정규화 후 전달하는지
3. **`briefings.highlights` JSONB 내부 구조 정의** — 단순 notification_id 배열인지 vs. 더 풍부한 구조인지
4. **`feedback_reports.report_type` 허용 값 목록 확정** — 현재 초안: `wrong_priority` | `bad_summary` | `duplicate` | `unnecessary`

---

# 👥 08. 역할별 할 일 — 페이즈별 정리

## 🟦 오진우 (팀장/풀스택)

**Phase 1 (지금 ~ D-3): 백엔드 집중**

| 파일 | 할 일 | 우선순위 |
| --- | --- | --- |
| `integrations/slack/client.py` | Slack SDK 래퍼 | P0 |
| `integrations/slack/events.py` | Slack 이벤트 타입 정의 | P0 |
| `integrations/slack/normalizer.py` | Slack → NotificationEvent 변환 | P0 |
| `ingress/slack_webhook.py` | Slack Webhook 수신 + 서명 검증 | P0 |
| `workers/notification_worker.py` | raw event → normalize → pipeline → DB | P0 |
| `services/realtime_service.py` | SSE 발행 로직 | P0 |
| `api/endpoints/streams.py` | SSE endpoint | P0 |
| `docs/api-spec.md` | 이창현과 공동 작성, API body 계약 관리 | P0 |

**Phase 2 (D-3~): 프론트 전환**

| 파일 | 할 일 |
| --- | --- |
| `app/dashboard/page.tsx` | 대시보드 페이지 (백엔드 실제 연결) |
| `hooks/useRealtime.ts` | SSE 수신 → 상태 업데이트 |
| `services/oauth.service.ts` | OAuth 플로우 연결 |
| 백엔드-프론트 통합 | API 실제 연결, 버그 수정 |

**Phase 3 (D-Day): 백엔드 마무리**

- 남은 백엔드 버그 수정, 데모 안정화, 통합 최종 확인

---

## 🟩 이창현 (풀스택)

**Phase 1 (지금 ~ D-3): 백엔드 집중**

| 파일 | 할 일 | 우선순위 |
| --- | --- | --- |
| `api/endpoints/integrations.py` | OAuth URL 발급, callback 처리, 연동 목록/해제 | P0 |
| `services/integration_service.py` | OAuth 토큰 저장/갱신/해제 로직 | P0 |
| `models/integration_account.py` | 유저-플랫폼 연결 단위 모델 | P0 |
| `models/integration_token.py` | access/refresh token 모델 | P0 |
| `repositories/integration_repository.py` | token CRUD | P0 |
| `docs/api-spec.md` | 오진우와 공동 작성 | P0 |
| `ingress/jira_webhook.py` | Jira Webhook 수신 (회의 결과에 따라) | P1 |
| `ingress/discord_gateway.py` | Discord WebSocket Gateway (회의 결과에 따라) | P1 |
| `integrations/jira/`, `integrations/discord/` | client, events, normalizer (회의 결과에 따라) | P1 |

**Phase 2 (D-3~): 프론트 전환**

| 파일 | 할 일 |
| --- | --- |
| `app/settings/integrations/page.tsx` | 연동 설정 페이지 (백엔드 실제 연결) |
| `features/integrations/` | OAuth 연결 버튼, 계정 목록 UI |
| `services/integration.service.ts` | API 실제 연결 |
| 백엔드-프론트 통합 | API 실제 연결, 버그 수정 |

**Phase 3 (D-Day): 백엔드 마무리**

- 남은 백엔드 버그 수정, 데모 안정화, 통합 최종 확인

---

## 🟨 김구 (생성AI)

> AI 파이프라인 전담. Phase 1에 집중하면 됩니다.
> 

| 파일 | 할 일 | 우선순위 |
| --- | --- | --- |
| `integrations/normalizer.py` | **NotificationEvent 공통 모델 정의** — 최우선, 다른 팀원 전부 이걸 씀 | ⭐ 최우선 |
| `pipelines/prompts/classify.py` | Critical/High/Medium/Low 분류 프롬프트 | P0 |
| `pipelines/prompts/summarize.py` | 한 줄 요약 프롬프트 | P0 |
| `pipelines/classifier.py` | LangGraph 분류 파이프라인 | P0 |
| `pipelines/summarizer.py` | LangGraph 요약 파이프라인 | P0 |
| `services/classification_service.py` | worker에서 pipeline 호출하는 오케스트레이션 | P0 |
| `pipelines/shared/embeddings.py` | pgvector 임베딩 유틸 | P1 |

> `normalizer.py`의 NotificationEvent 모델은 **첫날 오전 오진우 + 이창현과 합의 후 즉시 커밋** — 나머지 모든 팀원이 이 파일을 임포트함
> 

---

## 🟪 문정현 (디자이너/프론트)

**D-3까지: 화면 디자인 완료 (최우선)**

| 화면 | 내용 |
| --- | --- |
| 대시보드 | 알림 카드, priority 색상 뱃지, 필터 UI |
| 연동 설정 | OAuth 연결 버튼, 연결된 계정 목록, 해제 UI |
| 딥워크 모드 | 시작/종료 버튼, 세션 상태 표시 |
| 브리핑 | 브리핑 리포트 레이아웃 |

> 디자인 완료 후 오진우·이창현이 바로 개발할 수 있도록 D-3에 전달
> 

**D-Day 현장: 마수한과 함께 프론트 추가 개발**

| 파일 | 할 일 |
| --- | --- |
| `app/deepwork/page.tsx` | 딥워크 모드 페이지 |
| `app/briefing/page.tsx` | 브리핑 페이지 |
| `features/briefing/` | 브리핑 리포트 UI |
| `features/notifications/` | 알림 카드 UI 개선, 필터 |

---

## 🟧 김선호 (클라우드)

> **가장 먼저 끝내야 하는 사람.** 나머지 5명이 환경 세팅을 기다립니다.
> 

| 파일 | 할 일 | 우선순위 |
| --- | --- | --- |
| GitHub Repo | 브랜치 전략 세팅 (`main` / `develop` / `feature/*`) | ⭐ 최우선 |
| `.env.example` | 환경변수 템플릿 전체 목록 (오늘 회의 결과 반영) | ⭐ 최우선 |
| `infra/docker-compose.yml` | Postgres + Redis + Frontend + Backend + Nginx 전체 로컬 실행 | P0 |
| `infra/docker/backend.Dockerfile` | FastAPI 컨테이너 | P0 |
| `infra/docker/frontend.Dockerfile` | Next.js 컨테이너 | P0 |
| `infra/nginx/nginx.conf` | 프론트/백 라우팅 설정 | P0 |
| AWS 배포 환경 | 해커톤 D-Day 데모 전 배포 | P1 |

---

## 🟫 마수한 (PM)

**D-Day 전까지: 기획 및 관리**

| 할 일 | 설명 | 기한 |
| --- | --- | --- |
| GitHub 칸반보드 세팅 | 위 태스크들을 To Do 카드로 등록, 담당자 배정 | 회의 당일 |
| 일일 싱크 진행 | 매일 저녁 15분, "했냐/할거냐/막히냐" 3문장씩 | 매일 |
| `docs/api-spec.md` 관리 | 오진우/이창현이 API 수정할 때마다 문서 반영 확인 | 상시 |
| 데모 시나리오 작성 | 아래 10번 시나리오 기반으로 스크립트화 | D-Day 전날 |
| 발표 자료 준비 | 문정현 디자인 참고해서 발표 흐름 구성 | D-Day 전날 |

**D-Day 현장: 문정현과 함께 프론트 추가 개발**

| 파일 | 할 일 |
| --- | --- |
| `features/deepwork/` | 딥워크 시작/종료 버튼, 세션 상태 표시 |
| `hooks/useNotifications.ts` | 알림 목록 상태 관리 연결 |
| `features/notifications/` | 알림 상태 변경 (읽음/보류) 기능 |
| 피드백 리포트 UI | 리포트 버튼 연결 및 동작 확인 |

---

# 🔑 09. 환경변수 목록 (.env)

> 아래는 초안입니다. 오늘 회의 후 MVP 범위에 따라 불필요한 항목 제거 예정
> 

```bash
# DB / Cache
DATABASE_URL=            # 동기, Alembic용
ASYNC_DATABASE_URL=      # 비동기, 앱 런타임용 (asyncpg)
REDIS_URL=

# Slack (P0 필수)
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
SLACK_SIGNING_SECRET=

# 아래는 오늘 회의 결과에 따라 포함 여부 결정
JIRA_CLIENT_ID=
JIRA_CLIENT_SECRET=
DISCORD_BOT_TOKEN=
DISCORD_APPLICATION_ID=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_PUBSUB_TOPIC=      # Gmail push 구조에 필요

# AI
ANTHROPIC_API_KEY=

# App
FRONTEND_URL=
BACKEND_URL=
```

---

# 🎬 10. MVP 데모 시나리오

> 발표/멘토링 자리에서 보여줄 8단계 흐름
> 

| Step | 화면/행동 | 멘트 포인트 |
| --- | --- | --- |
| 1 | 설정 화면 진입 | "여러 업무 계정을 한 화면에서 통합 관리하는 것이 핵심입니다." |
| 2 | Slack 워크스페이스 2개 연결
및 Jira 계정 1개 연동 | "1회성 연동이 아니라 다계정 구조를 전제로 설계했습니다." |
| 3 | 이벤트 유입 시연 | "웹훅은 빠르게 받고, AI 처리는 비동기로 분리해 안정성을 확보했습니다." |
| 4 | 대시보드 반영 | "중요도 분류와 한 줄 요약으로 읽어야 할 것만 빠르게 볼 수 있습니다." |
| 5 | 딥워크 시작 | "알림 앱이 아니라 집중 흐름을 지켜주는 도구로 포지셔닝합니다." |
| 6 | 딥워크 종료 + 브리핑 | "작업이 끝난 뒤 놓친 핵심만 다시 묶어 보여주는 것이 브리핑 가치입니다." |
| 7 | 리포트 버튼 클릭 | "이 피드백은 모델 정확도 개선용 내부 데이터 자산이 됩니다." |
| 8 | 확장 방향 소개 | "MVP는 Slack 중심으로 좁히고, 나머지는 확장 가능 구조만 확보했습니다." |

## 실패 대비 플랜

- 실시간 웹훅이 꼬이면 → mock notification으로 대체
- SSE가 불안정하면 → 새로고침 후 최신 상태 조회로 전환
- 브리핑은 사전 생성본 준비해서 설명에 집중

---

# 📌 11. 개발 첫날 체크리스트

> 해커톤 시작 후 **첫날 오전 내로 완료해야 전원 병렬 개발 가능**
> 
- [ ]  김선호: GitHub Repo + 브랜치 전략 세팅 완료
- [ ]  김선호: `.env.example` 작성 + `docker-compose up` 확인
- [ ]  오진우 + 이창현 + 김구: NotificationEvent 공통 모델 30분 합의 후 커밋
- [ ]  오진우 + 이창현 + 김구: **`notifications` AI 출력 필드 스펙 합의** (reason, suggested_action 등 추가 여부)
- [ ]  이창현: `chore/init-project-setup` 브랜치 코드 리븷, `.env` 설정 후 `alembic revision --autogenerate -m "initial"` 실행
- [ ]  문정현: `types/` 타입 정의 초안 작성 후 mock 데이터로 UI 시작
- [ ]  마수한: GitHub 칸반 태스크 카드 전원 배정 완료

---

> 🔗 관련 문서
> 

> - [API 및 기능 명세서](https://www.notion.so/32f14877c98b806f86e3c84e252b50f4?pvs=21)
> 

> - [Repo 구조 확정](https://www.notion.so/33014877c98b80999a0dde506d884530?pvs=21)
> 

> - [오늘 회의 결정 사항](https://www.notion.so/33214877c98b81eaa887d45997cde1bc?pvs=21)
>
