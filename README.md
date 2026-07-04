# Breath of Fire III PSP 한국어 패치

PSP판 **Breath of Fire III** 한국어 패치 준비/배포 저장소입니다.

현재 릴리스는 `v0.3.0-alpha`입니다. 이번 버전의 목표는 조합형 렌더링이 아니라, **완성형 한글 폰트 이미지를 확장해서 한글 1글자당 12x12 비트맵 1칸으로 출력**하는 것입니다.

## 현재 상태

- 런타임 조합형이 아닙니다. 초성/중성/종성을 합성하지 않습니다.
- `ENDKANJI.EMI`를 확장해 441칸 페이지 3개, 총 1,323칸을 사용합니다.
- 현재 번역 전체에서 필요한 완성형 한글 1,147자를 모두 폰트 이미지로 배치했습니다.
- 전체 대사 7,799개 본문 인코딩 검증 결과 누락 0개, 실패 0개입니다.
- `FIRST.EMI`와 `BATL_RET.EMI`는 이번 패치 ISO에서 원본과 동일하게 유지됩니다.
- 추가 텍스처 페이지 `0x25`, `0x26`의 실제 화면 출력은 PPSSPP/PSP 실기 확인이 계속 필요합니다.

## 배포 방식

저장소와 GitHub 릴리스에는 원본 ISO, 패치 후 ISO, 게임 바이너리 원본 파일을 포함하지 않습니다.

배포는 `xdelta` 패치 방식입니다. 사용자는 본인이 보유한 정품 원본 ISO가 필요합니다.

## 빠른 적용 방법

릴리스의 `release-assets` 패키지를 사용하세요.

1. `release-assets` 폴더 안에 원본 ISO를 넣습니다.
2. 원본 ISO 파일 이름을 `Breath of Fire III.iso`로 맞춥니다.
3. `apply_iso_patch.bat`를 실행합니다.
4. `BOF3_KR_fontimage_v0.3.0-alpha.iso`가 생성됩니다.

## 체크섬

| 항목 | 값 |
|---|---|
| 원본 ISO 파일명 | `Breath of Fire III.iso` |
| 원본 ISO 크기 | `403,963,904` bytes |
| 원본 ISO MD5 | `C7081C9C0865ECAEB6F4D2A42F865528` |
| 패치 후 ISO 파일명 | `BOF3_KR_fontimage_v0.3.0-alpha.iso` |
| 패치 후 ISO 크기 | `404,197,376` bytes |
| 패치 후 ISO MD5 | `F56F7BE465B394B84C5F8F41932D94BA` |
| xdelta 패치 SHA-256 | `50C44FF16042493E6AD6B38FFC117A13EB60D1EF324E5C5E48DA9F9344C97480` |

## 개발/재생성 방법

ISO 패치가 아니라 추출된 `PSP_GAME` 트리에서 직접 재생성하려면 Python 3.12 이상과 의존성이 필요합니다.

```powershell
python -m pip install -r requirements.txt
python run_fontimage_patch.py
```

`run_fontimage_patch.py`는 내부 호환용 `run_multipage_patch.py`를 호출합니다. 일부 내부 파일명에는 이전 작업명인 `multipage`가 남아 있지만, 현재 경로는 완성형 폰트 이미지 확장 방식입니다.

`run_fontimage_patch.py`는 깨끗한 원본 파일을 `.orig`로 보존한 뒤 다음 작업을 수행합니다.

- 완성형 한글 1,147자 폰트 이미지 생성
- 확장 폰트 페이지 접근용 EBOOT 핸들러 생성
- 한국어 대사 EMI 주입
- 기존 분석에서 확인된 2개 파일의 byte 단위 보정 적용

## 폴더 구성

- `_ko/`: 현재 한국어 대사 텍스트
- `release-assets/`: xdelta 배포 파일
- `fonts/mulmaru/`: Mulmaru Mono 폰트 소스 데이터와 라이선스
- `docs/`: 분석/진행 보고서
- `reports/`: 인코딩 리포트와 한글 매핑 정보
- `assets/`: 폰트 미리보기 이미지

## 폰트 라이선스

폰트 생성에는 SIL Open Font License 1.1로 배포되는 Mulmaru Mono 데이터를 사용합니다.
자세한 내용은 `fonts/mulmaru/LICENSE.txt`를 확인하세요.
