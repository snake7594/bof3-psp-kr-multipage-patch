# BOF3 PSP 한글패치 v0.2.0-alpha 체크섬

## 원본 ISO

- 파일명: `Breath of Fire III.iso`
- 크기: `403,963,904` bytes
- MD5: `C7081C9C0865ECAEB6F4D2A42F865528`

## 패치 후 ISO

- 파일명: `BOF3_KR_multipage_v0.2.0-alpha.iso`
- 크기: `404,197,376` bytes
- MD5: `065E6C0E4554B96883733E1308C57670`

## xdelta 패치

- 파일명: `BOF3_KR_multipage_v0.2.0-alpha.iso.xdelta`
- 크기: `67,627,896` bytes
- MD5: `05EA524127FBE24323EBE9C231D14555`
- SHA-256: `8CD86737EA5E296CB24BFF93FA7EA60492FC891AF1804E80E0E5242CB12A2139`

## xdelta 실행 파일

- 파일명: `xdelta.exe`
- 크기: `624,463` bytes
- MD5: `93110BD8EAA3BE753E03DB56765F49A2`
- SHA-256: `6855C01CF4A1662BA421E6F95370CF9AFA2B3AB6C148473C63EFE60D634DFB9A`

## 검증

`xdelta.exe -d -s "Breath of Fire III.iso" "BOF3_KR_multipage_v0.2.0-alpha.iso.xdelta" "BOF3_KR_multipage_v0.2.0-alpha.iso"` 명령으로 복원한 ISO의 MD5가 `065E6C0E4554B96883733E1308C57670`임을 확인했습니다.
