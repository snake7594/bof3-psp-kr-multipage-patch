# Breath of Fire III PSP 한글패치 도구

PSP판 **Breath of Fire III** 한글패치 제작/배포용 저장소입니다.

현재 릴리스는 추가 폰트 페이지 접근 실험을 반영한 `v0.2.0-alpha`입니다.

## 현재 상태

- 현재 번역의 한글 1,147자를 손실 없이 수용합니다.
- 폰트 용량은 441칸 x 3페이지 = 1,323칸입니다.
- EBOOT에 6개 2바이트 lead bank를 처리하는 실험용 렌더링 핸들러를 추가했습니다.
- 대사 본문 7,799개 정적 인코딩 검증 결과 실패 0개입니다.
- 추가 텍스처 페이지 `0x25`, `0x26`의 실제 화면 출력은 아직 PPSSPP/PSP에서 런타임 확인이 필요합니다.

## 배포 원칙

이 저장소와 릴리스에는 다음 파일을 포함하지 않습니다.

- 원본 ISO
- 패치된 ISO
- 원본 게임 바이너리
- 패치된 `EBOOT.BIN`, `BOOT.BIN`, `.EMI` 게임 파일

배포는 `xdelta` 패치 방식입니다. 사용자는 본인이 보유한 정품 원본 ISO가 필요합니다.

## 빠른 적용 방법

릴리스의 `release-assets` 패키지를 사용하세요.

1. `release-assets` 폴더 안에 원본 ISO를 넣습니다.
2. 원본 ISO 파일 이름을 `Breath of Fire III.iso`로 맞춥니다.
3. `apply_iso_patch.bat`를 실행합니다.
4. `BOF3_KR_multipage_v0.2.0-alpha.iso`가 생성됩니다.

## 체크섬

| 항목 | 값 |
|---|---|
| 원본 ISO 파일명 | `Breath of Fire III.iso` |
| 원본 ISO 크기 | `403,963,904` bytes |
| 원본 ISO MD5 | `C7081C9C0865ECAEB6F4D2A42F865528` |
| 패치 후 ISO 파일명 | `BOF3_KR_multipage_v0.2.0-alpha.iso` |
| 패치 후 ISO 크기 | `404,197,376` bytes |
| 패치 후 ISO MD5 | `065E6C0E4554B96883733E1308C57670` |
| xdelta 패치 SHA-256 | `8CD86737EA5E296CB24BFF93FA7EA60492FC891AF1804E80E0E5242CB12A2139` |

## 개발/재생성 방법

ISO 패치가 아니라 추출된 `PSP_GAME` 트리에서 직접 재생성하려면 Python 3.12 이상과 의존성이 필요합니다.

```powershell
python -m pip install -r requirements.txt
python run_multipage_patch.py
```

`run_multipage_patch.py`는 깨끗한 원본 파일을 `.orig`로 보존한 뒤 다음 작업을 수행합니다.

- 1,147자 멀티페이지 한글 폰트 생성
- 실험용 EBOOT 핸들러 생성
- 한국어 대사 EMI 주입
- 기존 분석에서 확인한 2개 파일의 바이트 단위 보정 적용

## 폴더 구성

- `_ko/`: 현재 한국어 대사 텍스트
- `release-assets/`: xdelta 배포 파일
- `fonts/mulmaru/`: Mulmaru Mono 폰트 소스 데이터와 라이선스
- `docs/`: 분석/진행 보고서
- `reports/`: 검증 리포트와 한글 매핑 정보
- `assets/`: 폰트 미리보기 이미지

## 폰트 라이선스

폰트 생성에는 SIL Open Font License 1.1로 배포되는 Mulmaru Mono 데이터를 사용합니다.
자세한 내용은 `fonts/mulmaru/LICENSE.txt`를 확인하세요.
