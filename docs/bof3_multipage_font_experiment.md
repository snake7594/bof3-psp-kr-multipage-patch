# BOF3 완성형 폰트 이미지 확장 보고서

## 결론

이번 경로는 조합형 렌더링이 아닙니다. 초성, 중성, 종성을 런타임에서 합성하지 않고, 한글 1글자마다 미리 그려 둔 12x12 완성형 비트맵 1칸을 사용합니다.

`ENDKANJI.EMI`를 확장해 441칸 페이지 3개, 총 1,323칸을 확보했고, 현재 번역에서 필요한 한글 1,147자를 모두 배치했습니다. `FIRST.EMI`와 `BATL_RET.EMI`에도 같은 세 페이지를 넣어 메뉴/전투 등 보조 폰트 경로에서도 같은 글리프가 보이게 했습니다.

## 검증 결과

- 선택 한글: 1,147자 / 고유 한글 1,147자
- 폰트 용량: 1,323칸
- 초과 한글: 0자
- 인코딩 대상 본문: 7,799개
- 인코딩 실패: 0개
- 주입 EMI 파일: 199개
- 변경 파일 수: 206개
- `BOOT.BIN`: 패치 적용
- `EBOOT.BIN`: 패치 적용
- `FIRST.EMI`: 완성형 한글 폰트 페이지 3개 적용
- `BATL_RET.EMI`: 완성형 한글 폰트 페이지 3개 적용

## 생성 파일

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

스크립트/중간 산출물 이름에는 이전 작업명인 `multipage`가 남아 있지만, 구현 방식은 완성형 폰트 이미지 확장입니다.

## 패치 핵심 파일

- `PSP_GAME/SYSDIR/BOOT.BIN`
  - 크기: 5,081,397 bytes
  - SHA-256: `0015A901D618341C8F43C08708E337A2DECE4D353F8BCB89D5A4999A757924B3`
- `PSP_GAME/SYSDIR/EBOOT.BIN`
  - 크기: 5,081,397 bytes
  - SHA-256: `0015A901D618341C8F43C08708E337A2DECE4D353F8BCB89D5A4999A757924B3`
- `PSP_GAME/USRDIR/JPN/ETC/ENDKANJI.EMI`
  - 크기: 133,120 bytes
  - SHA-256: `498DA59B249439EC6CC92CED7B35CBF21DB5FA5D14446B2B4F180F6C2E95986B`
- `PSP_GAME/USRDIR/JPN/ETC/FIRST.EMI`
  - 크기: 362,496 bytes
  - SHA-256: `FB75CB8326A9AA08DE3D5D2266E2416C6B421246B26478B75AC13F1E4E8DA96C`
- `PSP_GAME/USRDIR/JPN/BATTLE/BATL_RET.EMI`
  - 크기: 163,840 bytes
  - SHA-256: `C3475AE798809FDB6CE502977DFBC78B02C1CF86815645D2A2FFE39C01A84D06`

## 인코딩

핸들러는 다음 2바이트 lead bank를 사용합니다.

- `0x12`
- `0x13`
- `0x1e`
- `0x1f`
- `0x23`
- `0x24`

다음 바이트는 충돌 방지를 위해 보존했습니다.

- `0x20`: 기존 박스/제어 처리
- `0x21`: 실제 `!` 문자

주입 전 검사 결과:

- 잘못된 한글 lead 후보: 0개
- 생성 lead byte와 충돌하는 본문 문자: 0개
- 텍스트 섹션 내 raw `0x20`: 4개
- 텍스트 섹션 내 raw `0x21`: 3개

## ENDKANJI 구성

`ENDKANJI.EMI`를 2섹션에서 4섹션으로 확장했습니다. `FIRST.EMI`는 15섹션에서 16섹션으로, `BATL_RET.EMI`는 7섹션에서 9섹션으로 확장했습니다.

| 섹션 | 크기 | RAM 태그 | 텍스처 페이지 |
|---:|---:|---:|---:|
| 0 | `0x8000` | `0x1e000200` | 원본 보존 |
| 1 | `0x8000` | `0x1e080200` | `0x3f` |
| 2 | `0x8000` | `0x0a000200` | `0x25` |
| 3 | `0x8000` | `0x0c000200` | `0x26` |

## EBOOT 핸들러

기존 오프셋의 문자 분기에서 위 lead byte를 새 핸들러로 보냅니다. v0.4부터는 `BOOT.BIN`과 `EBOOT.BIN`을 모두 같은 패치 바이너리로 교체합니다.

핸들러 동작:

1. `lead + index` 2바이트를 읽습니다.
2. 완성형 글리프 번호로 변환합니다.
3. 대응 텍스처 페이지와 12x12 셀을 조회합니다.
4. 텍스처 페이지를 직접 선택합니다.
5. 게임의 기존 스프라이트 출력 함수로 글리프를 그립니다.
6. 이후 일반 FIRST 페이지로 복귀합니다.

## 남은 위험

정적 검증은 통과했습니다. 남은 핵심 위험은 추가 ENDKANJI 섹션 `0x0a000200`, `0x0c000200`이 실제 렌더링 중 기대한 텍스처 페이지로 정확히 로드되고 샘플링되는지입니다.
