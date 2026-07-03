# BOF3 멀티페이지 한글 폰트 실험 보고서

## 결과

- 실험용 멀티페이지 완성형 한글 경로를 만들고 작업 트리에 배치했습니다.
- 현재 `_ko` 번역은 손실 치환 없이 전부 수용됩니다.
- 선택된 한글: 1,147자 / 1,147자
- 폰트 용량: 1,323칸 = 441칸 x 3 텍스처 페이지
- 초과 한글: 0자, 0회
- 인코딩한 대사 본문: 7,799개
- 인코딩 실패: 0개
- 주입한 EMI 파일: 199개

## 핵심 파일

- `BOOT_multipage.BIN`
- `ENDKANJI_multipage.EMI`
- `multipage_map.json`
- `multipage_encoding_report.json`
- `multipage_font_preview.png`
- `build_multipage_font.py`
- `build_eboot_multipage.py`
- `inject_multipage.py`
- `validate_multipage_encoding.py`
- `build_multipage_pipeline.py`

## 배치된 파일 해시

- `PSP_GAME/SYSDIR/EBOOT.BIN`
  - 크기: 5,081,397 bytes
  - SHA-256: `0015A901D618341C8F43C08708E337A2DECE4D353F8BCB89D5A4999A757924B3`
- `PSP_GAME/USRDIR/JPN/ETC/ENDKANJI.EMI`
  - 크기: 133,120 bytes
  - SHA-256: `498DA59B249439EC6CC92CED7B35CBF21DB5FA5D14446B2B4F180F6C2E95986B`

## 인코딩

새 핸들러는 다음 2바이트 lead bank를 사용합니다.

- `0x12`
- `0x13`
- `0x1e`
- `0x1f`
- `0x23`
- `0x24`

다음 바이트는 충돌 방지를 위해 보존했습니다.

- `0x20`: 기존 박스/기호 처리
- `0x21`: 실제 `!` 문자

주입 후 스캔 결과:

- 잘못된 한글 lead 슬롯: 0개
- 활성 lead byte와 충돌하는 원문 문자: 0개
- 텍스트 섹션 내 raw `0x20`: 4개
- 텍스트 섹션 내 raw `0x21`: 3개

## ENDKANJI 구성

`ENDKANJI.EMI`를 2섹션에서 4섹션으로 확장했습니다.

| 섹션 | 크기 | RAM 태그 | 텍스처 페이지 |
|---:|---:|---:|---:|
| 0 | `0x8000` | `0x1e000200` | 원본 보존 |
| 1 | `0x8000` | `0x1e080200` | `0x3f` |
| 2 | `0x8000` | `0x0a000200` | `0x25` |
| 3 | `0x8000` | `0x0c000200` | `0x26` |

## EBOOT 핸들러

점프테이블에서 다음 lead byte를 새 핸들러 `0x373670`으로 보냅니다.

- `0x12`, `0x13`, `0x1e`, `0x1f`, `0x23`, `0x24`

새 핸들러 동작:

1. `lead + index`를 읽습니다.
2. compact 한글 슬롯으로 변환합니다.
3. 대상 텍스처 페이지와 12x12 셀을 조회합니다.
4. 텍스처 페이지를 직접 선택합니다.
5. 게임의 기존 스프라이트 출력 함수로 글리프를 그립니다.
6. 이후 일반 FIRST 페이지로 복귀합니다.

## 남은 위험

정적 검증은 통과했지만 아직 PPSSPP/PSP 화면 검증은 하지 않았습니다.
남은 핵심 위험은 추가 ENDKANJI 섹션 `0x0a000200`, `0x0c000200`이 실제 렌더링 중 기대한 텍스처 페이지로 정확히 로드/샘플링되는지입니다.
